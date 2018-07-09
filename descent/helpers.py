from descent.codegen import gen_ast_module
from descent.combinators import compile_parser
from descent.convert import convert_to_dict
from descent.grammarcheck import check_grammar, get_invalid
from descent.parser import parser
from descent.macro import expand_macros
from descent.typeinference import infer_types


def parser_from_source(src, hooks=None):
    parsed = parser.parse(src)
    expanded = expand_macros(parsed)
    grammar = convert_to_dict(expanded)
    invalid = get_invalid(check_grammar(grammar))
    if invalid:
        raise ValueError(
            "Following rules are invalid: {}".format(", ".join(invalid))
        )
    types = infer_types(grammar)
    if types is None:
        raise ValueError("Got invalid type")
    ast = gen_ast_module(types)
    return compile_parser(grammar, ast, hooks)
