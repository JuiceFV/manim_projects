from __future__ import annotations
from .pi_creature import *
from ..drawings import SpeechBubble
from ..utils import parent_kwargs


class Blink(ApplyMethod):
    def __init__(self, pi_creature: PiCreature, **kwargs) -> None:
        super(Blink, self).__init__(pi_creature.blink, rate_func=squish_rate_func(there_and_back), **kwargs)


class PiCreatureBubbleIntroduction(AnimationGroup):

    def __init__(self, pi_creature: PiCreature, *content, **kwargs) -> None:
        """

        :param pi_creature:
        :param content:
        :param kwargs:
        """
        self.target_mode = kwargs.pop("target_mode", "speaking")
        self.bubble_class = kwargs.pop("bubble_class", SpeechBubble)
        self.change_mode_kwargs = kwargs.pop("change_mode_kwargs", {})
        self.bubble_creation_class = kwargs.pop("bubble_creation_class", DrawBorderThenFill)
        self.bubble_creation_kwargs = kwargs.pop("bubble_creation_kwargs", {})
        self.bubble_kwargs = kwargs.pop("bubble_kwargs", {})
        self.content_introduction_class = kwargs.pop("content_introduction_class", Write)
        self.content_introduction_kwargs = kwargs.pop("content_introduction_kwargs", {})
        self.look_at_arg = kwargs.pop("look_at_arg", None)

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
            **parent_kwargs(self, **kwargs)
        )


class PiCreatureSays(PiCreatureBubbleIntroduction):
    self_cfg = {"target_mode": "speaking", "bubble_class": SpeechBubble}

    def __init__(self, pi_creature: PiCreature, *content, **kwargs) -> None:
        self.self_cfg.update(kwargs)
        super(PiCreatureSays, self).__init__(pi_creature, *content, **self.self_cfg)


class RemovePiCreatureBubble(AnimationGroup):
    def __init__(self, pi_creature, **kwargs):
        self.target_mode = kwargs.pop("target_mode", "plain")
        self.look_at_arg = kwargs.pop("look_at_arg", None)
        self.remover = kwargs.pop("remover", True)
        if len(kwargs) > 0:
            raise TypeError(f"Wrong argument is passed {list(kwargs.keys())[0]}")

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
