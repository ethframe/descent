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


def _fmt_iter(fmt, it):
    return [fmt.format(i) for i in it]


def _fmt_and_join(fmt, it, sep=", "):
    return sep.join(_fmt_iter(fmt, it))


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
        _defm("to_dict", [], ["return {{'__type__': {!r}}}".format(tp.name)]),
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
        _defm("to_dict", [], [
            "return {{'__type__': {!r}, 'value': self.val}}".format(tp.name)
        ]),
        ""
    ])


def gen_nodetype(tp):
    lines = [
        "class {}:".format(tp.name),
        [
            "__slots__ = ({!r},)".format(list(tp.fields)[0])
            if len(tp.fields) == 1 else
            "__slots__ = ({})".format(_fmt_and_join("{!r}", tp.fields)),
            ""
        ],
        _defm("__init__", _fmt_iter("{}=None", tp.fields), [
            (
                "self.{0} = {0} or []" if field.arr else "self.{0} = {0}"
            ).format(name)
            for name, field in tp.fields.items()
        ]),
        _defm("__repr__", [], [
            "return '{}({})'.format(".format(
                tp.name, ", ".join(["{!r}"] * len(tp.fields))
            ),
            _fmt_iter("self.{},", tp.fields),
            ")"
        ]),
        _defm("__eq__", ["other"], [
            "return (",
            ["self.__class__ is other.__class__"],
            _fmt_iter("and self.{0} == other.{0}", tp.fields),
            ")"
        ]),
        _defm("unapply1", [], [
            "return self.{}".format(list(tp.fields)[0])
            if len(tp.fields) == 1 else
            "return self"
        ]),
        _defm("unapply", [], [
            "return (self.{},)".format(list(tp.fields)[0])
            if len(tp.fields) == 1 else
            "return ({})".format(_fmt_and_join("self.{}", tp.fields, ", "))
        ]),
        _defm("copy", [], [
            "return {}(".format(tp.name),
            [
                (
                    "list(self.{})," if tp.fields[name].arr else "self.{},"
                ).format(name) for name in tp.fields
            ],
            ")"
        ])
    ]
    for name, field in tp.fields.items():
        lines.append(
            _defm("append_{}".format(name), ["val"], [
                (
                    "self.{}.append(val)" if field.arr else "self.{} = val"
                ).format(name),
                "return self"
            ])
        )
        if field.arr:
            lines.append(
                _defm("extend_{}".format(name), ["val"], [
                    "self.{}.extend(val)".format(name),
                    "return self"
                ])
            )
    body = []
    for name, field in tp.fields.items():
        if field.arr:
            body.append("other.extend_{0}(self.{0})".format(name))
        elif field.opt:
            body.extend([
                "if self.{} is not None:".format(name),
                ["other.append_{0}(self.{0})".format(name)]
            ])
        else:
            body.append("other.append_{0}(self.{0})".format(name))
    body.append("return other")
    lines.append(_defm("splice_to", ["other", "converters"], body))
    body = ["'__type__': {!r},".format(tp.name)]
    for name, field in tp.fields.items():
        if field.arr:
            body.append("{0!r}: [i.to_dict() for i in self.{0}],".format(name))
        elif field.opt:
            body.append(
                "{0!r}: None if self.{0} is None"
                " else self.{0}.to_dict(),".format(name)
            )
        else:
            body.append("{0!r}: self.{0}.to_dict(),".format(name))
    lines.extend([_defm("to_dict", [], ["return {", body, "}"]), ""])
    return _concat(lines)


def gen_python_class(tp):
    return {
        NamedType: gen_namedtype,
        TokenType: gen_tokentype,
        NodeType: gen_nodetype,
    }[tp.__class__](tp)


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
