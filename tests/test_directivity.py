import numpy as np
import pytest
from matplotlib import pyplot as plt

from acoustics.directivity import (
    Cardioid,
    Custom,
    FigureEight,
    Omni,
    SphericalHarmonic,
    cardioid,
    cartesian_to_spherical,
    figure_eight,
    spherical_harmonic,
    spherical_to_cartesian,
)


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


class TestCardioid:
    def test_peak_at_zero_with_defaults(self):
        """a=k=1: peak value is |1 + cos(0)| = 2 at θ=0."""
        assert cardioid(0.0) == pytest.approx(2.0)

    def test_null_at_pi(self):
        """a=k=1: null at θ=π where 1 + cos(π) = 0."""
        assert cardioid(np.pi) == pytest.approx(0.0, abs=1e-12)

    def test_amplitude_scales_linearly(self):
        assert cardioid(0.0, a=3.0) == pytest.approx(6.0)

    def test_broadcasts_over_array(self):
        thetas = np.array([0.0, np.pi / 2.0, np.pi])
        result = cardioid(thetas)
        assert result.shape == thetas.shape
        np.testing.assert_allclose(result, [2.0, 1.0, 0.0], atol=1e-12)


class TestCoordinateConversions:
    def test_spherical_to_cartesian_at_north_pole(self):
        x, y, z = spherical_to_cartesian(1.0, theta=0.0, phi=0.0)
        assert (x, y, z) == pytest.approx((0.0, 0.0, 1.0))

    def test_spherical_to_cartesian_equator(self):
        x, y, z = spherical_to_cartesian(1.0, theta=np.pi / 2.0, phi=0.0)
        assert (x.item(), y.item(), z.item()) == pytest.approx((1.0, 0.0, 0.0), abs=1e-12)

    def test_cartesian_roundtrip(self):
        """Round-trip on a point in the first octant."""
        r_in, theta_in, phi_in = 2.0, np.pi / 3.0, np.pi / 4.0
        x, y, z = spherical_to_cartesian(r_in, theta_in, phi_in)
        r_out, theta_out, phi_out = cartesian_to_spherical(x, y, z)
        assert r_out.item() == pytest.approx(r_in)
        assert theta_out.item() == pytest.approx(theta_in)
        assert phi_out.item() == pytest.approx(phi_in)

    def test_cartesian_roundtrip_fourth_quadrant(self):
        """Azimuth keeps the correct quadrant when x > 0 and y < 0."""
        r_in, theta_in, phi_in = 2.0, np.pi / 3.0, 7.0 * np.pi / 4.0
        x, y, z = spherical_to_cartesian(r_in, theta_in, phi_in)
        r_out, theta_out, phi_out = cartesian_to_spherical(x, y, z)
        assert r_out.item() == pytest.approx(r_in)
        assert theta_out.item() == pytest.approx(theta_in)
        assert phi_out.item() == pytest.approx(phi_in)

    def test_cartesian_to_spherical_handles_y_axis(self):
        r, theta, phi = cartesian_to_spherical(0.0, 1.0, 0.0)
        assert r.item() == pytest.approx(1.0)
        assert theta.item() == pytest.approx(np.pi / 2.0)
        assert phi.item() == pytest.approx(np.pi / 2.0)

    def test_cartesian_to_spherical_zero_vector(self):
        r, theta, phi = cartesian_to_spherical(0.0, 0.0, 0.0)
        assert r.item() == pytest.approx(0.0)
        assert theta.item() == pytest.approx(np.pi / 2.0)
        assert phi.item() == pytest.approx(0.0)


class TestDirectivityBaseClass:
    def test_rotation_must_be_three_angles(self):
        with pytest.raises(ValueError, match="rotation must be a three-element vector"):
            Omni(rotation=[0.0, 0.0])

    def test_default_rotation_is_zero(self):
        d = Omni()
        np.testing.assert_allclose(d.rotation, np.zeros(3))


