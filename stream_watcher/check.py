# -*- coding: utf-8 -*-
"""TODO: 自带的检查器.

"""
import numpy

from scipy.spatial import distance


def hamming_check(image_0: numpy.ndarray, image_1: numpy.ndarray, threshold: float = 0.001) -> bool:
    """检查是否离线"""
    f_0 = image_0.flatten()
    f_1 = image_1.flatten()

    hamming_result = distance.hamming(f_0, f_1)

    return hamming_result > threshold
