import numpy as np
from typing import Optional, Sequence
from manim import *
from typing import Tuple, List, Union
from custom.characters.pi_creature import PiCreature
from custom.characters.pi_creature_scene import PiCreatureScene, CustomersScene
from custom.drawings import (
    VideoSeries, Tree, Sigmoid, Clusters, NotebookWithNotes, Lock, Cross, Check, SearchBar
)
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
        # pi at the right corner is greeting you
        self.pi_creature.scale(0.6)
        self.say("Привет!", target_mode="hooray", run_time=1)

    def show_series(self):
        series = VideoSeries(video_icon_kwargs={"stroke_width": 3, "fill_opacity": 0})
        for video in series:
            video.triangle.set_fill(video.color, opacity=1)
        series.to_edge(UP)
        # Expose current video by dying it yellow
        this_video = series[0]
        this_video.set_color(YELLOW)
        this_video.save_state()

        self.play(
            *[DrawBorderThenFill(video, lag_ratio=0.5, run_time=2) for video in series],
            Blink(self.pi_creature, run_time=0.5)
        )

        # snaking video series
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

        # Removing greeting
        self.play(FadeOut(self.get_primary_pi_creature().bubble),
                  FadeOut(self.get_primary_pi_creature().bubble.content))
        self.series = series

    def videos_thumbnail(self):
        # Rules which will be placing inside video box
        # 1. Bayes rule
        # 2. Gradient boost tree (MathTex("F_m = \\arg \\min_{\\gamma}\\sum_{i = 1}^n{L(y_i, \\gamma)}"))
        # 3. Sigmoid graph (MathTex("f(x) = \\frac{1}{1 + e^{-x}}"))
        # 4. Beta-distribution formula
        # 5. Clusters picture (MathTex("L = \\sum_{j=1}^k{\\sum_{i=1}^n{}\\lVert x_i^{(j)} - c_i\\rVert^2}"))
        # 6. Likelihood maximization
        rules = [
            MathTex("P(q|c) = \\frac{P(c|q)P(c)}{P(q)}"),
            Tree(),
            Sigmoid(),
            MathTex("f(x, \\alpha, \\beta) = \\frac{x^{\\alpha-1}(1 - x)^{\\beta - 1}}{\\text{B}(\\alpha, \\beta)}"),
            Clusters(),
            MathTex("L(\\theta) = \\prod_{i=1}^n{P(Y = y^{(i)}\\ |\\ X = x^{(i)})}")
        ]
        video_indices = [0, 1, 2, 3, 4, 5]
        class2scale = {Tree: 2, Sigmoid: 0.2, Clusters: 4}

        for rule in rules:
            rule.scale(class2scale.get(type(rule), 0.7))
            rule.next_to(self.pi_creature.get_corner(UP + RIGHT), UP)
            rule.shift_onto_screen()

        # Moving rules to the video boxes
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
        self.and_products_state = None  # Representation of the current products state inside AND boxe
        self.or_products_state = None  # Representation of the current products state inside OR boxe
        self.and_box = None  # type: SurroundingBox
        self.or_box = None  # type: SurroundingBox
        self.and_state = None  # The entire AND response box state
        self.or_state = None  # The entire OR response box state
        self.and_box_title = None  # The title for AND box
        self.or_box_title = None  # The title for OR box
        self.current_state = 0  # Current state iter

    def setup(self) -> None:
        PiCreatureScene.setup(self)
        self.query = VGroup(*[
            Text(word, t2c={'iPhone': GREEN, 'белый': BLUE}) for word in [
                "iPhone",
                "белый",
                "глазированный"
            ]
        ]).arrange(RIGHT).to_edge(UP)

        self.start_products = [
            Text(product) for product in [
                "Смартфон APPLE iPhone 12 чёрный",
                "Смартфон APPLE iPhone 11 чёрный",
                "Смартфон APPLE iPhone 13 белый",
                "Смартфон APPLE iPhone 12 белый"
            ]
        ]

        self.and_products_state = VGroup(*self.start_products).arrange(DOWN)
        self.or_products_state = self.and_products_state.copy()

        self.and_box = SurroundingRectangle(self.and_products_state, color=WHITE, buff=SMALL_BUFF)
        self.or_box = SurroundingRectangle(self.or_products_state, color=WHITE, buff=SMALL_BUFF)

        self.and_box_title = Text(
            "Все слова из запроса",
            width=int(self.and_box.width)
        ).scale(0.97).next_to(self.and_box, UP)

        self.or_box_title = Text(
            "Хотя бы 1 слово из запроса",
            width=int(self.or_box.width)
        ).scale(0.97).next_to(self.or_box, UP)

        self.and_state = VGroup(
            self.and_products_state,
            self.and_box,
            self.and_box_title
        ).set(width=self.query.width / 2).move_to(self.query.get_center() + 2 * DOWN + 3 * LEFT)

        self.or_state = VGroup(
            self.or_products_state,
            self.or_box,
            self.or_box_title
        ).set(width=self.query.width / 2).move_to(self.query.get_center() + 2 * DOWN + 3 * RIGHT)

    def get_response_boxes(self) -> List[Animation]:
        """The response boxes appears first"""
        return [FadeIn(self.and_box), FadeIn(self.and_box_title), FadeIn(self.or_box), FadeIn(self.or_box_title)]

    def get_query_state(self) -> List[Animation]:
        """Write the query word by word along with response states simultaneously"""
        return [Write(self.query[self.current_state])]

    def get_AND_first_state(self) -> Tuple[List[Animation], List[Animation]]:
        """Get all products which have 'iPhone' in the name. And dye 'iPhone' green."""
        main_anims = [FadeIn(product) for product in self.and_products_state]
        additional_anims = [
            product.animate.set_color_by_t2c(t2c={'[13:19]': GREEN})
            for product in self.and_products_state
        ]
        return main_anims, additional_anims

    def get_AND_second_state(self) -> Tuple[List[Animation], List[Animation]]:
        """Remove the products don't have 'white' in the name. Dye 'white' blue."""
        to_remove = self.and_products_state[:2]
        self.and_products_state -= self.start_products[0]
        self.and_products_state -= self.start_products[1]
        # t2c - dye 'white' blue
        main_anims = [product.animate.set_color_by_t2c(t2c={'[21:-1]': BLUE}) for product in self.and_products_state]
        additional_anims = [FadeOut(to_remove)]
        return main_anims, additional_anims

    def get_AND_third_state(self) -> Tuple[List[Animation], List[Animation]]:
        """The last state. Remove remaining products due to they do not have 'glaze' inside."""
        to_remove = self.and_products_state[:2]
        self.and_products_state -= self.start_products[2]
        self.and_products_state -= self.start_products[3]
        return [FadeOut(to_remove)], []

    def get_AND_state(self) -> Tuple[List[Animation], List[Animation]]:
        """A kind of API to get the proper AND state."""
        if self.current_state == 0:
            return self.get_AND_first_state()
        elif self.current_state == 1:
            return self.get_AND_second_state()
        else:
            return self.get_AND_third_state()

    def get_OR_first_state(self) -> Tuple[List[Animation], List[Animation]]:
        """At the first OR state we get the same response as the first AND state.
        And dye 'iPhone' green.
        """
        main_anims = [FadeIn(product) for product in self.or_products_state]
        additional_anims = [
            product.animate.set_color_by_t2c(t2c={'[13:19]': GREEN})
            for product in self.or_products_state
        ]
        return main_anims, additional_anims

    def get_OR_second_state(self) -> Tuple[List[Animation], List[Animation]]:
        """At the second OR state nothing disappears but those products which contain 'white'
        dyeing it in the blue color.
        """
        main_anims = [
            product.animate.set_color_by_t2c(t2c={'[21:-1]': BLUE})
            for product in self.or_products_state[2:4]
        ]
        additional_anims = []
        return main_anims, additional_anims

    def get_OR_third_state(self) -> Tuple[List[Animation], List[Animation]]:
        """At the last OR state we add new ('glaze') products down to the OR response and
        dyeing the 'glaze' purple."""
        glaze_products = [
            Text(product) for product in [
                'Конфеты глазированные "Отломи"',
                'Сырок глазированный с ванилью'
            ]
        ]
        # Adding the products
        for glaze_product in glaze_products:
            glaze_product.set(width=self.or_products_state[0].width)
            self.or_products_state += glaze_product
            glaze_product.next_to(self.or_products_state[-2], DOWN, buff=SMALL_BUFF)
        # Resizing the OR box
        prev_or_box = self.or_box
        self.or_box = SurroundingRectangle(self.or_products_state, color=WHITE, buff=SMALL_BUFF)

        main_anims = [
            Transform(prev_or_box, self.or_box), FadeIn(*self.or_products_state[4:]),
            self.or_products_state[-2].animate.set_color_by_t2c(t2c={'[7:20]': PURPLE}),
            self.or_products_state[-1].animate.set_color_by_t2c(t2c={'[5:18]': PURPLE})
        ]
        additional_anims = []
        return main_anims, additional_anims

    def get_OR_state(self):
        """A kind of API to get the proper OR state."""
        if self.current_state == 0:
            return self.get_OR_first_state()
        elif self.current_state == 1:
            return self.get_OR_second_state()
        else:
            return self.get_OR_third_state()

    def get_state(self) -> Tuple[List[Animation], List[List[Animation]], List[List[Animation]]]:
        """Query and boxes are changing simultaneously"""
        if self.current_state > 2:
            raise ValueError("The states count exceed over the bound")
        query_state = self.get_query_state()
        and_main_anims, and_add_anims = self.get_AND_state()
        or_main_anims, or_add_anims = self.get_OR_state()
        self.update_state()
        return query_state, [and_main_anims, and_add_anims], [or_main_anims, or_add_anims]

    def update_state(self) -> None:
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
        self.query = VGroup(*[
            Text(word) for word in ["\"iPhone\"", "и", "\"белый\"", "и", "\"глазированный\""]
        ]).arrange(RIGHT).to_edge(UP)
        # Transformation from the colored query to the probabilistic representation
        self.play(TransformMatchingShapes(old_query, self.query), run_time=1)

        # Pi creature says that it's almost impossible to handle this query. First two words are yellow
        what_pi_creature_says = Text("Навряд ли получится найти", t2c={'[0:8]': YELLOW})
        self.pi_creature_says(what_pi_creature_says, target_mode="sad")
        self.wait()

        # Retrieve two heading words and take it beyond the bubble along with placing it over the pi creature
        total_proba_in_words = what_pi_creature_says[:8].copy()
        total_proba_in_words.next_to(self.pi_creature, UP * 5)
        self.play(
            TransformFromCopy(what_pi_creature_says[:8], total_proba_in_words),
            FadeOut(*[self.pi_creature.bubble, self.pi_creature.bubble.content]),
            self.pi_creature.animate.change_mode("plain")
        )
        self.blink()

        probas_equation = VGroup(*[
            Tex(proba) for proba in [r"$P($iPhone$)$", r" и $P($белый$)$", r" и $P($глазированный$)$"]
        ]).arrange(RIGHT).set(height=total_proba_in_words.height)

        # We are not wanna to encompass the '=' sign with brace, thus write it separately
        eq_sign = Text(' = ').next_to(total_proba_in_words, RIGHT).set(height=total_proba_in_words.height / 3)
        self.play(Write(eq_sign))

        # Write the probability equation
        probas_equation.next_to(eq_sign, RIGHT)
        for proba in probas_equation:
            self.play(Write(proba))
        self.blink()

        # Underbrace notes
        braces_notes = [
            Text(note) for note in ["Большая вероятность", "Вероятность поменьше", "Очень маленькая вероятность"]
        ]

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
        # 2. P(white) - 0.78
        # 3. P(glaze) - 0.01
        self.play(*[
            ChangeDecimalToValue(decimal, target) for decimal, target in zip(probas_decimals, [0.99, 0.78, 0.01])
        ])
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

        # The answers in percent and normalized between 0 and 1
        ans_values = {
            '0_to_100': DecimalNumber(0.7, num_decimal_places=1),
            '0_to_1': DecimalNumber(0.007, num_decimal_places=3)
        }
        ans = VGroup(
            ans_values['0_to_100'],
            MathTex(r"\% = "),
            ans_values['0_to_1'],
            MathTex(r" \approx ")
        ).arrange(RIGHT).next_to(probas_decimals[0], LEFT)
        self.play(FadeIn(ans))
        self.wait()
        self.blink()

        # Probability is increasing while number of words is decreasing
        likely_words = Text("Скорее всего")
        likely_words.set_color(YELLOW).set(height=total_proba_in_words.height).next_to(eq_sign, LEFT)
        to_disappear = [
            braces_group[-1],
            probas_equation[-1],
            arrows[-1],
            probas_decimals[-1],
            mult_signs[-1],
            self.query[-2:]
        ]
        # First word disappears
        self.play(
            FadeOut(*to_disappear),
            # ChangeDecimalToValue(ans_values['0_to_1'], 0.772),
            Transform(
                ans_values['0_to_1'],
                DecimalNumber(0.772, num_decimal_places=3).move_to(ans_values['0_to_1'].get_center())
            ),
            # ChangeDecimalToValue(ans_values['0_to_100'], 77.2),
            Transform(
                ans_values['0_to_100'],
                DecimalNumber(77.2, num_decimal_places=1).move_to(ans_values['0_to_100'].get_center())
            ),
            Transform(total_proba_in_words, likely_words)
        )
        self.wait()

        absolutely_words = Text("Точно найдём")
        absolutely_words.set_color(YELLOW).set(height=likely_words.height).next_to(eq_sign, LEFT)
        to_disappear = [
            braces_group[-2],
            probas_equation[-2],
            arrows[-2],
            probas_decimals[-2],
            mult_signs[-2],
            self.query[-4:-2]
        ]
        # Second word disappears
        self.play(
            FadeOut(*to_disappear),
            # ChangeDecimalToValue(ans_values['0_to_1'], 0.990),
            Transform(
                ans_values['0_to_1'],
                DecimalNumber(0.990, num_decimal_places=3).move_to(ans_values['0_to_1'].get_center())
            ),
            # ChangeDecimalToValue(ans_values['0_to_100'], 99.0),
            Transform(
                ans_values['0_to_100'],
                DecimalNumber(99.0, num_decimal_places=1).move_to(ans_values['0_to_100'].get_center())
            ),
            Transform(total_proba_in_words, absolutely_words)
        )
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
    pi_customer = PiCreature(mode="angry")

    def construct(self):
        self.typo_query_probas_scene()

    def typo_query_probas_scene(self):
        """Showing the example when a typo is admitted.
        """
        # the typo query
        query = VGroup(*[Text(word) for word in ["iPhone", ",tksq"]]).arrange(RIGHT).to_edge(UP)
        self.play(AddTextWordByWord(query))

        # the probability of the entire query
        probas_query = MathTex(
            r"P(\text{query}) = ",
            r"P(\text{iPhone})",
            r"\times P(\text{,tksq})",
            r" = 0.99 \times",
            "?",
            "= 0"
        )
        # Showing the left part of equation
        self.play(FadeIn(probas_query[0]))
        # Cloning the words to its probabilities
        self.play(TransformMatchingShapes(query[0].copy(), probas_query[1]))
        self.play(TransformMatchingShapes(query[1].copy(), probas_query[2]))
        # Showing rest w/o the answer (= 0)
        self.play(FadeIn(probas_query[-3:-1]))
        self.wait()
        # Transforming '?' to the '0'.
        self.play(Transform(probas_query[-2], MathTex("0").move_to(probas_query[-2].get_center())))
        # Showing the answer
        self.play(FadeIn(probas_query[-1]))
        # Moving the equation under the label
        self.play(probas_query.animate.next_to(query, DOWN, buff=MED_SMALL_BUFF))

        # Depicting customer's frustration
        self.angry_customer_scene()

        # Trying to replace typo word with correct one
        query_wrong_word = query[1]
        probas_query_wrong_word = probas_query[2]
        query_correct_word = Text("белый").next_to(query[0]).set_color(YELLOW)
        probas_query_correct_word = MathTex(r"\times P(\text{белый})", tex_to_color_map={r'\text{белый}': YELLOW})
        probas_query_correct_word.move_to(probas_query_wrong_word.get_center())
        # Replace the probability of wrong word with the probability of correct one
        correct_proba = MathTex("0.78").next_to(probas_query[-3], buff=SMALL_BUFF).set_color(YELLOW)
        # The new total probability
        new_ans = MathTex("= 0.772", tex_to_color_map={'0.772': YELLOW}).next_to(correct_proba, buff=SMALL_BUFF)
        self.play(
            AnimationGroup(
                Transform(query_wrong_word, query_correct_word),
                TransformMatchingShapes(probas_query_wrong_word, probas_query_correct_word),
                Transform(probas_query[-2], correct_proba),
                TransformMatchingShapes(probas_query[-1], new_ans)
            )
        )

        # The customer gets happy:)
        happy_pi_customer = self.pi_customer.copy()
        happy_pi_customer.change_mode("happy")
        happy_pi_customer.body.set_color(BLUE)
        self.play(Transform(self.pi_customer, happy_pi_customer))
        self.wait()

    def angry_customer_scene(self):
        self.pi_customer.to_edge(DOWN).scale(0.6)
        self.pi_customer.body.set_color(RED)
        self.add(self.pi_customer)
        self.play(FadeIn(self.pi_customer))


