from __future__ import annotations
import random
from typing import Optional

import numpy as np

from .pi_creature_animations import *
from custom.utils import Singleton


class PiCreatureScene(Scene, metaclass=Singleton):
    def __init__(self, **kwargs) -> None:
        self.total_wait_time = kwargs.get("total_wait_time", 0)
        self.seconds_to_blink = kwargs.get("seconds_to_blink", 3)
        self.pi_creatures_start_on_screen = kwargs.get("pi_creatures_start_on_screen", True)
        self.default_pi_creature_kwargs = {
            "color": BLUE,
            "flip_at_start": False,
        }
        self.default_pi_creature_start_corner = kwargs.get("default_pi_creature_start_corner", DL)
        self.pi_creatures = None  # type: VGroup[PiCreature]
        self.pi_creature = None  # type: PiCreature
        super(PiCreatureScene, self).__init__()

    def setup(self) -> None:
        self.pi_creatures = VGroup(*self.create_pi_creatures())
        self.pi_creature = self.get_primary_pi_creature()
        if self.pi_creatures_start_on_screen:
            self.add(*self.pi_creatures)

    def create_pi_creatures(self) -> VGroup:
        """
        Likely updated for subclasses
        """
        return VGroup(self.create_pi_creature())

    def create_pi_creature(self) -> PiCreature:
        pi_creature = PiCreature(**self.default_pi_creature_kwargs)
        pi_creature.to_corner(self.default_pi_creature_start_corner)
        return pi_creature

    def get_pi_creatures(self) -> VGroup:
        return self.pi_creatures

    def get_primary_pi_creature(self) -> PiCreature:
        return self.pi_creatures[0]

    def any_pi_creatures_on_screen(self) -> bool:
        return len(self.get_on_screen_pi_creatures()) > 0

    def get_on_screen_pi_creatures(self) -> VGroup:
        mobjects = self.get_mobject_family_members()
        return VGroup(*[
            pi for pi in self.get_pi_creatures()
            if pi in mobjects
        ])

    def introduce_bubble(self, *args, **kwargs) -> None:
        if isinstance(args[0], PiCreature):
            pi_creature = args[0]
            content = args[1:]
        else:
            pi_creature = self.get_primary_pi_creature()
            content = args

        bubble_class = kwargs.pop("bubble_class", SpeechBubble)
        target_mode = kwargs.pop(
            "target_mode",
            "thinking" if bubble_class is ThoughtBubble else "speaking"
        )
        bubble_kwargs = kwargs.pop("bubble_kwargs", {})
        bubble_removal_kwargs = kwargs.pop("bubble_removal_kwargs", {})
        added_anims = kwargs.pop("added_anims", [])

        anims = []
        on_screen_mobjects = self.get_mobject_family_members()

        def has_bubble(pi: PiCreature) -> bool:
            return pi.bubble is not None and \
                   pi.bubble in on_screen_mobjects

        pi_creatures_with_bubbles = list(filter(has_bubble, self.get_pi_creatures()))
        if pi_creature in pi_creatures_with_bubbles:
            pi_creatures_with_bubbles.remove(pi_creature)
            old_bubble = pi_creature.bubble
            bubble = pi_creature.get_bubble(
                *content,
                bubble_class=bubble_class,
                **bubble_kwargs
            )
            anims += [
                ReplacementTransform(old_bubble, bubble),
                ReplacementTransform(old_bubble.content, bubble.content),
                pi_creature.change_mode, target_mode
            ]
        else:
            anims.append(PiCreatureBubbleIntroduction(
                pi_creature,
                *content,
                bubble_class=bubble_class,
                bubble_kwargs=bubble_kwargs,
                target_mode=target_mode,
                **kwargs
            ))
        anims += [
            RemovePiCreatureBubble(pi, **bubble_removal_kwargs)
            for pi in pi_creatures_with_bubbles
        ]
        anims += added_anims

        self.play(*anims, **kwargs)

    def pi_creature_says(self, *args, **kwargs) -> None:
        self.introduce_bubble(
            *args,
            bubble_class=SpeechBubble,
            **kwargs
        )

    def pi_creature_thinks(self, *args, **kwargs) -> None:
        self.introduce_bubble(
            *args,
            bubble_class=ThoughtBubble,
            **kwargs
        )

    def say(self, *content, **kwargs) -> None:
        self.pi_creature_says(self.get_primary_pi_creature(), *content, **kwargs)

    def think(self, *content, **kwargs) -> None:
        self.pi_creature_thinks(self.get_primary_pi_creature(), *content, **kwargs)

    def compile_animations(self, *args, **kwargs):
        """
        Add animations so that all pi creatures look at the
        first mobject being animated with each .play call
        """
        animations = Scene.compile_animations(self, *args, **kwargs)
        anim_mobjects = Group(*[a.mobject for a in animations])
        all_movers = anim_mobjects.get_family()
        if not self.any_pi_creatures_on_screen():
            return animations

        pi_creatures = self.get_on_screen_pi_creatures()
        non_pi_creature_anims = [
            anim
            for anim in animations
            if len(set(anim.mobject.get_family()).intersection(pi_creatures)) == 0
        ]
        if len(non_pi_creature_anims) == 0:
            return animations
        # Get pi creatures to look at whatever
        # is being animated
        first_anim = non_pi_creature_anims[0]
        main_mobject = first_anim.mobject
        for pi_creature in pi_creatures:
            if pi_creature not in all_movers:
                animations.append(ApplyMethod(
                    pi_creature.look_at,
                    main_mobject,
                ))
        return animations

    def blink(self) -> None:
        self.play(Blink(random.choice(self.get_on_screen_pi_creatures())))

    def joint_blink(self, pi_creatures: PiCreature = None, shuffle: bool = True, **kwargs) -> PiCreatureScene:
        if pi_creatures is None:
            pi_creatures = self.get_on_screen_pi_creatures()
        creatures_list = list(pi_creatures)
        if shuffle:
            random.shuffle(creatures_list)

        def get_rate_func(pi):
            index = creatures_list.index(pi)
            proportion = float(index) / len(creatures_list)
            start_time = 0.8 * proportion
            return squish_rate_func(
                there_and_back,
                start_time, start_time + 0.2
            )

        self.play(*[
            Blink(pi, rate_func=get_rate_func(pi), **kwargs)
            for pi in creatures_list
        ])
        return self

    def wait(self, _time: int = 1, blink: bool = True, **kwargs) -> Optional[PiCreatureScene, None]:
        if "stop_condition" in kwargs:
            self.non_blink_wait(_time, **kwargs)
            return
        while _time >= 1:
            time_to_blink = self.total_wait_time % self.seconds_to_blink == 0
            if blink and self.any_pi_creatures_on_screen() and time_to_blink:
                self.blink()
            else:
                self.non_blink_wait(**kwargs)
            _time -= 1
            self.total_wait_time += 1
        if _time > 0:
            self.non_blink_wait(_time, **kwargs)
        return self

    def non_blink_wait(self, duration_time: int = 1, **kwargs) -> PiCreatureScene:
        Scene.wait(self, duration_time, **kwargs)
        return self

    def change_mode(self, mode: str) -> None:
        self.play(self.get_primary_pi_creature().animate.change_mode(mode))

    def look_at(self, thing_to_look_at, pi_creatures: PiCreature = None, added_anims: list = None, **kwargs) -> None:
        if pi_creatures is None:
            pi_creatures = self.get_pi_creatures()
        anims = [
            pi.animate.look_at(thing_to_look_at)
            for pi in pi_creatures
        ]
        if added_anims is not None:
            anims.extend(added_anims)
        self.play(*anims, **kwargs)


