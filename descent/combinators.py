from descent.case import CaseVal


class Tree:
    def copy(self):
        return self


class Empty(Tree):
    pass


class Ignore(Tree):
    def consume(self, val):
        return self


class Rule:
    def __init__(self, name):
        self.name = name
        self.body = None

    def define(self, body):
        self.body = body

    def __call__(self, stream, pos, tree):
        return self.body(stream, pos, tree)

    def parse(self, stream):
        return self(stream, 0, Empty())[1]


def sequence(*subparsers):
    def _parser(stream, pos, tree):
        org = pos
        for parser in subparsers:
            pos, tree = parser(stream, pos, tree)
            if tree is None:
                return org, None
        return pos, tree
    return _parser


def choice(*subparsers):
    def _parser(stream, pos, tree):
        for parser in subparsers:
            new_pos, new_tree = parser(stream, pos, tree.copy())
            if new_tree is not None:
                return new_pos, new_tree
        return pos, None
    return _parser


def repeat(parser):
    def _parser(stream, pos, tree):
        while True:
            current = pos, tree
            pos, tree = parser(stream, pos, tree)
            if tree is None:
                return current
    return _parser


def repeat1(parser):
    def _parser(stream, pos, tree):
        pos, tree = parser(stream, pos, tree)
        if tree is None:
            return pos, None
        while True:
            current = pos, tree
            pos, tree = parser(stream, pos, tree)
            if tree is None:
                return current
    return _parser


def optional(parser):
    def _parser(stream, pos, tree):
        new_pos, new_tree = parser(stream, pos, tree)
        if new_tree is None:
            return pos, tree
        return new_pos, new_tree
    return _parser


def not_follow(parser):
    def _parser(stream, pos, tree):
        _, new_tree = parser(stream, pos, Ignore())
        if new_tree is None:
            return pos, tree
        return pos, None
    return _parser


def follow(parser):
    def _parser(stream, pos, tree):
        _, new_tree = parser(stream, pos, Ignore())
        if new_tree is None:
            return pos, None
        return pos, tree
    return _parser


def node(name, classes):
    cls = classes[name]

    def _parser(stream, pos, tree):
        return pos, cls()
    return _parser


def append(parser, name):
    method = "append_" + name

    def _parser(stream, pos, tree):
        new_pos, subtree = parser(stream, pos, Empty())
        if subtree is None:
            return pos, None
        if isinstance(tree, Ignore):
            return new_pos, tree
        return new_pos, getattr(tree, method)(subtree)
    return _parser


def top(parser, name):
    method = "append_" + name

    def _parser(stream, pos, tree):
        new_pos, top_tree = parser(stream, pos, Empty())
        if top_tree is None:
            return pos, None
        if isinstance(tree, Ignore):
            return new_pos, tree
        return new_pos, getattr(top_tree, method)(tree)
    return _parser


def splice(parser, splice_hooks):
    def _parser(stream, pos, tree):
        new_pos, subtree = parser(stream, pos, Empty())
        if subtree is None:
            return pos, None
        return new_pos, subtree.splice_to(tree, splice_hooks)
    return _parser


def top_splice(parser, splice_hooks):
    def _parser(stream, pos, tree):
        new_pos, top_tree = parser(stream, pos, Empty())
        if top_tree is None:
            return pos, None
        return new_pos, tree.splice_to(top_tree, splice_hooks)
    return _parser


def ignore(parser):
    def _parser(stream, pos, tree):
        new_pos, new_tree = parser(stream, pos, Ignore())
        if new_tree is None:
            return pos, None
        return new_pos, tree
    return _parser


def char_sequence(val):
    def _parser(stream, pos, tree):
        if pos + len(val) <= len(stream) and stream.startswith(val, pos):
            return pos + len(val), tree.consume(val)
        return pos, None
    return _parser


def char_range(start, end):
    def _parser(stream, pos, tree):
        if pos < len(stream) and start <= stream[pos] <= end:
            return pos + 1, tree.consume(stream[pos])
        return pos, None
    return _parser


def char_any(stream, pos, tree):
    if pos < len(stream):
        return pos + 1, tree.consume(stream[pos])
    return pos, None


class Compiler(CaseVal):
    def char_any(self, val):
        return char_any

    def string(self, val):
        return char_sequence(val)

    def char(self, val):
        return char_sequence(val)

    def char_range(self, val):
        return char_range(str(val.start), str(val.end))

    def sequence(self, val):
        return sequence(*(self(v) for v in val))

    def choice(self, val):
        return choice(*(self(v) for v in val))

    def repeat(self, val):
        return repeat(self(val))

    def repeat1(self, val):
        return repeat1(self(val))

    def optional(self, val):
        return optional(self(val))

    def not_follow(self, val):
        return not_follow(self(val))

    def follow(self, val):
        return follow(self(val))

    def reference(self, val):
        return self.rules[val]

    def node(self, val):
        return node(val, self.classes)

    def append(self, val):
        return append(self(val.expr), str(val.name))

    def top(self, val):
        return top(self(val.expr), str(val.name))

    def splice(self, val):
        return splice(self(val), self.splice_hooks)

    def top_splice(self, val):
        return top_splice(self(val), self.splice_hooks)

    def ignore(self, val):
        return ignore(self(val))


class DictWrapper:
    def __init__(self, module):
        self.module = module

    def __getitem__(self, item):
        return getattr(self.module, item)


def compile_parser(gram, ast_module, splice_hooks=None):
    rules = {k: Rule(k) for k in gram}
    case = Compiler(
        rules=rules,
        classes=DictWrapper(ast_module),
        splice_hooks=splice_hooks or {}
    )
    for rule, body in gram.items():
        rules[rule].define(case(body))
    return rules[list(gram)[0]]
