from descent.parser import parser
from descent.source import source
from descent.convert import convert_to_dict
from descent.typeinference import infer_types
from descent.codegen import gen_python_class


def generate():
    grammar = convert_to_dict(parser.parse(source))
    types = infer_types(grammar)
    classes = [gen_python_class(type_) for type_ in types]
    with open("descent/ast.py", "w") as fp:
        fp.write("\n".join(classes))

    with open("descent/grammar.py", "w") as fp:
        fp.write("from collections import OrderedDict\n\n")
        fp.write(
            "from .ast import "
            + ", ".join(type_.name for type_ in types) + "\n\n\n"
        )
        fp.write("grammar = OrderedDict([\n")
        for name, expr in grammar.items():
            fp.write("    ({!r}, {!r}),\n".format(name, expr))
        fp.write("])\n")


if __name__ == '__main__':
    generate()
