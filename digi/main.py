from manim import *
import itertools as it
from custom.characters.pi_creature_scene import PiCreatureScene
from custom.drawings import VideoSeries, Tree, Sigmoid, Clusters
from custom.characters.pi_creature_animations import Blink


class Introduction(PiCreatureScene):
    series = None

    def construct(self):
        PiCreatureScene().setup()
        self.thumbnail()
        self.videos_thumbnail()

    def thumbnail(self):
        self._pi_welcoming()
        self.show_series()

    def _pi_welcoming(self):
        self.pi_creature.scale(0.6)
        self.say("Привет!", target_mode="hooray", run_time=1)

    def show_series(self):
        series = VideoSeries(video_icon_kwargs={"stroke_width": 3, "fill_opacity": 0})
        for video in series:
            video.triangle.set_fill(video.color, opacity=1)
        series.to_edge(UP)
        this_video = series[0]
        this_video.set_color(YELLOW)
        this_video.save_state()

        self.play(*[DrawBorderThenFill(video, lag_ratio=0.5, run_time=2) for video in series],
                  Blink(self.pi_creature, run_time=0.5))

        self.play(*[
            ApplyMethod(
                video.shift, 0.5 * video.height * DOWN,
                run_time=3,
                rate_func=squish_rate_func(
                    there_and_back, alpha, alpha + 0.3
                )
            )
            for video, alpha in zip(series, np.linspace(0, 0.7, len(series)))
        ])

        self.play(FadeOut(self.get_primary_pi_creature().bubble),
                  FadeOut(self.get_primary_pi_creature().bubble.content))
        self.series = series

    def videos_thumbnail(self):
        rules = [
            MathTex("P(q|c) = \\frac{P(c|q)P(c)}{P(q)}"),
            Tree(),
            # MathTex("F_m = \\arg \\min_{\\gamma}\\sum_{i = 1}^n{L(y_i, \\gamma)}"),
            Sigmoid(),
            # MathTex("f(x) = \\frac{1}{1 + e^{-x}}"),
            MathTex("f(x, \\alpha, \\beta) = \\frac{x^{\\alpha-1}(1 - x)^{\\beta - 1}}{\\text{B}(\\alpha, \\beta)}"),
            Clusters(),
            # MathTex("L = \\sum_{j=1}^k{\\sum_{i=1}^n{}\\lVert x_i^{(j)} - c_i\\rVert^2}"),
            MathTex("L(\\theta) = \\prod_{i=1}^n{P(Y = y^{(i)}\\ |\\ X = x^{(i)})}")
            # MathTex("L(\\theta) = \\prod_{i=1}^n{\\sigma(\\theta^Tx^{(i)})^{y^{(i)}}" +
            #         "\\left[1 - \\sigma(\\theta^Tx^{(i)})^{y^{(i)}}\\right]^{(1 - y^{(i)})}}")
        ]
        video_indices = [0, 1, 2, 3, 4, 5]
        class2scale = {Tree: 2, Sigmoid: 0.2, Clusters: 4}

        for rule in rules:
            rule.scale(class2scale.get(type(rule), 0.7))
            rule.next_to(self.pi_creature.get_corner(UP + RIGHT), UP)
            rule.shift_onto_screen()

        self.play(Write(rules[0]), self.pi_creature.animate.change_mode("raise_right_hand"))
        self.wait()
        alt_rules_list = list(rules[1:]) + [VectorizedPoint(self.pi_creature.eyes.get_top())]
        for last_rule, rule, video_index in zip(rules, alt_rules_list, video_indices):
            video = self.series[video_index]
            self.play(last_rule.animate.replace(video), FadeIn(rule))
            self.play(Animation(rule))
            self.wait()
        self.play(self.pi_creature.animate.change_mode("happy"))


