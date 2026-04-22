import numpy as np
import pytest

from acoustics.directivity import *


@pytest.mark.parametrize(
    "given, expected, uncertainty",
    [
        (0.0, 1.0, 0.0),
        (1.0 / 2.0 * np.pi, 0.0, 0.0),
        (np.pi, +1.0, 0.0),
        (3.0 / 2.0 * np.pi, 0.0, 0.0),
        (2.0 * np.pi, +1.0, 0.0),
    ],
)
def test_figure_eight(given, expected, uncertainty):
    assert figure_eight(given) == pytest.approx(expected, uncertainty)


def test_spherical_harmonic_theta_phi_convention():
    assert spherical_harmonic(0.0, 0.0, m=0, n=0) == pytest.approx(1.0 / (2.0 * np.sqrt(np.pi)))
    assert spherical_harmonic(0.0, 0.0, m=0, n=1) == pytest.approx(np.sqrt(3.0 / (4.0 * np.pi)))
    assert spherical_harmonic(np.pi / 2.0, 0.0, m=0, n=1) == pytest.approx(0.0)
