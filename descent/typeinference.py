from descent.asttypes import (
    EmptyType, NamedType, TokenType, NodeType, StringType, UnknownType, or_type
)
from descent.fixpoint import CaseFix, fix


class TypeInference(CaseFix):
    def reference(self, val, ctype):
        return self.fix.get(val, ctype)

    def sequence(self, val, ctype):
        for p in val:
            ctype = self(p, ctype)
        return ctype

    def choice(self, val, ctype):
        return or_type(*(self(p, ctype) for p in val))

    def node(self, val, ctype):
        self.reg.add(ctype)
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
        self.reg.update(a)
        return ctype

    def not_follow(self, val, ctype):
        a = self(val, EmptyType())
        self.reg.update(a)
        return ctype

    def char_any(self, val, ctype):
        return ctype.splice(StringType())

    def char(self, val, ctype):
        return ctype.splice(StringType())

    def string(self, val, ctype):
        return ctype.splice(StringType())

    def char_range(self, val, ctype):
        return ctype.splice(StringType())

    def repeat(self, val, ctype):
        ntype = or_type(ctype, self(val, ctype))
        while ntype != ctype:
            ctype = ntype
            ntype = or_type(ctype, self(val, ctype))
        return ntype

    def repeat1(self, val, ctype):
        ntype = self(val, ctype)
        while ntype != ctype:
            ctype = ntype
            ntype = or_type(ctype, self(val, ctype))
        return ntype

    def optional(self, val, ctype):
        return or_type(ctype, self(val, ctype))


class Registry:
    def __init__(self):
        self.types = {}

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
    reg.update(inf[start].get((EmptyType(),), ()))
    return list(reg.types.values())
