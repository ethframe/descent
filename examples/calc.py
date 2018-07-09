from descent.case import CaseVals
from descent.helpers import parser_from_source

CALC_GRAMMAR = r"""
    calc <- _ expr !.
    expr <- mult (op1^left mult:right)*
    mult <- term (op2^left term:right)*
    term <- num / "("~ _ expr ")"~ _ / "-"~ _ @Neg expr:expr
    num <- @Int
           "-"?
           ("0" / [1-9][0-9]*)
           (@Float^^ "."[0-9]+)?
           (@Float^^ [eE][-+]?[0-9]+)?
           _

    op1 <- ("+"~ _ @Add / "-"~ _ @Sub)
    op2 <- ("*"~ _ @Mul / "/"~ _ @Div)

    _ <- ([ \t\r\n]*)~
"""


class Evaluator(CaseVals):
    def add(self, left, right):
        return self(left) + self(right)

    def sub(self, left, right):
        return self(left) - self(right)

    def mul(self, left, right):
        return self(left) * self(right)

    def div(self, left, right):
        return self(left) / self(right)

    def neg(self, val):
        return -self(val)

    def int(self, val):
        return int(val)

    def float(self, val):
        return float(val)


def main():
    calc_parser = parser_from_source(CALC_GRAMMAR)
    parsed = calc_parser.parse("(1 + 2) - 2 * 3 + 11 / 2.0 + - (3 / 2)")

    print(parsed)
    print(Evaluator()(parsed))


if __name__ == '__main__':
    main()
