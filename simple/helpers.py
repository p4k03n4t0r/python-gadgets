class RandomException:
    def __init__(self, e):
        self.message = repr(e)

    def __call__(self):
        # return "FLAG"
        return eval(self.arg, globals(), self._dict)


class RandomClass:
    # gadget to lose an argument
    # chain next __call__ class via a_method
    def __call__(self, an_argument):
        return self.a_method()


class RandomClass2:
    # gadget to lose an argument
    # set a_property to UpperRequest as placefiller
    # chain next __call__ class via a_method
    def __call__(self, an_argument):
        return self.a_property.a_method()