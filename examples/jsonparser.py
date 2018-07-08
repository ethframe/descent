from descent.case import CaseVal
from descent.helpers import parser_from_source

JSON_GRAMMAR = r"""
    json <- _ value !.
    value <- string / number / object / array / true / false / null
    object <- "{"~ _ @Dict (pair:items (","~ _ pair:items)*)? "}"~ _
    pair <- @Pair string:key ":"~ _ value:value
    array <- "["~ _ @Array (value:items (","~ _ value:items)*)? "]"~ _
    string <- '"'~ @String char::* '"'~ _
    char <- @escape "\\"~ ["\\/bfnrt]
          / @unicode "\\u"~ hex hex hex hex
          / @char !["\\\b\f\t\r\n] .
    hex <- [0-9a-fA-F]
    number <- @Number
              "-"?
              ("0" / [1-9][0-9]*)
              (@Float^^ "."[0-9]+)?
              (@Float^^ [eE][-+]?[0-9]+)?
              _
    true <- @True_ "true"~ _
    false <- @False_ "false"~ _
    null <- @Null "null"~ _

    _ <- ([ \t\r\n]*)~
"""

JSON_CONVERTERS = {
    "escape": {
        '"': '"',
        "\\": "\\",
        "/": "/",
        "b": "\b",
        "f": "\f",
        "n": "\n",
        "r": "\r",
        "t": "\t"
    }.__getitem__,
    "unicode": lambda v: chr(int(v, 16))
}


class Converter(CaseVal):
    def dict(self, val):
        return {self(p.key): self(p.value) for p in val}

    def number(self, val):
        return int(val)

    def float(self, val):
        return float(val)

    def string(self, val):
        return val

    def array(self, val):
        return [self(v) for v in val]

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
