from collections import OrderedDict


def convert_to_dict(grammar):
    grammar_dict = OrderedDict()
    for rule in grammar.rules:
        if str(rule.name) in grammar_dict:
            raise ValueError(
                "Duplicate definition of rule {}".format(rule.name)
            )
        grammar_dict[str(rule.name)] = rule.expr
    return grammar_dict
