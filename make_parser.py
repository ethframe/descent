from argparse import ArgumentParser

from descent.parser import parser
from descent.convert import convert_to_dict
from descent.grammarcheck import check_grammar, get_invalid
from descent.typeinference import infer_types
from descent.codegen import gen_ast_module_src
from descent.macro import expand_macros


def generate(input):
    parsed = parser.parse(input)
    if parsed is None:
        raise ValueError("Invald grammar")
    expanded = expand_macros(parsed)
    grammar = convert_to_dict(expanded)
    invalid = get_invalid(check_grammar(grammar))
    if invalid:
        raise ValueError("Invalid rules: {}".format(", ".join(invalid)))
    types = infer_types(grammar)

    yield "from collections import OrderedDict\n"
    yield "from descent.ast import *"
    yield "from descent.combinators import compile_parser\n\n"
    yield gen_ast_module_src(types)
    yield ""
    yield ""
    yield "parsed_grammar = OrderedDict(["
    for name, body in grammar.items():
        yield "    ({!r}, {!r}),".format(name, body)
    yield "])\n\n"
    yield "parser = compile_parser(parsed_grammar, types_map)"


def main():
    argparser = ArgumentParser()
    argparser.add_argument("input", help="Input file")
    argparser.add_argument("output", help="Output file")
    args = argparser.parse_args()
    with open(args.input) as inf, open(args.output, "w") as outf:
        for line in generate(inf.read()):
            outf.write(line)
            outf.write("\n")


if __name__ == '__main__':
    main()
