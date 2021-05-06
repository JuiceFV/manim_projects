from manim import *
from mnist_loader import get_image_as_pixel_array, load_mnist

config.background_color = WHITE


class ImagePixels(Scene):
    def construct(self):
        image = get_image_as_pixel_array(load_mnist()[0][4], True, True)
        pixel_image = self.get_pixel_matrix(image)
        fm = self.get_pixel_matrix(self.feature_map(image))
        for i in range(5):
            pixel_image[6+i][0][9:14].set_stroke(color=RED_C)
        pixel_image[10][0][9].set_fill(RED_C, opacity=1.0)
        pixel_image[9][0][9].set_fill(RED_C, opacity=1.0)
        pixel_image[8][0][10].set_fill(RED_C, opacity=1.0)
        pixel_image[7][0][11].set_fill(RED_C, opacity=1.0)
        pixel_image[7][0][12].set_fill(RED_C, opacity=1.0)
        pixel_image[7][0][13].set_fill(RED_C, opacity=1.0)

        img_and_fm = VGroup(pixel_image, fm).arrange(RIGHT, buff=LARGE_BUFF)
        line1 = Line(pixel_image[6][0][9].get_edge_center(UP), fm[6][0][9].get_edge_center(UP)).set_color(color=RED_C)
        line2 = Line(pixel_image[10][0][9].get_edge_center(UP), fm[6][0][9].get_edge_center(UP)).set_color(color=RED_C)
        line3 = Line(pixel_image[6][0][13].get_edge_center(DOWN), fm[6][0][9].get_edge_center(DOWN)).set_color(color=RED_C)
        line4 = Line(pixel_image[10][0][13].get_edge_center(DOWN), fm[6][0][9].get_edge_center(DOWN)).set_color(color=RED_C)
        fm[6][0][9].set_stroke(color=RED_C)
        self.add(img_and_fm, line1, line2, line3, line4)
        self.wait(1)

    def get_pixel_matrix(self, image):
        pixel_matrix = VGroup(*[
            self.get_column_pixels(len(image[i]), image[i])
            for i in range(len(image))
        ])
        pixel_matrix.arrange(RIGHT, buff=0.05)
        return pixel_matrix

    def get_column_pixels(self, size, pixels_array):
        column = VGroup()
        n_pixels = size
        pixels = VGroup(*[
            Circle(
                radius=0.07,
                stroke_color=BLACK,
                stroke_width=2,
                fill_color=BLACK,
                fill_opacity=pixels_array[pixel_index],
                   )
            for pixel_index in range(n_pixels)
        ])
        pixels.arrange(DOWN, buff=0.05)
        for pixel in pixels:
            pixel.edges_in = VGroup()
            pixel.edges_out = VGroup()
        column.add(pixels)
        return column

    def feature_map(self, image):
        fm = []
        kernel = np.array(
            [
                [0, 0, 0, 1, 1],
                [0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 1, 0, 0, 0]
            ])
        for i in range(len(image) - len(kernel) + 1):
            row = []
            for j in range(len(image) - len(kernel) + 1):
                row.append(np.sum([image[i + h][j:j + 5] for h in range(5)] * kernel))
            fm.append(row)
        return fm

