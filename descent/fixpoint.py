from descent.case import CaseVal


class CaseFix(CaseVal):
    def __init__(self, fix, **kwargs):
        super().__init__(**kwargs)
        self.fix = fix

    def reference(self, val, *args):
        return self.fix.get(val, *args)


class State:
    def __init__(self, keys, bot):
        self.bot = bot
        self.storage = {k: {} for k in keys}
        self.changed = False

    def update(self, val, key, *args):
        if self.storage[key][args] != val:
            self.storage[key][args] = val
            self.changed = True

    def get(self, key, *args):
        if args not in self.storage[key]:
            self.storage[key][args] = self.bot
            self.changed = True
        return self.storage[key][args]

    def next(self):
        changed = self.changed
        self.changed = False
        return changed

    def __iter__(self):
        for rule, rule_state in self.storage.items():
            for args in list(rule_state):
                yield rule, args


def fix(case, bottom):
    def fn(gram, rules, *args, **kwargs):
        state = State(gram.keys(), bottom)
        op = case(state, **kwargs)
        for rule in rules:
            state.get(rule, *args)

        while state.next():
            for rule, args in state:
                state.update(op(gram[rule], *args), rule, *args)

        return state.storage

    return fn


def result_by_args(state, *args):
    return {rule: res[args] for rule, res in state.items() if args in res}
