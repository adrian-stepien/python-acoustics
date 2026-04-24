"""
Tests for :class:`Acoustics.Octave.Octave`
"""

import numpy as np
import pytest

from acoustics.octave import Octave


class TestOctave:
    def test_interval(self):
        emin = 1.0
        emax = 4.0
        f = np.logspace(emin, emax, 50)

        o = Octave(interval=f)

        assert o.fmin == 10.0**emin
        assert o.fmax == 10.0**emax
        assert len(o.n) == len(o.center)

        o.unique = True
        assert len(o.n) == len(f)

    def test_minmax(self):
        fmin = 250.0
        fmax = 1000.0

        o = Octave(fmin=fmin, fmax=fmax)

        assert len(o.center) == 3  # 250, 500, and 1000 Hz
        assert len(o.n) == 3

    def test_default_octave_has_no_interval(self):
        o = Octave()
        assert o.interval is None

    def test_constructor_rejects_mixed_interval_and_bounds(self):
        with pytest.raises(ValueError, match="either interval or fmin/fmax"):
            Octave(interval=[100.0, 200.0], fmin=100.0)

    def test_fmin_requires_configuration(self):
        with pytest.raises(ValueError, match="fmin is undefined"):
            _ = Octave().fmin

    def test_fmax_requires_configuration(self):
        with pytest.raises(ValueError, match="fmax is undefined"):
            _ = Octave().fmax

    def test_setting_fmin_with_interval_raises(self):
        o = Octave(interval=[100.0, 200.0])
        with pytest.raises(ValueError, match="Cannot set fmin while interval is set"):
            o.fmin = 50.0

    def test_setting_fmax_with_interval_raises(self):
        o = Octave(interval=[100.0, 200.0])
        with pytest.raises(ValueError, match="Cannot set fmax while interval is set"):
            o.fmax = 250.0

    def test_setting_interval_with_bounds_raises(self):
        o = Octave(fmin=100.0, fmax=200.0)
        with pytest.raises(ValueError, match="Cannot set interval while fmin or fmax is set"):
            o.interval = [100.0, 200.0]

    def test_can_clear_interval_before_setting_bounds(self):
        o = Octave(interval=[100.0, 200.0])
        o.interval = None
        o.fmin = 80.0
        o.fmax = 250.0
        assert o.fmin == 80.0
        assert o.fmax == 250.0

    def test_can_clear_bounds_before_setting_interval(self):
        o = Octave(fmin=80.0, fmax=250.0)
        o.fmin = None
        o.fmax = None
        o.interval = [100.0, 200.0]
        np.testing.assert_allclose(o.interval, [100.0, 200.0])
