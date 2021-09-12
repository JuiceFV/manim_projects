from manim import *
from logos.youtube import IntroYTLayout
from utils import play_and_wait

__all__ = ['Intro']


class Intro:
    def __init__(self, scene: Scene):
        self._scene = scene
        self._yt_logos = IntroYTLayout()
        self._first_video = FirstVideoIntro(scene)
        self._second_video = SecondVideoIntro(scene)

    def play(self):
        self._draw_yt_icons()
        self._play_first_video_snapshot()
        self._move_first_video_content_inside_icon()
        self._play_second_video_snapshot()

    def _draw_yt_icons(self):
        play_and_wait(DrawBorderThenFill(self._yt_logos), scene=self._scene,
                      play_time=0.5, wait_time=0)

    def _play_first_video_snapshot(self):
        self._first_video.play()

    def _play_second_video_snapshot(self):
        self._second_video.play()

    def _move_first_video_content_inside_icon(self):
        play_and_wait(self._first_video.right_query.animate
                      .set_width(IntroYTLayout.CONFIG['logo_height'] + 0.2)
                      .move_to(self._yt_logos[0].get_center()),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0
                      )


class FirstVideoIntro:
    def __init__(self, scene: Scene):
        self._scene = scene
        self.wrong_query = Text("лореаль париж rhtv-красcк а", color=RED_D)
        self.layout_fixed_query = Text("лореаль париж крем-красcк а", color=YELLOW_D)
        self.brand_fixed_query = Text("l'oreal paris крем-красcк а", color=GOLD_D)
        self.spaces_fixed_query = Text("l'oreal paris крем-красcка", color=TEAL_D)
        self.right_query = Text("l'oreal paris крем-краcка", color=GREEN_D)

    def fix_layout(self):
        play_and_wait(Transform(self.wrong_query, self.layout_fixed_query), scene=self._scene,
                      play_time=0.8, wait_time=0)
        self.remove_query('wrong')

    def fix_brand(self):
        play_and_wait(Transform(self.layout_fixed_query, self.brand_fixed_query), scene=self._scene,
                      play_time=0.8, wait_time=0)
        self.remove_query('layout_fixed')

    def fix_space(self):
        play_and_wait(Transform(self.brand_fixed_query, self.spaces_fixed_query), scene=self._scene,
                      play_time=0.8, wait_time=0)
        self.remove_query('brand_fixed')

    def fix_typos(self):
        play_and_wait(TransformMatchingShapes(self.spaces_fixed_query, self.right_query), scene=self._scene,
                      play_time=0.8, wait_time=0)
        self.remove_query('spaces_fixed')

    def play(self):
        play_and_wait(Write(self.wrong_query), scene=self._scene, play_time=0.5, wait_time=0)
        self.fix_layout()
        self.fix_brand()
        self.fix_space()
        self.fix_typos()

    def remove_query(self, query_name):
        if hasattr(self, query_name + '_query'):
            self._scene.remove(getattr(self, query_name + '_query'))


