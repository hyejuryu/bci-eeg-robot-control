import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import mne
import numpy as np
from mne.datasets import eegbci
from scipy.signal import welch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "session-13"
FIGURE_DIR = PROJECT_ROOT / "figures" / "session-13"

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

FIGURE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

FEATURE_CSV_PATH = (
    RESULT_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_win-2s_step-1s_features.csv"
    )
)

SUMMARY_JSON_PATH = (
    RESULT_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha-win-2s-step-1s_summary.json"
    )
)

TIMESERIES_FIGURE_PATH = (
    FIGURE_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha-win-2s-step-1s_timeseries.png"
    )
)

SUBJECT = 1
RUNS = [1, 2]

RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

FILTER_LOW_HZ = 1.0
FILTER_HIGH_HZ = 40.0

TARGET_ANNOTATION = "T0"

WINDOW_LENGTH_SEC = 2.0
STEP_SIZE_SEC = 1.0
EXPECTED_WINDOWS_PER_RUN = 59

WELCH_N_PER_SEG = 160
WELCH_N_OVERLAP = 80
WELCH_N_FFT = 160

PSD_MIN_HZ = 1.0
PSD_MAX_HZ = 40.0

ALPHA_BAND = (8.0, 13.0)

FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

EXPECTED_TOTAL_ROWS = (
    EXPECTED_WINDOWS_PER_RUN * len(RUNS)
)

POSTERIOR_CHANNELS = [
    "Po3.",
    "Poz.",
    "Po4.",
    "O1..",
    "Oz..",
    "O2..",
]


def load_raw(run):
    file_path = eegbci.load_data(SUBJECT, [run])[0]

    raw = mne.io.read_raw_edf(
        file_path,
        preload=True,
        verbose=False,
    )

    return raw


def get_t0_interval(raw):
    t0_indices = np.where(
        raw.annotations.description == TARGET_ANNOTATION
    )[0]

    if len(t0_indices) != 1:
        raise ValueError(
            f"Expected exactly one {TARGET_ANNOTATION} annotation, "
            f"but found {len(t0_indices)}."
        )

    t0_index = t0_indices[0]

    onset = float(raw.annotations.onset[t0_index])
    duration = float(raw.annotations.duration[t0_index])
    end = onset + duration

    if not np.isfinite([onset, duration, end]).all():
        raise ValueError(
            f"{TARGET_ANNOTATION} annotation contains "
            "a non-finite value."
        )

    sfreq = float(raw.info["sfreq"])
    recording_duration = raw.n_times / sfreq

    if onset < 0:
        raise ValueError(
            f"{TARGET_ANNOTATION} onset is negative: {onset}"
        )

    if duration <= 0:
        raise ValueError(
            f"{TARGET_ANNOTATION} duration must be positive: "
            f"{duration}"
        )

    if end > recording_duration:
        raise ValueError(
            f"{TARGET_ANNOTATION} end ({end:.6f} s) exceeds "
            f"recording duration ({recording_duration:.6f} s)."
        )

    return onset, duration, end


def prepare_posterior_data(raw):
    missing_channels = [
        channel
        for channel in POSTERIOR_CHANNELS
        if channel not in raw.ch_names
    ]

    if missing_channels:
        raise ValueError(
            f"Missing posterior channels: {missing_channels}"
        )

    raw_filtered = raw.copy().filter(
        l_freq=FILTER_LOW_HZ,
        h_freq=FILTER_HIGH_HZ,
        verbose=False,
    )

    raw_posterior = raw_filtered.copy().pick(
        POSTERIOR_CHANNELS
    )

    posterior_channel_names = list(
        raw_posterior.ch_names
    )

    posterior_data = raw_posterior.get_data()

    if posterior_channel_names != POSTERIOR_CHANNELS:
        raise RuntimeError(
            "Posterior channel order does not match "
            "the configured order."
        )

    return posterior_data, posterior_channel_names


