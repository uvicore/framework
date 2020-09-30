class hybridmethod(classmethod):
    """Decorator for a class method that can be both a @classmethod or regular instance method"""
    def __get__(self, instance, type_):
        descr_get = super().__get__ if instance is None else self.__func__.__get__
        return descr_get(instance, type_)
