from manim import *

from ..drawings import SpeechBubble, ThoughtBubble


class Blink(ApplyMethod):
    def __init__(self, pi_creature, **kwargs):
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

    def __init__(self, pi_creature, *content, **kwargs):
        for key, value in self.self_defaults.items():
            setattr(self, key, kwargs.get(key, value))
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
            **kwargs
        )


class PiCreatureSays(PiCreatureBubbleIntroduction):
    def __init__(self, pi_creature, *content, **kwargs):
        # TODO: **kwargs overthrown default
        kwargs.update({"target_mode": "speaking", "bubble_class": SpeechBubble})
        super(PiCreatureSays, self).__init__(pi_creature, *content, **kwargs)


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
