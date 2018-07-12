from descent.ast import types_map
from descent.combinators import compile_parser
from descent.grammar import grammar
from descent.source import converters

parser = compile_parser(grammar, types_map, converters)

parse_grammar = parser.parse