class TeacherStudentsScene(PiCreatureScene):

    def __init__(self):
        self.student_colors = [BLUE_D, BLUE_E, BLUE_C]
        self.teacher_color = GREY_BROWN
        self.background_color = BLACK
        self.student_scale_factor = 0.8
        self.seconds_to_blink = 2
        self.screen_height = 3
        self.background = None
        self.screen = None
        self.hold_up_spot = None
        self.teacher = None
        self.students = None
        super(TeacherStudentsScene, self).__init__()

    def setup(self):
        self.background = FullScreenFadeRectangle(
            fill_color=self.background_color,
            fill_opacity=1,
        )
        self.add(self.background)
        PiCreatureScene.setup(self)
        self.screen = ScreenRectangle(height=self.screen_height)
        self.screen.to_corner(UP + LEFT)
        self.hold_up_spot = self.teacher.get_corner(UP + LEFT) + MED_LARGE_BUFF * UP

    def create_pi_creatures(self):
        self.teacher = Mortimer(color=self.teacher_color)
        self.teacher.to_corner(DOWN + RIGHT)
        self.teacher.look(DOWN + LEFT)
        self.students = VGroup(*[
            Randolph(color=c)
            for c in self.student_colors
        ])
        self.students.arrange(RIGHT)
        self.students.scale(self.student_scale_factor)
        self.students.to_corner(DOWN + LEFT)
        self.teacher.look_at(self.students[-1].eyes)
        for student in self.students:
            student.look_at(self.teacher.eyes)

        return [self.teacher] + list(self.students)

    def get_teacher(self):
        return self.teacher

    def get_students(self):
        return self.students

    def teacher_says(self, *content, **kwargs):
        return self.pi_creature_says(
            self.get_teacher(), *content, **kwargs
        )

    def student_says(self, *content, **kwargs):
        if "target_mode" not in kwargs:
            target_mode = random.choice([
                "raise_right_hand",
                "raise_left_hand",
            ])
            kwargs["target_mode"] = target_mode
        if "bubble_kwargs" not in kwargs:
            kwargs["bubble_kwargs"] = {"direction": LEFT}
        student = self.get_students()[kwargs.get("student_index", 2)]
        return self.pi_creature_says(
            student, *content, **kwargs
        )

    def teacher_thinks(self, *content, **kwargs):
        return self.pi_creature_thinks(
            self.get_teacher(), *content, **kwargs
        )

    def student_thinks(self, *content, **kwargs):
        student = self.get_students()[kwargs.get("student_index", 2)]
        return self.pi_creature_thinks(student, *content, **kwargs)

    def change_all_student_modes(self, mode, **kwargs):
        self.change_student_modes(*[mode] * len(self.students), **kwargs)

    def change_student_modes(self, *modes, **kwargs):
        added_anims = kwargs.pop("added_anims", [])
        self.play(
            self.get_student_changes(*modes, **kwargs),
            *added_anims
        )

    def get_student_changes(self, *modes, **kwargs):
        pairs = list(zip(self.get_students(), modes))
        pairs = [(s, m) for s, m in pairs if m is not None]
        start = VGroup(*[s for s, m in pairs])
        target = VGroup(*[s.copy().change_mode(m) for s, m in pairs])
        if "look_at_arg" in kwargs:
            for pi in target:
                pi.look_at(kwargs["look_at_arg"])
        anims = [
            Transform(s, t)
            for s, t in zip(start, target)
        ]
        return LaggedStart(
            *anims,
            lag_ratio=kwargs.get("lag_ratio", 0.5),
            run_time=1,
        )
        # return Transform(
        #     start, target,
        #     lag_ratio=lag_ratio,
        #     run_time=2
        # )

    def zoom_in_on_thought_bubble(self, bubble=None, radius=config.frame_y_radius + config.frame_x_radius):
        if bubble is None:
            for pi in self.get_pi_creatures():
                if pi.bubble is not None and isinstance(pi.bubble, ThoughtBubble):
                    bubble = pi.bubble
                    break
            if bubble is None:
                raise Exception("No pi creatures have a thought bubble")
        vect = -bubble.get_bubble_center()

        def func(point):
            centered = point + vect
            return radius * centered / np.linalg.norm(centered)
        self.play(*[
            ApplyPointwiseFunction(func, mob)
            for mob in self.mobjects
        ])


