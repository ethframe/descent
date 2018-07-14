source = r"""
    Args<Item> <- MOPEN (Item:args (COMMA Item:args)*)? MCLOSE
    LeftOp<Arg, Between, Type> <- Arg (Type^items (Between Arg:items)+)?
    LeftOp<Arg, Type> <- Arg (Type^items Arg:items+)?

    Grammar <- @grammar Spacing Definition:rules+ EndOfFile
    Definition <- @rule Identifier:name (@macro^^ Args<Identifier>)?
                  LEFTARROW Expression:expr

    Expression <- LeftOp<Sequence, SLASH, @choice>
    Sequence <- LeftOp<Prefix, @sequence>
    Prefix <- (AND / NOT) Suffix:expr / Suffix
    Suffix <- AstOp (QUESTION / STAR / PLUS)^expr?
    AstOp <- Primary ((APPEND / TOP)^expr Identifier:name /
                      REPLACE^expr Literal:value /
                      (SPLICE / TOPSPLICE / IGNORE)^expr)?
    Primary <- Identifier (@expand^name Args<Expression>)? !LEFTARROW
             / OPEN Expression CLOSE / Literal / Class / Any / Node

    Identifier <- @reference IdentStart IdentCont* Spacing
    IdentStart <- [a-zA-Z_]
    IdentCont <- IdentStart / [0-9]
    Node <- @node "@"~ IdentStart IdentCont* Spacing

    String<Q> <- Q~ (!Q Char::)* Q~ Spacing
    Literal <- @string (String<'"'> / String<"'">)
    Class <- "["~ (!"]" LeftOp<Range, !"]", @choice> / @fail) "]"~ Spacing
    Range <- @char_range Char:start "-"~ Char:end / Char
    Char <- @char char::
    char <- @char (!"\\" .
                 / "\\"~ (['\"\[\]\\\-] / "b":"\b" / "f":"\f"
                        / "n":"\n" / "r":"\r" / "t":"\t"))
          / @octal "\\"~ ([0-2][0-7][0-7] / [0-7][0-7]?)
    Any <- DOT

    Token<S> <- S~ Spacing
    Token<S, T> <- S~ Spacing T

    LEFTARROW <- Token<"<-">
    SLASH <- Token<"/">

    AND <- Token<"&", @follow>
    NOT <- Token<"!", @not_follow>

    QUESTION <- Token<"?", @optional>
    STAR <- Token<"*", @repeat>
    PLUS <- Token<"+", @repeat1>

    DOT <- Token<".", @char_any>

    APPEND <- Token<":", @append>
    REPLACE <- Token<":", @replace>
    TOP <- Token<"^", @top>
    SPLICE <- Token<"::", @splice>
    TOPSPLICE <- Token<"^^", @top_splice>
    IGNORE <- Token<"~", @ignore>

    OPEN <- Token<"(">
    CLOSE <- Token<")">
    MOPEN <- Token<"<">
    MCLOSE <- Token<">">
    COMMA <- Token<",">

    Spacing <- (Space / Comment)*
    Comment <- "#"~ (!EndOfLine .~)* EndOfLine
    Space <- [ \t]~ / EndOfLine
    EndOfLine <- "\r\n"~ / [\r\n]~
    EndOfFile <- !.
"""

converters = {
    "octal": lambda v: chr(int(v, 8))
}
