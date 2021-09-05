import numpy as np
from manim import *


class YTSVGLogo(SVGMobject):
    def __init__(self, height: float = 2, width: float = None,
                 unpack_groups: bool = True, stroke_width: float = 4,
                 fill_opacity: float = 1, should_center = True):
        super().__init__(
            "D:\Github\manim_projects\digi\logos\logos_svg\youtube_logo.svg",
            should_center=should_center,
            height=height,
            width=width,
            unpack_groups=unpack_groups,
            stroke_width=stroke_width,
            fill_opacity=fill_opacity
        )


class IntroYTLayout(VGroup):
    def __init__(self, logo_height: float = 0.85, logo_buff: float = 0.5,
                 logo_arrangement: np.ndarray = RIGHT, to_edge: np.ndarray = UP, edge_buff: float = 0.1):
        super().__init__(*[YTSVGLogo(height=logo_height, should_center=False) for _ in range(6)])
        self.arrange(logo_arrangement, buff=logo_buff).to_edge(to_edge, buff=edge_buff)