class SecondVideoIntro:
    def __init__(self, scene: Scene):
        self._scene = scene
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
        self.class_scores = VGroup(*[
            Text("0.99"),
            Text("0.01"),
            Text("0.06"),
            Text("0.07"),
            Text("0.06"),
            Text("\0")
        ]).scale(0.5).arrange(DOWN)
        self.classified_categories = None
        self.res_category = Text("Губы")
        self.redirect = Text("https://goldapple.ru/makijazh/guby")
        self.arrow_1 = None
        self.arrow_2 = None
        self.arrow_3 = None
        self.arrow_4 = None

    def write_query(self):
        """Write query, rescale and move it up-left
        """
        play_and_wait(Write(self.query),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        play_and_wait(self.query.animate.scale(0.3).to_edge(UL + [0.01, 4.5, 0]),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=2)

    def get_candidates(self):
        """
        Transform the query into candidates.
        Overtake candidates with box. Scale and place it next to query.
        """
        # Depict candidates from query
        print(self.product_candidates)
        play_and_wait(TransformFromCopy(self.query, self.product_candidates),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        print(self.product_candidates)

        # Surround box
        candidates_framebox = SurroundingRectangle(self.product_candidates, buff=0.2)
        play_and_wait(Create(candidates_framebox),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        # Name the operation
        candidates_label = Text("Кандидаты",
                               width=int(candidates_framebox.width) - 1).scale(0.5).next_to(candidates_framebox, UP)
        play_and_wait(Write(candidates_label),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        # Scale and move candidates + box + name up to the query
        self.product_candidates = VGroup(*[
            candidates_framebox, self.product_candidates, candidates_label
        ])
        print(self.product_candidates[1])
        play_and_wait(self.product_candidates.animate.scale(0.3).next_to(self.query, RIGHT * 2),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        # Set the arrow from the query to the candidates
        self.arrow_1 = Arrow(
            self.query.get_center() + [self.query.width/2, 0, 0],
            candidates_framebox.get_center() - [candidates_framebox.width/2, 0, 0],
            stroke_width=5, buff=0.1)
        play_and_wait(FadeIn(self.arrow_1),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

    def rank_categories(self):
        """
        Get categories from candidates.
        Paste a rank for every category. Surround with a box, name it and move next to the candidates.
        """
        # Depict categories from candidates
        print(self.product_candidates[1])
        play_and_wait(TransformFromCopy(self.product_candidates[1], self.categories),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        # paste rank one-by-one for each category
        play_and_wait(ShowIncreasingSubsets(self.rank_scores),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        self.categories = VGroup(*[self.categories, self.rank_scores])

        # Overbox categories and its ranks
        categories_framebox = SurroundingRectangle(self.categories, buff=0.2)
        play_and_wait(Create(categories_framebox),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        # name it
        categories_label = Text("Ранжирование категорий",
                                width=int(categories_framebox.width)).next_to(categories_framebox, UP)
        play_and_wait(Write(categories_label),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        # Group them, scale and move upt to candidates
        self.categories = VGroup(*[
            categories_framebox, self.categories, categories_label
        ])
        play_and_wait(self.categories.animate.scale(0.5).next_to(self.product_candidates, RIGHT * 2),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        # paste arrow from candidates
        self.arrow_2 = Arrow(
            self.product_candidates[0].get_center() + [self.product_candidates[0].width / 2, 0, 0],
            self.categories[0].get_center() - [self.categories[0].width / 2, 0, 0],
            stroke_width=5, buff=0.1)
        play_and_wait(FadeIn(self.arrow_2),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

    def classify_categories(self):
        self.classified_categories = self.categories[1].copy().set_height(self.class_scores.height)\
                                                              .next_to(self.categories, DOWN * 4)
        play_and_wait(TransformFromCopy(self.categories[1], self.classified_categories),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        self.class_scores.next_to(self.classified_categories, RIGHT)
        play_and_wait(ShowIncreasingSubsets(self.class_scores),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        self.classified_categories = VGroup(*[self.classified_categories, self.class_scores])

        for category, rank, proba in zip(self.classified_categories[0][0][3::2],  # Don't even ask, just try
                                         self.classified_categories[0][1][1:],
                                         self.classified_categories[1][1:]):
            print(category, rank, proba)
            play_and_wait(category.animate.set_color(RED_D),
                          rank.animate.set_color(RED_D),
                          proba.animate.set_color(RED_D),
                          scene=self._scene,
                          play_time=0.05,
                          wait_time=0)

        classified_categories_framebox = SurroundingRectangle(self.classified_categories, buff=0.2)
        play_and_wait(Create(classified_categories_framebox),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        classified_categories_label = Text("Классификация категорий", width=int(classified_categories_framebox.width))\
            .next_to(classified_categories_framebox, UP)

        play_and_wait(Write(classified_categories_label),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        self.classified_categories = VGroup(*[classified_categories_framebox,
                                              self.classified_categories,
                                              classified_categories_label])
        play_and_wait(self.classified_categories.animate.scale(0.5).next_to(self.categories, RIGHT * 2),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

        self.arrow_3 = Arrow(
            self.categories[0].get_center() + [self.categories[0].width / 2, 0, 0],
            self.classified_categories[0].get_center() - [self.classified_categories[0].width / 2, 0, 0],
            stroke_width=5, buff=0.1)
        play_and_wait(FadeIn(self.arrow_3),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

    def pick_category(self):
        self.res_category.scale(0.3).next_to(
            self.classified_categories[0].get_center() + [self.classified_categories[0].width / 2, 0, 0],
            RIGHT * 2)
        play_and_wait(TransformFromCopy(self.classified_categories[1][0][0], self.res_category),
                      self.res_category.animate.set_color(GREEN_D),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)
        self.arrow_4 = Arrow(
            self.classified_categories[0].get_center() + [self.classified_categories[0].width / 2, 0, 0],
            self.res_category.get_center() - [self.res_category.width/2, 0, 0],
            stroke_width=5, buff=0.1
        )
        play_and_wait(FadeIn(self.arrow_4),
                      scene=self._scene,
                      play_time=0.5,
                      wait_time=0)

    def play(self):
        self.write_query()
        self.get_candidates()
        self.rank_categories()
        self.classify_categories()
        self.pick_category()


