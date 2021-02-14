from manim import *

class NetworkMobject(Scene):
    def construct(self):
        layers = VGroup(*[
            self.get_layer(28)
            for i in range(28)
        ])
        layers.arrange(RIGHT, buff = SMALL_BUFF)
        self.add(layers)
        self.wait(1)
        
    def get_layer(self, size):
        layer = VGroup()
        n_neurons = size
        neurons = VGroup(*[
            Circle(radius = 0.05)
            for x in range(n_neurons)
        ])
        neurons.arrange(DOWN, buff=SMALL_BUFF)
        layer.add(neurons)
        return layer