def generate_window_bounds(
    t0_onset,
    t0_end,
    sfreq,
    n_samples,
):
    window_length_samples = int(
        round(WINDOW_LENGTH_SEC * sfreq)
    )

    step_size_samples = int(
        round(STEP_SIZE_SEC * sfreq)
    )

    t0_start_sample = int(
        round(t0_onset * sfreq)
    )

    t0_end_sample = int(
        np.floor(t0_end * sfreq)
    )

    if window_length_samples <= 0:
        raise ValueError(
            "Window length must be at least one sample."
        )

    if step_size_samples <= 0:
        raise ValueError(
            "Step size must be at least one sample."
        )

    if t0_start_sample < 0:
        raise ValueError(
            f"T0 start sample is negative: "
            f"{t0_start_sample}"
        )

    if t0_end_sample > n_samples:
        raise ValueError(
            f"T0 end sample ({t0_end_sample}) exceeds "
            f"the available sample count ({n_samples})."
        )

    window_bounds = []

    start_sample_values = range(
        t0_start_sample,
        t0_end_sample - window_length_samples + 1,
        step_size_samples,
    )

    for window_index, start_sample in enumerate(
        start_sample_values
    ):
        stop_sample = (
            start_sample + window_length_samples
        )

        start_sec = start_sample / sfreq
        end_sec = stop_sample / sfreq

        window_bounds.append({
            "window_index": window_index,
            "start_sample": start_sample,
            "stop_sample": stop_sample,
            "start_sec": start_sec,
            "end_sec": end_sec,
        })

    if len(window_bounds) != EXPECTED_WINDOWS_PER_RUN:
        raise RuntimeError(
            f"Expected {EXPECTED_WINDOWS_PER_RUN} windows, "
            f"but generated {len(window_bounds)}."
        )

    return (
        window_bounds,
        window_length_samples,
        step_size_samples,
    )


def validate_window_slices(
    posterior_data,
    window_bounds,
    window_length_samples,
):
    expected_shape = (
        posterior_data.shape[0],
        window_length_samples,
    )

    first_window_shape = None
    second_window_shape = None
    last_window_shape = None

    for window_index, window_bound in enumerate(
        window_bounds
    ):
        start_sample = window_bound["start_sample"]
        stop_sample = window_bound["stop_sample"]

        window_data = posterior_data[
            :,
            start_sample:stop_sample,
        ]

        if window_data.shape != expected_shape:
            raise RuntimeError(
                f"Window {window_index} has shape "
                f"{window_data.shape}, "
                f"but expected {expected_shape}."
            )

        if window_index == 0:
            first_window_shape = window_data.shape

        if window_index == 1:
            second_window_shape = window_data.shape

        if window_index == len(window_bounds) - 1:
            last_window_shape = window_data.shape

    return {
        "validated_window_count": len(window_bounds),
        "expected_window_shape": expected_shape,
        "first_window_shape": first_window_shape,
        "second_window_shape": second_window_shape,
        "last_window_shape": last_window_shape,
    }


