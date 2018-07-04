from collections import namedtuple

from descent.fixpoint import fix, CaseFix


state = namedtuple("state", "lin rec fix min")


class Linear(CaseFix):
    def reference(self, val):
        return self.fix.get(val)

    def char(self, val):
        return state(True, False, True, 1)

    def char_any(self, val):
        return state(True, False, True, 1)

    def char_range(self, val):
        return state(True, False, True, 1)

    def string(self, val):
        return state(True, False, True, len(val))

    def sequence(self, val):
        lin, rec, fix, l = True, False, True, 0
        for v in val[:-1]:
            st = self(v)
            lin &= not st.rec
            rec |= st.rec
            fix &= st.fix
            l += st.min
        st = self(val[-1])
        lin &= st.lin
        rec |= st.rec
        fix &= st.fix
        l += st.min
        return state(lin, rec, fix, l)

    def choice(self, val):
        lin, rec, fix, l = True, False, True, None
        for v in val:
            st = self(v)
            lin &= st.lin
            rec |= st.rec
            if l is None:
                l = st.min
            l = min(l, st.min)
        return state(lin, rec, fix, l)

    def not_follow(self, val):
        st = self(val)
        return state(not st.rec, st.rec, False, 0)

    def node(self, val):
        return state(True, False, True, 0)

    def append(self, val):
        return self(val.expr)

    def top(self, val):
        return self(val.expr)

    def splice(self, val):
        return self(val)

    def top_splice(self, val):
        return self(val)

    def ignore(self, val):
        return self(val)

    def repeat(self, val):
        st = self(val)
        return st._replace(fix=False, min=0)

    def repeat1(self, val):
        st = self(val)
        return st._replace(fix=False)

    def optional(self, val):
        st = self(val)
        return st._replace(fix=False, min=0)


_linear = fix(Linear, state(False, True, False, 0))


def linear(gram, start):
    return _linear(gram, [start])
