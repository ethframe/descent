from descent.case import Case


class Macroexpander(Case):
    def grammar(self, val, env):
        new_rules = []
        for rule in val.rules:
            res = self(rule, env)
            if res:
                new_rules.append(res)
        val.rules = new_rules
        return val

    def macro(self, val, env):
        val.expr = self(val.expr, env)
        self.macro_env[(str(val.name), len(val.args))] = val
        return None

    def rule(self, val, env):
        val.expr = self(val.expr.copy(), env)
        return val

    def expand(self, val, env):
        new_ns = dict(env)
        macro = self.macro_env[(str(val.name), len(val.args))]
        for arg, val in zip(macro.args, val.args):
            new_ns[str(arg)] = self(val.copy(), env)
        return self(macro.expr.copy(), new_ns)

    def _expand_expr(self, val, env):
        val.expr = self(val.expr.copy(), env)
        return val

    repeat1 = repeat = optional = _expand_expr
    follow = not_follow = _expand_expr
    ignore = top_splice = splice = top = append = _expand_expr

    def _expand_items(self, val, env):
        val.items = [self(item.copy(), env) for item in val.items]
        return val

    choice = sequence = _expand_items

    def reference(self, val, env):
        return env.get(str(val), val)

    def _expand_none(self, val, env):
        return val

    string = char_any = char_range = char = _expand_none
    node = _expand_none


def expand_macros(grammar):
    case = Macroexpander(macro_env={})
    return case(grammar, {})
