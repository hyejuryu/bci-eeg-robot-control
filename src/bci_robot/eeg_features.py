"""
Reusable EEG windowing and spectral-feature functions.

The functions in this module operate on NumPy arrays
and numeric parameters. They do not load a specific
dataset or write session output files.
"""

import numpy as np
from scipy.signal import welch


def generate_window_bounds(
    interval_start_sec,
    interval_end_sec,
    sfreq,
    n_samples,
    window_length_sec,
    step_size_sec,
):
    """
    Generate fixed-length window boundaries.

    Input:
        interval_start_sec:
            Start of the analysis interval in seconds.
        interval_end_sec:
            End of the analysis interval in seconds.
        sfreq:
            Sampling frequency in Hz.
        n_samples:
            Total available sample count.
        window_length_sec:
            Outer-window length in seconds.
        step_size_sec:
            Window-update step in seconds.

    Output:
        window_bounds:
            One dictionary per fully contained window.
        window_length_samples:
            Window length converted to samples.
        step_size_samples:
            Step size converted to samples.
    """

    window_length_samples = int(
        round(window_length_sec * sfreq)
    )

    step_size_samples = int(
        round(step_size_sec * sfreq)
    )

    interval_start_sample = int(
        round(interval_start_sec * sfreq)
    )

    interval_end_sample = int(
        np.floor(interval_end_sec * sfreq)
    )

    if window_length_samples <= 0:
        raise ValueError(
            "Window length must be at least "
            "one sample."
        )

    if step_size_samples <= 0:
        raise ValueError(
            "Step size must be at least "
            "one sample."
        )

    if interval_start_sample < 0:
        raise ValueError(
            "Analysis-interval start sample "
            f"is negative: {interval_start_sample}"
        )

    if interval_end_sample > n_samples:
        raise ValueError(
            "Analysis-interval end sample "
            f"({interval_end_sample}) exceeds "
            f"the available sample count "
            f"({n_samples})."
        )

    available_samples = (
        interval_end_sample
        - interval_start_sample
    )

    if available_samples < window_length_samples:
        raise ValueError(
            "The analysis interval is shorter "
            "than the configured window length."
        )

    expected_window_count = (
        1
        + (
            available_samples
            - window_length_samples
        )
        // step_size_samples
    )

    window_bounds = []

    start_sample_values = range(
        interval_start_sample,
        (
            interval_end_sample
            - window_length_samples
            + 1
        ),
        step_size_samples,
    )

    for window_index, start_sample in enumerate(
        start_sample_values
    ):
        stop_sample = (
            start_sample
            + window_length_samples
        )

        window_bounds.append({
            "window_index": int(
                window_index
            ),
            "start_sample": int(
                start_sample
            ),
            "stop_sample": int(
                stop_sample
            ),
            "start_sec": float(
                start_sample / sfreq
            ),
            "end_sec": float(
                stop_sample / sfreq
            ),
        })

    if len(window_bounds) != expected_window_count:
        raise RuntimeError(
            f"Expected {expected_window_count} "
            "windows, but generated "
            f"{len(window_bounds)}."
        )

    return (
        window_bounds,
        window_length_samples,
        step_size_samples,
    )


def compute_welch_psd(
    window_data,
    sfreq,
    *,
    n_per_seg,
    n_overlap,
    n_fft,
    psd_min_hz,
    psd_max_hz,
):
    """
    Calculate channel-wise Welch PSD.

    Input:
        window_data:
            Two-dimensional NumPy array with shape
            (channels, samples).
        sfreq:
            Sampling frequency in Hz.
        n_per_seg, n_overlap, n_fft:
            Welch parameters in samples.
        psd_min_hz, psd_max_hz:
            Inclusive frequency range retained
            in the returned PSD.

    Output:
        psd_data:
            PSD array with shape
            (channels, frequencies).
        freqs:
            One-dimensional frequency array.
    """

    if window_data.ndim != 2:
        raise ValueError(
            "Expected two-dimensional window "
            f"data, but received shape "
            f"{window_data.shape}."
        )

    if window_data.shape[1] < n_per_seg:
        raise ValueError(
            f"Window contains "
            f"{window_data.shape[1]} samples, "
            "but Welch requires at least "
            f"{n_per_seg} samples per segment."
        )

    if n_overlap >= n_per_seg:
        raise ValueError(
            "Welch overlap must be smaller "
            "than the segment length."
        )

    freqs, psd_data = welch(
        window_data,
        fs=sfreq,
        window="hann",
        nperseg=n_per_seg,
        noverlap=n_overlap,
        nfft=n_fft,
        detrend="constant",
        return_onesided=True,
        scaling="density",
        axis=-1,
        average="mean",
    )

    frequency_mask = (
        (freqs >= psd_min_hz)
        & (freqs <= psd_max_hz)
    )

    freqs = freqs[
        frequency_mask
    ]

    psd_data = psd_data[
        :,
        frequency_mask,
    ]

    if psd_data.shape[0] != (
        window_data.shape[0]
    ):
        raise RuntimeError(
            "PSD channel count does not match "
            "the input-window channel count."
        )

    if psd_data.shape[1] != len(freqs):
        raise RuntimeError(
            "PSD frequency dimension does not "
            "match the frequency-array length."
        )

    if not np.isfinite(psd_data).all():
        raise ValueError(
            "Welch PSD contains non-finite values."
        )

    if not np.isfinite(freqs).all():
        raise ValueError(
            "Welch frequency array contains "
            "non-finite values."
        )

    return psd_data, freqs


def extract_mean_band_psd(
    psd_data,
    freqs,
    *,
    band_low_hz,
    band_high_hz,
):
    """
    Average PSD across channels and a frequency band.

    Input:
        psd_data:
            Two-dimensional PSD array with shape
            (channels, frequencies).
        freqs:
            One-dimensional frequency array.
        band_low_hz:
            Inclusive lower band boundary.
        band_high_hz:
            Exclusive upper band boundary.

    Calculation:
        1. Average PSD across the input channels.
        2. Select band_low_hz <= f < band_high_hz.
        3. Average the selected frequency bins.

    Output:
        One scalar mean-band PSD value.
    """

    if psd_data.ndim != 2:
        raise ValueError(
            "Expected two-dimensional PSD data, "
            f"but received shape "
            f"{psd_data.shape}."
        )

    if freqs.ndim != 1:
        raise ValueError(
            "Expected a one-dimensional "
            "frequency array, but received "
            f"shape {freqs.shape}."
        )

    if psd_data.shape[1] != len(freqs):
        raise ValueError(
            "PSD frequency dimension does not "
            "match the frequency-array length."
        )

    channel_mean_psd = psd_data.mean(
        axis=0
    )

    band_mask = (
        (freqs >= band_low_hz)
        & (freqs < band_high_hz)
    )

    if not np.any(band_mask):
        raise RuntimeError(
            "No frequency bins were found "
            "inside the configured band."
        )

    band_psd_values = channel_mean_psd[
        band_mask
    ]

    mean_band_psd = float(
        band_psd_values.mean()
    )

    if not np.isfinite(mean_band_psd):
        raise ValueError(
            "Mean-band PSD is non-finite."
        )

    if mean_band_psd < 0:
        raise ValueError(
            "Mean-band PSD is negative."
        )

    return mean_band_psd