class VipryamitelBlackBoxScene(CustomersScene):
    def __init__(self):
        self.black_box = None        # black box of spellchecker
        self.box_label = None        # "Spellchecker"
        self.black_box_group = None  # the group of two above

        # Wrong instances
        self.wrong_queries = [
            Text(query).set_color(RED) for query in [
                "айфон белый",
                "iphone ,tksq",
                "iphone блый",
                "iphoneблый"
            ]
        ]

        # Generally, the same query
        self.correct_queries = [
            Text(correction).set_color(GREEN) for correction in ["iphone белый"] * 4
        ]
        super(VipryamitelBlackBoxScene, self).__init__()

    def construct(self) -> None:
        self.draw_blackbox()
        self.change_all_customers_modes("raise_right_hand", lag_ratio=0)
        self.get_wrong_queries()
        self.pass_queries_to_spellchecker_and_fix_it()
        self.change_all_customers_modes("plain", look_at_arg=self.black_box.get_center(), lag_ratio=0)
        self.change_all_customers_modes("hooray", lag_ratio=0)
        self.zoom_in_on_black_box()

    def draw_blackbox(self):
        """Drawing the spellchecker blackbox.
        """
        if self.black_box is not None:
            raise Exception("Box is already created")

        # Create the spellchecker blackbox
        self.black_box = Rectangle(
            width=config.frame_width / 2,
            height=config.frame_height - 2,
            fill_opacity=1,
            fill_color=BLACK
        )

        # Create the label
        self.box_label = Text("Spellchecker").move_to(self.black_box.get_center())

        # Form the blackckox and place it on screen
        self.black_box_group = VGroup(self.black_box, self.box_label)
        self.black_box_group.to_edge(RIGHT)
        self.add_foreground_mobject(self.black_box_group)

        # Show the blackbox
        self.play(
            AnimationGroup(
                Create(self.black_box),
                FadeIn(self.box_label),
                lag_ratio=0.5
            )
        )

    def get_wrong_queries(self):
        """Show the typo queries.
        """
        # Get 4 customers
        customers = self.get_customers()
        if not all(list(map(lambda c: c.mode == "raise_right_hand", customers))):
            raise Exception("Customers have to raise hand")

        # Place the query over the customers
        for idx, customer in enumerate(customers):
            self.wrong_queries[idx].scale(0.4).next_to(customer, UR)

        self.play(FadeIn(*[query for query in self.wrong_queries]))

    def pass_queries_to_spellchecker_and_fix_it(self):
        """Moving the queries to the spellchecker blackbox.
        """
        # Move query to the blackbox and make customers look after the query
        anims_wrong = [query.animate.move_to(self.black_box.get_center()) for query in self.wrong_queries] + \
                      [customer.animate.look_at(self.black_box.get_center()) for customer in self.customers]

        # Place the correct queries at the same place as the wrong queries
        for query in self.correct_queries:
            query.scale(0.4).move_to(self.black_box.get_center())

        # Move the correct queries back to the customers
        anims_correct = [q.animate.next_to(c, UR) for q, c in zip(self.correct_queries, self.get_customers())]
        for wrong_animation, correct_animation in zip(anims_wrong, anims_correct):
            self.play(wrong_animation)
            self.play(correct_animation)

    def zoom_in_on_black_box(self, radius=config.frame_width / 2 + config.frame_height / 2):
        """Zoom a little bit higher than "Spellchecker" label.
        """
        vect = -self.black_box.get_center() + [0, -1, 0]

        self.play(*[
            ApplyPointwiseFunction(lambda point: (point + vect) * radius, mob)
            for mob in self.mobjects
        ])


class FunnelTemplate:
    """Helpful Funnel class. It depicts the vipryamitel funnel and a query at specific level
    """
    def __init__(self, query: str = None, at_level: int = 0, buff: float = 0,
                 level_width: float = 4, level_height: float = 0.5, text_height: float = 0.3):
        """Constructor. Form the funnel.
        :param query: the query
        :param at_level: on which level we start
        :param buff: the buffer between levels
        :param level_width: the width if the first level (it's will be shrinking at each adjacent level)
        :param level_height: the height of all levels
        :param text_height: the height of text
        """
        # Create levels each arranged under preceding
        self.levels = VGroup(
            *[Rectangle(width=level_width, height=level_height) for _ in range(8)]
        ).arrange(DOWN, buff=buff)

        # default properties of levels and text
        self.default_level_props = {'width': level_width, 'height': level_height}
        self.default_text_props = {'height': text_height}

        # Each module name
        self.modules_names = VGroup(
            *[Text(label) for label in
              [
                "Query",
                "Replace similar symbols",
                "Replace brands",
                "Fix layout",
                "Handle punctuation",
                "Fix spaces",
                "Typo fixing",
                "Replace brands"
              ]])
        # The gradient of the funnel
        self.rgbas = color_gradient((RED_E, GREEN_E), 8)
        # The query
        self.query = query
        # The level the query starts
        self.query_level = at_level

        for idx in range(len(self.levels)):
            # Get the level with proper width
            level = self._get_level_rect(idx)
            # Color the level
            level.set_color(self.rgbas[idx]).set_fill(color=self.rgbas[idx], opacity=1)
            # Color and arrange the module name
            self.modules_names[idx].set(height=text_height).next_to(level, LEFT).to_edge(LEFT)
            self.modules_names[idx].set_color(self.rgbas[idx])

        if query:
            # if query was passed then adjust its style
            self.query = Text(query, color=self.rgbas[self.query_level])
            self.query.set(height=self.modules_names[0].height).next_to(self.levels[self.query_level], RIGHT)

    def _get_level_rect(self, level: int):
        """Returns level block with proper width depends on its postion.

        :param level: the position of level
        """
        if level == 0:
            return self.levels[0]
        elif self.levels[level].width < self.levels[level - 1].width:
            return self.levels[level]
        else:
            return self.levels[level].stretch_to_fit_width(width=self.levels[level - 1].width * (1 - level / 10))

    def move_query_further(self, new_query: str = None, direction: np.array = RIGHT, to_edge: bool = True) -> Text:
        """Moving query to the next level.
        :param new_query: the new query to the current should be transformed.
        :param direction: the direction from the funnel the query will be placed.
        :param to_edge: should the query be attached to the edge (according to the `direction`).
        """
        if not self.query:
            raise ValueError("Query is not defined")
        self.query_level += 1

        if new_query:
            new_query = Text(new_query).set(height=self.default_text_props['height'])
        else:
            new_query = self.query.copy()

        new_query.next_to(self.levels[self.query_level], direction)

        if to_edge:
            new_query.to_edge(direction / 5)

        new_query.set_color(self.rgbas[self.query_level])
        self.query = new_query
        return self.query


