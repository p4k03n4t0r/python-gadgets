class EvalClass:
    def __init__(self, e):
        self.message = repr(e)

    def __call__(self, a_dict):
        return eval(self.arg, globals(), a_dict)


class RandomClass1:
    def __call__(self):
        return self.a_method({})


class RandomClass2:
    def __call__(self):
        return self.a_property.a_property.a_property.a_method({})
