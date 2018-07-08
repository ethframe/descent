import py.test

from descent.parser import parser
from descent.convert import convert_to_dict
from descent.grammarcheck import check_grammar

WF_NULL = (True, True)
WF_NOT_NULL = (True, False)
NOT_WF_NULL = (False, True)
NOT_WF_NOT_NULL = (False, False)

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
    ("A <- A*", {"A": NOT_WF_NULL}),
    ("A <- A+", {"A": NOT_WF_NOT_NULL}),
]


@py.test.mark.parametrize("input, result", check_cases)
def test_parse(input, result):
    assert check_grammar(convert_to_dict(parser.parse(input))) == result
