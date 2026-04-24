import contextlib
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pytest

from acoustics import Signal


def test_wav():
    """Test writing to and reading from wav file."""

    duration = 5.0
    fs = 10025
    samples = int(fs * duration)
    channels = 3
    values = np.random.randn(channels, samples)

    signal = Signal(values, fs)
    signal.normalize(inplace=True)

    with tempfile.TemporaryFile() as file:
        signal.to_wav(file)
        file.seek(0)
        signal = Signal.from_wav(file)
        assert signal.samples == samples
        assert signal.fs == fs
        assert signal.channels == channels


class TestSignal:
    # (channels, samples, sample rate)
    @pytest.fixture(params=[(1, 88200, 22050), (3, 88200, 22050), (3, 88200, 44100)])
    def signal(self, request):
        return Signal(np.random.randn(request.param[0], request.param[1]), request.param[2])

    def test_calibrate_to_scalar(self, signal):
        # Scalar decibel
        signal.calibrate_to(100.0)
        signal.copy().calibrate_to(100.0, inplace=True)

    def test_calibrate_to_channels(self, signal):
        # Value per channel. Note that [...,None] is required!
        signal.calibrate_to((np.ones(signal.channels) * 100.0)[..., None])
        signal.copy().calibrate_to((np.ones(signal.channels) * 100.0)[..., None], inplace=True)

    def test_calibrate_to_samples(self, signal):
        # Value per samples
        signal.calibrate_to(np.ones(signal.samples))
        signal.copy().calibrate_to(np.ones(signal.samples), inplace=True)

    def test_calibrate_to_samples_channels(self, signal):
        # Value per sample per channel
        signal.calibrate_to(np.ones(signal.shape))
        signal.copy().calibrate_to(np.ones(signal.shape), inplace=True)

    def test_calibrate_with(self, signal):
        calibration_signal_level = 50.0
        decibel = 94.0
        calibration_signal = Signal(np.random.randn(signal.samples), signal.fs).calibrate_to(calibration_signal_level)

        out = signal.calibrate_with(calibration_signal, decibel)
        assert ((out.leq() - signal.leq()).mean() - (decibel - calibration_signal_level)) < 0.01

    def test_decimate(self, signal):
        factor = 4
        decimated = signal.decimate(factor)
        assert signal.fs / factor == decimated.fs

    def test_upsample(self, signal):
        factor = 2
        assert (signal.upsample(factor).fs / signal.fs) == factor

    def test_gain_scalar(self, signal):
        gain = +20.0
        # `.all()` because of multichannel signals
        assert (np.abs(signal.gain(gain).leq() - (signal.leq() + gain)) < 0.01).all()
        assert (np.abs(signal.copy().gain(gain, inplace=True).leq() - (signal.leq() + gain)) < 0.01).all()

    def test_correlate(self, signal):
        signal = signal[..., 0:100]
        if signal.channels > 1:  # Multichannel is not supported
            with pytest.raises(ValueError):
                assert (signal.correlate() == signal.correlate(signal)).all()
        else:
            assert (signal.correlate() == signal.correlate(signal)).all()

    def test_plot(self, signal):
        signal.plot()
        plt.close("all")

    def test_plot_levels(self, signal):
        signal.plot_levels()
        signal.plot_levels(method='average', time=1.0)
        signal.plot_levels(method='weighting', time=1.0)
        plt.close("all")

    def test_plot_octaves(self, signal):
        signal.plot_octaves()
        plt.close("all")

    def test_plot_third_octaves(self, signal):
        signal.plot_third_octaves()
        plt.close("all")

    def test_plot_fractional_octaves(self, signal):
        signal.plot_fractional_octaves(3)
        signal.plot_fractional_octaves(6)
        signal.plot_fractional_octaves(9)
        plt.close("all")

    def test_plot_power_spectrum(self, signal):
        signal.plot_power_spectrum()
        plt.close("all")

    def test_plot_phase_spectrum(self, signal):
        signal.plot_phase_spectrum()
        plt.close("all")

    def test_plot_spectrogram(self, signal):
        if signal.channels > 1:
            with pytest.raises(ValueError):
                signal.plot_spectrogram()
        else:
            # easy way to skip mpl 1.3.1 specgram mode issue
            with contextlib.suppress(NotImplementedError):
                signal.plot_spectrogram()
        plt.close("all")

    def test_pickling(self, signal):
        import pickle

        p = pickle.dumps(signal)
        obj = pickle.loads(p)

        assert (obj == signal).all()
        assert obj.fs == signal.fs
        assert type(obj) is type(signal)
