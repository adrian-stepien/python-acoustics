"""Tests for :mod:`acoustics.reflection`."""

import numpy as np
import pytest

from acoustics.reflection import (
    Boundary,
    impedance_attenborough,
    impedance_delany_and_bazley,
    numerical_distance,
    reflection_factor_plane_wave,
    reflection_factor_spherical_wave,
)


class TestReflectionFactorPlaneWave:
    def test_matched_impedance_gives_zero(self):
        """Normalized impedance Z=1 at normal incidence absorbs fully."""
        assert reflection_factor_plane_wave(impedance=1.0, angle=0.0) == pytest.approx(0.0)

    def test_rigid_boundary_reflects_fully(self):
        """As Z → ∞, the reflection factor approaches +1."""
        result = reflection_factor_plane_wave(impedance=1e9, angle=0.0)
        assert abs(result) == pytest.approx(1.0, abs=1e-6)

    def test_pressure_release_boundary(self):
        """As Z → 0, the reflection factor approaches -1."""
        result = reflection_factor_plane_wave(impedance=1e-9, angle=0.0)
        assert result == pytest.approx(-1.0, abs=1e-6)

    def test_grazing_incidence(self):
        """At grazing incidence (θ = π/2) and finite Z, R = -1 regardless of Z."""
        result = reflection_factor_plane_wave(impedance=2.0 + 1j, angle=np.pi / 2)
        assert result == pytest.approx(-1.0)


class TestImpedanceModels:
    def test_delany_and_bazley_returns_complex(self):
        z = impedance_delany_and_bazley(frequency=1000.0, flow_resistivity=200_000.0)
        assert z.real > 1.0  # real part above 1 for porous absorbers at mid frequencies
        assert z.imag < 0.0  # formula subtracts j·... so imaginary part is negative

    def test_delany_and_bazley_broadcasts(self):
        freqs = np.array([125.0, 500.0, 2000.0])
        z = impedance_delany_and_bazley(freqs, flow_resistivity=100_000.0)
        assert z.shape == freqs.shape
        # Real part decreases monotonically with frequency because the correction
        # term 9.08 (1000 f / σ)^{-0.75} shrinks as f grows.
        assert np.all(np.diff(z.real) < 0)

    def test_attenborough_returns_complex(self):
        z = impedance_attenborough(frequency=1000.0, flow_resistivity=200_000.0)
        assert z.real > 0.0
        assert z.imag < 0.0


class TestNumericalDistance:
    def test_magnitude_grows_with_distance(self):
        common = dict(impedance=2.0 + 1j, angle=np.pi / 4, wavenumber=2.0 * np.pi)
        w1 = numerical_distance(distance=1.0, **common)
        w10 = numerical_distance(distance=10.0, **common)
        assert abs(w10) > abs(w1)


class TestReflectionFactorSphericalWave:
    def test_returns_finite_complex(self):
        result = reflection_factor_spherical_wave(
            impedance=5.0 + 2j,
            angle=np.pi / 6,
            distance=2.0,
            wavenumber=10.0,
        )
        assert np.isfinite(result.real) and np.isfinite(result.imag)

    def test_broadcasts_over_frequency(self):
        k = np.array([1.0, 10.0, 100.0])
        result = reflection_factor_spherical_wave(
            impedance=3.0 + 1j,
            angle=np.pi / 4,
            distance=2.0,
            wavenumber=k,
        )
        assert result.shape == k.shape


class TestBoundary:
    def test_wavenumber_matches_formula(self):
        b = Boundary(frequency=343.0, flow_resistivity=100_000.0, soundspeed=343.0)
        assert b.wavenumber == pytest.approx(2.0 * np.pi)

    def test_wavenumber_vector(self):
        freqs = np.array([100.0, 200.0, 400.0])
        b = Boundary(frequency=freqs, flow_resistivity=100_000.0, soundspeed=343.0)
        expected = 2.0 * np.pi * freqs / 343.0
        np.testing.assert_allclose(b.wavenumber, expected)

    def test_impedance_delany_and_bazley_default(self):
        b = Boundary(frequency=1000.0, flow_resistivity=200_000.0, impedance_model='db')
        expected = impedance_delany_and_bazley(1000.0, 200_000.0)
        assert b.impedance == pytest.approx(expected)

    def test_impedance_attenborough_selected(self):
        b = Boundary(frequency=1000.0, flow_resistivity=200_000.0, impedance_model='att')
        expected = impedance_attenborough(1000.0, 200_000.0)
        assert b.impedance == pytest.approx(expected)

    def test_invalid_impedance_model_raises(self):
        b = Boundary(frequency=1000.0, flow_resistivity=200_000.0, impedance_model='bogus')
        with pytest.raises(ValueError, match="Incorrect impedance model"):
            _ = b.impedance

    def test_reflection_factor_requires_angle(self):
        b = Boundary(frequency=1000.0, flow_resistivity=200_000.0)
        with pytest.raises(AttributeError, match="self.angle has not been specified"):
            _ = b.reflection_factor

    def test_reflection_factor_spherical_requires_distance(self):
        b = Boundary(
            frequency=1000.0,
            flow_resistivity=200_000.0,
            angle=np.array([np.pi / 4]),
            reflection_model='spherical',
        )
        with pytest.raises(AttributeError, match="self.distance has not been specified"):
            _ = b.reflection_factor

    def test_reflection_factor_plane_shape(self):
        freqs = np.array([100.0, 500.0, 1000.0])
        angles = np.array([0.0, np.pi / 4])
        b = Boundary(frequency=freqs, flow_resistivity=200_000.0, angle=angles)
        R = b.reflection_factor
        assert R.shape == (len(angles), len(freqs))
