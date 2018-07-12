import sys

from descent.asttypes import NamedType, TokenType, NodeType


def _indent(lines):
    for line in lines:
        if isinstance(line, list):
            for indented in _indent(line):
                yield "    " + indented if indented else ""
        else:
            yield line


def _concat(lines):
    return "\n".join(_indent(lines))


def _fmt_each(fmt, it):
    return [fmt.format(i) for i in it]


def _fmt_and_join(fmt, it, j):
    return j.join(_fmt_each(fmt, it))


def _defm(name, args, body):
    return ["def {}({}):".format(name, ", ".join(["self"] + args)), body, ""]


def gen_namedtype(tp):
    return _concat([
        "class {}:".format(tp.name),
        _defm("__repr__", [], ["return '{}()'".format(tp.name)]),
        _defm("__hash__", [], ["return hash(self.__class__)"]),
        _defm("__eq__", ["other"], [
            "return self.__class__ is other.__class__"
        ]),
        _defm("unapply1", [], ["return self"]),
        _defm("unapply", [], ["return (self,)"]),
        _defm("copy", [], ["return self"]),
        _defm("splice_to", ["other"], ["return other"]),
        ""
    ])


def gen_tokentype(tp):
    return _concat([
        "class {}:".format(tp.name),
        _defm("__init__", ["val=''"], ["self.val = val"]),
        _defm("__str__", [], ["return self.val"]),
        _defm("__repr__", [], [
            "return '{}({{!r}})'.format(self.val)".format(tp.name)
        ]),
        _defm("__hash__", [], ["return hash((self.__class__, self.val))"]),
        _defm("__eq__", ["other"], [
            "return self.__class__ is other.__class__"
            + " and self.val == other.val"
        ]),
        _defm("unapply1", [], ["return self.val"]),
        _defm("unapply", [], ["return (self.val,)"]),
        _defm("copy", [], ["return {}(self.val)".format(tp.name)]),
        _defm("consume", ["val"], ["self.val += val", "return self"]),
        _defm("splice_to", ["other", "converters"], [
            "converter = converters.get('{}')".format(tp.name),
            "if converter:",
            ["return other.consume(converter(self.val))"],
            "return other.consume(self.val)"
        ]),
        ""
    ])


def gen_nodetype(tp):
    lines = ["class {}:".format(tp.name)]
    if len(tp.fields) == 1:
        lines.extend([
            ["__slots__ = ('{}',)".format(list(tp.fields)[0])],
            ""
        ])
    else:
        lines.extend([
            ["__slots__ = ({})".format(
                _fmt_and_join("'{}'", tp.fields, ", ")
            )],
            ""
        ])
    lines.extend([
        ["def __init__(self, {}):".format(
            _fmt_and_join("{}=None", tp.fields, ", ")
        ),
            ["self.{0} = {0} or []".format(name)
             if tp.fields[name].arr else
             "self.{0} = {0}".format(name)
             for name in tp.fields],
            "",
            "def __repr__(self):",
            ["return '{}({})'.format(".format(
                tp.name,
                ", ".join(["{!r}"] * len(tp.fields))
            ),
            _fmt_each("self.{},", tp.fields),
            ")"],
            "",
            "def __eq__(self, other):",
            [
                "return (",
                [
                    "self.__class__ is other.__class__",
                    *_fmt_each("and self.{0} == other.{0}", tp.fields)
                ],
                ")"
            ],
            "",
            "def unapply1(self):",
            ["return self.{}".format(list(tp.fields)[0])
             if len(tp.fields) == 1 else
             "return self"],
            "",
            "def unapply(self):",
            ["return (self.{},)".format(list(tp.fields)[0])
             if len(tp.fields) == 1 else
             "return ({})".format(
                _fmt_and_join("self.{}", tp.fields, ", ")
            )],
            "",
            "def copy(self):",
            ["return {}(".format(tp.name),
             ["list(self.{}),".format(name)
              if tp.fields[name].arr else
              "self.{},".format(name)
              for name in tp.fields],
             ")"],
            ""]
    ])
    for name, field in tp.fields.items():
        lines.append([
            "def append_{}(self, val):".format(name),
            ["self.{}.append(val)".format(name)
             if field.arr else
             "self.{} = val".format(name),
             "return self"],
            ""
        ])
        if field.arr:
            lines.append([
                "def extend_{}(self, val):".format(name),
                ["self.{}.extend(val)".format(name),
                 "return self"],
                ""
            ])
    lines.append([
        "def splice_to(self, other, hooks):"
    ])
    for name, field in tp.fields.items():
        if field.arr:
            lines.append(
                "        other.extend_{0}(self.{0})".format(name)
            )
        elif field.opt:
            lines.extend([
                "        if self.{} is not None:".format(name),
                "            other.append_{0}(self.{0})".format(name)
            ])
        else:
            lines.append(
                "        other.append_{0}(self.{0})".format(name)
            )
    lines.extend([
        "        return other",
        "",
        ""
    ])
    return _concat(lines)


def gen_python_class(tp):
    if isinstance(tp, NamedType):
        return gen_namedtype(tp)
    elif isinstance(tp, TokenType):
        return gen_tokentype(tp)
    elif isinstance(tp, NodeType):
        return gen_nodetype(tp)
    raise ValueError(tp)


def gen_types_map(types):
    lines = ["types_map = {"]
    for t in types:
        lines.append("   {0!r}: {0},".format(t.name))
    lines.append("}")
    return "\n".join(lines)


def gen_ast_module_src(types):
    elements = []
    for t in types:
        elements.append(gen_python_class(t))
    elements.append(gen_types_map(types))
    return "\n".join(elements)


def gen_ast_module(types):
    src = gen_ast_module_src(types)
    module = type(sys)("ast")
    exec(src, module.__dict__, module.__dict__)
    return getattr(module, "types_map")
