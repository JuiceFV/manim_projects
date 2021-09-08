from manim import *
from introduction import Intro


class DefaultTemplate(Scene):
    def construct(self):
        Intro(self).play()