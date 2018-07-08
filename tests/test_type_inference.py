import py.test

from descent.parser import parser
from descent.convert import convert_to_dict
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
    ("A <- @a / @b", {NamedType("a"), NamedType("b")}),
    ("A <- (@a / @b)::", {NamedType("a"), NamedType("b")}),
    ("A <- @a @b:a", {
        NamedType("b"),
        NodeType("a", {"a": Field(False, False)}, ["a"])
    }),
    ("A <- @a (@b:a / @b:b)", {
        NamedType("b"),
        NodeType(
            "a",
            {"a": Field(False, True), "b": Field(False, True)},
            ["a", "b"]
        )
    }),
    ("A <- @b @a^a", {
        NamedType("b"),
        NodeType("a", {"a": Field(False, False)}, ["a"])
    }),
    ("A <- @a @b:a?", {
        NamedType("b"),
        NodeType("a", {"a": Field(False, True)}, ["a"])
    }),
    ("A <- @a @b:a*", {
        NamedType("b"),
        NodeType("a", {"a": Field(True, True)}, ["a"])
    }),
    ("A <- @a (@b:a / @b:b*)", {
        NamedType("b"),
        NodeType(
            "a",
            {"a": Field(False, True), "b": Field(True, True)},
            ["a", "b"]
        )
    }),
    ("A <- @a @b:a+", {
        NamedType("b"),
        NodeType("a", {"a": Field(True, False)}, ["a"])
    }),
    ("A <- @a A:a / @b", {
        NamedType("b"),
        NodeType("a", {"a": Field(False, False)}, ["a"])
    }),
    ("A <- @a @b:a A:: / @a @b:a", {
        NamedType("b"),
        NodeType("a", {"a": Field(True, False)}, ["a"])
    }),

    ("A <- @a~", {NamedType("a")}),
    ("A <- !@a", {NamedType("a")}),
    ("A <- &@a", {NamedType("a")}),

    ("A <- @a 'a':a", set()),
    ("A <- @a ('a'~):a", set()),
    ("A <- @a (@b 'a'):a (@b 'a')::", set()),
    ("A <- (@a 'a') (@b 'a'):a", set()),
    ("A <- (@a 'a') (@b (@c 'a'):a)::", set()),

    ("A <- @a @b:b? @b:a", {
        NamedType("b"),
        NodeType(
            "a",
            {"a": Field(False, False), "b": Field(False, True)},
            ["b", "a"]
        )
    }),

    ("A <- @a @b:a @b:b / @a @b:b @b:a", {
        NamedType("b"),
        NodeType(
            "a",
            {"a": Field(False, False), "b": Field(False, False)},
            ["a", "b"]
        )
    }),
]


@py.test.mark.parametrize("input, result", type_cases)
def test_parse(input, result):
    assert set(infer_types(convert_to_dict(parser.parse(input)))) == result