class VipryamitelFunnel(Scene):
    def __init__(self):
        # The query at every level
        self.modifications = [
            "loсcitаne дхи ,en ghjdbyc длянего",
            "l'occitane дхи ,en ghjdbyc длянего",
            "l'occitane дхи ,en ghjdbyc длянего",
            "l'occitane дхи ,en провинс длянего",
            "l'occitane дхи, en провинс длянего",
            "l'occitane дхи, en провинс для него",
            "l'occitane духи, en прованс для него",
            "l'occitane духи, en provence для него"
        ]
        # The funnel itself
        self.funnel = FunnelTemplate(self.modifications[0], 0)
        # Probabilities at each level
        self.probas_at_level = {
            'typo_probas': np.linspace(1, 0, 8),
            'resp_probas': np.linspace(0, 1, 8)
        }
        # Probabilitites labels
        self.probas_label = [
            MathTex(r"P(\text{ошибки в запросе}) = ", color=RED_E),
            MathTex(r"P(\text{что-то найти по запросу}) = ", color=RED_E)
        ]
        # The group of two probabilities defined above
        self.probas = None  # type: VGroup
        super(VipryamitelFunnel, self).__init__()

    def construct(self):
        self.show_levels_scene()
        self.query_probas_scene()
        self.show_kostyl()

    def show_levels_scene(self):
        """Show the funnel level by level.
        """
        for idx in range(len(self.funnel.levels)):
            self.play(FadeIn(self.funnel.levels[idx], self.funnel.modules_names[idx]))

    def query_probas_scene(self):
        """The scene of representation vipryamitel affects to the query and its probabilities.
        """
        if self.probas is not None:
            raise ValueError("self.probas already created")

        # Wrapping the probabilities values and styling them up
        res_probas = []
        probas_nums = [self.probas_at_level[p_type][0] for p_type in self.probas_at_level]
        for num, label in zip(probas_nums, self.probas_label):
            decimal_num = DecimalNumber(num, num_decimal_places=2)
            res_probas.append(
                VGroup(label, decimal_num).arrange(RIGHT).set(height=self.funnel.default_text_props['height'])
            )
        # Arrange the probabilities labels
        self.probas = VGroup(*res_probas).set_color(RED_E).arrange(RIGHT, buff=LARGE_BUFF).to_edge(UP)

        # Show the query and probabilities
        self.play(FadeIn(self.funnel.query, self.probas))
        self.wait()

        # Emphasis the probabilities
        self.play(Circumscribe(self.probas[0], fade_out=True))
        self.play(Circumscribe(self.probas[1], fade_out=True))
        self.wait()

        # Surround the probabilities values
        typo_proba_box = SurroundingRectangle(self.probas[0][-1], buff=SMALL_BUFF)
        resp_proba_box = SurroundingRectangle(self.probas[1][-1], buff=SMALL_BUFF)
        self.play(
            AnimationGroup(
                Create(typo_proba_box),
                Create(resp_proba_box)
            )
        )
        # Moving the query down to the funnel and modify it along with the probabilities
        for query, typo_proba, resp_proba, p_color in zip(self.modifications[1:],
                                                          self.probas_at_level['typo_probas'][1:],
                                                          self.probas_at_level['resp_probas'][1:],
                                                          self.funnel.rgbas[1:]):
            self.probas.set_color(p_color)
            self.play(
                AnimationGroup(
                    ReplacementTransform(self.funnel.query, self.funnel.move_query_further(query, to_edge=True)),
                    ChangeDecimalToValue(self.probas[0][-1], typo_proba),
                    ChangeDecimalToValue(self.probas[1][-1], resp_proba),
                )
            )
            self.wait()

        # Probabilities are disappearing
        self.play(FadeOut(typo_proba_box, resp_proba_box, self.probas, self.funnel.query))

    def show_kostyl(self):
        """The kostyl layer representation.
        """
        # We wanna to spread the levels, thus make it copy and set another buffer
        spread_levels = self.funnel.levels.copy()
        spread_levels.arrange(DOWN, buff=MED_SMALL_BUFF)

        # Adding the kostyl representation (I suppose a line between the levels is good enough)
        kostyl = []
        for level in spread_levels[:-1]:
            kostyl.append(Line(color=YELLOW).next_to(level, DOWN, buff=MED_SMALL_BUFF / 2))
            kostyl[-1].set(width=level.width)
        kostyl = VGroup(*kostyl)

        # Don' forget to spread module names accordingly
        spread_names_anims = []
        for idx, name in enumerate(self.funnel.modules_names):
            spread_names_anims.append(name.animate.next_to(spread_levels[idx], LEFT).to_edge(LEFT))

        # Spreading the funnel with names up
        self.play(
            AnimationGroup(
                Transform(self.funnel.levels, spread_levels),
                *spread_names_anims
            )
        )
        # Show the kostyl lines
        self.play(FadeIn(kostyl))

        # Wiggling the lines
        self.play(*list(map(lambda instance: Wiggle(instance), kostyl)))

        # Transform the lines into the 'Kostyl' label
        kostyl_label = Text("Kostyl", color=YELLOW).to_edge(UP / 2)
        self.play(ReplacementTransform(kostyl, kostyl_label))
        self.play(FadeOut(*[obj for obj in self.mobjects if obj != kostyl_label]))
        self.wait()


class KostylScene(MovingCameraScene):
    def __init__(self):
        super(KostylScene, self).__init__()
        # The kostyl_label is taken from VipryamitelFunnel due to video coherence
        self.kostyl_label = Text("Kostyl", color=YELLOW).to_edge(UP / 2)
        # The funnel itself
        self.funnel = FunnelTemplate(buff=MED_SMALL_BUFF)

    def construct(self):
        self.add(self.kostyl_label)
        self.example()
        self.black_white_lists()
        self.bigrams()
        self.kostyl_summarization()

    def example(self):
        """Showing the example of work of Kostyl.
        """
        query = Text("Chanel ультра ле теинт тональный флюид")
        first_subquery = query[:6]      # The 'Chanel' has to blocked by Kostyl
        second_subquery = query[6:19]   # The 'ультра ле теинт' won't be blocked by Kostyl
        third_subquery = query[19:]     # The 'тональный флюид' has to blocked by Kostyl

        # Creating the boxes and the locks
        first_box = SurroundingRectangle(first_subquery, color=WHITE)
        second_box = SurroundingRectangle(third_subquery, color=WHITE)
        first_lock = Lock().next_to(first_box, UP).scale(0.6)
        second_lock = Lock().next_to(second_box, UP).scale(0.6)

        # Write the query and block the blocking parts
        self.play(Write(query))
        self.play(Create(first_box))
        self.play(FadeIn(first_lock))
        self.play(Create(second_box))
        self.play(FadeIn(second_lock))

        # Coloring the blocked parts green
        self.play(*list(map(lambda subquery: subquery.animate.set_color(GREEN), [first_subquery, third_subquery])))

        # Indicating and coloring the remaining parts
        self.play(ApplyWave(query))
        self.play(Indicate(second_subquery, color=RED))
        self.wait()
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.kostyl_label]))

    def black_white_lists(self):
        """Describing the black and white lists application.
        """
        # The query itself
        base_query = Text("парфюм essencial набор").scale(0.5).to_edge(LEFT + UP * 2.8)
        # The words of query
        words = VGroup(*[base_query[:6], base_query[6:15], base_query[15:]])
        self.play(Write(base_query))
        # The boxes surrounding every word
        every_word_boxes = [SurroundingRectangle(word) for word in words]
        # The boxes surrounding every two words
        boxes_by_two_words = [SurroundingRectangle(words[:2]), SurroundingRectangle(words[1:])]
        # The boxes surrounding the entire query
        entire_query_box = SurroundingRectangle(base_query)

        # Creating table
        table = MobjectTable(
            [[words[0].copy(), Cross(), Check(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[:2].copy(), Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [base_query.copy(), Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[1].copy(), Check(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[1:].copy(), Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[2].copy(), Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()]],
            row_labels=[],
            col_labels=[NotebookWithNotes(color=GREEN), NotebookWithNotes(color=RED), Text("Трансформация"), Lock()],
            include_outer_lines=True
        )
        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx % 5 == 0:
                # Scale every first entry in a row
                entry.scale(1.3)
            # Remove all entries in purpose to start from empty table
            self.remove(entry)

        # Rescale the table and draw it
        table.scale(0.4).next_to(base_query, DOWN).to_edge(LEFT)
        self.play(Create(table.get_vertical_lines()))
        self.play(Create(table.get_horizontal_lines()))
        self.play(FadeIn(table.get_col_labels(), run_time=2))
        self.wait()

        # Prepare animations for the words boxes representation
        boxes_anims = [
            Create(every_word_boxes[0]),
            ReplacementTransform(every_word_boxes[0], boxes_by_two_words[0]),
            ReplacementTransform(boxes_by_two_words[0], entire_query_box),
            ReplacementTransform(entire_query_box, every_word_boxes[1]),
            ReplacementTransform(every_word_boxes[1], boxes_by_two_words[1]),
            ReplacementTransform(boxes_by_two_words[1], every_word_boxes[2])
        ]

        # Block that indices which shouldn't be appeared, especially
        # 1. All transformation except for the one in the 3'd row
        # 2. All locks except for the very first and that one in the 3'd row
        blocked_indices = []
        for idx in range(len(table.get_entries_without_labels())):
            if (idx % 5 == 3 and idx != 18) or (idx % 5 == 4 and idx != 4 and idx != 19):
                blocked_indices.append(idx)

        # Fill the table
        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx not in blocked_indices:
                if idx % 5 == 0:
                    # If the entry is first in its row then let the watcher see the relation between the box and entry
                    self.play(
                        AnimationGroup(
                            boxes_anims[idx // 5],
                            FadeIn(entry),
                            lag_ratio=0.5
                        )
                    )
                else:
                    self.play(FadeIn(entry))

                if idx % 5 == 4:
                    # if the lock appears then let the watcher see the subquery where it occurred
                    self.wait()

        self.wait()

        self.play(Uncreate(every_word_boxes[-1]))

        # The proper query
        result_query = Text("парфюм ESSENTIAL PARFUMS PARIS набор").set(height=base_query.height)
        result_query.next_to(base_query, RIGHT * 5)
        blocked_part = result_query[:27]    # Define the part which will be blocked
        changable_part = result_query[27:]  # Define the part which won't be blocked

        # The box surrounding the blocked part
        block_box = SurroundingRectangle(blocked_part, color=WHITE, buff=SMALL_BUFF)
        # The lock over the blocked part
        lock = table.get_entries((1, 5))
        # The arrow from original query to the result query
        arrow = Arrow(start=base_query, end=result_query.get_center() - [result_query.width/2, 0, 0], color=WHITE)

        # Getting the proper query from original one
        self.play(TransformFromCopy(base_query.copy(), result_query))
        self.play(FadeIn(arrow))
        # Drawing the blocked part and coloring it.
        self.play(Create(block_box))
        self.play(lock.copy().animate.next_to(block_box, UP))
        self.play(
            AnimationGroup(
                blocked_part.animate.set_color(GREEN),
                changable_part.animate.set_color(RED)
            )
        )
        self.wait()

        # Here we wanna show the idea that it's impossible that
        # a phrase is in both black and white lists simultaneously

        # Set the blinder for entire screen
        fs_blinder = FullScreenRectangle(color=BLACK, fill_opacity=0.85)
        # Get the entries for the highlighting
        highlighted_row = [table.get_entries_without_labels((2, idx)) for idx in range(2, 4)]
        # Replace any cross in highlighted row with checks
        checks = [Check().set(height=cross.height).move_to(cross) for cross in highlighted_row]
        # Get the cells bounds for the crossing them further
        cells = [table.get_cell((3, 2)), table.get_cell((3, 3))]
        corners = {
            'UL': cells[0].get_boundary_point(UL),
            'DR': cells[1].get_boundary_point(DR),
            'UR': cells[1].get_boundary_point(UR),
            'DL': cells[0].get_boundary_point(DL)
        }
        # Crossing lines for the cells
        lines = [Line(corners['UL'], corners['DR'], color=RED), Line(corners['UR'], corners['DL'], color=RED)]
        # Highlight the row
        self.add_foreground_mobjects(*highlighted_row)
        # Blind the background
        self.play(FadeIn(fs_blinder))
        # Show crosses to checks transfromation
        self.play(
            AnimationGroup(
                ReplacementTransform(highlighted_row[0], checks[0]),
                ReplacementTransform(highlighted_row[1], checks[1])
            )
        )
        self.wait()
        # Cross the cells in purpose to show that case is impossible
        self.play(
            AnimationGroup(
                Create(lines[0]),
                Create(lines[1]),
                lag_ratio=0.8
            )
        )
        self.wait()
        # Emphasize by pi_creature words that case is impossible
        pi_creature = PiCreature("plain", flip_at_start=True).scale(0.7).to_corner(DR)
        self.play(
            PiCreatureSays(pi_creature, Text("Такого не может быть!", color=RED).scale(0.7), target_mode="speaking")
        )
        self.wait()
        # Show the way how handle such cases
        self.play(FadeOut(*[pi_creature.bubble, pi_creature.bubble.content, *lines]))
        # Replace the last check with a cross (we always prefer the white list rather than black list in such cases)
        replacement_cross = Cross().set(height=checks[1].height).move_to(checks[1])
        self.play(ReplacementTransform(checks[1], replacement_cross))
        self.play(pi_creature.animate.change_mode("hooray"))
        self.wait()
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.kostyl_label]))
        self.wait()

    def bigrams(self):
        """Show how do we handle bigrams.
        """
        # The query with bigrams
        base_query = Text("крем для лица ла мер").scale(0.5).to_edge(LEFT + UP * 2.8)
        # Break the query onto the words
        words = VGroup(*[base_query[:4], base_query[4:7], base_query[7:11], base_query[11:13], base_query[13:]])
        # Surround each two words with box for the further representation
        boxes = [SurroundingRectangle(words[idx: idx + 2]) for idx in range(len(words) - 1)]
        # Show the query
        self.play(AddTextLetterByLetter(base_query))
        # Creating the table
        table = MobjectTable(
            [[words[0:2].copy(), Check(), Lock()],
             [words[1:3].copy(), Check(), Lock()],
             [words[2:4].copy(), Cross(), Lock()],
             [words[3:].copy(), Cross(), Lock()]],
            row_labels=[],
            col_labels=[NotebookWithNotes(color=BLUE), Lock()],
            include_outer_lines=True
        )
        # Scale and positioning the table
        table.scale(0.4).next_to(base_query, DOWN).to_edge(LEFT)

        # Scale all head entry in every row and remove every entry for the further filling
        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx % 3 == 0:
                entry.scale(1.3)
            self.remove(entry)

        # Create the table
        self.play(Create(table.get_vertical_lines()))
        self.play(Create(table.get_horizontal_lines()))
        self.play(FadeIn(table.get_col_labels(), run_time=2))
        self.wait()

        # Creating the sequence of boxes animations
        boxes_anims = [
            Create(boxes[0]),
            *[ReplacementTransform(boxes[idx - 1], boxes[idx]) for idx in range(1, len(boxes))]
        ]

        # The indices which will not be representing
        blocked_indices = [8, 11]

        # Filling the table
        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx not in blocked_indices:
                if idx % 3 == 0:
                    # If the entry is first in its row then let the watcher see the relation between the box and entry
                    self.play(
                        AnimationGroup(
                            boxes_anims[idx // 3],
                            FadeIn(entry),
                            lag_ratio=0.5
                        )
                    )
                else:
                    self.play(FadeIn(entry))

                if idx % 3 == 2:
                    # if the lock appears then let the watcher see the subquery where it occurred
                    self.wait()

        self.wait()

        self.play(Uncreate(boxes[-1]))
        self.wait()

        # Blocking first three words
        block_box = SurroundingRectangle(words[0:3], color=WHITE, buff=SMALL_BUFF)
        # The lock from table is taken
        lock = table.get_entries((1, 3))
        blocked_part = words[0:3]
        changable_part = words[3:]

        # Show the blocking
        self.play(Create(block_box))
        self.play(lock.copy().animate.next_to(block_box, UP))
        self.play(
            AnimationGroup(
                blocked_part.animate.set_color(GREEN),
                changable_part.animate.set_color(RED)
            )
        )
        self.wait()
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.kostyl_label]))
        self.wait()

    def kostyl_summarization(self):
        """This scene represents the total kostyl idea.
        The scene is zoomed at the beginning (i.e. all committed before have also been zoomed in).
        The scene will show the zoom out effect back to the funnel.
        """
        def resize_mobject(mobject: Union[VMobject, Mobject], zoom_factor: int = 10) -> Union[VMobject, Mobject]:
            """All mobjects have to be properly resized.
            :param mobject: the resizing mobject
            :param zoom_factor: the coefficient by which the scene has been zoomed.
            """

            # If the mobject is a VMobject - then scale each submobject inside
            if isinstance(mobject, VMobject):
                for obj in mobject:
                    # height will be adjusted
                    obj.set(width=obj.width / zoom_factor)
                    # re-adjust the position
                    obj.move_to(obj.get_center() / zoom_factor)
                    if obj.stroke_width != 0:
                        # re-adjust stroke width
                        obj.set_stroke(width=mobject.stroke_width / zoom_factor)
            else:
                mobject.set(width=mobject.width / zoom_factor)
                mobject.move_to(mobject.get_center() / zoom_factor)
                if mobject.stroke_width != 0:
                    mobject.set_stroke(width=mobject.stroke_width / zoom_factor)
            return mobject

        # Zoom factor (adjusted manually)
        zf = 60

        # The kostyl equation itself (whitelist + blacklist + feed)
        kostyl_equation = VGroup(
            Text("Kostyl", color=YELLOW),
            MathTex("="),
            NotebookWithNotes(color=GREEN),
            MathTex("+"),
            NotebookWithNotes(color=RED),
            MathTex("+"),
            NotebookWithNotes(color=BLUE)
        ).arrange(RIGHT)

        # Yellow box for the kostyl as line representation
        box = SurroundingRectangle(kostyl_equation)

        # == At this code block we're working at 'zoomed out' state ==
        # Adding kostyl as lines as it's been in the VipryamitelFunnel
        kostyl_as_lines = []
        for level in self.funnel.levels[:-1]:
            kostyl_as_lines.append(Line(color=YELLOW).next_to(level, DOWN, buff=MED_SMALL_BUFF / 2))
            kostyl_as_lines[-1].set(width=level.width)
        kostyl_as_lines = VGroup(*kostyl_as_lines)
        # We wanna the kostyl lines be overlapped by levels when the funnel shrinks
        self.add_foreground_mobject(self.funnel.levels)
        # Adding the module names and the all kostyl lines except the middle one (it will be zoomed out from main scene)
        self.add(self.funnel.modules_names, *kostyl_as_lines[:3], *kostyl_as_lines[4:])
        # Save the state to which one we will be returning
        self.camera.frame.save_state()
        # == The end of 'zoomed out' state ==

        # == Making the effect of zooming out ==
        # Firstly, resize all mobjects on the screen according to the zoom factor
        self.kostyl_label = resize_mobject(self.kostyl_label, zf)
        kostyl_equation = resize_mobject(kostyl_equation, zf)
        box = resize_mobject(box, zf)

        # == Zoom the frame, the following actions are occurring in the zoomed state ==
        self.camera.frame.set(width=config.frame_width / zf)

        # The label replace the right part of equation
        self.play(ReplacementTransform(self.kostyl_label, kostyl_equation[0]))
        # The rest part of equation appears
        self.play(FadeIn(kostyl_equation[1:], run_time=3))
        self.wait()
        # Surrounding the equation with the box
        self.play(Create(box))
        self.play(box.animate.set_fill(color=box.color, opacity=1))
        # Remove underlying equation to avoid the problems when state turns back
        self.remove(*kostyl_equation)
        # Restore the state along with kostyl line
        self.play(Restore(self.camera.frame), ReplacementTransform(box, kostyl_as_lines[3]))
        self.wait()

        # Take the copy of funnel and shrink it
        return_levels = self.funnel.levels.copy().arrange(DOWN, buff=0)

        # Move the module names accordingly
        return_names_anims = []
        for idx, name in enumerate(self.funnel.modules_names):
            return_names_anims.append(name.animate.next_to(return_levels[idx], LEFT).to_edge(LEFT))

        # Move the kostyl lines under the levels accordingly
        kostyl_lines_anims = []
        for idx, line in enumerate(kostyl_as_lines):
            kostyl_lines_anims.append(line.animate.move_to(return_levels[idx].get_bottom()))

        # Play all animations at the same time
        self.play(
            AnimationGroup(
                Transform(self.funnel.levels, return_levels),
                *return_names_anims,
                *kostyl_lines_anims,
                run_time=1
            )
        )

        self.wait()


