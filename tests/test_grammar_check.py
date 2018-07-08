import py.test

from descent.parser import parser
from descent.convert import convert_to_dict
from descent.grammarcheck import check_grammar

WF_NULL = (True, True, False)
WF_NOT_NULL = (True, False, False)
WF_NOT_NULL_INV = (True, False, True)
NOT_WF_NULL = (False, True, False)
NOT_WF_NULL_INV = (False, True, True)
NOT_WF_NOT_NULL = (False, False, False)
NOT_WF_NOT_NULL_INV = (False, False, True)

check_cases = [
    ("A <- 'a'", {"A": WF_NOT_NULL}),
    ("A <- .", {"A": WF_NOT_NULL}),
    ("A <- ''", {"A": WF_NULL}),
    ("A <- [a-z0-9_]", {"A": WF_NOT_NULL}),
    ("A <- []", {"A": WF_NOT_NULL}),
    ("A <- 'a' A / ''", {"A": WF_NULL}),
    ("A <- 'a' A / 'a'", {"A": WF_NOT_NULL}),
    ("A <- 'a' A", {"A": WF_NOT_NULL}),
    ("A <- 'a'?", {"A": WF_NULL}),
    ("A <- 'a'*", {"A": WF_NULL}),
    ("A <- 'a'+", {"A": WF_NOT_NULL}),
    ("A <- @a", {"A": WF_NULL}),
    ("A <- @a:a", {"A": WF_NULL}),
    ("A <- (@a 'a'):a", {"A": WF_NOT_NULL}),
    ("A <- @a^a", {"A": WF_NULL}),
    ("A <- (@a 'a')^a", {"A": WF_NOT_NULL}),
    ("A <- @a::", {"A": WF_NULL}),
    ("A <- (@a 'a')::", {"A": WF_NOT_NULL}),
    ("A <- @a^^", {"A": WF_NULL}),
    ("A <- (@a 'a')^^", {"A": WF_NOT_NULL}),
    ("A <- @a~", {"A": WF_NULL}),
    ("A <- (@a 'a')~", {"A": WF_NOT_NULL}),
    ("A <- !'a'", {"A": WF_NULL}),
    ("A <- &'a'", {"A": WF_NOT_NULL}),

    ("A <- A", {"A": NOT_WF_NULL}),
    ("A <- A 'a' / 'a'", {"A": NOT_WF_NULL}),
    ("A <- !A", {"A": NOT_WF_NULL}),
    ("A <- A?", {"A": NOT_WF_NULL}),
    ("A <- A*", {"A": NOT_WF_NULL_INV}),
    ("A <- A+", {"A": NOT_WF_NOT_NULL_INV}),

    ("A <- ' ' ('')*", {"A": WF_NOT_NULL_INV}),
]


@py.test.mark.parametrize("input, result", check_cases)
def test_parse(input, result):
    assert check_grammar(convert_to_dict(parser.parse(input))) == result
