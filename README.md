# descent

Recursive descent parsing toolkit.

## Parsing expression syntax

### Terminals

* `"abc"`, `'abc'` - literal string
* `.` - any character
* `[a-z]`, `[abc]` - character classes

### Nonterminals

* `A <- "a"` - nonterminal definition
* `A` - nonterminal call

### Expressions

* `"abc" [a-z]` - sequence
* `"abc" / "def"` - ordered choice
* `"a"*` - zero or more repetition
* `"a"+` - one or more repetitions
* `"a"?` - optional
* `!"a"` - negative lookahead
* `&"a"` - positive lookahead

### AST operations

* `@Name` - returns new named node
* `"abc" / . / [a-z]` - extends current node with consumed string
* `A:a` - appends result of `A` to field `a` of current node
* `A^a` - appends current node to field `a` of result of `A`
* `A::` - extends current node with fields or string from result of `A`
* `A^^` - extends result of `A` with fields or string from current node
* `A~` - discards result of `A`
* `A:"a"` - replaces result of `A` with string `"a"`

### Macros

* `macro<arg1, arg2> <- arg1 ...` - macro definition
* `macro<A, "b" / "c">` - macro usage
* `macro<...> <- ... this ...` - reference to the rule in which the macro is used
