class char:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'char({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def unapply1(self):
        return self.val

    def unapply(self):
        return (self.val,)

    def copy(self):
        return char(self.val)

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, converters):
        converter = converters.get('char')
        if converter:
            return other.consume(converter(self.val))
        return other.consume(self.val)


class octal:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'octal({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def unapply1(self):
        return self.val

    def unapply(self):
        return (self.val,)

    def copy(self):
        return octal(self.val)

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, converters):
        converter = converters.get('octal')
        if converter:
            return other.consume(converter(self.val))
        return other.consume(self.val)


class string:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'string({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def unapply1(self):
        return self.val

    def unapply(self):
        return (self.val,)

    def copy(self):
        return string(self.val)

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, converters):
        converter = converters.get('string')
        if converter:
            return other.consume(converter(self.val))
        return other.consume(self.val)


class reference:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'reference({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def unapply1(self):
        return self.val

    def unapply(self):
        return (self.val,)

    def copy(self):
        return reference(self.val)

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, converters):
        converter = converters.get('reference')
        if converter:
            return other.consume(converter(self.val))
        return other.consume(self.val)


class rule:
    __slots__ = ('name', 'expr')

    def __init__(self, name=None, expr=None):
        self.name = name
        self.expr = expr

    def __repr__(self):
        return 'rule({!r}, {!r})'.format(
            self.name,
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.name == other.name
            and self.expr == other.expr
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.name, self.expr)

    def copy(self):
        return rule(
            self.name,
            self.expr,
        )

    def append_name(self, val):
        self.name = val
        return self

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_name(self.name)
        if self.expr is not None:
            other.append_expr(self.expr)
        return other


class fail:
    def __repr__(self):
        return 'fail()'

    def __hash__(self):
        return hash(self.__class__)

    def __eq__(self, other):
        return self.__class__ is other.__class__

    def unapply1(self):
        return self

    def unapply(self):
        return (self,)

    def copy(self):
        return self

    def splice_to(self, other):
        return other


class char_any:
    def __repr__(self):
        return 'char_any()'

    def __hash__(self):
        return hash(self.__class__)

    def __eq__(self, other):
        return self.__class__ is other.__class__

    def unapply1(self):
        return self

    def unapply(self):
        return (self,)

    def copy(self):
        return self

    def splice_to(self, other):
        return other


class char_range:
    __slots__ = ('start', 'end')

    def __init__(self, start=None, end=None):
        self.start = start
        self.end = end

    def __repr__(self):
        return 'char_range({!r}, {!r})'.format(
            self.start,
            self.end,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.start == other.start
            and self.end == other.end
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.start, self.end)

    def copy(self):
        return char_range(
            self.start,
            self.end,
        )

    def append_start(self, val):
        self.start = val
        return self

    def append_end(self, val):
        self.end = val
        return self

    def splice_to(self, other, hooks):
        other.append_start(self.start)
        other.append_end(self.end)
        return other


