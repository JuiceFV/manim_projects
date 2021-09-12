import os
from abc import ABC
from pathlib import Path
from typing import Union
from manim import *
from ..drawings import ThoughtBubble

PI_CREATURE_SCALE_FACTOR = 0.5

LEFT_EYE_INDEX = 0
RIGHT_EYE_INDEX = 1
LEFT_PUPIL_INDEX = 2
RIGHT_PUPIL_INDEX = 3
BODY_INDEX = 4
MOUTH_INDEX = 5


class PiCreature(SVGMobject, ABC):
    self_defaults = {
        "file_name_prefix": "PiCreature",
        "corner_scale_factor": 0.75,
        "flip_at_start": False,
        "is_looking_direction_purposeful": False,
        "start_corner": None,
        "pupil_to_eye_width_ratio": 0.4,
        "pupil_dot_to_pupil_width_ratio": 0.3,
    }
    parent_defaults = {
        "color": BLUE_E,
        "stroke_width": 0,
        "stroke_color": BLACK,
        "fill_opacity": 1.0,
        "height": 3
    }

    def __init__(self, mode: str = "plain", **kwargs) -> None:
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

        self.mouth = None
        self.body = None
        self.pupils = None
        self.eyes = None
        self.eye_parts = None
        self.bubble = None
        self.mode = mode
        self.parts_named = False
        try:
            svg_file = str(Path(__file__).parent / f"svgs/{self.file_name_prefix}_{mode}.svg")
            super(PiCreature, self).__init__(file_name=svg_file, **self.parent_defaults)
        except IOError as e:
            raise e

        if self.flip_at_start:
            self.flip()
        if self.start_corner is not None:
            self.to_corner(self.start_corner)

        self.purposeful_looking_direction = None

    def align_data(self, mobject: Mobject) -> None:
        # This ensures that after a transform into a different mode,
        # the pi creatures mode will be updated appropriately
        super(PiCreature, self).align_data(mobject)
        if isinstance(mobject, PiCreature):
            self.mode = mobject.get_mode()

    def name_parts(self):
        self.mouth = self.submobjects[MOUTH_INDEX]
        self.body = self.submobjects[BODY_INDEX]
        self.pupils = VGroup(*[
            self.submobjects[LEFT_PUPIL_INDEX],
            self.submobjects[RIGHT_PUPIL_INDEX]
        ])
        self.eyes = VGroup(*[
            self.submobjects[LEFT_EYE_INDEX],
            self.submobjects[RIGHT_EYE_INDEX]
        ])
        self.eye_parts = VGroup(self.eyes, self.pupils)
        self.parts_named = True

    def init_colors(self, propagate_colors: bool = False) -> SVGMobject:
        super(PiCreature, self).init_colors(propagate_colors)
        if not self.parts_named:
            self.name_parts()
        self.mouth.set_fill(BLACK, opacity=1)
        self.body.set_fill(self.color, opacity=1)
        self.body.set_stroke(self.color, opacity=1)
        self.eyes.set_fill(WHITE, opacity=1)
        self.init_pupils()
        return self

    def init_pupils(self):
        # Instead of what is drawn, make new circles.
        # This is mostly because the paths associated
        # with the eyes in all the drawings got slightly
        # messed up.
        for eye, pupil in zip(self.eyes, self.pupils):
            pupil_r = eye.get_width() / 2
            pupil_r *= self.pupil_to_eye_width_ratio
            dot_r = pupil_r
            dot_r *= self.pupil_dot_to_pupil_width_ratio

            new_pupil = Circle(
                radius=pupil_r,
                color=BLACK,
                fill_opacity=1,
                stroke_width=0,
            )
            dot = Circle(
                radius=dot_r,
                color=WHITE,
                fill_opacity=1,
                stroke_width=0,
            )
            new_pupil.move_to(pupil)
            pupil.become(new_pupil)
            dot.shift(
                new_pupil.get_boundary_point(UL) -
                dot.get_boundary_point(UL)
            )
            pupil.add(dot)

    def copy(self) -> SVGMobject:
        copy_mobject = SVGMobject.copy(self)
        copy_mobject.name_parts()
        return copy_mobject

    def set_color(self, color) -> SVGMobject:
        self.body.set_fill(color)
        self.color = color
        return self

    def change_mode(self, mode: str) -> SVGMobject:
        new_self = self.__class__(
            mode=mode,
        )

        new_self.match_style(self)
        new_self.match_height(self)
        if self.is_flipped() != new_self.is_flipped():
            new_self.flip()
        new_self.shift(self.eyes.get_center() - new_self.eyes.get_center())
        if self.purposeful_looking_direction is not None:
            new_self.look(self.purposeful_looking_direction)
        self.become(new_self)
        self.mode = mode
        return self

    def get_mode(self):
        return self.mode

    def look(self, direction: np.array) -> Union[None, SVGMobject]:
        norm = np.linalg.norm(direction)
        if norm == 0:
            return
        direction /= norm
        self.purposeful_looking_direction = direction
        for pupil, eye in zip(self.pupils.split(), self.eyes.split()):
            c = eye.get_center()
            right = eye.get_right() - c
            up = eye.get_top() - c
            vect = direction[0] * right + direction[1] * up
            v_norm = np.linalg.norm(vect)
            p_radius = 0.5 * pupil.get_width()
            vect *= (v_norm - 0.75 * p_radius) / v_norm
            pupil.move_to(c + vect)
        self.pupils[1].align_to(self.pupils[0], DOWN)
        return self

    def look_at(self, point_or_mobject):
        if isinstance(point_or_mobject, Mobject):
            point = point_or_mobject.get_center()
        else:
            point = point_or_mobject
        self.look(point - self.eyes.get_center())
        return self

    def change(self, new_mode: str, look_at_arg=None):
        self.change_mode(new_mode)
        if look_at_arg is not None:
            self.look_at(look_at_arg)
        return self

    def get_looking_direction(self):
        vect = self.pupils.get_center() - self.eyes.get_center()
        return normalize(vect)

    def get_look_at_spot(self):
        return self.eyes.get_center() + self.get_looking_direction()

    def is_flipped(self):
        return self.eyes.submobjects[0].get_center()[0] > \
               self.eyes.submobjects[1].get_center()[0]

    def blink(self):
        eye_parts = self.eye_parts
        eye_bottom_y = eye_parts.get_bottom()[1]
        eye_parts.apply_function(
            lambda p: [p[0], eye_bottom_y, p[2]]
        )
        return self

    def to_corner(self, vect=None, **kwargs):
        if vect is not None:
            SVGMobject.to_corner(self, vect, **kwargs)
        else:
            self.scale(self.corner_scale_factor)
            self.to_corner(DOWN + LEFT, **kwargs)
        return self

    def get_bubble(self, content, **kwargs):
        bubble_class = kwargs.get('bubble_class', ThoughtBubble)
        if 'bubble_class' in kwargs:
            kwargs.pop('bubble_class')
        bubble = bubble_class(**kwargs)
        if len(content) > 0:
            if isinstance(content[0], str):
                content_mob = Text(content)
            else:
                content_mob = content
            bubble.add_content(content_mob)
            if "height" not in kwargs and "width" not in kwargs:
                bubble.resize_to_content()
        bubble.pin_to(self)
        self.bubble = bubble
        return bubble

    def make_eye_contact(self, pi_creature):
        self.look_at(pi_creature.eyes)
        pi_creature.look_at(self.eyes)
        return self

    def shrug(self) -> SVGMobject:
        self.change_mode("shruggie")
        points = self.mouth.get_points()
        top_mouth_point, bottom_mouth_point = [
            points[np.argmax(points[:, 1])],
            points[np.argmin(points[:, 1])]
        ]
        self.look(top_mouth_point - bottom_mouth_point)
        return self


def get_all_pi_creature_modes():
    result = []
    prefix = PiCreature.self_defaults["file_name_prefix"] + "_"
    suffix = ".svg"
    for file in os.listdir(Path(__file__).parent/"svgs"):
        if file.startswith(prefix) and file.endswith(suffix):
            result.append(
                file[len(prefix):-len(suffix)]
            )
    return result


class Alex(PiCreature, ABC):
    pass  # Nothing more than an alternative name
