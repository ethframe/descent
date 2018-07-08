from collections import namedtuple

from descent.fixpoint import CaseFix, fix, result_by_args


state = namedtuple("State", "wf nul")


class GrammarCheck(CaseFix):
    def reference(self, val):
        return self.fix.get(val)

    def string(self, val):
        return state(True, not val)

    def char(self, val):
        return state(True, False)

    def char_any(self, val):
        return state(True, False)

    def char_range(self, val):
        return state(True, False)

    def sequence(self, val):
        nul = True
        for p in val:
            s = self(p)
            if nul and not s.wf:
                return self.fix.bot
            nul &= s.nul
        return state(True, nul)

    def choice(self, val):
        nul = False
        for p in val:
            s = self(p)
            if not s.wf:
                return self.fix.bot
            nul |= s.nul
        return state(True, nul)

    def not_follow(self, val):
        s = self(val)
        return state(s.wf, not (s.wf and s.nul))

    def follow(self, val):
        return self(val)

    def optional(self, val):
        s = self(val)
        return state(s.wf, True)

    def repeat(self, val):
        s = self(val)
        return state(s.wf and not s.nul, True)

    def repeat1(self, val):
        s = self(val)
        return state(s.wf and not s.nul, False)

    def node(self, val):
        return state(True, True)

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

    def fail(self, val):
        return state(True, False)


check = fix(GrammarCheck, state(False, True))


def check_grammar(gram):
    return result_by_args(check(gram, [list(gram)[0]]))


def get_not_wf(result):
    return [rule for rule, res in result.items() if not res.wf]
