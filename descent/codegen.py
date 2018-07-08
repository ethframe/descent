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
        _defm("get_value", [], ["return self"]),
        _defm("get_values", [], ["return (self,)"]),
        _defm("splice_to", ["other"], ["return other"]),
        _defm("copy", [], ["return self"]),
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
        _defm("get_value", [], ["return self.val"]),
        _defm("get_values", [], ["return (self.val,)"]),
        _defm("consume", ["val"], ["self.val += val", "return self"]),
        _defm("splice_to", ["other", "hooks"], [
            "hook = hooks.get('{}')".format(tp.name),
            "if hook:",
            ["return other.consume(hook(self.val))"],
            "return other.consume(self.val)"
        ]),
        _defm("copy", [], ["return {}(self.val)".format(tp.name)]),
        ""
    ])


def gen_nodetype(tp):
    field_names = tp.order
    lines = ["class {}:".format(tp.name)]
    if len(tp.fields) == 1:
        lines.extend([
            ["__slots__ = ('{}',)".format(field_names[0])],
            ""
        ])
    else:
        lines.extend([
            ["__slots__ = ({})".format(
                _fmt_and_join("'{}'", field_names, ", ")
            )],
            ""
        ])
    lines.extend([
        ["def __init__(self, {}):".format(
            _fmt_and_join("{}=None", field_names, ", ")
        ),
            ["self.{0} = {0} or []".format(name)
             if tp.fields[name].arr else
             "self.{0} = {0}".format(name)
             for name in field_names],
            "",
            "def __repr__(self):",
            ["return '{}({})'.format(".format(
                tp.name,
                ", ".join(["{!r}"] * len(field_names))
            ),
            _fmt_each("self.{},", field_names),
            ")"],
            "",
            "def __eq__(self, other):",
            [
                "return (",
                [
                    "self.__class__ is other.__class__",
                    *_fmt_each("and self.{0} == other.{0}", field_names)
                ],
                ")"
            ],
            "",
            "def get_value(self):",
            ["return self.{}".format(field_names[0])
             if len(field_names) == 1 else
             "return self"],
            "",
            "def get_values(self):",
            ["return (self.{},)".format(field_names[0])
             if len(field_names) == 1 else
             "return ({})".format(
                _fmt_and_join("self.{}", field_names, ", ")
            )],
            "",
            "def copy(self):",
            ["return {}(".format(tp.name),
             ["list(self.{}),".format(name)
              if tp.fields[name].arr else
              "self.{},".format(name)
              for name in field_names],
             ")"],
            ""]
    ])
    for name in field_names:
        field = tp.fields[name]
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
                "def appendmany_{}(self, val):".format(name),
                ["self.{}.extend(val)".format(name),
                 "return self"],
                ""
            ])
    lines.append([
        "def splice_to(self, other, hooks):"
    ])
    for name in field_names:
        field = tp.fields[name]
        if field.arr:
            lines.append(
                "        other.appendmany_{0}(self.{0})".format(name)
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


def gen_ast_module(types):
    classes = []
    for t in types:
        classes.append(gen_python_class(t))
    module = type(sys)("ast")
    exec("\n".join(classes), module.__dict__, module.__dict__)
    return module