def compute_welch_psd(
    window_data,
    sfreq,
):
    if window_data.ndim != 2:
        raise ValueError(
            f"Expected 2D window data, "
            f"but received shape {window_data.shape}."
        )

    if window_data.shape[1] < WELCH_N_PER_SEG:
        raise ValueError(
            f"Window contains {window_data.shape[1]} samples, "
            f"but Welch requires at least "
            f"{WELCH_N_PER_SEG} samples per segment."
        )

    if WELCH_N_OVERLAP >= WELCH_N_PER_SEG:
        raise ValueError(
            "Welch overlap must be smaller than "
            "the segment length."
        )

    freqs, psd_data = welch(
        window_data,
        fs=sfreq,
        window="hann",
        nperseg=WELCH_N_PER_SEG,
        noverlap=WELCH_N_OVERLAP,
        nfft=WELCH_N_FFT,
        detrend="constant",
        return_onesided=True,
        scaling="density",
        axis=-1,
        average="mean",
    )

    frequency_mask = (
        (freqs >= PSD_MIN_HZ)
        & (freqs <= PSD_MAX_HZ)
    )

    freqs = freqs[frequency_mask]
    psd_data = psd_data[:, frequency_mask]

    if psd_data.shape[0] != window_data.shape[0]:
        raise RuntimeError(
            "PSD channel count does not match "
            "the input window channel count."
        )

    if psd_data.shape[1] != len(freqs):
        raise RuntimeError(
            "PSD frequency dimension does not match "
            "the frequency array length."
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


def extract_posterior_alpha_mean_psd(
    psd_data,
    freqs,
):
    if psd_data.ndim != 2:
        raise ValueError(
            f"Expected 2D PSD data, "
            f"but received shape {psd_data.shape}."
        )

    if freqs.ndim != 1:
        raise ValueError(
            f"Expected a 1D frequency array, "
            f"but received shape {freqs.shape}."
        )

    if psd_data.shape[1] != len(freqs):
        raise ValueError(
            "PSD frequency dimension does not match "
            "the frequency array length."
        )

    posterior_mean_psd = psd_data.mean(axis=0)

    alpha_mask = (
        (freqs >= ALPHA_BAND[0])
        & (freqs < ALPHA_BAND[1])
    )

    if not np.any(alpha_mask):
        raise RuntimeError(
            "No frequency bins were found inside "
            "the configured alpha band."
        )

    alpha_psd_values = posterior_mean_psd[
        alpha_mask
    ]

    posterior_alpha_mean_psd = float(
        alpha_psd_values.mean()
    )

    if not np.isfinite(posterior_alpha_mean_psd):
        raise ValueError(
            "Posterior alpha mean PSD is non-finite."
        )

    if posterior_alpha_mean_psd < 0:
        raise ValueError(
            "Posterior alpha mean PSD is negative."
        )

    return posterior_alpha_mean_psd


def extract_run_features(
    run,
    posterior_data,
    window_bounds,
    sfreq,
):
    feature_rows = []

    expected_window_shape = (
        posterior_data.shape[0],
        int(round(WINDOW_LENGTH_SEC * sfreq)),
    )

    for window_bound in window_bounds:
        start_sample = window_bound["start_sample"]
        stop_sample = window_bound["stop_sample"]

        window_data = posterior_data[
            :,
            start_sample:stop_sample,
        ]

        if window_data.shape != expected_window_shape:
            raise RuntimeError(
                f"Run {run}, window "
                f"{window_bound['window_index']} has shape "
                f"{window_data.shape}, "
                f"but expected {expected_window_shape}."
            )

        psd_data, freqs = compute_welch_psd(
            window_data=window_data,
            sfreq=sfreq,
        )

        posterior_alpha_mean_psd = (
            extract_posterior_alpha_mean_psd(
                psd_data=psd_data,
                freqs=freqs,
            )
        )

        window_start_sec = float(
            window_bound["start_sec"]
        )

        window_end_sec = float(
            window_bound["end_sec"]
        )

        window_center_sec = (
            window_start_sec + window_end_sec
        ) / 2.0

        feature_rows.append({
            "subject": SUBJECT,
            "run": run,
            "condition": RUN_LABELS[run],
            "window_index": int(
                window_bound["window_index"]
            ),
            "window_start_sec": window_start_sec,
            "window_end_sec": window_end_sec,
            "window_center_sec": window_center_sec,
            "start_sample": int(start_sample),
            "stop_sample": int(stop_sample),
            "n_samples": int(
                stop_sample - start_sample
            ),
            "feature_name": FEATURE_NAME,
            "feature_unit": FEATURE_UNIT,
            "posterior_alpha_mean_psd": (
                posterior_alpha_mean_psd
            ),
        })

    if len(feature_rows) != EXPECTED_WINDOWS_PER_RUN:
        raise RuntimeError(
            f"Run {run} produced {len(feature_rows)} "
            f"feature rows, but expected "
            f"{EXPECTED_WINDOWS_PER_RUN}."
        )

    return feature_rows


def build_summary(feature_rows):
    if len(feature_rows) != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(
            f"Expected {EXPECTED_TOTAL_ROWS} total rows, "
            f"but received {len(feature_rows)}."
        )

    summary = {
        "session": 13,
        "subject": SUBJECT,
        "runs": RUNS,
        "run_conditions": {
            str(run): RUN_LABELS[run]
            for run in RUNS
        },
        "feature_name": FEATURE_NAME,
        "feature_unit": FEATURE_UNIT,
        "feature_definition": {
            "channel_operation": (
                "Mean PSD across the six posterior "
                "channels at each frequency."
            ),
            "frequency_operation": (
                "Mean of the posterior mean PSD over "
                "8 <= f < 13 Hz."
            ),
        },
        "preprocessing": {
            "filter_low_hz": FILTER_LOW_HZ,
            "filter_high_hz": FILTER_HIGH_HZ,
            "filter_scope": (
                "Filtering was applied to the full run "
                "before sliding-window extraction."
            ),
        },
        "annotation": {
            "target_description": TARGET_ANNOTATION,
            "window_inclusion_rule": (
                "Only windows fully contained within "
                "the target annotation interval were used."
            ),
        },
        "posterior_channels": POSTERIOR_CHANNELS,
        "outer_window": {
            "window_length_sec": WINDOW_LENGTH_SEC,
            "step_size_sec": STEP_SIZE_SEC,
            "expected_windows_per_run": (
                EXPECTED_WINDOWS_PER_RUN
            ),
        },
        "welch": {
            "n_per_seg_samples": WELCH_N_PER_SEG,
            "n_overlap_samples": WELCH_N_OVERLAP,
            "n_fft_samples": WELCH_N_FFT,
            "scaling": "density",
            "average": "mean",
        },
        "psd_frequency_range_hz": {
            "minimum": PSD_MIN_HZ,
            "maximum": PSD_MAX_HZ,
        },
        "alpha_band_hz": {
            "lower_inclusive": ALPHA_BAND[0],
            "upper_exclusive": ALPHA_BAND[1],
        },
        "total_feature_rows": len(feature_rows),
        "by_run": {},
    }

    for run in RUNS:
        run_rows = [
            row
            for row in feature_rows
            if row["run"] == run
        ]

        if len(run_rows) != EXPECTED_WINDOWS_PER_RUN:
            raise RuntimeError(
                f"Run {run} contains {len(run_rows)} "
                f"rows in the summary input, "
                f"but expected "
                f"{EXPECTED_WINDOWS_PER_RUN}."
            )

        feature_values = np.array(
            [
                row["posterior_alpha_mean_psd"]
                for row in run_rows
            ],
            dtype=float,
        )

        summary["by_run"][str(run)] = {
            "condition": RUN_LABELS[run],
            "n_windows": len(run_rows),
            "first_window_start_sec": float(
                run_rows[0]["window_start_sec"]
            ),
            "last_window_end_sec": float(
                run_rows[-1]["window_end_sec"]
            ),
            "mean": float(
                feature_values.mean()
            ),
            "median": float(
                np.median(feature_values)
            ),
            "standard_deviation_population": float(
                feature_values.std(ddof=0)
            ),
            "minimum": float(
                feature_values.min()
            ),
            "maximum": float(
                feature_values.max()
            ),
        }

    return summary


def save_feature_csv(feature_rows):
    fieldnames = [
        "subject",
        "run",
        "condition",
        "window_index",
        "window_start_sec",
        "window_end_sec",
        "window_center_sec",
        "start_sample",
        "stop_sample",
        "n_samples",
        "feature_name",
        "feature_unit",
        "posterior_alpha_mean_psd",
    ]

    with open(
        FEATURE_CSV_PATH,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(feature_rows)

    return FEATURE_CSV_PATH


def save_summary_json(summary):
    with open(
        SUMMARY_JSON_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            summary,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return SUMMARY_JSON_PATH


def save_feature_timeseries_figure(
    feature_rows,
):
    plt.figure(
        figsize=(11, 6),
    )

    for run in RUNS:
        run_rows = sorted(
            [
                row
                for row in feature_rows
                if row["run"] == run
            ],
            key=lambda row: row["window_index"],
        )

        window_center_times = [
            row["window_center_sec"]
            for row in run_rows
        ]

        feature_values = [
            row["posterior_alpha_mean_psd"]
            for row in run_rows
        ]

        plt.plot(
            window_center_times,
            feature_values,
            marker="o",
            markersize=3,
            linewidth=1.2,
            label=RUN_LABELS[run],
        )

    plt.xlabel(
        "Window center time (s)"
    )

    plt.ylabel(
        "Posterior alpha mean PSD (V²/Hz)"
    )

    plt.title(
        "Window-Level Posterior Alpha Mean PSD"
    )

    plt.ticklabel_format(
        axis="y",
        style="sci",
        scilimits=(0, 0),
    )

    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        TIMESERIES_FIGURE_PATH,
        dpi=150,
    )

    plt.close()

    return TIMESERIES_FIGURE_PATH


def validate_first_window_welch_psd(
    posterior_data,
    window_bounds,
    sfreq,
):
    first_window = window_bounds[0]

    start_sample = first_window["start_sample"]
    stop_sample = first_window["stop_sample"]

    first_window_data = posterior_data[
        :,
        start_sample:stop_sample,
    ]

    psd_data, freqs = compute_welch_psd(
        window_data=first_window_data,
        sfreq=sfreq,
    )

    if len(freqs) < 2:
        raise RuntimeError(
            "At least two frequency bins are required "
            "to calculate frequency spacing."
        )

    frequency_spacing = float(
        freqs[1] - freqs[0]
    )

    alpha_mask = (
        (freqs >= ALPHA_BAND[0])
        & (freqs < ALPHA_BAND[1])
    )

    alpha_frequency_bins = freqs[alpha_mask]

    if len(alpha_frequency_bins) == 0:
        raise RuntimeError(
            "No frequency bins were found inside "
            "the configured alpha band."
        )

    welch_segment_step_samples = (
        WELCH_N_PER_SEG - WELCH_N_OVERLAP
    )

    welch_segment_count = (
        1
        + (
            first_window_data.shape[1]
            - WELCH_N_PER_SEG
        )
        // welch_segment_step_samples
    )

    return {
        "input_window_shape": first_window_data.shape,
        "psd_shape": psd_data.shape,
        "frequency_shape": freqs.shape,
        "first_frequency_hz": float(freqs[0]),
        "last_frequency_hz": float(freqs[-1]),
        "frequency_spacing_hz": frequency_spacing,
        "alpha_frequency_bins_hz": alpha_frequency_bins,
        "welch_segment_step_samples": (
            welch_segment_step_samples
        ),
        "welch_segment_count": welch_segment_count,
        "psd_non_finite_count": int(
            np.count_nonzero(
                ~np.isfinite(psd_data)
            )
        ),
    }


def validate_first_window_alpha_feature(
    posterior_data,
    window_bounds,
    sfreq,
):
    first_window = window_bounds[0]

    start_sample = first_window["start_sample"]
    stop_sample = first_window["stop_sample"]

    first_window_data = posterior_data[
        :,
        start_sample:stop_sample,
    ]

    psd_data, freqs = compute_welch_psd(
        window_data=first_window_data,
        sfreq=sfreq,
    )

    posterior_alpha_mean_psd = (
        extract_posterior_alpha_mean_psd(
            psd_data=psd_data,
            freqs=freqs,
        )
    )

    posterior_mean_psd = psd_data.mean(axis=0)

    alpha_mask = (
        (freqs >= ALPHA_BAND[0])
        & (freqs < ALPHA_BAND[1])
    )

    alpha_frequency_bins = freqs[alpha_mask]
    alpha_psd_values = posterior_mean_psd[
        alpha_mask
    ]

    return {
        "psd_shape": psd_data.shape,
        "posterior_mean_psd_shape": (
            posterior_mean_psd.shape
        ),
        "alpha_frequency_bins_hz": (
            alpha_frequency_bins
        ),
        "alpha_psd_values_shape": (
            alpha_psd_values.shape
        ),
        "posterior_alpha_mean_psd": (
            posterior_alpha_mean_psd
        ),
    }


def print_run_diagnostics(
    run,
    raw,
    t0_onset,
    t0_duration,
    t0_end,
    posterior_data,
    posterior_channel_names,
    window_bounds,
    window_length_samples,
    step_size_samples,
    window_validation,
    welch_validation,
    alpha_validation,
):
    sfreq = float(raw.info["sfreq"])

    raw_shape = (
        len(raw.ch_names),
        raw.n_times,
    )

    sample_count_duration = raw.n_times / sfreq
    last_sample_time = float(raw.times[-1])

    non_finite_count = int(
        np.count_nonzero(
            ~np.isfinite(posterior_data)
        )
    )

    first_window = window_bounds[0]
    second_window = window_bounds[1]
    last_window = window_bounds[-1]

    print("\n========================================")
    print("Run:", run)
    print("Condition:", RUN_LABELS[run])
    print("Raw shape:", raw_shape)
    print("Sampling frequency:", sfreq, "Hz")

    print(
        "Sample-count duration:",
        f"{sample_count_duration:.6f}",
        "s",
    )

    print(
        "Last sample time:",
        f"{last_sample_time:.6f}",
        "s",
    )

    print(
        "T0 onset:",
        f"{t0_onset:.6f}",
        "s",
    )

    print(
        "T0 duration:",
        f"{t0_duration:.6f}",
        "s",
    )

    print(
        "T0 end:",
        f"{t0_end:.6f}",
        "s",
    )

    print(
        "Posterior channel names:",
        posterior_channel_names,
    )

    print(
        "Posterior data shape:",
        posterior_data.shape,
    )

    print(
        "Non-finite value count:",
        non_finite_count,
    )

    print(
        "Window length:",
        WINDOW_LENGTH_SEC,
        "s",
    )

    print(
        "Step size:",
        STEP_SIZE_SEC,
        "s",
    )

    print(
        "Window length in samples:",
        window_length_samples,
    )

    print(
        "Step size in samples:",
        step_size_samples,
    )

    print(
        "Number of windows:",
        len(window_bounds),
    )

    print(
        "First window:",
        f"{first_window['start_sec']:.1f}"
        f"–{first_window['end_sec']:.1f} s,",
        f"samples "
        f"{first_window['start_sample']}:"
        f"{first_window['stop_sample']}",
    )

    print(
        "Second window:",
        f"{second_window['start_sec']:.1f}"
        f"–{second_window['end_sec']:.1f} s,",
        f"samples "
        f"{second_window['start_sample']}:"
        f"{second_window['stop_sample']}",
    )

    print(
        "Last window:",
        f"{last_window['start_sec']:.1f}"
        f"–{last_window['end_sec']:.1f} s,",
        f"samples "
        f"{last_window['start_sample']}:"
        f"{last_window['stop_sample']}",
    )

    print(
        "Validated window slices:",
        window_validation["validated_window_count"],
    )

    print(
        "Expected window data shape:",
        window_validation["expected_window_shape"],
    )

    print(
        "First window data shape:",
        window_validation["first_window_shape"],
    )

    print(
        "Second window data shape:",
        window_validation["second_window_shape"],
    )

    print(
        "Last window data shape:",
        window_validation["last_window_shape"],
    )

    print(
        "Welch n_per_seg:",
        WELCH_N_PER_SEG,
    )

    print(
        "Welch n_overlap:",
        WELCH_N_OVERLAP,
    )

    print(
        "Welch n_fft:",
        WELCH_N_FFT,
    )

    print(
        "Welch segment step in samples:",
        welch_validation[
            "welch_segment_step_samples"
        ],
    )

    print(
        "Welch segments in first window:",
        welch_validation[
            "welch_segment_count"
        ],
    )

    print(
        "First-window input shape:",
        welch_validation[
            "input_window_shape"
        ],
    )

    print(
        "First-window PSD shape:",
        welch_validation[
            "psd_shape"
        ],
    )

    print(
        "Frequency array shape:",
        welch_validation[
            "frequency_shape"
        ],
    )

    print(
        "PSD frequency range:",
        f"{welch_validation['first_frequency_hz']:.1f}"
        "–"
        f"{welch_validation['last_frequency_hz']:.1f}",
        "Hz",
    )

    print(
        "Frequency spacing:",
        f"{welch_validation['frequency_spacing_hz']:.1f}",
        "Hz",
    )

    print(
        "Alpha frequency bins:",
        welch_validation[
            "alpha_frequency_bins_hz"
        ],
    )

    print(
        "PSD non-finite value count:",
        welch_validation[
            "psd_non_finite_count"
        ],
    )

    if non_finite_count != 0:
        raise ValueError(
            f"Posterior data contains "
            f"{non_finite_count} non-finite values."
        )

    print(
        "Posterior mean PSD shape:",
        alpha_validation[
            "posterior_mean_psd_shape"
        ],
    )

    print(
        "Alpha frequency bins for feature:",
        alpha_validation[
            "alpha_frequency_bins_hz"
        ],
    )

    print(
        "Alpha PSD values shape:",
        alpha_validation[
            "alpha_psd_values_shape"
        ],
    )

    print(
        "First-window posterior alpha mean PSD:",
        f"{alpha_validation['posterior_alpha_mean_psd']:.12e}",
        "V^2/Hz",
    )


def main():
    all_feature_rows = []

    for run in RUNS:
        raw = load_raw(run)

        t0_onset, t0_duration, t0_end = (
            get_t0_interval(raw)
        )

        posterior_data, posterior_channel_names = (
            prepare_posterior_data(raw)
        )

        (
            window_bounds,
            window_length_samples,
            step_size_samples,
        ) = generate_window_bounds(
            t0_onset=t0_onset,
            t0_end=t0_end,
            sfreq=float(raw.info["sfreq"]),
            n_samples=int(raw.n_times),
        )

        window_validation = validate_window_slices(
            posterior_data=posterior_data,
            window_bounds=window_bounds,
            window_length_samples=window_length_samples,
        )

        welch_validation = (
            validate_first_window_welch_psd(
                posterior_data=posterior_data,
                window_bounds=window_bounds,
                sfreq=float(raw.info["sfreq"]),
            )
        )

        alpha_validation = (
            validate_first_window_alpha_feature(
                posterior_data=posterior_data,
                window_bounds=window_bounds,
                sfreq=float(raw.info["sfreq"]),
            )
        )

        run_feature_rows = extract_run_features(
            run=run,
            posterior_data=posterior_data,
            window_bounds=window_bounds,
            sfreq=float(raw.info["sfreq"]),
        )

        all_feature_rows.extend(
            run_feature_rows
        )

        print_run_diagnostics(
            run=run,
            raw=raw,
            t0_onset=t0_onset,
            t0_duration=t0_duration,
            t0_end=t0_end,
            posterior_data=posterior_data,
            posterior_channel_names=posterior_channel_names,
            window_bounds=window_bounds,
            window_length_samples=window_length_samples,
            step_size_samples=step_size_samples,
            window_validation=window_validation,
            welch_validation=welch_validation,
            alpha_validation=alpha_validation,
        )

    if len(all_feature_rows) != EXPECTED_TOTAL_ROWS:
        raise RuntimeError(
            f"Expected {EXPECTED_TOTAL_ROWS} total "
            f"feature rows, but generated "
            f"{len(all_feature_rows)}."
        )

    summary = build_summary(
        feature_rows=all_feature_rows
    )

    csv_path = save_feature_csv(
        feature_rows=all_feature_rows
    )

    json_path = save_summary_json(
        summary=summary
    )

    figure_path = (
        save_feature_timeseries_figure(
            feature_rows=all_feature_rows
        )
    )

    print("\n========================================")
    print(
        "Total feature rows:",
        len(all_feature_rows),
    )

    for run in RUNS:
        run_summary = summary["by_run"][
            str(run)
        ]

        print(
            f"Run {run} window count:",
            run_summary["n_windows"],
        )

        print(
            f"Run {run} feature mean:",
            f"{run_summary['mean']:.12e}",
            FEATURE_UNIT,
        )

    print("Saved feature CSV:", csv_path)
    print("Saved summary JSON:", json_path)
    print(
        "Saved time-series figure:",
        figure_path,
    )

    print(
        "\nSession 13 Step 6 completed: "
        "118 window-level posterior alpha "
        "feature rows and session outputs saved."
    )

if __name__ == "__main__":
    main()