class CustomersScene(PiCreatureScene):
    def __init__(self, **kwargs):
        self.customers_colors = [BLUE_D, BLUE_E, BLUE_C, BLUE_B]
        self.background_color = BLACK
        self.customers_scale_factor = 0.3
        self.seconds_to_blink = 2
        self.screen_height = 3
        self.background = None
        self.screen = None
        self.customers = None
        super(CustomersScene, self).__init__(**kwargs)

    def setup(self):
        self.background = FullScreenFadeRectangle(
            fill_color=self.background_color,
            fill_opacity=1,
        )
        self.add(self.background)
        PiCreatureScene.setup(self)
        self.screen = ScreenRectangle(height=self.screen_height)
        self.screen.to_corner(UP + LEFT)

    def create_pi_creatures(self):
        self.customers = VGroup(*[
            Randolph(color=c)
            for c in self.customers_colors
        ])
        self.customers.arrange(DOWN, buff=LARGE_BUFF*1.5)
        self.customers.scale(self.customers_scale_factor)
        self.customers.to_edge(LEFT)
        for customer in self.customers:
            customer.look_at([0, 0, 0])

        return list(self.customers)

    def get_customers(self):
        return self.customers

    def change_all_customers_modes(self, mode, **kwargs):
        self.change_customer_modes(*[mode] * len(self.customers), **kwargs)

    def change_customer_modes(self, *modes, **kwargs):
        added_anims = kwargs.pop("added_anims", [])
        self.play(
            self.get_customers_changes(*modes, **kwargs),
            *added_anims
        )

    def get_customers_changes(self, *modes, **kwargs):
        pairs = list(zip(self.get_customers(), modes))
        pairs = [(s, m) for s, m in pairs if m is not None]
        start = VGroup(*[s for s, m in pairs])
        target = VGroup(*[c.copy().change_mode(m) for c, m in pairs])
        if "look_at_arg" in kwargs:
            for pi in target:
                pi.look_at(kwargs["look_at_arg"])
        anims = [
            Transform(s, t)
            for s, t in zip(start, target)
        ]
        return LaggedStart(
            *anims,
            lag_ratio=kwargs.get("lag_ratio", 0.5),
            run_time=1,
        )
