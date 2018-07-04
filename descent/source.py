source = r"""
    Grammar <- @grammar Spacing Definition:rules+ EndOfFile
    Definition <- @rule Identifier:name LEFTARROW Expression:expr

    Expression <- Sequence (@choice^items (SLASH Sequence:items)+)?
    Sequence <- Prefix (@sequence^items Prefix:items+)?
    Prefix <- (AND @follow / NOT @not_follow) Suffix:expr / Suffix
    Suffix <- AstOp (QUESTION @optional /
                     STAR @repeat /
                     PLUS @repeat1)^expr?
    AstOp <- Primary ((APPEND @append /
                       TOP @top)^expr Identifier:name /
                      (SPLICE @splice /
                       TOPSPLICE @top_splice /
                       IGNORE @ignore)^expr)?
    Primary <- Identifier !LEFTARROW
             / OPEN Expression CLOSE
             / Literal / Class / Any / Node

    Identifier <- @reference IdentStart IdentCont* Spacing
    IdentStart <- [a-zA-Z_]
    IdentCont <- IdentStart / [0-9]
    Node <- @node "@"~ IdentStart IdentCont* Spacing

    Literal <- "'"~ @string (!"'" Char::)* "'"~ Spacing
             / '"'~ @string (!'"' Char::)* '"'~ Spacing
    Class <- "["~ (!"]" Range (@choice^items (!"]" Range:items)+)? /
                   @fail) "]"~ Spacing
    Range <- @char_range Char:start "-"~ Char:end / Char
    Char <- @char char::
    char <- @escape "\\"~ [bfnrt'\"\[\]\\]
          / @octal "\\"~ [0-2][0-7][0-7]
          / @octal "\\"~ [0-7][0-7]?
          / @char !"\\" .
    Any <- DOT @char_any

    LEFTARROW <- "<-"~ Spacing
    SLASH <- "/"~ Spacing

    AND <- "&"~ Spacing
    NOT <- "!"~ Spacing

    QUESTION <- "?"~ Spacing
    STAR <- "*"~ Spacing
    PLUS <- "+"~ Spacing

    APPEND <- ":"~ Spacing
    TOP <- "^"~ Spacing
    SPLICE <- "::"~ Spacing
    TOPSPLICE <- "^^"~ Spacing
    IGNORE <- "~"~ Spacing

    OPEN <- "("~ Spacing
    CLOSE <- ")"~ Spacing
    DOT <- "."~ Spacing

    Spacing <- (Space / Comment)*
    Comment <- "#"~ (!EndOfLine .~)* EndOfLine
    Space <- [ \t]~ / EndOfLine
    EndOfLine <- "\r\n"~ / [\r\n]~
    EndOfFile <- !.
"""

hooks = {
    "escape": {
        "b": "\b",
        "f": "\f",
        "r": "\r",
        "n": "\n",
        "t": "\t",
        "\\": "\\",
        '"': '"',
        "'": "'",
        "[": "[",
        "]": "]"
    }.__getitem__,
    "octal": lambda v: chr(int(v, 8))
}
