import numpy as np
import pytest

from acoustics.ambisonics import acn, n3d, sn3d


def test_acn_first_order():
    assert list(acn(1)) == [(0, 0), (1, -1), (1, 0), (1, 1)]


@pytest.mark.parametrize(
    "m, n, expected",
    [
        (0, 0, 1.0 / np.sqrt(4.0 * np.pi)),
        (1, 1, 1.0 / np.sqrt(4.0 * np.pi)),
        (0, 1, 1.0 / np.sqrt(4.0 * np.pi)),
    ],
)
def test_sn3d_scalar(m, n, expected):
    assert sn3d(m, n) == pytest.approx(expected)


def test_n3d_equals_sn3d_times_sqrt_2n_plus_1():
    for m, n in [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]:
        assert n3d(m, n) == pytest.approx(sn3d(m, n) * np.sqrt(2 * n + 1))
