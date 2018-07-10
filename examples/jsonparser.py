from descent.case import CaseVal
from descent.helpers import parser_from_source

JSON_GRAMMAR = r"""
    t<S> <- S~ _
    t<S, T> <- t<S> T
    items<I> <- (I:items (t<","> I:items)*)?
    collection<T, I, O, C> <- t<O, T> items<I> t<C>

    json <- _ value !.
    value <- string / number / object / array / true / false / null
    object <- collection<@Object, pair, "{", "}">
    pair <- @Pair string:key t<":"> value:value
    array <- collection<@Array, value, "[", "]">
    string <- '"'~ @String char::* '"'~ _
    char <- @char (!["\\\b\f\t\r\n] . / "\\"~ ["\\/])
          / @escape "\\"~ ("b":"\b" / "f":"\f" / "t":"\t"
                           / "r":"\r" / "n":"\n")
          / @unicode "\\u"~ hex hex hex hex
    hex <- [0-9a-fA-F]
    number <- @Number
              "-"?
              ("0" / [1-9][0-9]*)
              (@Float^^ "."[0-9]+)?
              (@Float^^ [eE][-+]?[0-9]+)?
              _
    true <- t<"true", @True_>
    false <- t<"false", @False_>
    null <- t<"null", @Null>

    _ <- ([ \t\r\n]*)~
"""

JSON_CONVERTERS = {
    "unicode": lambda v: chr(int(v, 16))
}


class Converter(CaseVal):
    def object(self, val):
        return {self(p.key): self(p.value) for p in val}

    def number(self, val):
        return int(val)

    def float(self, val):
        return float(val)

    def string(self, val):
        return val

    def array(self, val):
        return [self(v) for v in val]

    def true_(self, val):
        return True

    def false_(self, val):
        return False

    def null(self, val):
        return None


def main():
    json_parser = parser_from_source(JSON_GRAMMAR, JSON_CONVERTERS)
    parsed = json_parser.parse("""
        {
            "some": 1,
            "json": [
                1,
                3.14,
                4,
                "tab\\tunicode\\u0010"
            ],
            "inner": {
                "bool": false,
                "val": null
            }
        }
""")

    print(parsed)
    print(Converter()(parsed))


if __name__ == '__main__':
    main()