class TestDirectivityClasses:
    def test_omni_is_unit_everywhere(self):
        d = Omni()
        theta = np.linspace(0.0, np.pi, 7)
        phi = np.linspace(0.0, 2.0 * np.pi, 7)
        np.testing.assert_allclose(d.using_spherical(1.0, theta, phi), 1.0)

    def test_cardioid_class_matches_function(self):
        d = Cardioid()
        theta = np.array([0.0, np.pi / 2, np.pi])
        np.testing.assert_allclose(d.using_spherical(1.0, theta, phi=0.0), cardioid(theta))

    def test_legacy_using_spherical_signature_still_works(self):
        d = Cardioid()
        theta = np.array([0.0, np.pi / 2, np.pi])
        np.testing.assert_allclose(d.using_spherical(theta, 0.0), cardioid(theta))

    def test_keyword_using_spherical_signature_still_works(self):
        d = Cardioid()
        theta = np.array([0.0, np.pi / 2, np.pi])
        np.testing.assert_allclose(d.using_spherical(r=1.0, theta=theta, phi=0.0), cardioid(theta))

    def test_using_spherical_requires_theta_and_phi(self):
        d = Cardioid()
        with pytest.raises(TypeError, match="requires theta and phi coordinates"):
            d.using_spherical(theta=np.pi / 4.0)

    def test_figure_eight_class_matches_function(self):
        d = FigureEight()
        theta = np.array([0.0, np.pi / 4, np.pi / 2])
        np.testing.assert_allclose(d.using_spherical(1.0, theta, phi=0.0), figure_eight(theta))

    def test_spherical_harmonic_class_matches_function(self):
        d = SphericalHarmonic(m=0, n=1)
        theta = np.array([0.0, np.pi / 3, np.pi / 2])
        np.testing.assert_allclose(
            d.using_spherical(1.0, theta, phi=0.0),
            spherical_harmonic(theta, 0.0, m=0, n=1),
        )

    def test_using_cartesian_matches_using_spherical(self):
        """Feeding Cartesian input should match the spherical path after conversion."""
        d = Omni()
        x, y, z = spherical_to_cartesian(1.0, theta=np.pi / 3, phi=np.pi / 6)
        via_cartesian = d.using_cartesian(x, y, z)
        via_spherical = d.using_spherical(1.0, np.pi / 3, np.pi / 6)
        np.testing.assert_allclose(via_cartesian, via_spherical)

    def test_rotation_changes_sampling_direction(self):
        d = Cardioid(rotation=[0.0, np.pi, 0.0])
        # Rotating the pattern by pi about the y-axis flips the cardioid peak
        # from +z (theta=0) to -z (theta=pi).
        assert d.using_spherical(0.0, 0.0) == pytest.approx(0.0)
        assert d.using_spherical(np.pi, 0.0) == pytest.approx(2.0)

    def test_include_rotation_false_uses_unrotated_pattern(self):
        d = Cardioid(rotation=[0.0, np.pi, 0.0])
        assert d.using_spherical(0.0, 0.0, include_rotation=False) == pytest.approx(2.0)
        assert d.using_spherical(0.0, 0.0, include_rotation=True) == pytest.approx(0.0)

    def test_using_cartesian_respects_rotation(self):
        d = Cardioid(rotation=[0.0, np.pi, 0.0])
        # Point on +z axis. With the flipped cardioid this becomes the null.
        assert d.using_cartesian(0.0, 0.0, 1.0) == pytest.approx(0.0)
        assert d.using_cartesian(0.0, 0.0, 1.0, include_rotation=False) == pytest.approx(2.0)

    def test_custom_interpolates_grid(self):
        """Custom returns the grid values at the original sample points."""
        theta = np.linspace(0.1, np.pi - 0.1, 5)
        phi = np.linspace(0.0, 2.0 * np.pi, 6)
        grid = np.outer(np.sin(theta), np.cos(phi))
        d = Custom(theta=theta, phi=phi, r=grid)
        # Evaluate at a single original sample.
        value = d._directivity(theta[2], phi[3])
        np.testing.assert_allclose(value[0, 0], grid[2, 3])

    def test_custom_accepts_rotation(self):
        d = Custom(
            theta=np.linspace(0.1, np.pi - 0.1, 5),
            phi=np.linspace(0.0, 2.0 * np.pi, 6),
            r=np.ones((5, 6)),
            rotation=[0.1, 0.2, 0.3],
        )
        np.testing.assert_allclose(d.rotation, [0.1, 0.2, 0.3])

    def test_plot_supports_filename_and_sphere_keyword(self, tmp_path):
        d = Omni()
        filename = tmp_path / "directivity.png"
        fig = d.plot(filename=filename, sphere=True)
        try:
            assert filename.exists()
            assert len(fig.axes) >= 1
        finally:
            plt.close(fig)
