from collections import OrderedDict

from descent.asttypes import (
    InvalidType, UnknownType, EmptyType, StringType,
    NamedType, TokenType, NodeType, merge_types
)
from descent.fixpoint import CaseFix, fix


class TypeInference(CaseFix):
    def sequence(self, val, ctype):
        for p in val:
            ctype = self(p, ctype)
        return ctype

    def choice(self, val, ctype):
        return merge_types(self(p, ctype) for p in val)

    def node(self, val, ctype):
        if isinstance(ctype, InvalidType):
            return ctype
        self.reg.update(ctype)
        return NamedType(val)

    def top(self, val, ctype):
        a = self(val.expr, EmptyType())
        self.reg.update(ctype)
        return a.append(ctype, str(val.name))

    def append(self, val, ctype):
        a = self(val.expr, EmptyType())
        self.reg.update(a)
        return ctype.append(a, str(val.name))

    def splice(self, val, ctype):
        a = self(val, EmptyType())
        self.reg.update(a)
        return ctype.splice(a)

    def top_splice(self, val, ctype):
        a = self(val, EmptyType())
        self.reg.update(ctype)
        return a.splice(ctype)

    def ignore(self, val, ctype):
        a = self(val, EmptyType())
        if isinstance(a, InvalidType):
            return a
        self.reg.update(a)
        return ctype

    not_follow = follow = ignore

    def replace(self, val, ctype):
        a = self(val.expr, EmptyType())
        self.reg.update(a)
        return ctype.splice(StringType())

    def char(self, val, ctype):
        return ctype.splice(StringType())

    string = char_any = char_range = char

    def repeat(self, val, ctype):
        ntype = merge_types((ctype, self(val, ctype)))
        while ntype != ctype:
            ctype = ntype
            ntype = merge_types((ctype, self(val, ctype)))
        return ntype

    def repeat1(self, val, ctype):
        ntype = self(val, ctype)
        while ntype != ctype:
            ctype = ntype
            ntype = merge_types((ctype, self(val, ctype)))
        return ntype

    def optional(self, val, ctype):
        return merge_types((ctype, self(val, ctype)))


class Registry:
    def __init__(self):
        self.types = OrderedDict()

    def add(self, tp):
        if isinstance(tp, (NamedType, TokenType, NodeType)):
            if tp.name not in self.types:
                self.types[tp.name] = tp
            else:
                self.types[tp.name] = self.types[tp.name].merge(tp)

    def update(self, tps):
        for tp in tps:
            self.add(tp)


infer = fix(TypeInference, UnknownType())


def infer_types(gram):
    start = list(gram)[0]
    reg = Registry()
    inf = infer(gram, [start], EmptyType(), reg=reg)
    top = inf[start].get((EmptyType(),), ())
    if isinstance(top, InvalidType):
        return None
    reg.update(top)
    return list(reg.types.values())
