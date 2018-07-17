from itertools import product

from descent.case import CaseUnapply
from descent.helpers import parser_from_source


DYNAMIC_GRAMMAR = r"""
    Start<B> <- _ B !.
    Tok<S> <- S~ _
    Tok<S, T> <- Tok<S> T
    KW<S> <- S~ !ident _
    Op<S> <- @Op S _
    LExpr<E, O, R> <- E ((@BinOp O:op)^left R:right)*
    LExpr<E, O> <- LExpr<E, O, E>
    RExpr<E, O, S> <- E (O^left S:right)?
    RExpr<E, O> <- RExpr<E, O, this>
    UExpr<E, O> <- @UnaryOp O:op this:expr / E
    Paren<O, E, C> <- Tok<O> E Tok<C>
    List<I, D> <- (I (Tok<D> I)*)?
    OneOpt<A, B> <- A B? / B

    Program <- Start<Statements>
    Statements <- @Statements Statement:statements*
    Empty <- @Statements
    Statement <- Condition / Assignment
    Block <- Paren<"{", Statements, "}">
    Assignment <- @Assignment Variable:lvalue Tok<"="> Expression:rvalue
    Condition <- @Condition
        KW<"if"> Expression:predicate
        Block:true
        (KW<"else"> (Condition / Block) / Empty):false

    Expression <- P5
    P5 <- LExpr<P4, Op<"==":"eq" / "!=":"neq">>
    P4 <- LExpr<P3, Op<"+":"add" / "-":"sub">>
    P3 <- LExpr<P2, Op<"*":"mul" / "/":"div">>
    P2 <- UExpr<P1, Op<"-":"neg">>
    P1 <- LExpr<P0, Op<"":"index">, Paren<"[", Expression, "]">>
    P0 <- Call / Variable / Number / String / Paren<"(", Expression, ")">

    Call <- @Call (@Name identifier):name
            Paren<"(", List<Expression:args, ","> ,")">

    Number <- @Integer "-"? ("0" / [1-9][0-9]*)
              (OneOpt<"."[0-9]+, [eE][-+]?[0-9]+> @Float^^ @Float^^)? _

    Variable <- @Variable !keywords identifier _
    String <- '"'~ @String char* '"'~ _
    identifier <- ident_start ident*
    ident_start <- [a-zA-Z_]
    ident <- [a-zA-Z0-9_]
    char <- "\\"~ (["\\/] / "b":"\b" / "f":"\f" /
                   "t":"\t" / "r":"\r" / "n":"\n")
          / !["\\\b\f\t\r\n] .
    keywords <- ("if" / "else") !ident

    _ <- ([ \t\r\n]*)~
"""


TYPES_GRAMMAR = r"""
    Start<B> <- _ B !.
    Tok<S> <- S~ _
    List<I, D> <- I (Tok<D> I)*

    Types <- Start<@Types Element:elements*>
    Element <- Function / Type
    Type <- @Type Name:name (Tok<"<:"> Name:base)?
    Function <- @Function List<Name:names, "|"> Tok<":"> List<FType:types, "|">
    FType <- @FType (Tok<"()"> / List<Name:args, ",">) Tok<"->"> Name:result

    Name <- @Name [a-zA-Z_][a-zA-Z0-9_]* _
    _ <- ([ \t\r\n]*)~
"""


types_parser = parser_from_source(TYPES_GRAMMAR)


class TypesDef(CaseUnapply):
    def types(self, items):
        for item in items:
            self(item)
        return self.env

    def type(self, name, base):
        name = str(name)
        if name in self.env:
            raise TypeError("Duplicate definition: {}".format(name))
        if base is None:
            self.env[name] = name
        else:
            base = str(base)
            if base not in self.env:
                raise TypeError("Not defined: {}".format(base))
            self.env[name] = base

    def function(self, names, types):
        types = {
            tuple(str(arg) for arg in tp.args): str(tp.result)
            for tp in types
        }
        for args, result in types.items():
            if result not in self.env:
                raise TypeError("Not defined: {}".format(result))
            for arg in args:
                if arg not in self.env:
                    raise TypeError("Not defined: {}".format(arg))
        names = [str(name) for name in names]
        for name in names:
            if name in self.env:
                sigs = self.env[name]
                for args, result in types.items():
                    if args in sigs:
                        raise TypeError(
                            "Duplicate definition: {}".format(name)
                        )
                    sigs[args] = result
            else:
                self.env[name] = dict(types)


