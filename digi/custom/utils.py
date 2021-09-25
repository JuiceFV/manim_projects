import typing

from manim import *

__all__ = ["Singleton", "is_singleton_initialized", "parent_kwargs"]


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


def _get_bubble_kwargs(**kwargs) -> dict:
    res_kwargs = {
        "color": BLACK,
        "fill_opacity": 0.8,
        "stroke_color": WHITE,
        "stroke_width": 3,
        "height": 5,
        "width": 8
    }
    for key, value in res_kwargs.items():
        res_kwargs[key] = kwargs.pop(key, value)

    if len(kwargs) > 0:
        raise TypeError(f"Wrong argument is passed {list(kwargs.keys())[0]}")

    return res_kwargs


def _get_pcbi_kwargs(**kwargs) -> dict:
    res_kwargs = {
            'lag_ratio': 0.0,
            'run_time': 1.0,
            'rate_func': smooth,
            'name': None,
            'remover': False,
            'suspend_mobject_updating': True,
        }

    for key, value in res_kwargs.items():
        res_kwargs[key] = kwargs.pop(key, value)

    if len(kwargs) > 0:
        raise TypeError(f"Wrong argument is passed {list(kwargs.keys())[0]}")

    return res_kwargs


def _get_pi_creature_kwargs(**kwargs) -> dict:
    res_kwargs = {
        "color": BLUE_E,
        "stroke_width": 0,
        "stroke_color": BLACK,
        "fill_opacity": 1.0,
        "height": 3
    }

    for key, value in res_kwargs.items():
        res_kwargs[key] = kwargs.pop(key, value)

    if len(kwargs) > 0:
        raise TypeError(f"Wrong argument is passed {list(kwargs.keys())[0]}")

    return res_kwargs


def parent_kwargs(class_obj, **kwargs):
    res_kwargs = {}
    parent_classnames = list(map(lambda class_type: class_type.__name__, type(class_obj).__bases__))

    if "Bubble" in parent_classnames + [type(class_obj).__name__]:
        res_kwargs = _get_bubble_kwargs(**kwargs)
    elif "PiCreatureBubbleIntroduction" in parent_classnames + [type(class_obj).__name__]:
        res_kwargs = _get_pcbi_kwargs(**kwargs)
    elif "PiCreature" in parent_classnames + [type(class_obj).__name__]:
        res_kwargs = _get_pi_creature_kwargs(**kwargs)

    return res_kwargs

