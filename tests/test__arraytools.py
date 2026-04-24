"""Parity tests for :mod:`acoustics._arraytools` against ``scipy.signal._arraytools``.

The helpers are vendored from SciPy, so this suite guards against drift
if we ever touch the vendored copies by accident.
"""

import numpy as np
import pytest
from scipy.signal import _arraytools as sp

from acoustics import _arraytools as vendored


@pytest.fixture
def arrays():
    rng = np.random.default_rng(42)
    return [
        rng.normal(size=50),
        rng.normal(size=(5, 50)),
        rng.normal(size=(6, 7, 40)),
    ]


def test_axis_slice_matches_scipy(arrays):
    for x in arrays:
        for axis in range(x.ndim):
            np.testing.assert_array_equal(
                vendored.axis_slice(x, 2, 10, 1, axis=axis),
                sp.axis_slice(x, 2, 10, 1, axis=axis),
            )


def test_axis_reverse_matches_scipy(arrays):
    for x in arrays:
        for axis in range(x.ndim):
            np.testing.assert_array_equal(
                vendored.axis_reverse(x, axis=axis),
                sp.axis_reverse(x, axis=axis),
            )


@pytest.mark.parametrize("name", ["odd_ext", "even_ext", "const_ext"])
def test_extension_matches_scipy(arrays, name):
    for x in arrays:
        for axis in range(x.ndim):
            max_n = x.shape[axis] - 1
            for n in (0, 1, min(3, max_n), max_n):
                np.testing.assert_array_equal(
                    getattr(vendored, name)(x, n, axis=axis),
                    getattr(sp, name)(x, n, axis=axis),
                )


@pytest.mark.parametrize("name", ["odd_ext", "even_ext"])
def test_extension_too_long_raises(name):
    x = np.zeros(5)
    with pytest.raises(ValueError, match="extension length"):
        getattr(vendored, name)(x, 10)


def test_const_ext_tolerates_large_n():
    """const_ext has no length guard in SciPy either."""
    x = np.arange(3)
    result = vendored.const_ext(x, 5)
    expected = sp.const_ext(x, 5)
    np.testing.assert_array_equal(result, expected)
