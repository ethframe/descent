from collections import OrderedDict

from descent.case import Case


class Macroexpander(Case):
    def grammar(self, val, env):
        rules = OrderedDict()
        for rule in val.rules:
            res = self(rule, env)
            if res:
                rules[str(res.name)] = res.expr
        return rules

    def macro(self, val, env):
        val.expr = self(val.expr, env)
        self.macro_env[(str(val.name), len(val.args))] = val
        return None

    def rule(self, val, env):
        val.expr = self(val.expr, env)
        return val

    def expand(self, val, env):
        new_env = dict(env)
        macro = self.macro_env[(str(val.name), len(val.args))]
        for arg, val in zip(macro.args, val.args):
            new_env[str(arg)] = self(val, env)
        return self.copying_expander(macro.expr.copy(), new_env)

    def _expand_expr(self, val, env):
        val.expr = self(val.expr, env)
        return val

    repeat1 = repeat = optional = _expand_expr
    follow = not_follow = _expand_expr
    ignore = top_splice = splice = top = append = _expand_expr

    def _expand_items(self, val, env):
        val.items = [self(item, env) for item in val.items]
        return val

    choice = sequence = _expand_items

    def reference(self, val, env):
        return env.get(str(val), val)

    def _expand_none(self, val, env):
        return val

    string = char_any = char_range = char = _expand_none
    fail = node = _expand_none


class Copyingexpander(Case):
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
    fail = node = _expand_none


def expand_macros(grammar):
    macro_env = {}
    case = Macroexpander(
        macro_env=macro_env,
        copying_expander=Copyingexpander(macro_env=macro_env)
    )
    return case(grammar, {})
