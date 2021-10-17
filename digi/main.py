from manim import *
import itertools as it
from typing import Tuple, List, Union
from custom.characters.pi_creature import PiCreature
from custom.characters.pi_creature_scene import PiCreatureScene, CustomersScene
from custom.drawings import VideoSeries, Tree, Sigmoid, Clusters, NotebookWithNotes, Lock, Cross, Check
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
        # 2. P(white) - 0.78
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
    pi_customer = PiCreature(mode="angry")

    def construct(self):
        self.typo_query_probas_scene()

    def typo_query_probas_scene(self):
        query = VGroup(*[Text(word) for word in ["iPhone", ",tksq"]]).arrange(RIGHT).to_edge(UP)
        self.play(AddTextWordByWord(query))
        probas_query = MathTex(r"P(\text{query}) = ", r"P(\text{iPhone})", r"\times P(\text{,tksq})",
                               r" = 0.99 \times", "?", "= 0")
        self.play(FadeIn(probas_query[0]))
        self.play(TransformMatchingShapes(query[0].copy(), probas_query[1]))
        self.play(TransformMatchingShapes(query[1].copy(), probas_query[2]))
        self.play(FadeIn(probas_query[-3:-1]))
        self.wait()
        self.play(Transform(probas_query[-2], MathTex("0").move_to(probas_query[-2].get_center())))
        self.play(FadeIn(probas_query[-1]))
        self.play(probas_query.animate.next_to(query, DOWN, buff=MED_SMALL_BUFF))

        self.angry_customer_scene()

        query_wrong_word = query[1]
        probas_query_wrong_word = probas_query[2]
        query_correct_word = Text("белый").next_to(query[0]).set_color(YELLOW)
        probas_query_correct_word = MathTex(r"\times P(\text{белый})", tex_to_color_map={r'\text{белый}': YELLOW})
        probas_query_correct_word.move_to(probas_query_wrong_word.get_center())
        correct_proba = MathTex("0.78").next_to(probas_query[-3], buff=SMALL_BUFF).set_color(YELLOW)
        new_ans = MathTex("= 0.772", tex_to_color_map={'0.772': YELLOW}).next_to(correct_proba, buff=SMALL_BUFF)
        self.play(
            AnimationGroup(
                Transform(query_wrong_word, query_correct_word),
                TransformMatchingShapes(probas_query_wrong_word, probas_query_correct_word),
                Transform(probas_query[-2], correct_proba),
                TransformMatchingShapes(probas_query[-1], new_ans)
            )
        )

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


class VimpryamitelBlackBoxScene(CustomersScene):
    black_box = None
    box_label = None
    black_box_group = None
    wrong_queries = [Text(query).set_color(RED) for query in ["айфон белый", "iphone ,tksq",
                                                              "iphone блый", "iphoneблый"]]
    correct_queries = [Text(correction).set_color(GREEN) for correction in ["iphone белый"] * 4]

    def construct(self) -> None:
        self.draw_blackbox()
        self.change_all_customers_modes("raise_right_hand", lag_ratio=0)
        self.get_wrong_queries()
        self.pass_queries_to_spellchecker_and_fix_it()
        self.change_all_customers_modes("plain", look_at_arg=self.black_box.get_center(), lag_ratio=0)
        self.change_all_customers_modes("hooray", lag_ratio=0)
        self.zoom_in_on_black_box()

    def draw_blackbox(self):
        if self.black_box is not None:
            raise Exception("Box is already created")
        self.black_box = Rectangle(width=config.frame_width/2, height=config.frame_height-2,
                                   fill_opacity=1, fill_color=BLACK)
        self.box_label = Text("Spellchecker").move_to(self.black_box.get_center())
        self.black_box_group = VGroup(self.black_box, self.box_label)
        self.black_box_group.to_edge(RIGHT)
        self.add_foreground_mobject(self.black_box_group)
        self.play(
            AnimationGroup(
                Create(self.black_box),
                FadeIn(self.box_label),
                lag_ratio=0.5
            )
        )

    def get_wrong_queries(self):
        customers = self.get_customers()
        if not all(list(map(lambda c: c.mode == "raise_right_hand", customers))):
            raise Exception("Customers have to raise hand")
        for idx, customer in enumerate(customers):
            self.wrong_queries[idx].scale(0.4).next_to(customer, UR)

        self.play(FadeIn(*[query for query in self.wrong_queries]))

    def pass_queries_to_spellchecker_and_fix_it(self):
        anims_wrong = [query.animate.move_to(self.black_box.get_center()) for query in self.wrong_queries] + \
                [customer.animate.look_at(self.black_box.get_center()) for customer in self.customers]

        for query in self.correct_queries:
            query.scale(0.4).move_to(self.black_box.get_center())
        anims_correct = [q.animate.next_to(c, UR) for q, c in zip(self.correct_queries, self.get_customers())]

        for wrong_animation, correct_animation in zip(anims_wrong, anims_correct):
            self.play(wrong_animation)
            self.play(correct_animation)

    def zoom_in_on_black_box(self, radius=config.frame_width/2 + config.frame_height/2):
        # Zoom a little bit higher than "Spellchecker" label
        vect = -self.black_box.get_center() + [0, -1, 0]

        self.play(*[
            ApplyPointwiseFunction(lambda point: (point + vect) * radius, mob)
            for mob in self.mobjects
        ])


