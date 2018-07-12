class Case:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __call__(self, val, *args):
        method = getattr(self, type(val).__name__.lower())
        return method(val, *args)


class CaseUnapply1(Case):
    def __call__(self, val, *args):
        method = getattr(self, type(val).__name__.lower())
        return method(val.unapply1(), *args)


class CaseUnapply(Case):
    def __call__(self, val, *args):
        method = getattr(self, type(val).__name__.lower())
        return method(*val.unapply(), *args)
