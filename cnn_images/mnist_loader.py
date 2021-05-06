import numpy as np
from mnist import MNIST


def load_mnist(mnist_data_path='./data'):
    mn_data = MNIST(mnist_data_path)
    return mn_data.load_training()


def get_image_as_pixel_array(pixel_array, reshape, normalize=False):
    pixel_array = np.array(pixel_array)
    if reshape:
        pixel_array = pixel_array.reshape(28, 28)
    if normalize:
        pixel_array = pixel_array/255.0
    return pixel_array.transpose()
