from abc import ABC
from manim import *
from pathlib import Path


class YTSVGLogo(SVGMobject, ABC):
    def __init__(self, height: float = 2, width: float = None,
                 unpack_groups: bool = True, stroke_width: float = 4,
                 fill_opacity: float = 1, should_center = True):
        super(YTSVGLogo, self).__init__(
            str(Path(__file__).parent) + "/logos_svg/youtube_logo.svg",
            should_center=should_center,
            height=height,
            width=width,
            unpack_groups=unpack_groups,
            stroke_width=stroke_width,
            fill_opacity=fill_opacity
        )


class IntroYTLayout(VGroup, ABC):
    CONFIG = {
        'logo_height': 0.85,
        'logo_width': None,
        'logo_unpack_groups': True,
        'logo_stroke_width': 4,
        'logo_fill_opacity': 1,
        'logo_should_center': False,
        'logo_buff': 0.5,
        'logo_arrangement': RIGHT,
        'to_edge': UP,
        'edge_buff': 0.1
    }

    def __init__(self):
        super(IntroYTLayout, self).__init__(
            *[YTSVGLogo(
                height=self.CONFIG['logo_height'],
                width=self.CONFIG['logo_width'],
                unpack_groups=self.CONFIG['logo_unpack_groups'],
                stroke_width=self.CONFIG['logo_stroke_width'],
                fill_opacity=self.CONFIG['logo_fill_opacity'],
                should_center=self.CONFIG['logo_should_center']
            ) for _ in range(6)]
        )
        self.arrange(self.CONFIG['logo_arrangement'], buff=self.CONFIG['logo_buff']).to_edge(
            self.CONFIG['to_edge'],
            buff=self.CONFIG['edge_buff']
        )
