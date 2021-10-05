from manim import *
import itertools as it
from typing import Tuple, List
from custom.characters.pi_creature import PiCreature
from custom.characters.pi_creature_scene import PiCreatureScene
from custom.drawings import VideoSeries, Tree, Sigmoid, Clusters
from custom.characters.pi_creature_animations import Blink, PiCreatureSays


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
        self.query = None  # The Query
        self.start_products = None  # The products at the beginning of scene
        self.and_products_state = None
        self.or_products_state = None
        self.and_box = None
        self.or_box = None
        self.and_state = None
        self.or_state = None
        self.and_box_title = None
        self.or_box_title = None
        self.current_state = 0

    def setup(self) -> None:
        PiCreatureScene.setup(self)
        self.query = VGroup(*[Text(word, t2c={'iPhone': GREEN, 'белый': BLUE})
                              for word in ["iPhone", "белый", "глазированный"]]).arrange(RIGHT).to_edge(UP)

        self.start_products = [Text(product) for product in ["Смартфон APPLE iPhone 12 чёрный",
                                                             "Смартфон APPLE iPhone 11 чёрный",
                                                             "Смартфон APPLE iPhone 13 белый",
                                                             "Смартфон APPLE iPhone 12 белый"]]

        self.and_products_state = VGroup(*self.start_products).arrange(DOWN)
        self.or_products_state = self.and_products_state.copy()

        self.and_box = SurroundingRectangle(self.and_products_state, color=WHITE, buff=SMALL_BUFF)
        self.or_box = SurroundingRectangle(self.or_products_state, color=WHITE, buff=SMALL_BUFF)

        self.and_box_title = Text("Все слова из запроса",
                                  width=int(self.and_box.width)).scale(0.97).next_to(self.and_box, UP)
        self.or_box_title = Text("Хотя бы 1 слово из запроса",
                                 width=int(self.or_box.width)).scale(0.97).next_to(self.or_box, UP)

        self.and_state = VGroup(self.and_products_state,
                                self.and_box,
                                self.and_box_title).set(width=self.query.width/2)\
            .move_to(self.query.get_center() + 2*DOWN + 3*LEFT)

        self.or_state = VGroup(self.or_products_state,
                               self.or_box,
                               self.or_box_title).set(width=self.query.width/2)\
            .move_to(self.query.get_center() + 2*DOWN + 3*RIGHT)

    def get_response_boxes(self):
        return [FadeIn(self.and_box), FadeIn(self.and_box_title), FadeIn(self.or_box), FadeIn(self.or_box_title)]

    def get_query_state(self):
        return [Write(self.query[self.current_state])]

    def get_AND_first_state(self) -> Tuple[List[Animation], List[Animation]]:
        main_anims = [FadeIn(product) for product in self.and_products_state]
        additional_anims = [product.animate.set_color_by_t2c(t2c={'[13:19]': GREEN})
                            for product in self.and_products_state]
        return main_anims, additional_anims

    def get_AND_second_state(self) -> Tuple[List[Animation], List[Animation]]:
        to_remove = self.and_products_state[:2]
        self.and_products_state -= self.start_products[0]
        self.and_products_state -= self.start_products[1]
        main_anims = [product.animate.set_color_by_t2c(t2c={'[21:-1]': BLUE}) for product in self.and_products_state]
        additional_anims = [FadeOut(to_remove)]
        return main_anims, additional_anims

    def get_AND_third_state(self) -> Tuple[List[Animation], List[Animation]]:
        to_remove = self.and_products_state[:2]
        self.and_products_state -= self.start_products[2]
        self.and_products_state -= self.start_products[3]
        return [FadeOut(to_remove)], []

    def get_AND_state(self):
        if self.current_state == 0:
            return self.get_AND_first_state()
        elif self.current_state == 1:
            return self.get_AND_second_state()
        else:
            return self.get_AND_third_state()

    def get_OR_first_state(self) -> Tuple[List[Animation], List[Animation]]:
        main_anims = [FadeIn(product) for product in self.or_products_state]
        additional_anims = [product.animate.set_color_by_t2c(t2c={'[13:19]': GREEN})
                            for product in self.or_products_state]
        return main_anims, additional_anims

    def get_OR_second_state(self) -> Tuple[List[Animation], List[Animation]]:
        main_anims = [product.animate.set_color_by_t2c(t2c={'[21:-1]': BLUE})
                      for product in self.or_products_state[2:4]]
        additional_anims = []
        return main_anims, additional_anims

    def get_OR_third_state(self) -> Tuple[List[Animation], List[Animation]]:
        glaze_products = [Text(product) for product in ['Конфеты глазированные "Отломи"',
                                                        'Сырок глазированный с ванилью']]
        for glaze_product in glaze_products:
            glaze_product.set(width=self.or_products_state[0].width)
            self.or_products_state += glaze_product
            glaze_product.next_to(self.or_products_state[-2], DOWN, buff=SMALL_BUFF)

        prev_or_box = self.or_box
        self.or_box = SurroundingRectangle(self.or_products_state, color=WHITE, buff=SMALL_BUFF)
        main_anims = [Transform(prev_or_box, self.or_box), FadeIn(*self.or_products_state[4:]),
                      self.or_products_state[-2].animate.set_color_by_t2c(t2c={'[7:20]': PURPLE}),
                      self.or_products_state[-1].animate.set_color_by_t2c(t2c={'[5:18]': PURPLE})]
        additional_anims = []
        return main_anims, additional_anims

    def get_OR_state(self):
        if self.current_state == 0:
            return self.get_OR_first_state()
        elif self.current_state == 1:
            return self.get_OR_second_state()
        else:
            return self.get_OR_third_state()

    def get_state(self):
        if self.current_state > 2:
            raise ValueError("The states count exceeds over the bound")
        query_state = self.get_query_state()
        and_main_anims, and_add_anims = self.get_AND_state()
        or_main_anims, or_add_anims = self.get_OR_state()
        self.update_state()
        return query_state, [and_main_anims, and_add_anims], [or_main_anims, or_add_anims]

    def update_state(self):
        self.current_state += 1


