from manim import *
from logos.youtube import IntroYTLayout

__all__ = ['Intro']


class Intro:
    def __init__(self, scene: Scene, scene_play_time: list):
        if len(scene_play_time) != 6:
            raise
        if sum(scene_play_time) < 6:
            raise
        self._scene = scene
        self._first_video = FirstVideoIntro(scene, scene_play_time[0])
        self._second_video = SecondVideoIntro(scene, scene_play_time[1])
        self._yt_logos = IntroYTLayout()

    def play(self):
        self._draw_yt_icons()
        self._play_first_video_snapshot()
        self._move_first_video_content_inside_icon()
        self._play_second_video_snapshot()

    def _draw_yt_icons(self):
        self._scene.play(DrawBorderThenFill(self._yt_logos))

    def _play_first_video_snapshot(self):
        self._first_video.play()

    def _play_second_video_snapshot(self):
        self._second_video.play()

    def _move_first_video_content_inside_icon(self):
        self._scene.play(
            self._first_video.right_query.animate.set_width(
                IntroYTLayout.CONFIG['logo_height'] + 0.2).move_to(self._yt_logos[0].get_center())
        )


class FirstVideoIntro:
    CONFIG = {
        'fix_layout_wait_time': 1,
        'fix_brand_wait_time': 1,
        'fix_space_wait_time': 1,
        'fix_typos_wait_time': 1,
    }

    def __init__(self, scene: Scene, play_time: int = 15):
        self.scene = scene
        self.play_time = play_time
        self.wrong_query = Text("лореаль париж rhtv-красcк а", color=RED_D)
        self.layout_fixed_query = Text("лореаль париж крем-красcк а", color=YELLOW_D)
        self.brand_fixed_query = Text("l'oreal paris крем-красcк а", color=GOLD_D)
        self.spaces_fixed_query = Text("l'oreal paris крем-красcка", color=TEAL_D)
        self.right_query = Text("l'oreal paris крем-краcка", color=GREEN_D)

    def fix_layout(self):
        self.scene.play(Transform(self.wrong_query, self.layout_fixed_query, run_time=self.play_time/5))
        self.scene.wait(self.CONFIG['fix_layout_wait_time'])
        self.remove_query('wrong')

    def fix_brand(self):
        self.scene.play(Transform(self.layout_fixed_query, self.brand_fixed_query, run_time=self.play_time/5))
        self.scene.wait(self.CONFIG['fix_brand_wait_time'])
        self.remove_query('layout_fixed')

    def fix_space(self):
        self.scene.play(Transform(self.brand_fixed_query, self.spaces_fixed_query, run_time=self.play_time/5))
        self.scene.wait(self.CONFIG['fix_space_wait_time'])
        self.remove_query('brand_fixed')

    def fix_typos(self):
        self.scene.play(TransformMatchingShapes(self.spaces_fixed_query, self.right_query, run_time=self.play_time/5))
        self.scene.wait(self.CONFIG['fix_typos_wait_time'])
        self.remove_query('spaces_fixed')

    def play(self):
        self.scene.play(Write(self.wrong_query, run_time=self.play_time/5))
        self.fix_layout()
        self.fix_brand()
        self.fix_space()
        self.fix_typos()

    def remove_query(self, query_name):
        if hasattr(self, query_name + '_query'):
            self.scene.remove(getattr(self, query_name + '_query'))


class SecondVideoIntro:
    def __init__(self, scene: Scene, play_time: int = 15):
        self.scene = scene
        self.play_time = play_time
        self.query = Text("Помада GUCCI")
        self.product_candidates = VGroup(*[
            Text("Губная помада | GUCCI | Rouge à Lèvres Voile").scale(0.5),
            Text("Губная помада | GUCCI | Rouge à Lèvres Mat").scale(0.5),
            Text("Губная помада | GUCCI | Rouge à Lèvres Satin").scale(0.5),
            Text("Губная помада | GUCCI | Baume à Lèvres").scale(0.5),
            Tex(r"$\vdots$"),
            Text("Губная помада | GUCCI | Rouge de Beauté Brillant").scale(0.5),
        ]).arrange(DOWN)
        self.categories = VGroup(*[
            Text("Губы"),
            Text("лицо"),
            Text("Брови"),
            Text("женские ароматы"),
            Text("детям")
        ]).scale(0.5).arrange(DOWN)
        self.rank_scores = VGroup(*[
            Text("3.43"),
            Text("-3.55"),
            Text("-3.66"),
            Text("-4.30"),
            Text("-7.14"),
            Text("\0")
        ]).scale(0.5).arrange(DOWN).next_to(self.categories, RIGHT)

    def write_query(self):
        self.scene.play(Write(self.query, run_time=self.play_time / 5))
        self.scene.play(self.query.animate.scale(0.3).to_edge(UL + [0.01, 4, 0]))

    def get_candidates(self):
        self.scene.play(TransformFromCopy(self.query, self.product_candidates))

        candidates_framebox = SurroundingRectangle(self.product_candidates, buff=0.5)
        self.scene.play(Create(candidates_framebox))

        candidates_label = Text("Кандидаты",
                               width=int(candidates_framebox.width) - 1).scale(0.5).next_to(candidates_framebox, UP)
        self.scene.play(Write(candidates_label))

        inboxed_candidates = VGroup(*[
            candidates_framebox, self.product_candidates, candidates_label
        ])
        self.scene.play(inboxed_candidates.animate.scale(0.3).next_to(self.query, RIGHT * 2))
        arrow_1 = Arrow(
            self.query, candidates_framebox.get_center() - [candidates_framebox.width/2, 0, 0],
            stroke_width=5, buff=0.1)
        self.scene.play(FadeIn(arrow_1))

    def play(self):
        self.write_query()
        self.get_candidates()

        self.scene.play(TransformFromCopy(self.product_candidates, self.categories))
        self.scene.play(ShowIncreasingSubsets(self.rank_scores))