class QueryResponseScene(PiCreatureScene):

    def __init__(self):
        super(QueryResponseScene, self).__init__()
        self.query = None
        self.start_products = None
        self.and_products_state = None
        self.or_products_state = None
        self.and_box = None
        self.or_box = None
        self.and_state = None
        self.or_state = None
        self.and_box_title = None
        self.or_box_title = None
        self.current_state = -1

    def setup(self) -> None:
        PiCreatureScene.setup(self)
        self.query = VGroup(*[Text(word, t2c={'iPhone': GREEN, 'белый': BLUE})
                              for word in ["iPhone", "белый", "глазированный"]]).arrange(RIGHT).to_edge(UP)

        self.start_products = [Text(product) for product in ["Смартфон APPLE iPhone 12 чёрный",
                                                             "Смартфон APPLE iPhone 11 чёрный",
                                                             "Смартфон APPLE iPhone XR белый",
                                                             "Смартфон APPLE iPhone 12 белый"]]

        self.and_products_state = VGroup(*self.start_products).arrange(DOWN)
        self.or_products_state = self.and_products_state.copy()

        self.and_box = SurroundingRectangle(self.and_products_state, color=WHITE, buff=SMALL_BUFF)
        self.or_box = SurroundingRectangle(self.or_products_state, color=WHITE, buff=SMALL_BUFF)

        self.and_box_title = Text("Все слова из запроса",
                                  width=int(self.and_box.width)).scale(0.97).next_to(self.and_box, UP)
        self.or_box_title = Text("Хотя бы 1 слово из запроса",
                                 width=int(self.or_box.width)).scale(0.5).next_to(self.or_box, UP)

        self.and_state = VGroup(self.and_products_state,
                                self.and_box,
                                self.and_box_title).set(width=self.query.width/2)\
            .move_to(self.query.get_center() + 2*DOWN + 3*LEFT)

        self.or_state = VGroup(self.or_products_state,
                               self.or_box,
                               self.or_box_title).set(width=self.query.width/2)\
            .move_to(self.query.get_center() + 2*DOWN + 3*RIGHT)

    def get_query_state(self, state: int):
        if any([state >= 3, state < 0, state - 1 != self.current_state]):
            raise ValueError("Wrong state")
        return [Write(self.query[state])]

    def get_AND_state(self, state: int):
        if any([state >= 3, state < 0, state - 1 != self.current_state]):
            raise ValueError("Wrong state")

        if state == 0:
            return [FadeIn(product) for product in self.and_products_state] + \
                   [FadeIn(self.and_box), FadeIn(self.and_box_title)]
        elif state == 1:
            to_remove = self.and_products_state[:2]
            self.and_products_state -= self.start_products[0]
            self.and_products_state -= self.start_products[1]
            return [FadeOut(to_remove), self.and_products_state.animate.move_to(self.and_box.get_center())]
        elif state == 2:
            to_remove = self.and_products_state[:2]
            self.and_products_state -= self.start_products[2]
            self.and_products_state -= self.start_products[3]
            return [FadeOut(to_remove)]

    def get_OR_state(self, state: int):
        if any([state >= 3, state < 0, state - 1 != self.current_state]):
            raise ValueError("Wrong state")

        if state == 0:
            return [FadeIn(product) for product in self.and_products_state] + \
                   [FadeIn(self.and_box), FadeIn(self.and_box_title)]
        elif state == 1:
            to_remove = self.and_products_state[:2]
            self.and_products_state -= self.start_products[0]
            self.and_products_state -= self.start_products[1]
            return [FadeOut(to_remove), self.and_products_state.animate.move_to(self.and_box.get_center())]
        elif state == 2:
            to_remove = self.and_products_state[:2]
            self.and_products_state -= self.start_products[2]
            self.and_products_state -= self.start_products[3]
            return [FadeOut(to_remove)]

    def update_state(self):
        self.current_state += 1


class QueryMeaning(QueryResponseScene):

    def construct(self):
        QueryResponseScene().setup()
        self._pi_creature_think_about_query()
        self.play(self.pi_creature.animate.change_mode("pondering"))
        self.play(*[])
        self.play(*self.get_query_state(0))
        self.play(*self.get_AND_state(0))
        self.update_state()
        self.play(*self.get_query_state(1))
        self.play(*self.get_AND_state(1))
        self.update_state()
        self.play(*self.get_query_state(2))
        self.play(*self.get_AND_state(2))

        #self.show_and_response()

    def _pi_creature_think_about_query(self):
        self.pi_creature.scale(0.6)
        self.think("Что такое запрос?", target_mode="confused", run_time=1)
        self.play(FadeOut(self.pi_creature.bubble), FadeOut(self.pi_creature.bubble.content))

    @staticmethod
    def _write_query_word(index: int) -> Animation:
        query = ["iphone", "белый", "глазированный"]
        return Write(Text(query[index]))

    def _get_response(self):
        pass
