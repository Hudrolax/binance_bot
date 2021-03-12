class BaseClass:
    _working = True

    @classmethod
    def working(cls):
        return cls._working

    @classmethod
    def exit(cls):
        cls._working = False