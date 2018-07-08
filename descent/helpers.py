from descent.codegen import gen_ast_module
from descent.combinators import compile_parser
from descent.convert import convert_to_dict
from descent.grammarcheck import check_grammar, get_not_wf
from descent.parser import parser
from descent.typeinference import infer_types


def parser_from_source(src, hooks=None):
    parsed = parser.parse(src)
    grammar = convert_to_dict(parsed)
    not_wf = get_not_wf(check_grammar(grammar))
    if not_wf:
        raise ValueError(
            "Following rules are not well-formed: {}".format(", ".join(not_wf))
        )
    types = infer_types(grammar)
    ast = gen_ast_module(types)
    return compile_parser(grammar, ast, hooks)