def kostyl_scan(self: Scene, obj: Mobject):
    """The scene of kostyl scanning.
    """
    # Vertical kostyl line
    kostyl_line = Line(start=obj.get_top(), end=obj.get_bottom(), color=YELLOW).next_to(obj, LEFT, buff=0)
    # Kostyl label over line
    kostyl_label = Text("Kostyl", color=YELLOW).scale(0.5).next_to(kostyl_line, UP)
    # Make label able to follow the line (scanner)
    kostyl_label.add_updater(lambda label: label.next_to(kostyl_line, UP))
    # Create the path which one the scanner will pass
    path = Line().set(width=obj.width).move_to(obj.get_center())

    # Play the kostyl animation
    self.play(FadeIn(kostyl_label, kostyl_line))
    self.play(MoveAlongPath(kostyl_line, path, rate_func=linear))
    self.play(FadeOut(kostyl_label, kostyl_line))


class SimilarSymbolsReplace(Scene):
    def __init__(self):
        # The funnel wit the query starting at the very first level
        self.funnel = FunnelTemplate(query="запрос", at_level=0)
        # Copy the name of module
        self.module_label = self.funnel.modules_names[1].copy().center().to_edge(UP).set_color(WHITE)
        # Symbols of english alphabet (lowercase)
        self.eng_alpha = list(map(chr, range(97, 123)))
        a = ord('а')
        # Symbols of russian alphabet (lowercase)
        self.rus_alpha = list(map(chr, range(a, a + 6))) + [chr(a + 33)] + list(map(chr, range(a + 6, a + 32)))
        # Keep the alphabets in dictionary
        self.str_alphas = {'rus': self.rus_alpha, 'eng': self.eng_alpha}
        # Lock of forbidden part
        self.lock = None
        self.new_total_query = None
        super(SimilarSymbolsReplace, self).__init__()

    def construct(self):
        # Start the scene from the end of previous one
        self.add(self.funnel.levels, self.funnel.modules_names)
        self.query_to_level()
        self.wait()
        self.print_alpha()
        self.abstract_examples()
        self.query_example()
        self.back_to_funnel()

    def query_to_level(self):
        # The query appears right side from funnel
        self.play(FadeIn(self.funnel.query))
        # Move the query down to the next level
        self.play(ReplacementTransform(self.funnel.query, self.funnel.move_query_further(to_edge=False)))
        self.wait()

        # Mark the current level as highlighting one
        self.add_foreground_mobjects(self.funnel.modules_names[1], self.funnel.levels[1], self.funnel.query)
        fs_blinder = FullScreenRectangle(color=BLACK, fill_opacity=0.85)
        self.module_label.set(height=self.funnel.modules_names[1].height)

        # Save current module name and its style
        temp_module_name = self.funnel.modules_names[1].copy()
        # Highlight the current level and replace the module label from module name
        self.play(FadeIn(fs_blinder))
        self.play(
            AnimationGroup(
                ReplacementTransform(self.funnel.modules_names[1], self.module_label),
                FadeOut(self.funnel.query, self.funnel.levels[1]),
                fs_blinder.animate.set_fill(BLACK, opacity=1)
            )
        )
        # Return the module name back
        self.funnel.modules_names[1] = temp_module_name
        self.remove(*[mobject for mobject in self.mobjects if mobject != self.module_label])

    def print_alpha(self):
        """Print the alphabets.
        """
        # The table of russian alphabet by four symbols in a row.
        rus_table = [
            self.rus_alpha[:4],
            self.rus_alpha[4:8],
            self.rus_alpha[8:12],
            self.rus_alpha[12:16],
            self.rus_alpha[16:20],
            self.rus_alpha[20:24],
            self.rus_alpha[24:28],
            self.rus_alpha[28:32],
            self.rus_alpha[32:] + [''] * 3,
        ]

        # The table of english alphabet by four symbols in a row.
        eng_table = [
            self.eng_alpha[:4],
            self.eng_alpha[4:8],
            self.eng_alpha[8:12],
            self.eng_alpha[12:16],
            self.eng_alpha[16:20],
            self.eng_alpha[20:24],
            self.eng_alpha[24:] + [''] * 2
        ]

        # Create the tables in purpose to properly arrange the symbols
        rus_table = Table(rus_table).scale(0.5)
        eng_table = Table(eng_table).scale(0.5)

        # Extract the symbols of alphabets
        self.rus_alpha = rus_table.get_entries_without_labels()
        self.eng_alpha = eng_table.get_entries_without_labels()
        # Place the alphabets and color them
        self.rus_alpha.to_edge(LEFT).set_color(BLUE)
        self.eng_alpha.to_edge(RIGHT).set_color(YELLOW)
        # Show the alphabets
        self.play(
            AnimationGroup(
                LaggedStartMap(GrowFromCenter, self.rus_alpha, lag_ratio=0.5),
                LaggedStartMap(GrowFromCenter, self.eng_alpha, lag_ratio=0.5)
            )
        )

        # Color similar symbols with red
        self.play(
            AnimationGroup(
                *[self.rus_alpha[self.str_alphas['rus'].index(s)].animate.set_color(RED) for s in 'хсаореукм'],
                *[self.eng_alpha[self.str_alphas['eng'].index(s)].animate.set_color(RED) for s in 'xcaopeykm']
            )
        )

        # Indicate similar symbols
        self.play(
            AnimationGroup(
                *[Indicate(self.rus_alpha[self.str_alphas['rus'].index(s)], color=RED, scale_factor=2)
                  for s in 'хсаореукм'],
                *[Indicate(self.eng_alpha[self.str_alphas['eng'].index(s)], color=RED, scale_factor=2)
                  for s in 'xcaopeykm']
            )
        )

    def abstract_examples(self):
        """Just example of words for each case.
        1. loccitane - english replacement
        2. духи - russian replacement
        3. муka - unable to replace
        4. qwrtбвгд - unable to replace
        """
        def color_word(word: Text) -> VGroup:
            """Color the word letter by letter.
            """
            lang_letters = []
            for idx, letter in enumerate(word.text):
                if letter in 'хсаореукмxcaopeykm':
                    # color any of similar symbols to red
                    self.play(word[idx].animate.set_color(RED))
                elif letter in self.str_alphas['rus']:
                    # coloring the symbols of russian alphabet to BLUE
                    lang_letters.append(word[idx])
                    self.play(word[idx].animate.set_color(BLUE))
                else:
                    # coloring the symbols of russian alphabet to YELLOW
                    lang_letters.append(word[idx])
                    self.play(word[idx].animate.set_color(YELLOW))
            return VGroup(*lang_letters)

        # The examples of words
        examples = VGroup(*list(map(Text, ["loccitane", "духи", "муka", "qwrtбвгд"]))).scale(0.5)
        examples.arrange(DOWN, buff=LARGE_BUFF)

        # the languages
        langs = {
            'rus': Text('рус.', color=BLUE, height=examples[0].height / 2),
            'eng': Text('англ.', color=YELLOW, height=examples[0].height / 2),
            '?': Text('?', color=RED, height=examples[0].height / 2),
        }

        # Process first word
        self.play(Write(examples[0]))
        lang_letters = color_word(examples[0])
        self.wait()
        self.play(TransformFromCopy(lang_letters, langs['eng'].copy().next_to(examples[0], UP, buff=SMALL_BUFF)))
        self.wait()
        self.play(examples[0].animate.set_color(YELLOW))
        self.play(Animation(Check().set(height=examples[0].height).next_to(examples[0], RIGHT)))

        # Process second word
        self.play(Write(examples[1]))
        lang_letters = color_word(examples[1])
        self.wait()
        self.play(TransformFromCopy(lang_letters, langs['rus'].copy().next_to(examples[1], UP, buff=SMALL_BUFF)))
        self.wait()
        self.play(examples[1].animate.set_color(BLUE))
        self.play(Animation(Check().set(height=examples[0].height).next_to(examples[1], RIGHT)))

        # Process third word
        self.play(Write(examples[2]))
        color_word(examples[2])
        self.wait()
        self.play(TransformFromCopy(examples[2], langs['?'].copy().next_to(examples[2], UP, buff=SMALL_BUFF)))
        self.wait()
        self.play(Animation(Cross().set(height=examples[0].height).next_to(examples[2], RIGHT)))

        # Process forth word
        self.play(Write(examples[3]))
        lang_letters = color_word(examples[3])
        self.wait()
        self.play(TransformFromCopy(lang_letters, langs['?'].copy().next_to(examples[3], UP, buff=SMALL_BUFF)))
        self.wait()
        self.play(Animation(Cross().set(height=examples[0].height).next_to(examples[3], RIGHT)))

    def query_example(self):
        """The example with entire query.
        """
        self.remove(*[mobject for mobject in self.mobjects if mobject != self.module_label])
        # Write the query
        total_query = Text("loсcitаne дхи ,en ghjdbyc длянего")
        sb = SearchBar(search_term=total_query, corner_radius=0.9)
        self.play(sb.appear_search_box())
        self.play(sb.type_search_term())
        self.wait()
        self.play(sb.vanish_search_box())
        # Scan the query with kostyl
        kostyl_scan(self, total_query)
        self.play(total_query.animate.set_color(RED))
        self.wait()
        # Highlight the unique symbols of alphabets
        animations = []
        for idx, letter in enumerate(total_query.text):
            if letter in 'хсаореукмxcaopeykm,':
                continue
            elif letter in self.str_alphas['rus']:
                animations.append(total_query[idx].animate.set_color(BLUE))
            else:
                animations.append(total_query[idx].animate.set_color(YELLOW))
        self.play(*animations)
        self.wait()
        # Highlight the entire words in proper color (language)
        self.play(
            AnimationGroup(
                total_query[:9].animate.set_color(YELLOW),
                total_query[9:12].animate.set_color(BLUE),
                total_query[13:15].animate.set_color(YELLOW),
                total_query[15:22].animate.set_color(YELLOW),
                total_query[22:].animate.set_color(BLUE)
            )
        )
        self.wait()
        # Scan the query with kostyl again
        kostyl_scan(self, total_query)
        self.play(
            AnimationGroup(
                total_query[:9].animate.set_color(GREEN),
                total_query[9:].animate.set_color(RED)
            )
        )
        # Show that the kostyl found the l'occitane by blocking it
        new_total_query = Text("l'occitane дхи ,en ghjdbyc длянего").move_to(total_query.get_center())
        new_total_query[:10].set_color(GREEN)
        new_total_query[10:].set_color(RED)
        self.play(ReplacementTransform(total_query, new_total_query))
        self.lock = Lock().set(width=new_total_query[:9].width / 6).next_to(new_total_query[:9], UP)
        self.new_total_query = new_total_query
        self.play(DrawBorderThenFill(self.lock))

    def back_to_funnel(self):
        """Return to the Vipryamitel funnel
        """
        self.play(
            AnimationGroup(
                ReplacementTransform(self.module_label, self.funnel.modules_names[1]),
                ReplacementTransform(self.new_total_query, self.funnel.query),
                FadeIn(self.funnel.levels),
                FadeIn(self.funnel.modules_names[0], *self.funnel.modules_names[2:]),
                FadeOut(self.lock)
            )
        )


