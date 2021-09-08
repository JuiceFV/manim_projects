from manim import *
from typing import Union, List


def play_and_wait(*animations, scene: Scene,
                  play_time: Union[int, List[int]] = 1, wait_time: int = 1):
    for idx, animation in enumerate(animations):
        pt = play_time[idx] if isinstance(play_time, list) else play_time
        animation.set_run_time(pt)
    scene.play(*animations)
    scene.wait(wait_time)

