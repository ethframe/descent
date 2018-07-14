from collections import OrderedDict

from .ast import (
    append,
    char,
    char_any,
    char_range,
    choice,
    ignore,
    node,
    not_follow,
    optional,
    reference,
    repeat,
    repeat1,
    replace,
    sequence,
    splice,
    string,
    top,
    top_splice,
)

grammar = OrderedDict(
    [
        (
            "Grammar",
            sequence(
                [
                    node("grammar"),
                    reference("Spacing"),
                    repeat1(
                        append(reference("Definition"), reference("rules"))
                    ),
                    reference("EndOfFile"),
                ]
            ),
        ),
        (
            "Definition",
            sequence(
                [
                    node("rule"),
                    append(reference("Identifier"), reference("name")),
                    optional(
                        sequence(
                            [
                                top_splice(node("macro")),
                                sequence(
                                    [
                                        reference("MOPEN"),
                                        optional(
                                            sequence(
                                                [
                                                    append(
                                                        reference(
                                                            "Identifier"
                                                        ),
                                                        reference("args"),
                                                    ),
                                                    repeat(
                                                        sequence(
                                                            [
                                                                reference(
                                                                    "COMMA"
                                                                ),
                                                                append(
                                                                    reference(
                                                                        "Identifier"
                                                                    ),
                                                                    reference(
                                                                        "args"
                                                                    ),
                                                                ),
                                                            ]
                                                        )
                                                    ),
                                                ]
                                            )
                                        ),
                                        reference("MCLOSE"),
                                    ]
                                ),
                            ]
                        )
                    ),
                    reference("LEFTARROW"),
                    append(reference("Expression"), reference("expr")),
                ]
            ),
        ),
        (
            "Expression",
            sequence(
                [
                    reference("Sequence"),
                    optional(
                        sequence(
                            [
                                top(node("choice"), reference("items")),
                                repeat1(
                                    sequence(
                                        [
                                            reference("SLASH"),
                                            append(
                                                reference("Sequence"),
                                                reference("items"),
                                            ),
                                        ]
                                    )
                                ),
                            ]
                        )
                    ),
                ]
            ),
        ),
        (
            "Sequence",
            sequence(
                [
                    reference("Prefix"),
                    optional(
                        sequence(
                            [
                                top(node("sequence"), reference("items")),
                                repeat1(
                                    append(
                                        reference("Prefix"), reference("items")
                                    )
                                ),
                            ]
                        )
                    ),
                ]
            ),
        ),
        (
            "Prefix",
            choice(
                [
                    sequence(
                        [
                            choice([reference("AND"), reference("NOT")]),
                            append(reference("Suffix"), reference("expr")),
                        ]
                    ),
                    reference("Suffix"),
                ]
            ),
        ),
        (
            "Suffix",
            sequence(
                [
                    reference("AstOp"),
                    optional(
                        top(
                            choice(
                                [
                                    reference("QUESTION"),
                                    reference("STAR"),
                                    reference("PLUS"),
                                ]
                            ),
                            reference("expr"),
                        )
                    ),
                ]
            ),
        ),
        (
            "AstOp",
            sequence(
                [
                    reference("Primary"),
                    optional(
                        choice(
                            [
                                sequence(
                                    [
                                        top(
                                            choice(
                                                [
                                                    reference("APPEND"),
                                                    reference("TOP"),
                                                ]
                                            ),
                                            reference("expr"),
                                        ),
                                        append(
                                            reference("Identifier"),
                                            reference("name"),
                                        ),
                                    ]
                                ),
                                sequence(
                                    [
                                        top(
                                            reference("REPLACE"),
                                            reference("expr"),
                                        ),
                                        append(
                                            reference("Literal"),
                                            reference("value"),
                                        ),
                                    ]
                                ),
                                top(
                                    choice(
                                        [
                                            reference("SPLICE"),
                                            reference("TOPSPLICE"),
                                            reference("IGNORE"),
                                        ]
                                    ),
                                    reference("expr"),
                                ),
                            ]
                        )
                    ),
                ]
            ),
        ),
        (
            "Primary",
            choice(
                [
                    sequence(
                        [
                            reference("Identifier"),
                            optional(
                                sequence(
                                    [
                                        top(node("expand"), reference("name")),
                                        sequence(
                                            [
                                                reference("MOPEN"),
                                                optional(
                                                    sequence(
                                                        [
                                                            append(
                                                                reference(
                                                                    "Expression"
                                                                ),
                                                                reference(
                                                                    "args"
                                                                ),
                                                            ),
                                                            repeat(
                                                                sequence(
                                                                    [
                                                                        reference(
                                                                            "COMMA"
                                                                        ),
                                                                        append(
                                                                            reference(
                                                                                "Expression"
                                                                            ),
                                                                            reference(
                                                                                "args"
                                                                            ),
                                                                        ),
                                                                    ]
                                                                )
                                                            ),
                                                        ]
                                                    )
                                                ),
                                                reference("MCLOSE"),
                                            ]
                                        ),
                                    ]
                                )
                            ),
                            not_follow(reference("LEFTARROW")),
                        ]
                    ),
                    sequence(
                        [
                            reference("OPEN"),
                            reference("Expression"),
                            reference("CLOSE"),
                        ]
                    ),
                    reference("Literal"),
                    reference("Class"),
                    reference("Any"),
                    reference("Node"),
                ]
            ),
        ),
        (
            "Identifier",
            sequence(
                [
                    node("reference"),
                    reference("IdentStart"),
                    repeat(reference("IdentCont")),
                    reference("Spacing"),
                ]
            ),
        ),
        (
            "IdentStart",
            choice(
                [
                    char_range(char("a"), char("z")),
                    char_range(char("A"), char("Z")),
                    char("_"),
                ]
            ),
        ),
        (
            "IdentCont",
            choice(
                [reference("IdentStart"), char_range(char("0"), char("9"))]
            ),
        ),
        (
            "Node",
            sequence(
                [
                    node("node"),
                    ignore(string("@")),
                    reference("IdentStart"),
                    repeat(reference("IdentCont")),
                    reference("Spacing"),
                ]
            ),
        ),
        (
            "Literal",
            sequence(
                [
                    node("string"),
                    choice(
                        [
                            sequence(
                                [
                                    ignore(string('"')),
                                    repeat(
                                        sequence(
                                            [
                                                not_follow(string('"')),
                                                splice(reference("Char")),
                                            ]
                                        )
                                    ),
                                    ignore(string('"')),
                                    reference("Spacing"),
                                ]
                            ),
                            sequence(
                                [
                                    ignore(string("'")),
                                    repeat(
                                        sequence(
                                            [
                                                not_follow(string("'")),
                                                splice(reference("Char")),
                                            ]
                                        )
                                    ),
                                    ignore(string("'")),
                                    reference("Spacing"),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ),
        (
            "Class",
            sequence(
                [
                    ignore(string("[")),
                    choice(
                        [
                            sequence(
                                [
                                    not_follow(string("]")),
                                    sequence(
                                        [
                                            reference("Range"),
                                            optional(
                                                sequence(
                                                    [
                                                        top(
                                                            node("choice"),
                                                            reference("items"),
                                                        ),
                                                        repeat1(
                                                            sequence(
                                                                [
                                                                    not_follow(
                                                                        string(
                                                                            "]"
                                                                        )
                                                                    ),
                                                                    append(
                                                                        reference(
                                                                            "Range"
                                                                        ),
                                                                        reference(
                                                                            "items"
                                                                        ),
                                                                    ),
                                                                ]
                                                            )
                                                        ),
                                                    ]
                                                )
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                            node("fail"),
                        ]
                    ),
                    ignore(string("]")),
                    reference("Spacing"),
                ]
            ),
        ),
        (
            "Range",
            choice(
                [
                    sequence(
                        [
                            node("char_range"),
                            append(reference("Char"), reference("start")),
                            ignore(string("-")),
                            append(reference("Char"), reference("end")),
                        ]
                    ),
                    reference("Char"),
                ]
            ),
        ),
        ("Char", sequence([node("char"), splice(reference("char"))])),
        (
            "char",
            choice(
                [
                    sequence(
                        [
                            node("char"),
                            choice(
                                [
                                    sequence(
                                        [not_follow(string("\\")), char_any()]
                                    ),
                                    sequence(
                                        [
                                            ignore(string("\\")),
                                            choice(
                                                [
                                                    choice(
                                                        [
                                                            char("'"),
                                                            char('"'),
                                                            char("["),
                                                            char("]"),
                                                            char("\\"),
                                                            char("-"),
                                                        ]
                                                    ),
                                                    replace(
                                                        string("b"),
                                                        string("\x08"),
                                                    ),
                                                    replace(
                                                        string("f"),
                                                        string("\x0c"),
                                                    ),
                                                    replace(
                                                        string("n"),
                                                        string("\n"),
                                                    ),
                                                    replace(
                                                        string("r"),
                                                        string("\r"),
                                                    ),
                                                    replace(
                                                        string("t"),
                                                        string("\t"),
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                    sequence(
                        [
                            node("octal"),
                            ignore(string("\\")),
                            choice(
                                [
                                    sequence(
                                        [
                                            char_range(char("0"), char("2")),
                                            char_range(char("0"), char("7")),
                                            char_range(char("0"), char("7")),
                                        ]
                                    ),
                                    sequence(
                                        [
                                            char_range(char("0"), char("7")),
                                            optional(
                                                char_range(
                                                    char("0"), char("7")
                                                )
                                            ),
                                        ]
                                    ),
                                ]
                            ),
                        ]
                    ),
                ]
            ),
        ),
        ("Any", reference("DOT")),
        ("LEFTARROW", sequence([ignore(string("<-")), reference("Spacing")])),
        ("SLASH", sequence([ignore(string("/")), reference("Spacing")])),
        (
            "AND",
            sequence(
                [ignore(string("&")), reference("Spacing"), node("follow")]
            ),
        ),
        (
            "NOT",
            sequence(
                [ignore(string("!")), reference("Spacing"), node("not_follow")]
            ),
        ),
        (
            "QUESTION",
            sequence(
                [ignore(string("?")), reference("Spacing"), node("optional")]
            ),
        ),
        (
            "STAR",
            sequence(
                [ignore(string("*")), reference("Spacing"), node("repeat")]
            ),
        ),
        (
            "PLUS",
            sequence(
                [ignore(string("+")), reference("Spacing"), node("repeat1")]
            ),
        ),
        (
            "DOT",
            sequence(
                [ignore(string(".")), reference("Spacing"), node("char_any")]
            ),
        ),
        (
            "APPEND",
            sequence(
                [ignore(string(":")), reference("Spacing"), node("append")]
            ),
        ),
        (
            "REPLACE",
            sequence(
                [ignore(string(":")), reference("Spacing"), node("replace")]
            ),
        ),
        (
            "TOP",
            sequence([ignore(string("^")), reference("Spacing"), node("top")]),
        ),
        (
            "SPLICE",
            sequence(
                [ignore(string("::")), reference("Spacing"), node("splice")]
            ),
        ),
        (
            "TOPSPLICE",
            sequence(
                [
                    ignore(string("^^")),
                    reference("Spacing"),
                    node("top_splice"),
                ]
            ),
        ),
        (
            "IGNORE",
            sequence(
                [ignore(string("~")), reference("Spacing"), node("ignore")]
            ),
        ),
        ("OPEN", sequence([ignore(string("(")), reference("Spacing")])),
        ("CLOSE", sequence([ignore(string(")")), reference("Spacing")])),
        ("MOPEN", sequence([ignore(string("<")), reference("Spacing")])),
        ("MCLOSE", sequence([ignore(string(">")), reference("Spacing")])),
        ("COMMA", sequence([ignore(string(",")), reference("Spacing")])),
        (
            "Spacing",
            repeat(choice([reference("Space"), reference("Comment")])),
        ),
        (
            "Comment",
            sequence(
                [
                    ignore(string("#")),
                    repeat(
                        sequence(
                            [
                                not_follow(reference("EndOfLine")),
                                ignore(char_any()),
                            ]
                        )
                    ),
                    reference("EndOfLine"),
                ]
            ),
        ),
        (
            "Space",
            choice(
                [
                    ignore(choice([char(" "), char("\t")])),
                    reference("EndOfLine"),
                ]
            ),
        ),
        (
            "EndOfLine",
            choice(
                [
                    ignore(string("\r\n")),
                    ignore(choice([char("\r"), char("\n")])),
                ]
            ),
        ),
        ("EndOfFile", not_follow(char_any())),
    ]
)