class QueryMeaning(QueryResponseScene):

    def construct(self):
        QueryResponseScene().setup()
        self._pi_creature_think_about_query()
        self.query_responses()
        self.query_probas()

    def _pi_creature_think_about_query(self):
        self.pi_creature.scale(0.6)
        self.think("Что такое запрос?", target_mode="confused", run_time=1)
        self.play(FadeOut(self.pi_creature.bubble), FadeOut(self.pi_creature.bubble.content))

    def query_state(self, run_time: int = 1):
        query_state, AND_states, OR_states = self.get_state()
        self.play(*query_state)
        for and_state, or_state in zip(AND_states, OR_states):
            state = and_state + or_state
            if len(state) > 0:
                self.play(*state, run_time=run_time)

    def query_responses(self):
        self.play(self.pi_creature.animate.change_mode("pondering"))
        self.play(*self.get_response_boxes())
        self.query_state()  # 'iPhone' response
        self.blink()
        self.query_state()  # 'white' response
        self.blink()
        self.query_state()  # 'glaze' response
        self.blink()
        self.play(self.pi_creature.animate.change_mode("hooray"))
        self.play(Indicate(self.and_state))
        self.blink()
        self.play(FadeOut(self.and_state, self.or_state))
        self.play(self.pi_creature.animate.change_mode("plain"))

    def query_probas(self):
        old_query = self.query  # Save query for transformation

        # New query into one the old will be transformed
        self.query = VGroup(*[Text(word) for word in ["\"iPhone\"", "и", "\"белый\"",
                                                      "и", "\"глазированный\""]]).arrange(RIGHT).to_edge(UP)
        # Transformation from the colored query to the probabilistic representation
        self.play(TransformMatchingShapes(old_query, self.query), run_time=1)

        # Pi creature says that it's almost impossible to handle this query. First two words are yellow
        what_pi_creature_says = Text("Навряд ли получится найти", t2c={'[0:8]': YELLOW})
        self.pi_creature_says(what_pi_creature_says, target_mode="sad")
        self.wait()

        # Retrieve two heading words and take it beyond the bubble along with placing it over the pi creature
        total_proba_in_words = what_pi_creature_says[:8].copy()
        total_proba_in_words.next_to(self.pi_creature, UP*5)
        self.play(TransformFromCopy(what_pi_creature_says[:8], total_proba_in_words),
                  FadeOut(*[self.pi_creature.bubble, self.pi_creature.bubble.content]),
                  self.pi_creature.animate.change_mode("plain"))
        self.blink()

        probas_equation = VGroup(*[
            Tex(proba) for proba in [r"$P($iPhone$)$", r" и $P($белый$)$", r" и $P($глазированный$)$"]
        ]).arrange(RIGHT).set(height=total_proba_in_words.height)

        # We are not wanna to encompass the '=' sign with brace, thus write it separately
        eq_sign = Text(' = ').next_to(total_proba_in_words, RIGHT).set(height=total_proba_in_words.height/3)
        self.play(Write(eq_sign))

        # Write the probability equation
        probas_equation.next_to(eq_sign, RIGHT)
        for proba in probas_equation:
            self.play(Write(proba))
        self.blink()

        # Underbrace notes
        braces_notes = [Text(note) for note in ["Большая вероятность",
                                                "Вероятность поменьше",
                                                "Очень маленькая вероятность"]]

        # Place the braces so that the adjacent one incorporates previous one and the current probability
        braces_group = []
        for idx, note in enumerate(braces_notes):
            if len(braces_group) == 0:
                brace = Brace(probas_equation[idx])
                brace.next_to(probas_equation[idx], DOWN)
                note.set(width=brace.width)
            else:
                group_with_prev = braces_group[-1] + probas_equation[idx]
                brace = Brace(group_with_prev)
                brace.next_to(group_with_prev, DOWN)
                note.set(width=braces_group[0].width)
            group = VGroup(brace, note.next_to(brace, DOWN))
            braces_group.append(group)

        # Show braces one-by-one
        for brace in braces_group:
            self.play(FadeIn(brace))
        self.blink()

        # Show notes one-by-one
        for note in braces_notes:
            self.play(Indicate(note))
        # The probability numbers as an example for every probability in the equation
        probas_decimals = [
            DecimalNumber(0, num_decimal_places=2),
            DecimalNumber(0, num_decimal_places=2),
            DecimalNumber(0, num_decimal_places=2)
        ]
        # Arrows linking the probability and its quantitative representation
        arrows = [
            Arrow(buff=0.7, start=DOWN, end=UP),
            Arrow(buff=0.7, start=DOWN, end=UP),
            Arrow(buff=0.7, start=DOWN, end=UP)
        ]
        # Place one-over-one (number over arrow over equation part)
        for proba, number, arrow in zip(probas_equation, probas_decimals, arrows):
            arrow.next_to(proba, UP)
            number.next_to(arrow, UP)

        # Show the arrows and numbers
        self.play(FadeIn(*arrows), run_time=1)
        self.play(FadeIn(*probas_decimals), run_time=1)
        self.blink()

        # Counting numbers up to target
        # 1. P(iPhone) - 0.99
        # 2. P(white) - 0.77
        # 3. P(glaze) - 0.01
        self.play(*[ChangeDecimalToValue(decimal, target)
                    for decimal, target in zip(probas_decimals, [0.99, 0.78, 0.01])])
        self.wait()
        self.blink()

        # Transformation from 'and' to the multiplication sign
        mult_signs = []
        and_symbols = []
        for idx, equation_part in enumerate(probas_equation[1:]):
            and_symbols.append(equation_part[0][0])
            position = (probas_decimals[idx + 1].get_center() + probas_decimals[idx].get_center()) / 2
            mult_signs.append(MathTex(r"\times").move_to(position))
        self.play(*[TransformFromCopy(and_sym, sign) for sign, and_sym in zip(mult_signs, and_symbols)])

        # The answer in percent and normalized between 0 and 1
        ans_values = {
            '0_to_100': DecimalNumber(0.7, num_decimal_places=1),
            '0_to_1': DecimalNumber(0.007, num_decimal_places=3)
        }
        ans = VGroup(ans_values['0_to_100'], MathTex(r"\% = "), ans_values['0_to_1'], MathTex(r" \approx "))\
            .arrange(RIGHT)\
            .next_to(probas_decimals[0], LEFT)
        self.play(FadeIn(ans))
        self.wait()
        self.blink()

        # Probability is increasing while number of words is decreasing
        likely_words = Text("Скорее всего")
        likely_words.set_color(YELLOW).set(height=total_proba_in_words.height).next_to(eq_sign, LEFT)
        to_disappear = [braces_group[-1], probas_equation[-1],
                        arrows[-1], probas_decimals[-1],
                        mult_signs[-1], self.query[-2:]]
        # First word disappears
        self.play(FadeOut(*to_disappear),
                  # ChangeDecimalToValue(ans_values['0_to_1'], 0.772),
                  Transform(ans_values['0_to_1'],
                            DecimalNumber(0.772, num_decimal_places=3).move_to(ans_values['0_to_1'].get_center())),
                  # ChangeDecimalToValue(ans_values['0_to_100'], 77.2),
                  Transform(ans_values['0_to_100'],
                            DecimalNumber(77.2, num_decimal_places=1).move_to(ans_values['0_to_100'].get_center())),
                  Transform(total_proba_in_words, likely_words))
        self.wait()

        absolutely_words = Text("Точно найдём")
        absolutely_words.set_color(YELLOW).set(height=likely_words.height).next_to(eq_sign, LEFT)
        to_disappear = [braces_group[-2], probas_equation[-2],
                        arrows[-2], probas_decimals[-2],
                        mult_signs[-2], self.query[-4:-2]]
        # Second word disappears
        self.play(FadeOut(*to_disappear),
                  # ChangeDecimalToValue(ans_values['0_to_1'], 0.990),
                  Transform(ans_values['0_to_1'],
                            DecimalNumber(0.990, num_decimal_places=3).move_to(ans_values['0_to_1'].get_center())),
                  # ChangeDecimalToValue(ans_values['0_to_100'], 99.0),
                  Transform(ans_values['0_to_100'],
                            DecimalNumber(99.0, num_decimal_places=1).move_to(ans_values['0_to_100'].get_center())),
                  Transform(total_proba_in_words, absolutely_words))
        self.wait()
        self.blink()

        # All objects in the scene except pi creature have to disappear
        to_disappear = [mobject for mobject in self.mobjects if not isinstance(mobject, PiCreature)]
        self.play(FadeOut(*to_disappear))
        self.blink()

        # Generalized query
        gquery = MathTex(r"\text{query} = \text{word}_1\ \text{word}_2\ \ldots\ \text{word}_n")
        probas_gquery = MathTex(r"P(\text{query}) = P(\text{word}_1) \times P(\text{word}_2) \times "
                                r"\ldots \times P(\text{word}_n)")
        probas_gquery_box = SurroundingRectangle(probas_gquery, buff=0.5)
        self.play(Write(gquery))
        self.play(TransformMatchingShapes(gquery, probas_gquery))
        self.blink()
        self.play(self.pi_creature.animate.change_mode("hooray"))
        self.play(ShowPassingFlash(probas_gquery_box.copy().set_color(BLUE), run_time=2, time_width=0.5))
        self.wait()


class VipryamitelMeaning(Scene):
    def construct(self):
        pass
