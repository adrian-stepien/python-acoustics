"""Array helpers vendored from ``scipy.signal._arraytools``.

These functions are private in SciPy and have no public equivalents,
so :func:`acoustics.signal._sosfiltfilt` vendors the handful it needs
rather than reaching into an underscore-prefixed module.
"""

import numpy as np


def axis_slice(a, start=None, stop=None, step=None, axis=-1):
    """Return ``a`` sliced with ``slice(start, stop, step)`` along ``axis``."""
    a_slice = [slice(None)] * a.ndim
    a_slice[axis] = slice(start, stop, step)
    return a[tuple(a_slice)]


def axis_reverse(a, axis=-1):
    """Reverse ``a`` along ``axis``."""
    return axis_slice(a, step=-1, axis=axis)


def _check_ext_length(x, n, axis):
    if n > x.shape[axis] - 1:
        raise ValueError(
            f"The extension length n ({n}) is too big. "
            f"It must not exceed x.shape[axis]-1, which is {x.shape[axis] - 1}."
        )


def odd_ext(x, n, axis=-1):
    """Odd (point-symmetric) extension of length ``n`` at each end of ``x``."""
    if n < 1:
        return x
    _check_ext_length(x, n, axis)
    left_end = axis_slice(x, start=0, stop=1, axis=axis)
    left_ext = axis_slice(x, start=n, stop=0, step=-1, axis=axis)
    right_end = axis_slice(x, start=-1, axis=axis)
    right_ext = axis_slice(x, start=-2, stop=-(n + 2), step=-1, axis=axis)
    return np.concatenate((2 * left_end - left_ext, x, 2 * right_end - right_ext), axis=axis)


def even_ext(x, n, axis=-1):
    """Even (mirrored) extension of length ``n`` at each end of ``x``."""
    if n < 1:
        return x
    _check_ext_length(x, n, axis)
    left_ext = axis_slice(x, start=n, stop=0, step=-1, axis=axis)
    right_ext = axis_slice(x, start=-2, stop=-(n + 2), step=-1, axis=axis)
    return np.concatenate((left_ext, x, right_ext), axis=axis)


def const_ext(x, n, axis=-1):
    """Constant-valued extension of length ``n`` at each end of ``x``."""
    if n < 1:
        return x
    left_end = axis_slice(x, start=0, stop=1, axis=axis)
    right_end = axis_slice(x, start=-1, axis=axis)
    ones_shape = [1] * x.ndim
    ones_shape[axis] = n
    ones = np.ones(ones_shape, dtype=x.dtype)
    return np.concatenate((ones * left_end, x, ones * right_end), axis=axis)