class Definitions:
    def __init__(self, source):
        self.env = TypesDef(env={})(types_parser.parse(source))

    def seq(self, t):
        yield t
        while self.env[t] != t:
            t = self.env[t]
            yield t

    def common(self, t1, t2):
        t1s = set(self.seq(t1))
        while t2 not in t1s:
            t2 = self.env[t2]
        return t2

    def func(self, name, args):
        ts = self.env[name]
        for a in product(*(self.seq(t) for t in args)):
            if a in ts:
                return ts[a]
        raise TypeError(name, args, ts)


class Types(CaseUnapply):
    _types = Definitions("""
        dynamic
        string <: dynamic
        float <: dynamic
        integer <: float
        bool <: dynamic
        dict <: dynamic

        add | sub | mul | div : float, float -> float
        add | sub | mul : integer, integer -> integer
        add : string, string -> string
        neg : float -> float
            | integer -> integer

        eq | neq : dynamic, dynamic -> bool
        to_string : integer -> string

        index : dict, dynamic -> dynamic

        environment : () -> dict
""")

    def statements(self, statements):
        for statement in statements:
            self(statement)

    def assignment(self, lvalue, rvalue):
        var = str(lvalue)
        value = self(rvalue)
        self.env[var] = self._types.common(self.env.get(var, value), value)

    def integer(self, value):
        return "integer"

    def float(self, value):
        return "float"

    def string(self, value):
        return "string"

    def variable(self, value):
        return self.env[value]

    def binop(self, op, left, right):
        return self._types.func(str(op), (self(left), self(right)))

    def unaryop(self, op, expr):
        return self._types.func(str(op), (self(expr),))

    def condition(self, predicate, true, false):
        if self(predicate) != "bool":
            raise TypeError(predicate)
        self(true)
        self(false)

    def call(self, name, args):
        return self._types.func(str(name), tuple(self(arg) for arg in args))


class Evaluate(CaseUnapply):
    def statements(self, statements):
        for statement in statements:
            self(statement)

    def assignment(self, lvalue, rvalue):
        self.env[str(lvalue)] = self(rvalue)

    def integer(self, value):
        return int(value)

    def float(self, value):
        return float(value)

    def string(self, value):
        return value

    def variable(self, value):
        return self.env[value]

    def binop(self, op, left, right):
        return {
            "mul": lambda a, b: a * b,
            "div": lambda a, b: a / b,
            "add": lambda a, b: a + b,
            "sub": lambda a, b: a - b,
            "eq": lambda a, b: a == b,
            "neq": lambda a, b: a != b,
            "index": lambda a, b: a[b],
        }[str(op)](self(left), self(right))

    def unaryop(self, op, expr):
        return {
            "neg": lambda a: -a
        }[str(op)](self(expr))

    def condition(self, predicate, true, false):
        if self(predicate) is True:
            self(true)
        else:
            self(false)

    def call(self, name, args):
        return {
            "to_string": str,
            "environment": lambda: self.env,
        }[str(name)](*(self(arg) for arg in args))


def main():
    dynamic_parser = parser_from_source(DYNAMIC_GRAMMAR)
    parsed = dynamic_parser.parse(r"""
        a = 3
        b = a
        c = "foo" + "bar"
        d = a * 3
        e = 3
        a = -(d + 2) * 0.3 + 1
        f = 2 / 3
        g = 1
        g = "1"

        flag = 3
        if flag * 2 == 2 {
            var = flag * 12
        } else if flag != 2 {
            var = flag / 2
        } else {
            var = to_string(flag - 1) + "a"
        }

        if flag != 0 {
            env = environment()
        }

        item = env["flag"]
    """)
    print(parsed)
    env = {}
    Types(env=env)(parsed)
    print(env)
    env = {}
    Evaluate(env=env)(parsed)
    print(env)


if __name__ == '__main__':
    main()
