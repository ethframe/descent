from collections import namedtuple, OrderedDict


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
            return merge_types(self.splice(t) for t in other)
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
            return merge_types(self.splice(t) for t in other)
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
        return NodeType(self.name, OrderedDict([(name, Field(False, False))]))

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
            return merge_types(self.splice(t) for t in other)
        return InvalidType()

    def flat(self):
        return self

    def merge(self, other):
        if self == other:
            return self
        return other.merge(self)


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
            return merge_types(self.splice(t) for t in other)
        return InvalidType()

    def flat(self):
        return NamedType(self.name)

    def merge(self, other):
        if self == other:
            return self
        if isinstance(other, NamedType):
            return self
        return InvalidType()


class Field(namedtuple("Field", "arr opt")):
    def append(self, other):
        return Field(True, self.opt or other.opt)

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
        if isinstance(other, UnknownType):
            return other
        other = other.flat()
        if isinstance(other, InvalidType):
            return other
        fields = OrderedDict(self.fields)
        if name in fields:
            fields[name] = fields[name].append(Field(False, False))
        else:
            fields[name] = Field(False, False)
        return NodeType(self.name, fields)

    def splice(self, other):
        if isinstance(other, (EmptyType, NamedType)):
            return self
        if isinstance(other, NodeType):
            fields = OrderedDict(self.fields)
            for name, of in other.fields.items():
                if name in fields:
                    of = fields[name].append(of)
                fields[name] = of
            return NodeType(self.name, fields)
        if isinstance(other, OrType):
            return merge_types(self.splice(t) for t in other)
        if isinstance(other, UnknownType):
            return other
        return InvalidType()

    def flat(self):
        return NamedType(self.name)

    def merge(self, other):
        if self == other:
            return self
        if isinstance(other, NamedType):
            fields = OrderedDict()
            for name, field in self.fields.items():
                fields[name] = Field(field.arr, True)
            return NodeType(self.name, fields)
        if isinstance(other, NodeType):
            fields = OrderedDict()
            for name, sf in self.fields.items():
                of = other.fields.get(name, Field(False, True))
                fields[name] = Field(sf.arr or of.arr, sf.opt or of.opt)
            for name, of in other.fields.items():
                if name not in self.fields:
                    fields[name] = Field(of.arr, True)
            return NodeType(self.name, fields)
        return InvalidType()


class OrType(Type):
    def __init__(self, items):
        self.items = tuple(items)

    def __repr__(self):
        return "({})".format(' | '.join(repr(i) for i in self.items))

    def __eq__(self, other):
        return self.__class__ is other.__class__ \
            and set(self.items) == set(other.items)

    def __hash__(self):
        return hash((self.__class__, self.items))

    def __iter__(self):
        return iter(self.items)

    def append(self, other, name):
        return merge_types(i.append(other, name) for i in self.items)

    def splice(self, other):
        return merge_types(i.splice(other) for i in self.items)

    def flat(self):
        return merge_types(i.flat() for i in self.items)


def merge_types(types):
    types_list = []
    for tp in types:
        if isinstance(tp, InvalidType):
            return tp
        elif isinstance(tp, UnknownType):
            continue
        else:
            types_list.extend(tp)
    merged = OrderedDict()
    for tp in types_list:
        if isinstance(tp, (EmptyType, StringType)):
            merged[tp] = tp
        else:
            if tp.name in merged:
                tp = merged[tp.name].merge(tp)
            merged[tp.name] = tp
    distinct_types = list(merged.values())
    if not distinct_types:
        return UnknownType()
    if len(distinct_types) == 1:
        return distinct_types[0]
    return OrType(distinct_types)
