from collections import namedtuple


class Type:
    def __iter__(self):
        yield self


class ScalarType(Type):
    def __eq__(self, other):
        return self.__class__ is other.__class__

    def __hash__(self):
        return hash(self.__class__)

    def merge(self, other):
        return None


class UnknownType(ScalarType):
    def __repr__(self):
        return '?'

    def append(self, other, name):
        return self

    def splice(self, other):
        return self

    def flat(self):
        return self


class InvalidType(ScalarType):
    def __repr__(self):
        return '#'

    def append(self, other, name):
        return self

    def splice(self, other):
        return self

    def flat(self):
        return self


class EmptyType(ScalarType):
    def __repr__(self):
        return '()'

    def append(self, other, name):
        return InvalidType()

    def splice(self, other):
        if isinstance(other, UnknownType):
            return other
        if isinstance(other, (EmptyType, NamedType)):
            return self
        if isinstance(other, (StringType, TokenType)):
            return StringType()
        if isinstance(other, OrType):
            return or_type(*(self.splice(t) for t in other))
        return InvalidType()

    def flat(self):
        return InvalidType()


class StringType(ScalarType):
    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)

    def append(self, other, name):
        return InvalidType()

    def splice(self, other):
        if isinstance(other, UnknownType):
            return other
        if isinstance(other, (EmptyType, NamedType, StringType, TokenType)):
            return self
        if isinstance(other, OrType):
            return or_type(*(self.splice(t) for t in other))
        return InvalidType()

    def flat(self):
        return InvalidType()


class NamedType(Type):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.name == other.name

    def __hash__(self):
        return hash((self.__class__, self.name))

    def append(self, other, name):
        if isinstance(other, UnknownType):
            return other
        other = other.flat()
        if isinstance(other, InvalidType):
            return InvalidType()
        return NodeType(self.name, {name: Field(False, False)})

    def splice(self, other):
        if isinstance(other, UnknownType):
            return other
        if isinstance(other, (EmptyType, NamedType)):
            return self
        if isinstance(other, (StringType, TokenType)):
            return TokenType(self.name)
        if isinstance(other, NodeType):
            return NodeType(self.name, other.fields)
        if isinstance(other, OrType):
            return or_type(*(self.splice(t) for t in other))
        return InvalidType()

    def flat(self):
        return self

    def merge(self, other):
        if self == other:
            return self
        if isinstance(other, (TokenType, NodeType)):
            return other.merge(self)
        return OrType(self, other)


class TokenType(Type):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '${}'.format(self.name)

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.name == other.name

    def __hash__(self):
        return hash((self.__class__, self.name))

    def append(self, other, name):
        return InvalidType()

    def splice(self, other):
        if isinstance(other, UnknownType):
            return other
        if isinstance(other, (EmptyType, NamedType, StringType, TokenType)):
            return self
        if isinstance(other, OrType):
            return or_type(*(self.splice(t) for t in other))
        return InvalidType()

    def flat(self):
        return NamedType(self.name)

    def merge(self, other):
        if self == other:
            return self
        if isinstance(other, NamedType):
            if self.name == other.name:
                return self
        if isinstance(other, NodeType):
            if self.name == other.name:
                return InvalidType()
        return OrType(self, other)


class Field(namedtuple("Field", "arr opt")):
    def append(self, other):
        return Field(True, False)

    def __repr__(self):
        if self.arr:
            return "[]"
        elif self.opt:
            return "?"
        return "_"


class NodeType(Type):
    def __init__(self, name, fields):
        self.name = name
        self.fields = fields

    def __repr__(self):
        return '{}({})'.format(
            self.name,
            ', '.join(
                '{}={!r}'.format(name, field)
                for name, field in self.fields.items()
            )
        )

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.name == other.name \
            and self.fields == other.fields

    def __hash__(self):
        return hash(
            (self.__class__, self.name, tuple(sorted(self.fields.items())))
        )

    def append(self, other, name):
        if isinstance(other, InvalidType):
            return InvalidType()
        if isinstance(other, UnknownType):
            return other
        other = other.flat()
        fields = dict(self.fields)
        if name in fields:
            fields[name] = fields[name].append(Field(False, False))
        else:
            fields[name] = Field(False, False)
        return NodeType(self.name, fields)

    def splice(self, other):
        if isinstance(other, (EmptyType, NamedType)):
            return self
        if isinstance(other, NodeType):
            fields = dict(self.fields)
            for name, of in other.fields.items():
                if name in fields:
                    fields[name] = fields[name].append(of)
                else:
                    fields[name] = of
            return NodeType(self.name, fields)
        if isinstance(other, OrType):
            return or_type(*(self.splice(t) for t in other))
        if isinstance(other, UnknownType):
            return other
        return InvalidType()

    def flat(self):
        return NamedType(self.name)

    def merge(self, other):
        if self == other:
            return self
        if isinstance(other, NamedType):
            if self.name == other.name:
                fields = {}
                for name, field in self.fields.items():
                    fields[name] = Field(field.arr, True)
                return NodeType(self.name, fields)
        if isinstance(other, TokenType):
            if self.name == other.name:
                return InvalidType()
        if isinstance(other, NodeType):
            if self.name == other.name:
                fields = {}
                for name, sf in self.fields.items():
                    of = other.fields.get(name, Field(False, True))
                    fields[name] = Field(sf.arr or of.arr, sf.opt or of.opt)
                for name, of in other.fields.items():
                    if name not in self.fields:
                        fields[name] = Field(of.arr, True)
                return NodeType(self.name, fields)
        return None


class OrType(Type):
    def __init__(self, *items):
        self.items = frozenset(items)

    def __repr__(self):
        return "({})".format(' | '.join(repr(i) for i in self.items))

    def __eq__(self, other):
        return self.__class__ is other.__class__ and self.items == other.items

    def __hash__(self):
        return hash((self.__class__, self.items))

    def __iter__(self):
        return iter(self.items)

    def append(self, other, name):
        return or_type(*(i.append(other, name) for i in self.items))

    def splice(self, other):
        return or_type(*(i.splice(other) for i in self.items))

    def flat(self):
        return or_type(*(i.flat() for i in self.items))


def or_type(*args):
    nargs = []
    for a in args:
        if isinstance(a, InvalidType):
            return a
        elif isinstance(a, UnknownType):
            continue
        elif isinstance(a, OrType):
            nargs.extend(a)
        else:
            nargs.append(a)
    merged = {}
    for a in nargs:
        if isinstance(a, InvalidType):
            return a
        elif isinstance(a, UnknownType):
            continue
        elif isinstance(a, (EmptyType, StringType)):
            merged[a] = a
        elif a.name in merged:
            merged[a.name] = merged[a.name].merge(a)
        else:
            merged[a.name] = a
    nargs = merged.values()
    if not nargs:
        return UnknownType()
    if len(nargs) == 1:
        return list(nargs)[0]
    return OrType(*nargs)