class append:
    __slots__ = ('expr', 'name')

    def __init__(self, expr=None, name=None):
        self.expr = expr
        self.name = name

    def __repr__(self):
        return 'append({!r}, {!r})'.format(
            self.expr,
            self.name,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
            and self.name == other.name
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.expr, self.name)

    def copy(self):
        return append(
            self.expr,
            self.name,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def append_name(self, val):
        self.name = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        other.append_name(self.name)
        return other


class top:
    __slots__ = ('expr', 'name')

    def __init__(self, expr=None, name=None):
        self.expr = expr
        self.name = name

    def __repr__(self):
        return 'top({!r}, {!r})'.format(
            self.expr,
            self.name,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
            and self.name == other.name
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.expr, self.name)

    def copy(self):
        return top(
            self.expr,
            self.name,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def append_name(self, val):
        self.name = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        other.append_name(self.name)
        return other


class splice:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'splice({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return splice(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class top_splice:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'top_splice({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return top_splice(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class ignore:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'ignore({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return ignore(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class node:
    def __init__(self, val=''):
        self.val = val

    def __str__(self):
        return self.val

    def __repr__(self):
        return 'node({!r})'.format(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.val == other.val

    def unapply1(self):
        return self.val

    def unapply(self):
        return (self.val,)

    def copy(self):
        return node(self.val)

    def consume(self, val):
        self.val += val
        return self

    def splice_to(self, other, converters):
        converter = converters.get('node')
        if converter:
            return other.consume(converter(self.val))
        return other.consume(self.val)


class optional:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'optional({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return optional(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class repeat:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'repeat({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return repeat(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class repeat1:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'repeat1({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return repeat1(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class replace:
    __slots__ = ('expr', 'value')

    def __init__(self, expr=None, value=None):
        self.expr = expr
        self.value = value

    def __repr__(self):
        return 'replace({!r}, {!r})'.format(
            self.expr,
            self.value,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
            and self.value == other.value
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.expr, self.value)

    def copy(self):
        return replace(
            self.expr,
            self.value,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def append_value(self, val):
        self.value = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        other.append_value(self.value)
        return other


class follow:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'follow({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return follow(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class not_follow:
    __slots__ = ('expr',)

    def __init__(self, expr=None):
        self.expr = expr

    def __repr__(self):
        return 'not_follow({!r})'.format(
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.expr == other.expr
        )

    def unapply1(self):
        return self.expr

    def unapply(self):
        return (self.expr,)

    def copy(self):
        return not_follow(
            self.expr,
        )

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_expr(self.expr)
        return other


class choice:
    __slots__ = ('items',)

    def __init__(self, items=None):
        self.items = items or []

    def __repr__(self):
        return 'choice({!r})'.format(
            self.items,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.items == other.items
        )

    def unapply1(self):
        return self.items

    def unapply(self):
        return (self.items,)

    def copy(self):
        return choice(
            list(self.items),
        )

    def append_items(self, val):
        self.items.append(val)
        return self

    def extend_items(self, val):
        self.items.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.extend_items(self.items)
        return other


class sequence:
    __slots__ = ('items',)

    def __init__(self, items=None):
        self.items = items or []

    def __repr__(self):
        return 'sequence({!r})'.format(
            self.items,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.items == other.items
        )

    def unapply1(self):
        return self.items

    def unapply(self):
        return (self.items,)

    def copy(self):
        return sequence(
            list(self.items),
        )

    def append_items(self, val):
        self.items.append(val)
        return self

    def extend_items(self, val):
        self.items.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.extend_items(self.items)
        return other


class expand:
    __slots__ = ('name', 'args')

    def __init__(self, name=None, args=None):
        self.name = name
        self.args = args or []

    def __repr__(self):
        return 'expand({!r}, {!r})'.format(
            self.name,
            self.args,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.name == other.name
            and self.args == other.args
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.name, self.args)

    def copy(self):
        return expand(
            self.name,
            list(self.args),
        )

    def append_name(self, val):
        self.name = val
        return self

    def append_args(self, val):
        self.args.append(val)
        return self

    def extend_args(self, val):
        self.args.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.append_name(self.name)
        other.extend_args(self.args)
        return other


class macro:
    __slots__ = ('name', 'args', 'expr')

    def __init__(self, name=None, args=None, expr=None):
        self.name = name
        self.args = args or []
        self.expr = expr

    def __repr__(self):
        return 'macro({!r}, {!r}, {!r})'.format(
            self.name,
            self.args,
            self.expr,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.name == other.name
            and self.args == other.args
            and self.expr == other.expr
        )

    def unapply1(self):
        return self

    def unapply(self):
        return (self.name, self.args, self.expr)

    def copy(self):
        return macro(
            self.name,
            list(self.args),
            self.expr,
        )

    def append_name(self, val):
        self.name = val
        return self

    def append_args(self, val):
        self.args.append(val)
        return self

    def extend_args(self, val):
        self.args.extend(val)
        return self

    def append_expr(self, val):
        self.expr = val
        return self

    def splice_to(self, other, hooks):
        other.append_name(self.name)
        other.extend_args(self.args)
        other.append_expr(self.expr)
        return other


class grammar:
    __slots__ = ('rules',)

    def __init__(self, rules=None):
        self.rules = rules or []

    def __repr__(self):
        return 'grammar({!r})'.format(
            self.rules,
        )

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.rules == other.rules
        )

    def unapply1(self):
        return self.rules

    def unapply(self):
        return (self.rules,)

    def copy(self):
        return grammar(
            list(self.rules),
        )

    def append_rules(self, val):
        self.rules.append(val)
        return self

    def extend_rules(self, val):
        self.rules.extend(val)
        return self

    def splice_to(self, other, hooks):
        other.extend_rules(self.rules)
        return other


types_map = {
   'char': char,
   'octal': octal,
   'string': string,
   'reference': reference,
   'rule': rule,
   'fail': fail,
   'char_any': char_any,
   'char_range': char_range,
   'append': append,
   'top': top,
   'splice': splice,
   'top_splice': top_splice,
   'ignore': ignore,
   'node': node,
   'optional': optional,
   'repeat': repeat,
   'repeat1': repeat1,
   'replace': replace,
   'follow': follow,
   'not_follow': not_follow,
   'choice': choice,
   'sequence': sequence,
   'expand': expand,
   'macro': macro,
   'grammar': grammar,
}