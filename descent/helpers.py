from descent.codegen import gen_ast_module
from descent.combinators import compile_parser
from descent.convert import convert_to_dict
from descent.parser import parser
from descent.typeinference import infer_types


def parser_from_source(src, hooks):
    parsed = parser.parse(src)
    grammar = convert_to_dict(parsed)
    types = infer_types(grammar)
    ast = gen_ast_module(types)
    return compile_parser(grammar, ast, hooks)
