from descent import ast
from descent.combinators import compile_parser
from descent.grammar import grammar
from descent.source import hooks

parser = compile_parser(grammar, ast, hooks)
