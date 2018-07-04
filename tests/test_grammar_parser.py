import py.test

from descent.parser import parser
from descent.ast import *


def single_rule_grammar(name, body):
    return grammar([rule(name=reference(name), expr=body)])


parse_cases = [
    ("A <- 'a'", single_rule_grammar("A", string("a"))),
    ("A <- \"a\"", single_rule_grammar("A", string("a"))),
    ("A <- '\\n'", single_rule_grammar("A", string("\n"))),
    ("A <- '\\010'", single_rule_grammar("A", string("\010"))),
    ("A <- [a]", single_rule_grammar("A", char("a"))),
    ("A <- [a-z]", single_rule_grammar(
        "A", char_range(start=char("a"), end=char("z"))
    )),
    ("A <- []", single_rule_grammar("A", fail())),
    ("A <- [ab]", single_rule_grammar("A", choice([char("a"), char("b")]))),
    ("A <- .", single_rule_grammar("A", char_any())),
    ("A <- B", single_rule_grammar("A", reference("B"))),
    ("A <- B / C", single_rule_grammar(
        "A", choice([reference("B"), reference("C")])
    )),
    ("A <- B*", single_rule_grammar("A", repeat(reference("B")))),
    ("A <- B+", single_rule_grammar("A", repeat1(reference("B")))),
    ("A <- B?", single_rule_grammar("A", optional(reference("B")))),
    ("A <- !B", single_rule_grammar("A", not_follow(reference("B")))),
    ("A <- &B", single_rule_grammar("A", follow(reference("B")))),
    ("A <- @B", single_rule_grammar("A", node("B"))),
    ("A <- B~", single_rule_grammar("A", ignore(reference("B")))),
    ("A <- B:a", single_rule_grammar(
        "A", append(reference("B"), reference("a"))
    )),
    ("A <- B^a", single_rule_grammar(
        "A", top(reference("B"), reference("a"))
    )),
    ("A <- B::", single_rule_grammar("A", splice(reference("B")))),
    ("A <- B^^", single_rule_grammar("A", top_splice(reference("B")))),
]


@py.test.mark.parametrize("input, parsed", parse_cases)
def test_parse(input, parsed):
    assert parser.parse(input) == parsed
