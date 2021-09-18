class Singleton(type):
    """
    Meta-class from https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python#6798042.
    """
    instances = {}

    def __call__(cls, *args, **kwargs):
        """
        This class is a Singleton. Exact docstring and init
        signature should be found at the class definition.
        """
        if cls not in cls.instances:
            cls.instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls.instances[cls]


def is_singleton_initialized(cls):
    """
    Checks if singleton class was already initialized.
    """
    return cls in Singleton.instances