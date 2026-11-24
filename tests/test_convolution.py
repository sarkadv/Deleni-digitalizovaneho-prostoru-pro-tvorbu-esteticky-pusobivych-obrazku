"""Discrete convolution helpers (util/convolution.py)."""

import pytest

from helpers import image_from_rows


# CV-01
def test_kernels(backend):
    k = backend.convolution_kernels()
    assert k["LAPLACE"] == [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    assert k["GAUSSIAN"] == [[1 / 16, 1 / 8, 1 / 16], [1 / 8, 1 / 4, 1 / 8], [1 / 16, 1 / 8, 1 / 16]]


# CV-02
def test_padding_replicates_edges(backend):
    padded = backend.create_convolution_padding([[1, 2, 3], [4, 5, 6]])
    assert padded == [[1, 1, 2, 3, 3],
                      [1, 1, 2, 3, 3],
                      [4, 4, 5, 6, 6],
                      [4, 4, 5, 6, 6]]


# CV-03
def test_padding_single_column(backend):
    # the only column is both the leftmost and the rightmost one -> copied to both sides
    assert backend.create_convolution_padding([[7], [8]]) == [[7, 7, 7], [7, 7, 7], [8, 8, 8], [8, 8, 8]]


# CV-04
def test_padding_single_row(backend):
    assert backend.create_convolution_padding([[1, 2]]) == [[1, 1, 2, 2], [1, 1, 2, 2], [1, 1, 2, 2]]


# CV-05
def test_convolute_result_is_two_smaller(backend):
    m = [[0] * 6 for _ in range(5)]
    res = backend.convolute(m, backend.convolution_kernels()["LAPLACE"])
    assert len(res) == 3 and all(len(row) == 4 for row in res)


# CV-06
def test_laplace_of_impulse(backend):
    m = [[0] * 5 for _ in range(5)]
    m[2][2] = 1
    res = backend.convolute(m, backend.convolution_kernels()["LAPLACE"])
    assert res == [[0, 1, 0], [1, -4, 1], [0, 1, 0]]


# CV-07
def test_laplace_of_constant_is_zero(backend):
    m = [[9] * 4 for _ in range(4)]
    assert backend.convolute(m, backend.convolution_kernels()["LAPLACE"]) == [[0, 0], [0, 0]]


# CV-08
def test_laplace_of_linear_ramp_is_zero(backend):
    m = [[x + 2 * y for x in range(5)] for y in range(4)]
    assert backend.convolute(m, backend.convolution_kernels()["LAPLACE"]) == [[0] * 3, [0] * 3]


# CV-09
def test_gaussian_blur_values(backend):
    m = [[0, 0, 0], [0, 16, 0], [0, 0, 0]]
    res = backend.convolute(m, backend.convolution_kernels()["GAUSSIAN"])
    assert res == [[4.0]]
    m = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert backend.convolute(m, backend.convolution_kernels()["GAUSSIAN"])[0][0] == pytest.approx(5.0)


# CV-10
def test_separate_color_channels(backend):
    img = image_from_rows([[(1, 2, 3), (4, 5, 6)],
                           [(7, 8, 9), (10, 11, 12)]])
    r, g, b = backend.separate_color_channels(img)
    assert r == [[1, 1, 4, 4], [1, 1, 4, 4], [7, 7, 10, 10], [7, 7, 10, 10]]
    assert g == [[2, 2, 5, 5], [2, 2, 5, 5], [8, 8, 11, 11], [8, 8, 11, 11]]
    assert b == [[3, 3, 6, 6], [3, 3, 6, 6], [9, 9, 12, 12], [9, 9, 12, 12]]
