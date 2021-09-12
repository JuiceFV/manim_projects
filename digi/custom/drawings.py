from abc import ABC

import numpy as np
from pathlib import Path
from manim import *


class Bubble(SVGMobject, ABC):
    self_defaults = {
        "direction": LEFT,
        "center_point": ORIGIN,
        "content_scale_factor": 0.75,
        "bubble_center_adjustment_factor": 1. / 8,
        "file_name": None,
    }
    parent_defaults = {
        "color": BLACK,
        "fill_opacity": 0.8,
        "stroke_color": WHITE,
        "stroke_width": 3,
        "height": 5,
        "width": 8,
    }

    def __init__(self, **kwargs):
        self.direction_was_specified = ("direction" in kwargs)

        for key, value in self.self_defaults.items():
            setattr(self, key, kwargs.get(key, value))
            if key in kwargs:
                kwargs.pop(key)

        for key, value in self.parent_defaults.items():
            self.parent_defaults[key] = kwargs.get(key, value)
            if key in kwargs:
                kwargs.pop(key)

        if len(kwargs) > 0:
            raise TypeError(f"Wrong argument is passed {kwargs.keys()[0]}")

        if self.file_name is None:
            raise Exception("Must invoke Bubble subclass")
        super(Bubble, self).__init__(self.file_name, **self.parent_defaults)

        self.center()
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.width)
        if self.direction[0] > 0:
            self.flip()
        self.content = Mobject()
        if config.renderer == "opengl":
            self.refresh_triangulation()

    def get_tip(self) -> np.ndarray:
        # TODO, find a better way
        return self.get_corner(DOWN + self.direction) - 0.6 * self.direction

    def get_bubble_center(self):
        factor = self.bubble_center_adjustment_factor
        return self.get_center() + factor * self.get_height() * UP

    def move_tip_to(self, point):
        mover = VGroup(self)
        if self.content is not None:
            mover.add(self.content)
        mover.shift(point - self.get_tip())
        return self

    def flip(self, axis: np.ndarray = UP, **kwargs) -> SVGMobject:
        Mobject.flip(self, axis=axis, **kwargs)
        if config.renderer == "opengl":
            self.refresh_unit_normal()
            self.refresh_triangulation()
        if abs(axis[1]) > 0:
            self.direction = -np.array(self.direction)
        return self

    def pin_to(self, mobject: Mobject) -> SVGMobject:
        mob_center = mobject.get_center()
        want_to_flip = np.sign(mob_center[0]) != np.sign(self.direction[0])
        print(want_to_flip, self.direction, mob_center)
        can_flip = not self.direction_was_specified
        if want_to_flip and can_flip:
            self.flip()
        if config.renderer == "opengl":
            boundary_point = mobject.get_bounding_box_point(UP - self.direction)
        else:
            boundary_point = mobject.get_critical_point(UP - self.direction)
        vector_from_center = 1.0 * (boundary_point - mob_center)
        self.move_tip_to(mob_center + vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        scaled_width = self.content_scale_factor * self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.set_width(scaled_width)
        mobject.shift(
            self.get_bubble_center() - mobject.get_center()
        )
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, *text):
        self.add_content(Tex(*text))
        return self

    def resize_to_content(self):
        target_width = self.content.get_width()
        target_width += max(MED_LARGE_BUFF, 2)
        target_height = self.content.get_height()
        target_height += 2.5 * LARGE_BUFF
        tip_point = self.get_tip()
        self.stretch_to_fit_width(target_width)
        self.stretch_to_fit_height(target_height)
        self.move_tip_to(tip_point)
        self.position_mobject_inside(self.content)

    def clear(self):
        self.add_content(VMobject())
        return self


class SpeechBubble(Bubble, ABC):
    def __init__(self, **kwargs):
        # TODO: **kwargs overthrown default
        kwargs.update({"file_name": str(Path(__file__).parent/"svgs/Bubbles_speech.svg"), "height": 4})
        super(SpeechBubble, self).__init__(**kwargs)


class ThoughtBubble(Bubble, ABC):
    def __init__(self, **kwargs):
        # TODO: **kwargs overthrown default
        kwargs.update({"file_name": str(Path(__file__).parent/"svgs/Bubbles_thought.svg")})
        super(ThoughtBubble, self).__init__(**kwargs)
        self.submobjects.sort(
            key=lambda m: m.get_bottom()[1]
        )

    def make_green_screen(self):
        self.submobjects[-1].set_fill(PURE_GREEN, opacity=1)
        return self
