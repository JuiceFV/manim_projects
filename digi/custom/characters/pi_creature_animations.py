from manim import *

from .pi_creature import *
from ..drawings import SpeechBubble


class Blink(ApplyMethod):
    def __init__(self, pi_creature: PiCreature, **kwargs) -> None:
        super(Blink, self).__init__(pi_creature.blink, rate_func=squish_rate_func(there_and_back), **kwargs)


class PiCreatureBubbleIntroduction(AnimationGroup):
    self_defaults = {
        "target_mode": "speaking",
        "bubble_class": SpeechBubble,
        "change_mode_kwargs": {},
        "bubble_creation_class": DrawBorderThenFill,
        "bubble_creation_kwargs": {},
        "bubble_kwargs": {},
        "content_introduction_class": Write,
        "content_introduction_kwargs": {},
        "look_at_arg": None,
    }
    parent_defaults = {
        'lag_ratio': 0.0,
        'run_time': 1.0,
        'rate_func': smooth,
        'name': None,
        'remover': False,
        'suspend_mobject_updating': True,
    }

    def __init__(self, pi_creature: PiCreature, *content, **kwargs) -> None:
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

        bubble = pi_creature.get_bubble(
            *content,
            bubble_class=self.bubble_class,
            **self.bubble_kwargs
        )
        Group(bubble, bubble.content).shift_onto_screen()

        pi_creature.generate_target()
        pi_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            pi_creature.target.look_at(self.look_at_arg)

        change_mode = MoveToTarget(pi_creature, **self.change_mode_kwargs)
        bubble_creation = self.bubble_creation_class(
            bubble, **self.bubble_creation_kwargs
        )
        content_introduction = self.content_introduction_class(
            bubble.content, **self.content_introduction_kwargs
        )
        AnimationGroup.__init__(
            self, change_mode, bubble_creation, content_introduction,
            **self.parent_defaults
        )


class PiCreatureSays(PiCreatureBubbleIntroduction):
    self_cfg = {"target_mode": "speaking", "bubble_class": SpeechBubble}

    def __init__(self, pi_creature: PiCreature, *content, **kwargs) -> None:
        self.self_cfg.update(kwargs)
        super(PiCreatureSays, self).__init__(pi_creature, *content, **self.self_cfg)


class RemovePiCreatureBubble(AnimationGroup):
    self_defaults = {
        "target_mode": "plain",
        "look_at_arg": None,
        "remover": True,
    }

    def __init__(self, pi_creature, **kwargs):
        for key, value in self.self_defaults.items():
            setattr(self, key, kwargs.get(key, value))
            if key in kwargs:
                kwargs.pop(key)
        if len(kwargs) > 0:
            raise TypeError(f"Wrong argument is passed {kwargs.keys()[0]}")
        self.pi_creature = pi_creature
        if self.pi_creature.bubble is None:
            raise AttributeError(f"{type(pi_creature).__name__} has no bubbles")
        self.pi_creature.generate_target()
        self.pi_creature.target.change_mode(self.target_mode)
        if self.look_at_arg is not None:
            pi_creature.target.look_at(self.look_at_arg)

        AnimationGroup.__init__(
            self,
            MoveToTarget(pi_creature),
            FadeOut(pi_creature.bubble),
            FadeOut(pi_creature.bubble.content),
        )

    def clean_up_from_scene(self, scene=None):
        super(RemovePiCreatureBubble, self).clean_up_from_scene(scene)
        self.pi_creature.bubble = None
        if scene is not None:
            scene.add(self.pi_creature)
