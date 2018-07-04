class octal:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'octal({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def get_value(self):
        return self.val

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, hooks):
        hook = hooks.get('octal')
        if hook:
            return other.consume(hook(self.val))
        return other.consume(self.val)

    def copy(self):
        return octal(self.val)


class escape:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'escape({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def get_value(self):
        return self.val

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, hooks):
        hook = hooks.get('escape')
        if hook:
            return other.consume(hook(self.val))
        return other.consume(self.val)

    def copy(self):
        return escape(self.val)


class char:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'char({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def get_value(self):
        return self.val

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, hooks):
        hook = hooks.get('char')
        if hook:
            return other.consume(hook(self.val))
        return other.consume(self.val)

    def copy(self):
        return char(self.val)


class char_any:
    def __repr__(self):
        return 'char_any()'

    def __hash__(self):
        return hash(self.__class__)

    def __eq__(self, other):
        return self.__class__ is other.__class__

    def get_value(self):
        return self

    def splice_to(self, other):
        return other

    def copy(self):
        return self


class reference:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'reference({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def get_value(self):
        return self.val

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, hooks):
        hook = hooks.get('reference')
        if hook:
            return other.consume(hook(self.val))
        return other.consume(self.val)

    def copy(self):
        return reference(self.val)


class top_splice:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'top_splice({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return top_splice(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class ignore:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'ignore({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return ignore(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class splice:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'splice({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return splice(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class string:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'string({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def get_value(self):
        return self.val

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, hooks):
        hook = hooks.get('string')
        if hook:
            return other.consume(hook(self.val))
        return other.consume(self.val)

    def copy(self):
        return string(self.val)


class fail:
    def __repr__(self):
        return 'fail()'

    def __hash__(self):
        return hash(self.__class__)

    def __eq__(self, other):
        return self.__class__ is other.__class__

    def get_value(self):
        return self

    def splice_to(self, other):
        return other

    def copy(self):
        return self


class char_range:
    __slots__ = ('end', 'start')

    def __init__(self, end=None, start=None):
        self.end = end
        self.start = start

    def __repr__(self):
        return 'char_range({!r}, {!r})'.format(
            self.end,
            self.start,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.end == other.end
            and self.start == other.start
        )

    def get_value(self):
        return self

    def copy(self):
        return char_range(
            self.end,
            self.start,
        )

    def append_end(self, val):
        self.end = val
        return self

    def append_start(self, val):
        self.start = val
        return self

    def splice_to(self, other, hooks):
        other.append_end(self.end)
        other.append_start(self.start)
        return other


class repeat1:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'repeat1({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return repeat1(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class repeat:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'repeat({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return repeat(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class optional:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'optional({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return optional(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class top:
    __slots__ = ('expr', 'name')

    def __init__(self, expr=None, name=None):
        self.expr = expr
        self.name = name

    def __repr__(self):
        return 'top({!r}, {!r})'.format(
            self.expr,
            self.name,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
            and self.name == other.name
        )

    def get_value(self):
        return self

    def copy(self):
        return top(
            self.expr,
            self.name,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def append_name(self, val):
        self.name = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        other.append_name(self.name)
        return other


class append:
    __slots__ = ('expr', 'name')

    def __init__(self, expr=None, name=None):
        self.expr = expr
        self.name = name

    def __repr__(self):
        return 'append({!r}, {!r})'.format(
            self.expr,
            self.name,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
            and self.name == other.name
        )

    def get_value(self):
        return self

    def copy(self):
        return append(
            self.expr,
            self.name,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def append_name(self, val):
        self.name = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        other.append_name(self.name)
        return other


class node:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'node({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def get_value(self):
        return self.val

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, hooks):
        hook = hooks.get('node')
        if hook:
            return other.consume(hook(self.val))
        return other.consume(self.val)

    def copy(self):
        return node(self.val)


class follow:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'follow({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return follow(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class not_follow:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'not_follow({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def get_value(self):
        return self.expr

    def copy(self):
        return not_follow(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class sequence:
    __slots__ = ('items',)

    def __init__(self, items=None):
        self.items = items or []

    def __repr__(self):
        return 'sequence({!r})'.format(
            self.items,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.items == other.items
        )

    def get_value(self):
        return self.items

    def copy(self):
        return sequence(
            list(self.items),
        )

    def append_items(self, val):
        self.items.append(val)
        return self

    def appendmany_items(self, val):
        self.items.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.appendmany_items(self.items)
        return other


class choice:
    __slots__ = ('items',)

    def __init__(self, items=None):
        self.items = items or []

    def __repr__(self):
        return 'choice({!r})'.format(
            self.items,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.items == other.items
        )

    def get_value(self):
        return self.items

    def copy(self):
        return choice(
            list(self.items),
        )

    def append_items(self, val):
        self.items.append(val)
        return self

    def appendmany_items(self, val):
        self.items.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.appendmany_items(self.items)
        return other


class rule:
    __slots__ = ('expr', 'name')

    def __init__(self, expr=None, name=None):
        self.expr = expr
        self.name = name

    def __repr__(self):
        return 'rule({!r}, {!r})'.format(
            self.expr,
            self.name,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
            and self.name == other.name
        )

    def get_value(self):
        return self

    def copy(self):
        return rule(
            self.expr,
            self.name,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def append_name(self, val):
        self.name = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        other.append_name(self.name)
        return other


class grammar:
    __slots__ = ('rules',)

    def __init__(self, rules=None):
        self.rules = rules or []

    def __repr__(self):
        return 'grammar({!r})'.format(
            self.rules,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.rules == other.rules
        )

    def get_value(self):
        return self.rules

    def copy(self):
        return grammar(
            list(self.rules),
        )

    def append_rules(self, val):
        self.rules.append(val)
        return self

    def appendmany_rules(self, val):
        self.rules.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.appendmany_rules(self.rules)
        return other

