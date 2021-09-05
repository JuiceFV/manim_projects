from manim import *
from logos.youtube import IntroYTLayout

__all__ = ['Intro']

class Intro:
    CONFIG = {
        'logo_height': 1,
        'logo_buff': 0.8
    }
    def __init__(self, scene: Scene):
        self._scene = scene
        self._first_video = FirstVideoSnapshot(scene)
        self._yt_logos = IntroYTLayout(logo_height=self.CONFIG['logo_height'], logo_buff=self.CONFIG['logo_buff'])

    def play(self):
        self.draw_yt_icons()
        self.play_first_video_snapshot()
        self.move_first_video_content_inside_icon()

    def draw_yt_icons(self):
        self._scene.play(DrawBorderThenFill(self._yt_logos))

    def play_first_video_snapshot(self):
        self._first_video.play()

    def move_first_video_content_inside_icon(self):
        self._scene.play(self._first_video.right_query.animate.set_width(self.CONFIG['logo_height'] + 0.2).move_to(
            self._yt_logos[0].get_center()
        ))
        self._scene.remove(self._first_video.wrong_query)


class FirstVideoSnapshot:
    def __init__(self, scene: Scene, play_time: int = 10, wait_time: int = 5):
        self.scene = scene
        self.play_time = play_time
        self.wait_time = wait_time
        self.wrong_query = Text("лореаль париж rhtv-красcк а", color=RED_D)
        self.layout_fixed = Text("лореаль париж крем-красcк а", color=YELLOW_D)
        self.brand_fixed = Text("l'oreal paris крем-красcк а", color=GOLD_D)
        self.spaces_fixed = Text("l'oreal paris крем-красcка", color=TEAL_D)
        self.right_query = Text("l'oreal paris крем-краcка", color=GREEN_D)

    def fix_layout(self):
        self.scene.play(Transform(self.wrong_query, self.layout_fixed, run_time=self.play_time/5))
        self.scene.wait(self.wait_time / 5)
        self.scene.remove(self.wrong_query)
        self.wrong_query = self.layout_fixed

    def fix_brand(self):
        self.scene.play(Transform(self.wrong_query, self.brand_fixed, run_time=self.play_time/5))
        self.scene.wait(self.wait_time / 5)
        self.scene.remove(self.wrong_query)
        self.wrong_query = self.brand_fixed

    def fix_space(self):
        self.scene.play(Transform(self.wrong_query, self.spaces_fixed, run_time=self.play_time/5))
        self.scene.wait(self.wait_time/5)
        self.scene.remove(self.wrong_query)
        self.wrong_query = self.spaces_fixed

    def fix_typos(self):
        self.scene.play(Transform(self.wrong_query, self.right_query, run_time=self.play_time/5))
        self.scene.wait(self.wait_time/5)
        self.scene.remove(self.wrong_query)
        self.wrong_query = self.spaces_fixed


    def play(self):
        self.scene.play(Write(self.wrong_query, run_time=self.play_time/5))
        self.fix_layout()
        self.fix_brand()
        self.fix_space()
        self.fix_typos()

