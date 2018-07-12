from collections import OrderedDict as od

import py.test

from descent.parser import parse_grammar
from descent.macro import expand_macros
from descent.typeinference import infer_types
from descent.asttypes import NamedType, TokenType, NodeType, Field


type_cases = [
    ("A <- 'a'", set()),
    ("A <- @a", {NamedType("a")}),
    ("A <- @a 'a'", {TokenType("a")}),
    ("A <- @a .", {TokenType("a")}),
    ("A <- @a [a]", {TokenType("a")}),
    ("A <- @a [a-z]", {TokenType("a")}),
    ("A <- 'a' @a^^", {TokenType("a")}),
    ("A <- @a::", {NamedType("a")}),
    ("A <- @a @b:'a'", {TokenType("a"), NamedType("b")}),
    ("A <- @a / @b", {NamedType("a"), NamedType("b")}),
    ("A <- (@a / @b)::", {NamedType("a"), NamedType("b")}),
    ("A <- @a @b:a", {
        NamedType("b"),
        NodeType("a", od([("a", Field(False, False))]))
    }),
    ("A <- @a (@b:a / @b:b)", {
        NamedType("b"),
        NodeType(
            "a",
            od([("a", Field(False, True)), ("b", Field(False, True))])
        )
    }),
    ("A <- @b @a^a", {
        NamedType("b"),
        NodeType("a", od([("a", Field(False, False))]))
    }),
    ("A <- @a @b:a?", {
        NamedType("b"),
        NodeType("a", od([("a", Field(False, True))]))
    }),
    ("A <- @a @b:a*", {
        NamedType("b"),
        NodeType("a", od([("a", Field(True, True))]))
    }),
    ("A <- @a (@b:a / @b:b*)", {
        NamedType("b"),
        NodeType(
            "a",
            od([("a", Field(False, True)), ("b", Field(True, True))])
        )
    }),
    ("A <- @a @b:a+", {
        NamedType("b"),
        NodeType("a", od([("a", Field(True, False))]))
    }),
    ("A <- @a A:a / @b", {
        NamedType("b"),
        NodeType("a", od([("a", Field(False, False))]))
    }),
    ("A <- @a @b:a A:: / @a @b:a", {
        NamedType("b"),
        NodeType("a", od([("a", Field(True, False))]))
    }),

    ("A <- @a~", {NamedType("a")}),
    ("A <- !@a", {NamedType("a")}),
    ("A <- &@a", {NamedType("a")}),

    ("A <- A:: / @a", {NamedType("a")}),
    ("A <- 'a' A:: / ''", set()),
    ("A <- 'a' 'a'::", set()),

    ("A <- @a 'a':a", None),
    ("A <- @a ('a'~):a", None),
    ("A <- @a (@b 'a'):a (@b 'a')::", None),
    ("A <- (@a 'a') (@b 'a'):a", None),
    ("A <- (@a 'a') (@b (@c 'a'):a)::", None),

    ("A <- @a @b:b? @b:a", {
        NamedType("b"),
        NodeType(
            "a",
            od([("b", Field(False, True)), ("a", Field(False, False))])
        )
    }),

    ("A <- @a @b:a @b:b / @a @b:b @b:a", {
        NamedType("b"),
        NodeType(
            "a",
            od([("a", Field(False, False)), ("b", Field(False, False))])
        )
    }),

    ("A <- A:: / @a 'a':a", None),
    ("A <- @a:a", None),
    ("A <- 'a' @a:a", None),
    ("A <- 'a' A:: / @a / @b", {NamedType("a"), NamedType("b")}),
    ("A <- 'a' ('a' @a:a)::", None),

    ("A <- @a A:: / @a 'a'", {TokenType("a")}),
    ("A <- @a A:: / @a (@b 'a'):a", {
        TokenType("b"),
        NodeType("a", od([("a", Field(False, False))]))
    }),
    ("A <- @a A:: / @a", {NamedType("a")}),
    ("A <- @a A:: / (@a / @b)", {NamedType("a"), NamedType("b")}),
    ("A <- @a A:: / @a 'a':a", None),
]


@py.test.mark.parametrize("input, result", type_cases)
def test_parse(input, result):
    types = infer_types(expand_macros(parse_grammar(input)))
    assert types is None and result is None or set(types) == result