class VipryamitelFunnel(Scene):
    modules_names = VGroup(*[Text(label) for label in ["Query",
                                                       "Replace similar symbols",
                                                       "Replace brands",
                                                       "Fix layout",
                                                       "Handle punctuation",
                                                       "Fix spaces",
                                                       "Typo fixing",
                                                       "Replace brands"]])
    default_level_props = {'width': 4.0, 'height': 0.5}
    levels = VGroup(*[Rectangle(width=4.0, height=0.5) for _ in range(8)]).arrange(DOWN, buff=0)
    query_at_level = [Text(query).set(height=0.3) for query in ["Лосситан дхи ,en ghjdbyc длянего",
                                                                "l'occitane дхи ,en ghjdbyc длянего",
                                                                "l'occitane дхи ,en ghjdbyc длянего",
                                                                "l'occitane дхи ,en провинс длянего",
                                                                "l'occitane дхи, en провинс длянего",
                                                                "l'occitane дхи, en провинс для него",
                                                                "l'occitane духи, en прованс для него",
                                                                "l'occitane духи, en provence для него"]]
    rgbas = color_gradient((RED_E, GREEN_E), 8)
    probas_at_level = {
        'typo_probas': [p for p in np.linspace(1, 0, 8)],
        'resp_probas': [p for p in np.linspace(0, 1, 8)]
    }
    probas_label = [MathTex(r"P(\text{ошибки в запросе}) = ", color=RED),
                    MathTex(r"P(\text{что-то найти по запросу}) = ", color=RED)]
    probas = None
    text_height = 0.3

    def construct(self):
        self.show_levels_scene()
        self.query_probas_scene()
        self.show_kostyl()

    def _get_level_rect(self, level: int):
        if level == 0:
            return self.levels[0]
        elif self.levels[level].width < self.levels[level - 1].width:
            return self.levels[level]
        else:
            return self.levels[level].stretch_to_fit_width(width=self.levels[level-1].width*(1 - level/10))

    def show_levels_scene(self):
        for idx in range(len(self.levels)):
            level = self._get_level_rect(idx)
            level.set_color(self.rgbas[idx]).set_fill(color=self.rgbas[idx], opacity=1)
            self.modules_names[idx].set(height=self.text_height).next_to(level, LEFT).to_edge(LEFT)
            self.modules_names[idx].set_color(self.rgbas[idx])
            self.play(FadeIn(level, self.modules_names[idx]))

    def query_probas_scene(self):
        if self.probas is not None:
            raise ValueError("self.probas already created")
        res_probas = []
        probas_nums = [self.probas_at_level[p_type][0] for p_type in self.probas_at_level]
        for num, label in zip(probas_nums, self.probas_label):
            decimal_num = DecimalNumber(num, num_decimal_places=2)
            res_probas.append(VGroup(label, decimal_num).arrange(RIGHT).set(height=self.text_height))
        self.probas = VGroup(*res_probas).set_color(RED).arrange(RIGHT, buff=LARGE_BUFF).to_edge(UP)

        for idx, query in enumerate(self.query_at_level):
            query.next_to(self.levels[idx], RIGHT).to_edge(RIGHT/5)
            query.set_color(self.rgbas[idx])
        self.query_at_level[0].set_color(RED)
        self.play(FadeIn(self.query_at_level[0], self.probas))
        self.wait()

        self.play(Circumscribe(self.probas[0], fade_out=True))
        self.play(Circumscribe(self.probas[1], fade_out=True))
        self.wait()
        curr_query = self.query_at_level[0]
        typo_proba_box = SurroundingRectangle(self.probas[0][-1], buff=SMALL_BUFF)
        resp_proba_box = SurroundingRectangle(self.probas[1][-1], buff=SMALL_BUFF)
        self.play(
            AnimationGroup(
                Create(typo_proba_box),
                Create(resp_proba_box)
            )
        )
        for query, typo_proba, resp_proba, p_color in zip(self.query_at_level[1:],
                                                          self.probas_at_level['typo_probas'][1:],
                                                          self.probas_at_level['resp_probas'][1:],
                                                          self.rgbas[1:]):
            self.probas.set_color(p_color)
            self.play(
                AnimationGroup(
                    ReplacementTransform(curr_query, query),
                    ChangeDecimalToValue(self.probas[0][-1], typo_proba),
                    ChangeDecimalToValue(self.probas[1][-1], resp_proba),
                )
            )
            curr_query = query
            self.wait()
        self.play(FadeOut(typo_proba_box, resp_proba_box, self.probas, self.query_at_level[-1]))

    def show_kostyl(self):
        spread_levels = self.levels.copy()
        spread_levels.arrange(DOWN, buff=MED_SMALL_BUFF)
        kostyl = []
        for level in spread_levels[:-1]:
            kostyl.append(Line(color=YELLOW).next_to(level, DOWN, buff=MED_SMALL_BUFF/2))
            kostyl[-1].set(width=level.width)
        kostyl = VGroup(*kostyl)

        spread_names_anims = []
        for idx, name in enumerate(self.modules_names):
            spread_names_anims.append(name.animate.next_to(spread_levels[idx], LEFT).to_edge(LEFT))

        self.play(
            AnimationGroup(
                Transform(self.levels, spread_levels),
                *spread_names_anims
            )
        )
        self.play(FadeIn(kostyl))

        self.play(*list(map(lambda instance: Wiggle(instance), kostyl)))
        kostyl_label = Text("Kostyl", color=YELLOW).to_edge(UP/2)
        self.play(ReplacementTransform(kostyl, kostyl_label))
        self.play(FadeOut(*[obj for obj in self.mobjects if obj != kostyl_label]))
        self.wait()


