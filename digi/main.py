from manim import *
from custom.characters.pi_creature import *
from custom.characters.pi_creature_animations import PiCreatureSays, RemovePiCreatureBubble, Blink


class Intro(Scene):
    def construct(self):
        pi = PiCreature("plain").flip().to_corner(RIGHT + DOWN)
        self.play(PiCreatureSays(pi, Tex("$\\psi$ hello"), target_mode="angry"))
        self.play(RemovePiCreatureBubble(pi))