class ReplaceBrands(PiCreatureScene, ThreeDScene):
    def __init__(self):
        # The starting Vipryamitel funnel
        self.funnel = FunnelTemplate("запрос", 1)
        # The module name
        self.module_label = self.funnel.modules_names[2].copy().center().to_edge(UP).set_color(WHITE)
        super(ReplaceBrands, self).__init__()
        # W/o pi creature at the beginning
        self.pi_creatures_start_on_screen = False
        # Bigram containing query
        self.colombo_new_query = Text("плитка коломбо нью")
        # Unigram containing query
        self.linoleum_query = Text("линолеум кафель для ванны розовый")
        # The list of brands of entire vertical
        vertical_brands_notebook = NotebookWithNotes(color=ORANGE).scale(2)
        # The brand list with its label
        self.vertical_brands_list = VGroup(
            vertical_brands_notebook,
            Text(
                "vertical\nbrand\nlist",
                color=ORANGE,
                width=vertical_brands_notebook.width * 0.9
            ).next_to(vertical_brands_notebook, UP)
        )

        self.questions = VGroup()
        self.setup()

    def construct(self):
        self.pi_creature.scale(0.5).to_corner(RIGHT).flip()
        self.add(self.funnel.levels, self.funnel.modules_names, self.funnel.query)
        self.play(self.funnel.query.animate.next_to(self.funnel.levels[2], RIGHT).set_color(self.funnel.rgbas[2]))
        self.wait()
        self.level_repr()
        self.colombo_new_example()
        self.wait()
        self.accumulate_brand_dict()
        self.wait()
        self.colombo_new_decomposition()
        self.wait()
        self.linoleum_decomposition()
        self.wait()
        self.decision_formalization()
        self.wait()

    def level_repr(self):
        """Showing the level at which we now.
        """
        # Getting the items will be highlighted
        self.add_foreground_mobjects(self.funnel.modules_names[2], self.funnel.levels[2], self.funnel.query)
        # Define the blinder
        fs_blinder = FullScreenRectangle(color=BLACK, fill_opacity=0.85)
        self.module_label.set(height=self.funnel.modules_names[2].height)

        temp_module_name = self.funnel.modules_names[2].copy()
        # Highlight the current level
        self.play(FadeIn(fs_blinder))
        # Replace the module label with the module name
        self.play(
            AnimationGroup(
                ReplacementTransform(self.funnel.modules_names[2], self.module_label),
                FadeOut(self.funnel.query, self.funnel.levels[2]),
                fs_blinder.animate.set_fill(BLACK, opacity=1)
            )
        )
        self.funnel.modules_names[2] = temp_module_name
        self.remove(*[mobject for mobject in self.mobjects if mobject != self.module_label])

    def colombo_new_example(self):
        """Show the example with 'colombo new' brand.
        """
        # Type the query
        sb = SearchBar(search_term=self.colombo_new_query, corner_radius=0.9)
        self.play(sb.appear_search_box())
        self.play(sb.type_search_term())
        self.wait()
        self.play(sb.vanish_search_box())
        # Scan the query with the kostyl
        kostyl_scan(self, self.colombo_new_query)
        # Indicate the part we're looking for
        self.play(self.colombo_new_query.animate.set_color(RED))
        self.wait()
        self.play(Indicate(self.colombo_new_query[6:]))
        self.wait()
        self.play(FadeOut(self.colombo_new_query))

    def accumulate_brand_dict(self):
        """Show the gathering of all brands from the entire vertical.
        """
        # Organizing the mapping in the beauty way
        table_src = [
            [Text("азори"), Arrow(LEFT, RIGHT), Text("azori")],
            [Text("фратини"), Arrow(LEFT, RIGHT), Text("frattini")],
            [Text("веллдорис"), Arrow(LEFT, RIGHT), Text("velldoris")],
            [Text("оранж"), Arrow(LEFT, RIGHT), Text("orange")],
            [Text("коломбо нью"), Arrow(LEFT, RIGHT), Text("colombo new")]
        ]
        table = MobjectTable(table_src)
        mapping = table.get_entries_without_labels().scale(0.3)
        table_mapping = VGroup()
        # Form the mapping
        for idx in range(3, len(mapping) - 2, 3):
            table_mapping += mapping[idx - 3:idx]
            self.play(GrowFromEdge(mapping[idx - 3:idx], RIGHT))

        # Show the mapping
        self.play(
            AnimationGroup(
                table_mapping[-1].animate.become(MathTex(r"\vdots")
                                                 .next_to(table_mapping[-2], DOWN, buff=0).scale(0.9)),
                GrowFromEdge(mapping[-3:].next_to(table_mapping[-1], DOWN), RIGHT)
            )
        )
        table_mapping += mapping[-3:]

        # Boxing the mapping and label it
        box = SurroundingRectangle(table_mapping, color=WHITE)
        id_label = Text("brands list maxipro", width=box.width * 0.9).next_to(box, UP)
        brands_stuff = VGroup(table_mapping, box, id_label)
        self.play(
            AnimationGroup(
                Create(box),
                Write(id_label)
            )
        )
        self.wait()

        # Create the sequence of site brand lists
        vertical_brand_lists = VGroup(
            NotebookWithNotes(color=WHITE).scale(0.5).to_edge(LEFT),
            *[NotebookWithNotes(color=WHITE).scale(0.5).next_to(self.pi_creature, UL) for _ in range(6)]
        )
        # Move the maxipro brand list to the left edge
        self.play(ReplacementTransform(brands_stuff, vertical_brand_lists[0]))
        # Questioning what happens if there is no brand list for site
        self.think("А что если для сайта нету такого списка?", target_mode="pondering")
        self.wait()
        self.play(FadeOut(self.pi_creature.bubble, self.pi_creature.bubble.content))
        self.wait()

        # Showing that we adds other brand list from the same vertical
        self.play(self.pi_creature.animate.change_mode("raise_right_hand"))
        for idx, brand_list in enumerate(vertical_brand_lists[1:]):
            # place at the random place surrounding the first brand list
            pos = vertical_brand_lists[0].get_center() + np.random.random(3)
            if idx == 0:
                # For the first list it just appears over Pi creature
                self.play(FadeIn(brand_list))
            else:  # Pizdec concheno=)))
                # For the rest of lists the current one appears and the previous one moving to its position
                # Due to one of the lists is already at its position we start from the second one, but
                # its index is 0)))
                self.play(vertical_brand_lists[idx].animate.move_to(pos), FadeIn(brand_list))
        self.play(vertical_brand_lists[-1].animate.move_to(vertical_brand_lists[0].get_center() + np.random.random(3)))

        # Transform the sites brand lists to the huge vertical brand list
        self.play(ReplacementTransform(vertical_brand_lists, self.vertical_brands_list))
        self.play(self.pi_creature.animate.change_mode("hooray"))
        self.wait()
        self.play(FadeOut(*[mobj for mobj in self.mobjects if mobj != self.module_label]))

    def colombo_new_decomposition(self):
        """The algorithm of work over bigram brands.
        """
        # Show the observable query and move it left and up
        self.play(FadeIn(self.colombo_new_query))
        self.play(self.colombo_new_query.animate.scale(0.5).next_to(self.module_label, DOWN).to_edge(LEFT))
        # Words of the query
        words = VGroup(self.colombo_new_query[:6], self.colombo_new_query[6:13], self.colombo_new_query[13:])
        # boxes surrounding all combinations of words
        boxes = [
            SurroundingRectangle(words[0], color=YELLOW, buff=SMALL_BUFF),
            SurroundingRectangle(words[:2], color=YELLOW, buff=SMALL_BUFF),
            SurroundingRectangle(words, color=YELLOW, buff=SMALL_BUFF),
            SurroundingRectangle(words[1], color=YELLOW, buff=SMALL_BUFF),
            SurroundingRectangle(words[1:], color=YELLOW, buff=SMALL_BUFF),
            SurroundingRectangle(words[2], color=YELLOW, buff=SMALL_BUFF),
        ]

        # The table of appearance of a combination in the vertical brand list
        table = MobjectTable(
            [
                [
                    words[0].copy().scale(1.8),
                    Cross(),
                    Text("colombo new", height=words[0].height).scale(1.8)
                ],
                [
                    words[:2].copy().scale(1.8),
                    Cross(),
                    Text("colombo new", height=words[0].height).scale(1.8)
                ],
                [
                    self.colombo_new_query.copy().scale(1.8),
                    Cross(),
                    Text("colombo new", height=words[0].height).scale(1.8)
                ],
                [
                    words[1].copy().scale(1.8),
                    Cross(),
                    Text("colombo new", height=words[0].height).scale(1.8)
                ],
                [
                    words[1:].copy().scale(1.8),
                    Check(),
                    Text("colombo new", height=words[0].height).scale(1.8)
                ],
                [
                    words[2].copy().scale(1.8),
                    Cross(),
                    Text("colombo new", height=words[0].height).scale(1.8)
                ],
            ],
            row_labels=[],
            col_labels=[NotebookWithNotes(color=ORANGE), Text("Замена")],
            include_outer_lines=True
        )
        # Remove all entries
        for idx, entry in enumerate(table.get_entries_without_labels()):
            self.remove(entry)

        # Place the table under the query
        table.scale(0.4).next_to(self.colombo_new_query, DOWN).to_edge(LEFT)
        # Show table and labels w/o entries
        self.play(Create(table.get_vertical_lines()))
        self.play(Create(table.get_horizontal_lines()))
        self.play(FadeIn(table.get_col_labels(), run_time=2))
        self.wait()
        # Boxes transformation animations
        boxes_anims = [
            Create(boxes[0]),
            ReplacementTransform(boxes[0], boxes[1]),
            ReplacementTransform(boxes[1], boxes[2]),
            ReplacementTransform(boxes[2], boxes[3]),
            ReplacementTransform(boxes[3], boxes[4]),
            ReplacementTransform(boxes[4], boxes[5])
        ]

        # All transliterations wouldn't be appear except the one in the 4th row
        blocked_indices = []
        for idx in range(len(table.get_entries_without_labels())):
            if idx % 3 == 2 and idx != 14:
                blocked_indices.append(idx)

        # Fill the table
        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx not in blocked_indices:
                if idx % 3 == 0:
                    # If the entry is first in its row then let the watcher see the relation between the box and entry
                    self.play(
                        AnimationGroup(
                            boxes_anims[idx // 3],
                            FadeIn(entry),
                            lag_ratio=0.5
                        )
                    )
                else:
                    self.play(FadeIn(entry))

                if idx % 3 == 2:
                    # if the transliteration appears then let the watcher see the subquery where it occurred
                    self.wait()

        self.wait()

        # Remove the last box
        self.play(Uncreate(boxes[-1]))
        # The transliterated brand which will be replacing the original spelling
        correction = Text("colombo new", height=words[1:].height, color=RED).move_to(words[1:].get_center())
        self.play(
            ReplacementTransform(
                words[1:],
                correction
            )
        )
        words[1:] = correction
        # Scan the correct query with kostyl
        kostyl_scan(self, words)
        self.wait()
        # Coloring and block the words which were masked by kostyl (brand 'colombo new')
        self.play(
            words[1:].animate.set_color(GREEN),
            DrawBorderThenFill(Lock().set(width=words[1:].width / 10).next_to(words[1:], UP))
        )
        self.wait()
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.module_label]))

    def linoleum_decomposition(self):
        """Explanation of the decision making with unigram brand.
        """
        # Type the query
        sb = SearchBar(search_term=self.linoleum_query, corner_radius=0.9)
        self.play(sb.appear_search_box())
        self.play(sb.type_search_term())
        self.wait()
        self.play(sb.vanish_search_box())
        # Scan the query with kostyl
        kostyl_scan(self, self.linoleum_query)  # линолеум кафель для ванны розовый
        # Break the query over the words
        words = VGroup(
            self.linoleum_query[:8],
            self.linoleum_query[8:14],
            self.linoleum_query[14:17],
            self.linoleum_query[17:22],
            self.linoleum_query[22:],
        )

        # The lock over the words which were detected by the kostyl
        mid_lock = Lock().set(width=words[1:4].width / 10).next_to(words[1:4], UP)

        # Block the middle words which were detected by the kostyl
        self.play(
            AnimationGroup(
                words[0].animate.set_color(RED),
                words[1:4].animate.set_color(GREEN),
                words[4].animate.set_color(RED),
                DrawBorderThenFill(mid_lock)
            )
        )
        self.wait()
        # Indicate the word we will process
        self.play(Indicate(words[0]))
        self.wait()

        # The boxes of the brand replacement which are checking unblocked words
        boxes = [SurroundingRectangle(words[0], color=YELLOW), SurroundingRectangle(words[-1], color=YELLOW)]
        self.play(Create(boxes[0]))
        self.wait()
        self.play(ReplacementTransform(boxes[0], boxes[1]))
        self.wait()
        self.play(Uncreate(boxes[1]))
        # We have found the 'линолеум' transliteration and replace it
        translit = Text("linoleum кафель для ванны розовый",
                        t2c={
                            '[:8]': RED,
                            '[8:22]': GREEN,
                            '[22:]': RED
                        })
        # Change the words (original -> transliteration)
        self.play(Transform(self.linoleum_query, translit), mid_lock.animate.next_to(translit[8:22], UP))
        # Scan the new query with kostyl
        kostyl_scan(self, translit)
        # Emphasize that the transliteration is the correct one
        self.play(translit[:8].animate.set_color(GREEN))
        self.wait()
        # Make illusion that it's the proper way to solve
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.module_label]))
        # Pi Creature asking if the solution was correct
        self.play(FadeIn(self.pi_creature))
        thoughts = Text('А точно "linoleum", а не "линолеум"?', t2c={'[7:15]': GREEN, '[21:29]': RED})
        self.think(thoughts, target_mode="pondering")
        self.wait()

        # Copying the disputable words mapping (original -> transliteration)
        translit_word = thoughts[7:15].copy()
        original_word = thoughts[21:29].copy()
        self.add(translit_word, original_word)
        # Remove pi creature thoughts
        self.play(FadeOut(self.pi_creature.bubble, self.pi_creature.bubble.content))
        # We wanna place the words over the hands, like lying on them, thus make a copy of pi creature
        pi_creature_copy = self.pi_creature.copy().change_mode("maybe").center().to_edge(DOWN)
        # Move the original pi creature and words at its positions
        self.play(
            AnimationGroup(
                self.pi_creature.animate.change_mode("maybe").center().to_edge(DOWN),
                translit_word.animate.next_to(pi_creature_copy, UL),
                original_word.animate.next_to(pi_creature_copy, UR),
            )
        )
        self.wait()
        del pi_creature_copy

        # Pi creature thinks which one should be choosen
        self.think(Text("Какое выбрать?").scale(0.4))
        self.wait()
        # What is the 'decision' on a problem in math language
        decision_math = Tex(r"Решение =", r" выводы $\times$ увереность в выводах")
        expanded_decision_math = MathTex(
            r"\text{Решение}=\ ",
            r"&\text{вывод}_1 \times \text{увереность в выводе}_1 +\\",
            r"&\text{вывод}_2 \times \text{увереность в выводе}_2 +\\",
            r"&\qquad\qquad\qquad\vdots\\",
            r"&\text{вывод}_n \times \text{увереность в выводе}_n\\"
        )

        # Show the 'decision' equation and its expanded form
        decision_math.scale(0.5).next_to(self.module_label, DOWN)
        expanded_decision_math.scale(0.5).next_to(self.module_label, DOWN)
        self.play(Write(decision_math))
        self.wait()
        self.play(ReplacementTransform(decision_math, expanded_decision_math))
        self.wait()

        # The column of 'линолеум' and 'linoleum' words in 8:3 ratio, respectively
        feed_linoleum_rate = VGroup(
            *[Text(s).scale(0.4).set_color(RED) for s in ["линолеум"] * 6],
            MathTex(r"\vdots").scale(0.4).set_color(RED),
            Text("линолеум").scale(0.4).set_color(RED),
            Text("linoleum").scale(0.4).set_color(GREEN),
            MathTex(r"\vdots").scale(0.4).set_color(GREEN),
            Text("linoleum").scale(0.4).set_color(GREEN)
        ).arrange(DOWN).to_edge(RIGHT)

        # Make the ration bars from these column
        feed_rate_boxes = VGroup(
            SurroundingRectangle(feed_linoleum_rate[:8], color=RED, fill_opacity=1, buff=0),
            SurroundingRectangle(feed_linoleum_rate[8:], color=GREEN, fill_opacity=1, buff=0)
        )
        # Make them width equal
        feed_rate_boxes[1].set(width=feed_rate_boxes[0].width)
        feed_box = SurroundingRectangle(feed_rate_boxes, color=WHITE)
        feed_label = Text("Фид", width=feed_box.width * 0.9).next_to(feed_box, UP)
        feed = VGroup(feed_rate_boxes, feed_box, feed_label)
        # Vertical box is virtually the same except the quantity of words ratio
        vertical = feed.copy().to_edge(LEFT)
        vertical_label = Text("Вертикаль", width=vertical[1].width * 0.9).next_to(vertical[1], UP)
        vertical[2] = vertical_label
        # Set the labels height equal
        feed[2].set(height=vertical_label.height).next_to(feed_box, UP)

        # Create "feed" box
        self.play(
            Create(feed_box),
            Write(feed_label),
            FadeOut(expanded_decision_math, self.pi_creature.bubble, self.pi_creature.bubble.content),
            self.pi_creature.animate.change_mode("plain")
        )

        # Transform the words over pi's hands to the feed's bars
        self.play(
            AnimationGroup(
                ReplacementTransform(translit_word, feed_linoleum_rate[8:]),
                ReplacementTransform(original_word, feed_linoleum_rate[:8])
            )
        )

        # Draw the bars
        self.play(DrawBorderThenFill(feed_rate_boxes[0]), DrawBorderThenFill(feed_rate_boxes[1]))
        self.remove(*feed_linoleum_rate)
        # Store the total height in purpose to get the ration of it
        total_feed_height = feed_rate_boxes[0].height + feed_rate_boxes[1].height

        # Original word is 90%  of the feed (90% of original + transliteration)
        # Consequently, transliterated word is 10% of the feed.
        self.play(
            feed_rate_boxes[0].animate.stretch_to_fit_height(height=total_feed_height * 0.9, about_edge=UP),
            feed_rate_boxes[1].animate.stretch_to_fit_height(height=total_feed_height * 0.1, about_edge=DOWN),
        )

        # Similarly, original word is 99% of the vertical, thus transliterated is 1%
        vertical[0][0].stretch_to_fit_height(height=total_feed_height * 0.99, about_edge=UP)
        vertical[0][1].stretch_to_fit_height(height=total_feed_height * 0.01, about_edge=DOWN)

        # Copying from feed to vertical ratio box's representation
        self.play(TransformFromCopy(feed, vertical))

        # Brace the bars, where the height of them is the representation of the number of the words inside
        braces_and_height = [
            (Brace(feed[0][0], LEFT), Integer(feed[0][0].height * 100).scale(0.5)),
            (Brace(feed[0][1], LEFT), Integer(feed[0][1].height * 100).scale(0.5)),
            # Consider that in the vertical the number of words is much higher
            (Brace(vertical[0][0], RIGHT), Integer(vertical[0][0].height * 1000).scale(0.5)),
            (Brace(vertical[0][1], RIGHT), Integer(vertical[0][1].height * 1000).scale(0.5))
        ]

        # Place a number of words on the proper side of a brace
        idx = 0
        for brace, height in braces_and_height:
            if idx < 2:
                direction = LEFT
            else:
                direction = RIGHT
            height.next_to(brace, direction)
            idx += 1
        del idx

        # Show the braces with the number of words
        self.play(
            FadeIn(*[b for b, _ in braces_and_height], *[n for _, n in braces_and_height]),
            self.pi_creature.animate.shift(RIGHT * 3)
        )

        # The scales inside the thoughts
        scales_line = NumberLine(
            x_range=[-1, 1, 0.1],
            length=4,
            include_numbers=False,
            include_ticks=False
        )
        scales_line.set_color_by_gradient((GREEN, RED))
        indicator = Triangle(fill_opacity=1).scale(0.1).rotate(180 * DEGREES).next_to(scales_line, UP)
        scales = VGroup(scales_line, indicator)
        self.think(scales)

        def decision(const, vo, vt, fo, ft, b):
            """Decision equation.
            """
            return const * -0.388 + 0.122 * (vt) / (vo + 1) + (ft) / (fo + 1) * 0.103 - b

        def get_indicator_pos(number: float, _indicator: Mobject, number_line: NumberLine):
            """The scales' indicator position depends on value given by scales.
            """
            pos = _indicator.get_center()
            pos[0] = number_line.number_to_point(number)[0]
            return pos

        # The equation of "linoleum" to "линолеум".
        linoleum_sol = MathTex(
            r"\text{Решение}=",
            r"\text{ да }",
            r"\times \text{ на 38 \%}",
            r"+\text{ в }",
            r"{",
            r"\phantom{12345}",
            r"\over",
            r"\phantom{12345}",
            r"}",
            r"\text{ раз }",
            r"\times \text{на 12 \%}",
            r"+\text{ в }",
            r"{",
            r"\phantom{12345}",
            r"\over",
            r"\phantom{12345}",
            r"}",
            r"\text{ раз }",
            r"\times \text{на 10 \%}",
            r"+ \text{предвзяты на 12\%}"
        ).scale(0.4).next_to(self.module_label, DOWN)

        # Store numerators and denominators
        numerators = [
            braces_and_height[3][1].copy().next_to(linoleum_sol[6], UP, buff=0.1),  # vertical
            braces_and_height[1][1].copy().next_to(linoleum_sol[14], UP, buff=0.1)  # feed
        ]
        denominators = [
            braces_and_height[2][1].copy().next_to(linoleum_sol[6], DOWN, buff=0.1),
            braces_and_height[0][1].copy().next_to(linoleum_sol[14], DOWN, buff=0.1)
        ]

        # Extracting the parts of equation into the variables
        overs = [linoleum_sol[6], linoleum_sol[14]]
        confidences = [linoleum_sol[2], linoleum_sol[10], linoleum_sol[18]]
        times_word = [linoleum_sol[9], linoleum_sol[17]]
        in_word = [linoleum_sol[3], linoleum_sol[11]]

        questions = [Text(q).scale(0.3).next_to(self.pi_creature.bubble, UP)
                     for q in ["Существует ли ориг. слово?",
                               "На сколько мы в этом уверены?",
                               "Во сколько раз транслитирации больше, чем ориг. слова в вертикали?",
                               "На сколько мы уверены, что больше?",
                               "Во сколько раз транслитирации больше, чем ориг. слова в фиде?",
                               "На сколько мы уверены, что больше?"]
                     ]

        questions_copy = list(map(lambda q: q.copy(), questions))

        self.play(
            FadeIn(questions[0]),
        )
        self.wait()
        self.play(FadeIn(linoleum_sol[:2]))
        self.wait()
        self.play(ReplacementTransform(questions[0], questions[1]))
        self.wait()
        self.play(
            FadeIn(confidences[0]),
            indicator.animate.move_to(get_indicator_pos(decision(1, 0, 0, 0, 0, 0), indicator, scales_line))
        )
        self.wait()
        self.play(ReplacementTransform(questions[1], questions[2]))
        self.wait()
        self.play(
            FadeIn(in_word[0]),
            Create(overs[0])
        )
        self.play(ReplacementTransform(braces_and_height[3][1], numerators[0]))
        self.play(ReplacementTransform(braces_and_height[2][1], denominators[0]), FadeIn(times_word[0]))
        self.wait()
        self.play(ReplacementTransform(questions[2], questions[3]))
        self.wait()
        self.play(
            FadeIn(confidences[1]),
            indicator.animate.move_to(get_indicator_pos(decision(1, 4487, 45, 0, 0, 0), indicator, scales_line))
        )
        self.play(ReplacementTransform(questions[3], questions[4]))
        self.wait()
        self.play(
            FadeIn(in_word[1]),
            Create(overs[1])
        )
        self.play(ReplacementTransform(braces_and_height[1][1], numerators[1]))
        self.play(ReplacementTransform(braces_and_height[0][1], denominators[1]), FadeIn(times_word[1]))
        self.wait()
        self.play(ReplacementTransform(questions[4], questions[5]))
        self.wait()
        self.play(
            FadeIn(confidences[2]),
            indicator.animate.move_to(get_indicator_pos(decision(1, 4487, 45, 408, 45, 0), indicator, scales_line))
        )
        self.wait()

        def vertical_num_updater(num):
            num.set_value(vertical[0][1].height * 1000)
            num.next_to(linoleum_sol[6], UP, buff=0.1)

        def feed_num_updater(num):
            num.set_value(feed[0][1].height * 100)
            num.next_to(linoleum_sol[14], UP, buff=0.1)

        def vertical_denom_updater(num):
            num.set_value(vertical[0][0].height * 1000)
            num.next_to(linoleum_sol[6], DOWN, buff=0.1)

        def feed_denom_updater(num):
            num.set_value(feed[0][0].height * 100)
            num.next_to(linoleum_sol[14], DOWN, buff=0.1)

        numerators[0].add_updater(vertical_num_updater)
        numerators[1].add_updater(feed_num_updater)
        denominators[0].add_updater(vertical_denom_updater)
        denominators[1].add_updater(feed_denom_updater)

        def vertical_lower_brace_updater(b):
            new_brace = Brace(vertical[0][1], RIGHT)
            b.match_points(new_brace)

        def feed_lower_brace_updater(b):
            new_brace = Brace(feed[0][1], LEFT)
            b.match_points(new_brace)

        def vertical_upper_brace_updater(b):
            new_brace = Brace(vertical[0][0], RIGHT)
            b.match_points(new_brace)

        def feed_upper_brace_updater(b):
            new_brace = Brace(feed[0][0], LEFT)
            b.match_points(new_brace)

        braces_and_height[0][0].add_updater(feed_upper_brace_updater)
        braces_and_height[1][0].add_updater(feed_lower_brace_updater)
        braces_and_height[2][0].add_updater(vertical_upper_brace_updater)
        braces_and_height[3][0].add_updater(vertical_lower_brace_updater)

        def indicator_updater(ind):
            ind.move_to(
                get_indicator_pos(
                    decision(
                        1,
                        int(vertical[0][0].height * 1000),
                        int(vertical[0][1].height * 1000),
                        int(feed[0][0].height * 100),
                        int(feed[0][1].height * 100),
                        0
                    ),
                    indicator,
                    scales_line
                )
            )

        indicator.add_updater(indicator_updater)

        self.play(
            FadeOut(questions[-1]),
            feed[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.7, about_edge=UP),
            feed[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.3, about_edge=DOWN),
            vertical[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.97, about_edge=UP),
            vertical[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.03, about_edge=DOWN)
        )
        self.wait()

        self.play(
            feed[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.1, about_edge=UP),
            feed[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.9, about_edge=DOWN),
            vertical[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.91, about_edge=UP),
            vertical[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.09, about_edge=DOWN)
        )
        self.wait()

        to_much = Text("Всё равно достаточно много", color=RED).scale(0.5).next_to(self.pi_creature.bubble, UP)
        arrow = Arrow(to_much, braces_and_height[2][0].get_center(), color=RED)
        self.play(FadeIn(to_much, arrow))
        self.wait(2)

        new_arrow = Arrow(to_much, linoleum_sol[-1].get_center(), color=RED)
        self.play(
            FadeIn(linoleum_sol[-1]),
            arrow.animate.become(new_arrow),
            indicator.animate.move_to(
                get_indicator_pos(
                    decision(
                        1,
                        int(vertical[0][0].height * 1000),
                        int(vertical[0][1].height * 1000),
                        int(feed[0][0].height * 100),
                        int(feed[0][1].height * 100),
                        0.123
                    ),
                    indicator,
                    scales_line
                )
            )
        )
        self.wait()

        self.play(FadeOut(to_much, arrow))
        self.wait()

        self.play(
            feed[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.5, about_edge=UP),
            feed[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.5, about_edge=DOWN),
            vertical[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.95, about_edge=UP),
            vertical[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.05, about_edge=DOWN)
        )
        self.wait()

        self.play(
            vertical[0][0].animate.stretch_to_fit_height(height=total_feed_height * 0.2, about_edge=UP),
            vertical[0][1].animate.stretch_to_fit_height(height=total_feed_height * 0.8, about_edge=DOWN)
        )
        self.wait()

        self.play(
            FadeOut(
                feed,
                vertical,
                *[b[0] for b in braces_and_height],
                self.pi_creature.bubble,
                self.pi_creature.bubble.content,
                self.pi_creature,
                linoleum_sol,
                *numerators,
                *denominators
            )
        )
        self.questions = VGroup(*questions_copy).arrange(DOWN)
        q_box = SurroundingRectangle(self.questions, color=WHITE)
        self.questions = VGroup(self.questions, q_box)

    def decision_formalization(self):
        formal_eq = MathTex(
            r"D(", r"\text{ориг}", ",", r"\text{транс}", ")", "=",
            r"\{", "1", ",", "0", r"\ |\ ", r"\text{ориг. слово существует}", r"\}", r"\times -0.38", "+",
            "{", r"\text{количество транс. в вертикали}", r"\over", r"\text{количество ориг. в вертикали}", "}",
            r"\times 0.12", "+",
            "{", r"\text{количество транс. в фиде}", r"\over", r"\text{количество ориг. в фиде}", "}",
            r"\times 0.10", "-", "0.12",
            tex_to_color_map={
                r"\text{ориг}": RED,
                r"\text{транс}": GREEN,
                r"\text{количество транс. в вертикали}": GREEN,
                r"\text{количество ориг. в вертикали}": RED,
                r"\text{количество транс. в фиде}": GREEN,
                r"\text{количество ориг. в фиде}": RED
            }
        ).scale(0.4)
        formal_equation_parts = {
            'D': formal_eq[:6],
            'indicator': formal_eq[6:13],
            'numerators': [formal_eq[15:17], formal_eq[22:24]],
            'denominators': [formal_eq[18:20], formal_eq[25:27]],
            'overs': [formal_eq[17], formal_eq[24]],
            'confidences': [formal_eq[13:15], formal_eq[20:22], formal_eq[27]],
            'bayes': formal_eq[-2:]
        }
        formal_equation_parts['indicator'][1].set_color(RED)
        formal_equation_parts['indicator'][3].set_color(GREEN)

        self.play(FadeIn(self.questions.next_to(self.module_label, DOWN)))

        question_boxes = [SurroundingRectangle(q, color=YELLOW) for q in self.questions[0]]
        self.play(Write(formal_equation_parts['D']))

        self.play(Create(question_boxes[0]))
        self.wait()
        self.play(Write(formal_equation_parts['indicator']))

        self.wait()
        self.play(
            Indicate(formal_equation_parts['indicator'][1], color=RED),
            Indicate(formal_equation_parts['indicator'][-2], color=RED),
        )
        self.wait()
        self.play(Indicate(formal_equation_parts['indicator'][3], color=GREEN))
        self.wait()

        self.play(ReplacementTransform(question_boxes[0], question_boxes[1]))
        self.wait()
        self.play(Write(formal_equation_parts['confidences'][0]))

        self.play(ReplacementTransform(question_boxes[1], question_boxes[2]))
        self.wait()
        self.play(
            FadeIn(
                formal_equation_parts['numerators'][0],
                formal_equation_parts['overs'][0],
                formal_equation_parts['denominators'][0]
            ),
        )

        self.play(ReplacementTransform(question_boxes[2], question_boxes[3]))
        self.wait()
        self.play(Write(formal_equation_parts['confidences'][1]))

        self.play(ReplacementTransform(question_boxes[3], question_boxes[4]))
        self.wait()
        self.play(
            FadeIn(
                formal_equation_parts['numerators'][1],
                formal_equation_parts['overs'][1],
                formal_equation_parts['denominators'][1]
            ),
        )

        self.play(ReplacementTransform(question_boxes[4], question_boxes[5]))
        self.wait()
        self.play(Write(formal_equation_parts['confidences'][2]))

        self.play(
            Uncreate(question_boxes[-1]),
            Write(formal_equation_parts['bayes'])
        )

        self.wait()
        self.play(FadeOut(self.questions))

        equation_box = SurroundingRectangle(formal_eq, buff=0.5)
        self.play(ShowPassingFlash(equation_box.copy().set_color(BLUE), run_time=2, time_width=0.5))
        self.wait()

        brand_list = self.vertical_brands_list.copy().scale(0.4).next_to(formal_equation_parts['D'][:-1], RIGHT)
        trans_exists = VGroup(brand_list, formal_equation_parts['D'][:-1])
        trans_exists_box = SurroundingRectangle(trans_exists, color=WHITE)
        trans_exists_label = Text(
            "Транслитирация существует",
            width=0.9*trans_exists_box.width
        ).next_to(trans_exists_box, UP)
        trans_exists_stuff = VGroup(trans_exists, trans_exists_box, trans_exists_label)
        self.play(
            FadeIn(brand_list),
            FadeOut(*[p for p in formal_eq if p not in trans_exists[1]])
        )
        self.play(Create(trans_exists_box), Write(trans_exists_label))

        self.wait()

        self.pi_creature.to_corner(DR)
        self.think("А что если транслитерация не заведена?")


    #
    # def math_decision_equation(self):
    #     """The decision equation written in math
    #     """
    #     equation = self.linoleum_equation
    #
    #     if any([len(self.numerators) != 2, len(self.denominators) != 2]):
    #         raise Exception("Call the linoleum_decomposition first.")
    #
    #     def write_feed_to_vertical_eq(vert_data: Integer, feed_data: Integer, eq):
    #         vert_data.clear_updaters()
    #         feed_data.clear_updaters()
    #         self.play(Write(eq[0]))
    #         self.play(ReplacementTransform(vert_data, eq[1]))
    #         self.play(Write(eq[2]), ReplacementTransform(feed_data, eq[5]))
    #         self.wait()
    #         self.play(FadeIn(eq[3:5]))
    #
    #     numerator_eq = Tex(
    #         "Кол-во linoleum в вертикали = ",
    #         f"3,626",
    #         " = ",
    #         f"15.97",
    #         r" $\times$ ",
    #         f"227"
    #     ).scale(0.4).to_edge(LEFT)
    #     write_feed_to_vertical_eq(self.numerators[0], self.numerators[1], numerator_eq)
    #
    #     denominator_eq = Tex(
    #         "Кол-во линолеум в вертикали = ",
    #         f"907",
    #         " = ",
    #         f"3.99",
    #         r" $\times$ ",
    #         f"227"
    #     ).scale(0.4).next_to(numerator_eq, DOWN).to_edge(LEFT)
    #     write_feed_to_vertical_eq(self.denominators[0], self.denominators[1], denominator_eq)
    #
    #     wider_equation = MathTex(
    #         *[e.get_tex_string() for e in equation[:4]],
    #         r"{",
    #         r"\phantom{12345567891011}",
    #         r"\over",
    #         r"\phantom{1234556789101}",
    #         r"}",
    #         *[e.get_tex_string() for e in equation[9:]],
    #     ).scale(0.4).move_to(equation)
    #
    #     num_denom_copies = [
    #         numerator_eq[5].copy(),
    #         denominator_eq[5].copy(),
    #         numerator_eq[3:6].copy(),
    #         denominator_eq[3:6].copy()
    #     ]
    #     self.play(
    #         AnimationGroup(
    #             ReplacementTransform(equation, wider_equation),
    #             num_denom_copies[0].animate.next_to(wider_equation[14], UP, buff=0.1),
    #             num_denom_copies[1].animate.next_to(wider_equation[14], DOWN, buff=0.1),
    #             num_denom_copies[2].animate.next_to(wider_equation[6], UP, buff=0.1),
    #             num_denom_copies[3].animate.next_to(wider_equation[6], DOWN, buff=0.1),
    #             FadeOut(numerator_eq, denominator_eq)
    #         )
    #     )
    #
    #     math_eq = MathTex(
    #         r"D(", "N", ",", "M", ",", "a, b)",
    #         "=", r"\{1, 0\ |\ ", "N", r"> 0\}", r"\times -0.38",
    #         r"+ {b \times ", "M", r"\over a \times", "N", "}", r"\times 0.12",
    #         r"+ {", "M", r"\over", "N", "}", r"\times 0.1", "- 0.12",
    #         substrings_to_isolate=[r"N", r"M"]
    #     ).scale(0.4)
    #     math_eq_parts = {
    #         'left_part': math_eq[:7],
    #         'indicator': math_eq[7:10],
    #         'confidences': [math_eq[10], math_eq[16], math_eq[22]],
    #         'ratios': [math_eq[11:16], math_eq[17:22]],
    #         'bayes': math_eq[23]
    #
    #     }
    #
    #     math_eq.set_color_by_tex_to_color_map({
    #         r"N": RED,
    #         r"M": GREEN
    #     })
    #
    #     N_label = Tex(
    #         "$N$ - Кол-во оригинального слова в фиде",
    #         color=RED
    #     ).scale(0.4).next_to(math_eq[1], DOWN * 4)
    #     M_label = Tex(
    #         "$M$ - Кол-во транслитирированного слова в фиде",
    #         color=GREEN
    #     ).scale(0.4).next_to(N_label, DOWN)
    #
    #     self.play(FadeIn(math_eq_parts['left_part'], N_label, M_label))
    #     self.play(FadeIn(math_eq_parts['indicator']))
    #     self.play(FadeIn(math_eq_parts['confidences'][0]))
    #     self.play(FadeIn(math_eq_parts['ratios'][0]))
    #     self.play(FadeIn(math_eq_parts['confidences'][1]))
    #     self.play(FadeIn(math_eq_parts['ratios'][1]))
    #     self.play(FadeIn(math_eq_parts['confidences'][2]))
    #     self.play(FadeIn(math_eq_parts['bayes']))
    #
    #     indicator_label = Text("Индикатор", color=YELLOW).next_to(math_eq_parts['indicator'], UP*2.5)
    #     indicator_arrow = Arrow(indicator_label.get_center(), math_eq_parts['indicator'].get_center(), color=YELLOW)
    #     self.play(FadeIn(indicator_label, indicator_arrow))
    #     self.wait(2)
    #
    #     self.play(
    #         FadeOut(wider_equation, M_label, N_label, indicator_label, indicator_arrow, *num_denom_copies),
    #         math_eq.animate.next_to(self.module_label, DOWN)
    #     )
    #
    #     self.math_equation_stuff['equation'] = math_eq
    #     self.math_equation_stuff['parts'] = math_eq_parts
    #
    # def model_surface(self):
    #     resolution_fa = 70
    #     self.set_camera_orientation(zoom=0.5)
    #
    #     b_label = MathTex("b=")
    #     a_label = MathTex("a=")
    #     surface_display_data = VGroup(*[
    #         VGroup(b_label, DecimalNumber(1.0, num_decimal_places=2)).arrange(RIGHT),
    #         VGroup(a_label, DecimalNumber(10.99, num_decimal_places=2)).arrange(RIGHT)
    #     ]).arrange(DOWN).scale(0.4).to_edge(RIGHT)
    #
    #     self.add_fixed_in_frame_mobjects(
    #         self.math_equation_stuff['equation'],
    #         self.module_label
    #     )
    #
    #     def decision(feed_original, feed_trans, orig_factor, trans_factor):
    #         """Decision equation.
    #         """
    #         x = feed_original
    #         y = feed_trans
    #         z = -0.388 * 1 + 0.122 * (y * trans_factor + 1) / (x * orig_factor + 1) + (y + 1) / (x + 1) * 0.103 - 0.123
    #         return z
    #
    #     axes = ThreeDAxes(x_range=[0, 10, 1], y_range=[0, 10, 1], z_range=[0, 10, 1], tips=False)
    #     labels = axes.get_axis_labels3D(
    #         r"\text{кол-во ориг. в фиде }(N)",
    #         r"\text{кол-во транс. в фиде }(M)",
    #         r"\text{Решение }(D)"
    #     )
    #     labels[0].next_to(axes[0], DOWN*2)
    #     labels[1].next_to(axes[1], UL)
    #     labels[2].next_to(axes[2], UL)
    #
    #     def color_surface(sur):
    #         for tile in sur:
    #             dec = axes.c2p(*tile.get_center())[-1]
    #             if dec > 0:
    #                 tile.set_color(GREEN)
    #             else:
    #                 tile.set_color(RED)
    #
    #     self.play(Create(axes[:2]), Write(labels[:2]))
    #     self.wait()
    #     self.move_camera(phi=75 * DEGREES, theta=-75 * DEGREES, run_time=3)
    #     self.play(Create(axes[-1]), Write(labels[-1]))
    #     self.play(FadeIn(surface_display_data))
    #     self.add_fixed_in_frame_mobjects(surface_display_data)
    #     self.wait()
    #
    #     surfaces = VGroup(*[
    #         Surface(
    #             lambda u, v: axes.c2p(u, v, decision(u, v, 10.99, 1)),
    #             u_range=[0, 10],
    #             v_range=[0, 10],
    #             resolution=(resolution_fa, resolution_fa)
    #         ),
    #         Surface(
    #             lambda u, v: axes.c2p(u, v, decision(u, v, 11.48, 8.48)),
    #             u_range=[0, 10],
    #             v_range=[0, 10],
    #             resolution=(resolution_fa, resolution_fa)
    #         ),
    #         Surface(
    #             lambda u, v: axes.c2p(u, v, decision(u, v, 3.99, 15.97)),
    #             u_range=[0, 10],
    #             v_range=[0, 10],
    #             resolution=(resolution_fa, resolution_fa)
    #         )
    #     ])
    #     for surface in surfaces:
    #         color_surface(surface)
    #         surface.set_fill(opacity=0.8)
    #         surface.set_stroke(width=0)
    #
    #     graph_stuff = VGroup(axes, labels, surfaces).shift(DOWN*4 + 3*RIGHT)
    #     self.play(Create(surfaces[0]))
    #     self.wait(3)
    #     self.play(
    #         # ReplacementTransform(surfaces[0], surfaces[1]),
    #         ChangeDecimalToValue(surface_display_data[0][1], 8.48),
    #         ChangeDecimalToValue(surface_display_data[1][1], 11.48)
    #     )
    #     self.wait(3)
    #     self.play(
    #         # ReplacementTransform(surfaces[1], surfaces[2]),
    #         ChangeDecimalToValue(surface_display_data[0][1], 15.97),
    #         ChangeDecimalToValue(surface_display_data[1][1], 3.99)
    #     )
    #     self.wait(3)
    #
    #     dot = Dot3D()