class KostylScene(MovingCameraScene):
    def __init__(self):
        super(KostylScene, self).__init__()
        self.kostyl_label = Text("Kostyl", color=YELLOW).to_edge(UP / 2)
        self.modules_names = VipryamitelFunnel.modules_names
        self.default_level_props = VipryamitelFunnel.default_level_props
        self.levels = VipryamitelFunnel.levels.arrange(DOWN, buff=MED_SMALL_BUFF)
        self.rgbas = VipryamitelFunnel.rgbas

    def construct(self):
        self.add(self.kostyl_label)
        self.example()
        self.black_white_lists()
        self.bigrams()
        self.kostyl_summarization()

    def example(self):
        query = Text("Chanel ультра ле теинт тональный флюид")
        first_subquery = query[:6]
        second_subquery = query[6:19]
        third_subquery = query[19:]
        first_box = SurroundingRectangle(first_subquery, color=WHITE)
        second_box = SurroundingRectangle(third_subquery, color=WHITE)
        first_lock = Lock().next_to(first_box, UP).scale(0.6)
        second_lock = Lock().next_to(second_box, UP).scale(0.6)

        self.play(Write(query))
        self.play(Create(first_box))
        self.play(FadeIn(first_lock))
        self.play(Create(second_box))
        self.play(FadeIn(second_lock))
        self.play(*list(map(lambda subquery: subquery.animate.set_color(GREEN), [first_subquery, third_subquery])))
        self.play(ApplyWave(query))
        self.play(Indicate(second_subquery, color=RED))
        self.wait()
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.kostyl_label]))

    def black_white_lists(self):
        base_query = Text("парфюм essencial набор").scale(0.5).to_edge(LEFT + UP*2.8)
        words = VGroup(*[base_query[:6], base_query[6:15], base_query[15:]])
        self.play(Write(base_query))
        every_word_boxes = [SurroundingRectangle(word) for word in words]
        boxes_by_two_words = [SurroundingRectangle(words[:2]), SurroundingRectangle(words[1:])]
        entire_query_box = SurroundingRectangle(base_query)
        table = MobjectTable(
            [[words[0].copy(),   Cross(), Check(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[:2].copy(),  Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [base_query.copy(), Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[1].copy(),   Check(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[1:].copy(),  Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()],
             [words[2].copy(),   Cross(), Cross(), Text("ESSENTIAL PARFUMS PARIS"), Lock()]],
            row_labels=[],
            col_labels=[NotebookWithNotes(color=GREEN), NotebookWithNotes(color=RED), Text("Трансформация"), Lock()],
            include_outer_lines=True
        )
        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx % 5 == 0:
                entry.scale(1.3)
            self.remove(entry)
        table.scale(0.4).next_to(base_query, DOWN).to_edge(LEFT)
        self.play(Create(table.get_vertical_lines()))
        self.play(Create(table.get_horizontal_lines()))
        self.play(FadeIn(table.get_col_labels(), run_time=2))
        self.wait()
        boxes_anims = [
            Create(every_word_boxes[0]),
            ReplacementTransform(every_word_boxes[0], boxes_by_two_words[0]),
            ReplacementTransform(boxes_by_two_words[0], entire_query_box),
            ReplacementTransform(entire_query_box, every_word_boxes[1]),
            ReplacementTransform(every_word_boxes[1], boxes_by_two_words[1]),
            ReplacementTransform(boxes_by_two_words[1], every_word_boxes[2])
        ]
        blocked_indices = []
        for idx in range(len(table.get_entries_without_labels())):
            if (idx % 5 == 3 and idx != 18) or (idx % 5 == 4 and idx != 4 and idx != 19):
                blocked_indices.append(idx)

        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx not in blocked_indices:
                if idx % 5 == 0:
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
                    self.wait()

        self.wait()

        self.play(Uncreate(every_word_boxes[-1]))

        result_query = Text("парфюм ESSENTIAL PARFUMS PARIS набор").set(height=base_query.height)
        result_query.next_to(base_query, RIGHT*5)
        blocked_part = result_query[:27]
        changable_part = result_query[27:]
        block_box = SurroundingRectangle(blocked_part, color=WHITE, buff=SMALL_BUFF)
        lock = table.get_entries((1, 5))
        arrow = Arrow(start=base_query, end=result_query, color=WHITE)
        self.play(TransformFromCopy(base_query.copy(), result_query))
        self.play(FadeIn(arrow))
        self.play(Create(block_box))
        self.play(lock.copy().animate.next_to(block_box, UP))
        self.play(
            AnimationGroup(
                blocked_part.animate.set_color(GREEN),
                changable_part.animate.set_color(RED)
            )
        )
        self.wait()
        fs_blinder = FullScreenRectangle(color=BLACK, fill_opacity=0.85)
        highlighted_row = [table.get_entries_without_labels((2, idx)) for idx in range(2, 4)]
        checks = [Check().set(height=cross.height).move_to(cross) for cross in highlighted_row]
        cells = [table.get_cell((3, 2)), table.get_cell((3, 3))]
        corners = {
            'UL': cells[0].get_boundary_point(UL),
            'DR': cells[1].get_boundary_point(DR),
            'UR': cells[1].get_boundary_point(UR),
            'DL': cells[0].get_boundary_point(DL)
        }
        lines = [Line(corners['UL'], corners['DR'], color=RED), Line(corners['UR'], corners['DL'], color=RED)]
        self.add_foreground_mobjects(*highlighted_row)
        self.play(FadeIn(fs_blinder))
        self.play(
            AnimationGroup(
                ReplacementTransform(highlighted_row[0], checks[0]),
                ReplacementTransform(highlighted_row[1], checks[1])
            )
        )
        self.wait()
        self.play(
            AnimationGroup(
                Create(lines[0]),
                Create(lines[1]),
                lag_ratio=0.8
            )
        )
        self.wait()
        pi_creature = PiCreature("plain", flip_at_start=True).scale(0.7).to_corner(DR)
        self.play(
            PiCreatureSays(pi_creature, Text("Такого не может быть!", color=RED).scale(0.7), target_mode="speaking")
        )
        self.wait()
        self.play(FadeOut(*[pi_creature.bubble, pi_creature.bubble.content, *lines]))
        replacement_cross = Cross().set(height=checks[1].height).move_to(checks[1])
        self.play(ReplacementTransform(checks[1], replacement_cross))
        self.play(pi_creature.animate.change_mode("hooray"))
        self.wait()
        self.play(FadeOut(*[mobject for mobject in self.mobjects if mobject != self.kostyl_label]))
        self.wait()

    def bigrams(self):
        base_query = Text("крем для лица ла мер").scale(0.5).to_edge(LEFT + UP*2.8)
        words = VGroup(*[base_query[:4], base_query[4:7], base_query[7:11], base_query[11:13], base_query[13:]])
        boxes = [SurroundingRectangle(words[idx: idx + 2]) for idx in range(len(words) - 1)]
        self.play(AddTextLetterByLetter(base_query))
        table = MobjectTable(
            [[words[0:2].copy(), Check(), Lock()],
             [words[1:3].copy(), Check(), Lock()],
             [words[2:4].copy(), Cross(), Lock()],
             [words[3:].copy(),  Cross(), Lock()]],
            row_labels=[],
            col_labels=[NotebookWithNotes(color=BLUE), Lock()],
            include_outer_lines=True
        )
        table.scale(0.4).next_to(base_query, DOWN).to_edge(LEFT)

        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx % 3 == 0:
                entry.scale(1.3)
            self.remove(entry)
        self.play(Create(table.get_vertical_lines()))
        self.play(Create(table.get_horizontal_lines()))
        self.play(FadeIn(table.get_col_labels(), run_time=2))
        self.wait()
        boxes_anims = [
            Create(boxes[0]),
            *[ReplacementTransform(boxes[idx-1], boxes[idx]) for idx in range(1, len(boxes))]
        ]

        blocked_indices = [8, 11]

        for idx, entry in enumerate(table.get_entries_without_labels()):
            if idx not in blocked_indices:
                if idx % 3 == 0:
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
                    self.wait()

        self.wait()

        self.play(Uncreate(boxes[-1]))
        self.wait()

        block_box = SurroundingRectangle(words[0:3], color=WHITE, buff=SMALL_BUFF)
        lock = table.get_entries((1, 3))
        blocked_part = words[0:3]
        changable_part = words[3:]

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

    def _prepare_levels(self):
        for idx in range(len(self.levels)):
            level = VipryamitelFunnel._get_level_rect(self, idx)
            level.set_color(self.rgbas[idx]).set_fill(color=self.rgbas[idx], opacity=1)
            self.modules_names[idx].set(height=0.3).next_to(level, LEFT).to_edge(LEFT)
            self.modules_names[idx].set_color(self.rgbas[idx])

    def kostyl_summarization(self):
        def resize_mobject(mobject: Union[VMobject, Mobject], zoom_factor: int = 10) -> Union[VMobject, Mobject]:
            if isinstance(mobject, VMobject):
                for obj in mobject:
                    obj.set(width=obj.width / zoom_factor)
                    obj.move_to(obj.get_center() / zoom_factor)
                    if obj.stroke_width:
                        obj.set_stroke(width=mobject.stroke_width / zoom_factor)
            else:
                mobject.set(width=mobject.width/zoom_factor)
                mobject.move_to(mobject.get_center()/zoom_factor)
                if mobject.stroke_width != 0:
                    mobject.set_stroke(width=mobject.stroke_width/zoom_factor)
            return mobject

        zf = 60

        kostyl_equation = VGroup(
            Text("Kostyl", color=YELLOW), MathTex("="), NotebookWithNotes(color=GREEN),
            MathTex("+"), NotebookWithNotes(color=RED), MathTex("+"),
            NotebookWithNotes(color=BLUE)
        ).arrange(RIGHT)
        box = SurroundingRectangle(kostyl_equation)
        self._prepare_levels()
        kostyl_as_lines = []
        for level in self.levels[:-1]:
            kostyl_as_lines.append(Line(color=YELLOW).next_to(level, DOWN, buff=MED_SMALL_BUFF / 2))
            kostyl_as_lines[-1].set(width=level.width)
        kostyl_as_lines = VGroup(*kostyl_as_lines)
        self.add_foreground_mobject(self.levels)
        self.add(self.modules_names, *kostyl_as_lines[:3], *kostyl_as_lines[4:])
        self.camera.frame.save_state()

        self.kostyl_label = resize_mobject(self.kostyl_label, zf)
        kostyl_equation = resize_mobject(kostyl_equation, zf)
        box = resize_mobject(box, zf)

        self.camera.frame.set(width=config.frame_width/zf)
        self.play(ReplacementTransform(self.kostyl_label, kostyl_equation[0]))
        self.play(FadeIn(kostyl_equation[1:], run_time=3))
        self.wait()
        self.play(Create(box))
        self.play(box.animate.set_fill(color=box.color, opacity=1))
        self.remove(*kostyl_equation)
        self.play(Restore(self.camera.frame), ReplacementTransform(box, kostyl_as_lines[3]))
        self.wait()

        return_levels = self.levels.copy().arrange(DOWN, buff=0)
        return_names_anims = []
        for idx, name in enumerate(self.modules_names):
            return_names_anims.append(name.animate.next_to(return_levels[idx], LEFT).to_edge(LEFT))

        kostyl_lines_anims = []
        for idx, line in enumerate(kostyl_as_lines):
            kostyl_lines_anims.append(line.animate.move_to(return_levels[idx].get_bottom()))

        self.play(
            AnimationGroup(
                Transform(self.levels, return_levels),
                *return_names_anims,
                *kostyl_lines_anims,
                run_time=1
            )
        )

        self.wait()





