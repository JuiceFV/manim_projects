from abc import ABC

from manim import *
from pathlib import Path
from .utils import parent_kwargs


class Bubble(SVGMobject, ABC):

    def __init__(self, **kwargs):
        self.direction_was_specified = ("direction" in kwargs)

        self.direction = kwargs.pop("direction", LEFT)
        self.center_point = kwargs.pop("center_point", ORIGIN)
        self.content_scale_factor = kwargs.pop("content_scale_factor", 0.75)
        self.bubble_center_adjustment_factor = kwargs.pop("bubble_center_adjustment_factor", 1. / 8)
        self.file_name = kwargs.pop("file_name", None)

        if self.file_name is None:
            raise Exception("Must invoke Bubble subclass")

        super(Bubble, self).__init__(self.file_name, **parent_kwargs(self, **kwargs))

        self.center()
        self.stretch_to_fit_height(self.height)
        self.stretch_to_fit_width(self.width)
        if self.direction[0] > 0:
            self.flip()
        self.content = Mobject()
        if config.renderer == "opengl":
            self.refresh_triangulation()

    def get_tip(self) -> np.ndarray:
        # TODO, find a better way
        return self.get_corner(DOWN + self.direction) - 0.6 * self.direction

    def get_bubble_center(self):
        factor = self.bubble_center_adjustment_factor
        return self.get_center() + factor * self.get_height() * UP

    def move_tip_to(self, point):
        mover = VGroup(self)
        if self.content is not None:
            mover.add(self.content)
        mover.shift(point - self.get_tip())
        return self

    def flip(self, axis: np.ndarray = UP, **kwargs) -> SVGMobject:
        Mobject.flip(self, axis=axis, **kwargs)
        if config.renderer == "opengl":
            self.refresh_unit_normal()
            self.refresh_triangulation()
        if abs(axis[1]) > 0:
            self.direction = -np.array(self.direction)
        return self

    def pin_to(self, mobject: Mobject) -> SVGMobject:
        mob_center = mobject.get_center()
        want_to_flip = np.sign(mob_center[0]) != np.sign(self.direction[0])
        print(want_to_flip, self.direction, mob_center)
        can_flip = not self.direction_was_specified
        if want_to_flip and can_flip:
            self.flip()
        if config.renderer == "opengl":
            boundary_point = mobject.get_bounding_box_point(UP - self.direction)
        else:
            boundary_point = mobject.get_critical_point(UP - self.direction)
        vector_from_center = 1.0 * (boundary_point - mob_center)
        self.move_tip_to(mob_center + vector_from_center)
        return self

    def position_mobject_inside(self, mobject):
        scaled_width = self.content_scale_factor * self.get_width()
        if mobject.get_width() > scaled_width:
            mobject.set_width(scaled_width)
        mobject.shift(
            self.get_bubble_center() - mobject.get_center()
        )
        return mobject

    def add_content(self, mobject):
        self.position_mobject_inside(mobject)
        self.content = mobject
        return self.content

    def write(self, *text):
        self.add_content(Tex(*text))
        return self

    def resize_to_content(self):
        target_width = self.content.get_width()
        target_width += max(MED_LARGE_BUFF, 2)
        target_height = self.content.get_height()
        target_height += 2.5 * LARGE_BUFF
        tip_point = self.get_tip()
        self.stretch_to_fit_width(target_width)
        self.stretch_to_fit_height(target_height)
        self.move_tip_to(tip_point)
        self.position_mobject_inside(self.content)

    def clear(self):
        self.add_content(VMobject())
        return self


class SpeechBubble(Bubble, ABC):
    def __init__(self, **kwargs):
        default_kwargs = {"file_name": str(Path(__file__).parent/"svgs/Bubbles_speech.svg"), "height": 4}
        default_kwargs.update(kwargs)
        super(SpeechBubble, self).__init__(**default_kwargs)


class ThoughtBubble(Bubble, ABC):
    def __init__(self, **kwargs):
        default_kwargs = {"file_name": str(Path(__file__).parent/"svgs/Bubbles_thought.svg")}
        default_kwargs.update(kwargs)
        super(ThoughtBubble, self).__init__(**default_kwargs)
        self.submobjects.sort(
            key=lambda m: m.get_bottom()[1]
        )

    def make_green_screen(self):
        self.submobjects[-1].set_fill(PURE_GREEN, opacity=1)
        return self


class VideoIcon(SVGMobject, ABC):
    def __init__(self, **kwargs):
        default_kwargs = {"file_name": str(Path(__file__).parent/"svgs/video_icon"), "width": config.frame_width / 16}
        default_kwargs.update(kwargs)
        super(VideoIcon, self).__init__(**default_kwargs)
        self.center()
        self.set_stroke(color=WHITE, width=kwargs.pop("stroke_width", 3))
        self.set_fill(color=WHITE, opacity=kwargs.pop("fill_opacity", 0))

    @property
    def triangle(self) -> Mobject:
        return self[1]

    @property
    def rectangle(self) -> Mobject:
        return self[0]


class VideoSeries(VGroup, ABC):
    def __init__(self, **kwargs):
        self.num_videos = kwargs.pop("num_videos", 6)
        self.gradient_colors = kwargs.pop("gradient_colors", [BLUE_B, BLUE_D])
        self.video_icon_kwargs = kwargs.pop("video_icon_kwargs", {})
        videos = [VideoIcon(**self.video_icon_kwargs) for _ in range(self.num_videos)]
        super(VideoSeries, self).__init__(*videos, **kwargs)
        self.arrange()
        self.set_width(kwargs.pop("width", config.frame_width/2))
        self.set_color_by_gradient(*self.gradient_colors)


class Tree(SVGMobject, ABC):
    def __init__(self, **kwargs):
        default_kwargs = {"file_name": str(Path(__file__).parent / "svgs/tree"), "width": config.frame_width / 16}
        default_kwargs.update(kwargs)
        super(Tree, self).__init__(**default_kwargs)
        self.center()
        self.set_stroke(color=WHITE, width=kwargs.pop("stroke_width", 1))
        self.set_fill(color=GREEN, opacity=kwargs.pop("fill_opacity", 0.5))
        self[0].set_fill(color=BLUE, opacity=0.5)
        self[1].set_fill(color=BLUE, opacity=0.5)
        self[2].set_fill(color=BLUE, opacity=0.5)


class Sigmoid(VGroup, ABC):
    # TODO: Make more general
    def __init__(self, **kwargs):
        axes = Axes(
            x_range=[-10, 10, 1],
            y_range=[0, 1, 0.1],
            x_length=10,
            axis_config={"color": BLUE}
        )
        sigmoid_graph = axes.get_graph(lambda x: sigmoid(x), color=RED)
        sigmoid_graph.set_stroke(width=2)
        super(Sigmoid, self).__init__(axes, sigmoid_graph)


class Clusters(SVGMobject, ABC):
    def __init__(self, **kwargs):
        default_kwargs = {"file_name": str(Path(__file__).parent / "svgs/clusters"),
                          "width": config.frame_width / 16}
        default_kwargs.update(kwargs)
        super(Clusters, self).__init__(**default_kwargs)
        self.center()
        self.set_stroke(color=WHITE, width=kwargs.pop("stroke_width", 1))
        self.set_fill(color=GREEN, opacity=kwargs.pop("fill_opacity", 0.5))
        self[0:18].set_color(YELLOW)
        self[18:29].set_color(RED)
        self[29:].set_color(BLUE)
