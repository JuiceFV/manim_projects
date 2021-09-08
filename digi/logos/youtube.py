from abc import ABC
from manim import *
from pathlib import Path


class YTSVGLogo(SVGMobject, ABC):
    """
    Youtube icon for the intro.
    """
    def __init__(self, height: float = 2, width: float = None, unpack_groups: bool = True,
                 stroke_width: float = 4, fill_opacity: float = 1, should_center = True):
        # initialize SVGMobject with svg-logo
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
    """
    The layout of 6 Youtube icons
    """
    CONFIG = {
        'logo_height': 0.85,  # every single icon height
        'logo_width': None,  # adjusted for the height
        'logo_unpack_groups': True,  # get set of simple figures (Mobjects)
        'logo_stroke_width': 4,  # stroke width of icon
        'logo_fill_opacity': 1,  # fill opacity of icon
        'logo_should_center': False,  # should logo be centered
        'logo_buff': 0.5,  # the margin between every logo
        'logo_arrangement': RIGHT,  # logo arrangement in layout
        'to_edge': UP,  # the edge to one layout is attached
        'edge_buff': 0.1  # the padding from an edge
    }

    def __init__(self):
        # initialize the group via 6 Youtube icons
        super(IntroYTLayout, self).__init__(*[YTSVGLogo(
                height=self.CONFIG['logo_height'],
                width=self.CONFIG['logo_width'],
                unpack_groups=self.CONFIG['logo_unpack_groups'],
                stroke_width=self.CONFIG['logo_stroke_width'],
                fill_opacity=self.CONFIG['logo_fill_opacity'],
                should_center=self.CONFIG['logo_should_center']
            ) for _ in range(6)]
        )
        # set them one-by-one in right direction and attach a little bit lower
        # upper edge
        self.arrange(self.CONFIG['logo_arrangement'], buff=self.CONFIG['logo_buff'])\
            .to_edge(self.CONFIG['to_edge'], buff=self.CONFIG['edge_buff'])
