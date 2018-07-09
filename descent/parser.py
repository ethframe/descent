from descent.ast import types_map
from descent.combinators import compile_parser
from descent.grammar import grammar
from descent.source import hooks

parser = compile_parser(grammar, types_map, hooks)
