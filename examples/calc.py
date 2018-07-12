from descent.case import CaseUnapply
from descent.helpers import parser_from_source

CALC_GRAMMAR = r"""
    t<S> <- S~ _
    t<S, T> <- t<S> T
    expr<E, O> <- E (O^left E:right)*
    expr<E, O, R> <- E (O^left R:right)?
    unary<E, O> <- O E:expr / E
    paren<O, E, C> <- t<O> E t<C>

    calc <- _ expr !.
    expr <- p0
    p0 <- expr<p1, t<"+", @Add> / t<"-", @Sub>>
    p1 <- expr<p2, t<"*", @Mul> / t<"/", @Div>>
    p2 <- expr<p3, t<"**", @Pow>, p2>
    p3 <- unary<p4, t<"-", @Neg>>
    p4 <- num / paren<"(", expr, ")">

    num <- @Int
           "-"?
           ("0" / [1-9][0-9]*)
           (@Float^^ "."[0-9]+)?
           (@Float^^ [eE][-+]?[0-9]+)?
           _

    _ <- ([ \t\r\n]*)~
"""


class Evaluator(CaseUnapply):
    def add(self, left, right):
        return self(left) + self(right)

    def sub(self, left, right):
        return self(left) - self(right)

    def mul(self, left, right):
        return self(left) * self(right)

    def div(self, left, right):
        return self(left) / self(right)

    def pow(self, left, right):
        return self(left) ** self(right)

    def neg(self, val):
        return -self(val)

    def int(self, val):
        return int(val)

    def float(self, val):
        return float(val)


def main():
    calc_parser = parser_from_source(CALC_GRAMMAR)
    parse = calc_parser.parse
    evaluate = Evaluator()
    calc = lambda s: evaluate(parse(s))
    print(calc("(1 + 2) ** 2 - 2 * 3 + 11 / 2.0 + - (3 / 2)"))
    print(calc("2 ** 3 ** 2 + -3 * --4"))


if __name__ == '__main__':
    main()
