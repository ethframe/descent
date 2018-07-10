from collections import namedtuple

from descent.fixpoint import CaseFix, fix, result_by_args


state = namedtuple("State", "wf nul inv")


class GrammarCheck(CaseFix):
    def reference(self, val):
        return self.fix.get(val)

    def string(self, val):
        return state(True, not val, False)

    def char(self, val):
        return state(True, False, False)

    def char_any(self, val):
        return state(True, False, False)

    def char_range(self, val):
        return state(True, False, False)

    def sequence(self, val):
        nul = True
        inv = False
        for p in val:
            s = self(p)
            if nul and not s.wf:
                return self.fix.bot
            nul &= s.nul
            inv |= s.inv
        return state(True, nul, inv)

    def choice(self, val):
        nul = False
        for p in val:
            s = self(p)
            if not s.wf:
                return self.fix.bot
            nul |= s.nul
        return state(True, nul, False)

    def not_follow(self, val):
        s = self(val)
        return state(s.wf, not (s.wf and s.nul), s.inv)

    def follow(self, val):
        return self(val)

    def optional(self, val):
        s = self(val)
        return state(s.wf, True, s.inv)

    def repeat(self, val):
        s = self(val)
        return state(s.wf and not s.nul, True, s.inv or s.nul)

    def repeat1(self, val):
        s = self(val)
        return state(s.wf and not s.nul, False, s.inv or s.nul)

    def node(self, val):
        return state(True, True, False)

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

    def replace(self, val):
        return self(val.expr)

    def fail(self, val):
        return state(True, False, False)


check = fix(GrammarCheck, state(False, True, False))


def check_grammar(gram):
    return result_by_args(check(gram, [list(gram)[0]]))


def get_invalid(result):
    return [rule for rule, res in result.items() if res.inv]
