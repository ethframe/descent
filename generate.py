from descent.parser import parser
from descent.source import source, hooks
from descent.convert import convert_to_dict
from descent.typeinference import infer_types
from descent.codegen import (
    gen_python_class, gen_ast_module, gen_ast_module_src
)
from descent.combinators import compile_parser


def generate():
    grammar = convert_to_dict(parser.parse(source))
    types = infer_types(grammar)

    new_parser = compile_parser(grammar, gen_ast_module(types), hooks)
    grammar = convert_to_dict(new_parser.parse(source))
    types = infer_types(grammar)

    with open("descent/ast.py", "w") as fp:
        fp.write(gen_ast_module_src(types))

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
