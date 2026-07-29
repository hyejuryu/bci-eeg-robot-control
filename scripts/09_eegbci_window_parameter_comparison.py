# Session 14 window-parameter comparison.
# Runs five predefined window/step configurations
# and validates configuration-dependent feature outputs.

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import mne
import numpy as np
from mne.datasets import eegbci

from bci_robot.eeg_features import (
    compute_welch_psd,
    extract_mean_band_psd,
    generate_window_bounds,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "session-14"
FIGURE_DIR = PROJECT_ROOT / "figures" / "session-14"

# Keep intermediate validation runs from creating
# incomplete Session 14 output files.
SAVE_OUTPUTS = True
PRINT_DETAILED_DIAGNOSTICS = False

RESULT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

FIGURE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


OUTPUT_PREFIX = (
    "eegbci_subject-001_runs-01-02_"
    "posterior-alpha"
)

WINDOW_FEATURE_CSV_PATH = (
    RESULT_DIR
    / f"{OUTPUT_PREFIX}_window-features.csv"
)

CONDITION_SUMMARY_CSV_PATH = (
    RESULT_DIR
    / f"{OUTPUT_PREFIX}_condition-summary.csv"
)

CONFIGURATION_COMPARISON_CSV_PATH = (
    RESULT_DIR
    / (
        f"{OUTPUT_PREFIX}_"
        "configuration-comparison.csv"
    )
)

METADATA_JSON_PATH = (
    RESULT_DIR
    / (
        f"{OUTPUT_PREFIX}_"
        "parameter-comparison_metadata.json"
    )
)

WINDOW_LENGTH_FIGURE_PATH = (
    FIGURE_DIR
    / (
        f"{OUTPUT_PREFIX}_"
        "window-length-comparison.png"
    )
)

STEP_SIZE_FIGURE_PATH = (
    FIGURE_DIR
    / (
        f"{OUTPUT_PREFIX}_"
        "step-size-comparison.png"
    )
)

LOCAL_DECOMPOSITION_CSV_PATH = (
    RESULT_DIR
    / (
        "eegbci_subject-001_run-01_"
        "posterior-alpha_local-decomposition_"
        "center-25s.csv"
    )
)

SELECTED_BASELINE_CONFIGURATION_ID = (
    "win-2s_step-1s"
)

SELECTED_BASELINE_VERSION = "v0.1"

SUBJECT = 1
RUNS = [1, 2]

RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

EYES_OPEN_RUN = 1
EYES_CLOSED_RUN = 2

FILTER_LOW_HZ = 1.0
FILTER_HIGH_HZ = 40.0

TARGET_ANNOTATION = "T0"

CONFIGURATIONS = [
    {
        "configuration_id": "win-2s_step-1s",
        "window_length_sec": 2.0,
        "step_size_sec": 1.0,
    },
    {
        "configuration_id": "win-1s_step-1s",
        "window_length_sec": 1.0,
        "step_size_sec": 1.0,
    },
    {
        "configuration_id": "win-4s_step-1s",
        "window_length_sec": 4.0,
        "step_size_sec": 1.0,
    },
    {
        "configuration_id": "win-2s_step-0p5s",
        "window_length_sec": 2.0,
        "step_size_sec": 0.5,
    },
    {
        "configuration_id": "win-2s_step-2s",
        "window_length_sec": 2.0,
        "step_size_sec": 2.0,
    },
]

WINDOW_LENGTH_COMPARISON_IDS = [
    "win-1s_step-1s",
    "win-2s_step-1s",
    "win-4s_step-1s",
]

CONFIGURATION_DISPLAY_LABELS = {
    "win-1s_step-1s": "1 s window / 1 s step",
    "win-2s_step-1s": "2 s window / 1 s step",
    "win-4s_step-1s": "4 s window / 1 s step",
    "win-2s_step-0p5s": "2 s window / 0.5 s step",
    "win-2s_step-2s": "2 s window / 2 s step",
}

# 절대허용오차와 상대 오차 
SHARED_WINDOW_RTOL = 1e-12
SHARED_WINDOW_ATOL = 0.0

WELCH_N_PER_SEG = 160
WELCH_N_OVERLAP = 80
WELCH_N_FFT = 160

PSD_MIN_HZ = 1.0
PSD_MAX_HZ = 40.0

ALPHA_BAND = (8.0, 13.0)

FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

POSTERIOR_CHANNELS = [
    "Po3.",
    "Poz.",
    "Po4.",
    "O1..",
    "Oz..",
    "O2..",
]


def calculate_outer_window_overlap_fraction(
    window_length_sec,
    step_size_sec,
):
    if not np.isfinite(
        [window_length_sec, step_size_sec]
    ).all():
        raise ValueError(
            "Window length and step size must "
            "contain finite values."
        )

    if window_length_sec <= 0:
        raise ValueError(
            "Window length must be positive."
        )

    if step_size_sec <= 0:
        raise ValueError(
            "Step size must be positive."
        )

    overlap_duration_sec = max(
        0.0,
        window_length_sec - step_size_sec,
    )

    overlap_fraction = (
        overlap_duration_sec
        / window_length_sec
    )

    return float(overlap_fraction)


def calculate_welch_segment_count(
    window_length_samples,
):
    welch_segment_step_samples = (
        WELCH_N_PER_SEG - WELCH_N_OVERLAP
    )

    if welch_segment_step_samples <= 0:
        raise ValueError(
            "Welch segment step must be positive."
        )

    if window_length_samples < WELCH_N_PER_SEG:
        raise ValueError(
            "Outer window is shorter than one "
            "Welch segment."
        )

    welch_segment_count = (
        1
        + (
            window_length_samples
            - WELCH_N_PER_SEG
        )
        // welch_segment_step_samples
    )

    return int(welch_segment_count)


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


def extract_run_features(
    run,
    posterior_data,
    window_bounds,
    sfreq,
    configuration_id,
    window_length_sec,
    step_size_sec,
):
    feature_rows = []

    window_length_samples = int(
        round(window_length_sec * sfreq)
    )

    expected_window_shape = (
        posterior_data.shape[0],
        window_length_samples,
    )

    outer_window_overlap_fraction = (
        calculate_outer_window_overlap_fraction(
            window_length_sec=window_length_sec,
            step_size_sec=step_size_sec,
        )
    )

    welch_segment_count = (
        calculate_welch_segment_count(
            window_length_samples=(
                window_length_samples
            )
        )
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
            n_per_seg=WELCH_N_PER_SEG,
            n_overlap=WELCH_N_OVERLAP,
            n_fft=WELCH_N_FFT,
            psd_min_hz=PSD_MIN_HZ,
            psd_max_hz=PSD_MAX_HZ,
        )

        posterior_alpha_mean_psd = (
        extract_mean_band_psd(
            psd_data=psd_data,
            freqs=freqs,
            band_low_hz=ALPHA_BAND[0],
            band_high_hz=ALPHA_BAND[1],
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
            "configuration_id": configuration_id,
            "window_length_sec": float(
                window_length_sec
            ),
            "step_size_sec": float(
                step_size_sec
            ),
            "outer_window_overlap_fraction": (
                outer_window_overlap_fraction
            ),
            "welch_segment_count": (
                welch_segment_count
            ),
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

    if len(feature_rows) != len(window_bounds):
        raise RuntimeError(
            f"Run {run} produced {len(feature_rows)} "
            f"feature rows, but expected "
            f"{len(window_bounds)}."
        )

    return feature_rows


def build_summary(
    feature_rows,
    expected_window_counts,
    configuration_id,
    window_length_sec,
    step_size_sec,
):
    expected_total_rows = sum(
        expected_window_counts.values()
    )

    if len(feature_rows) != expected_total_rows:
        raise RuntimeError(
            f"Expected {expected_total_rows} total rows, "
            f"but received {len(feature_rows)}."
        )

    summary = {
        "session": 14,
        "configuration_id": configuration_id,
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
            "window_length_sec": window_length_sec,
            "step_size_sec": step_size_sec,
            "window_counts_by_run": {
                str(run): expected_window_counts[run]
                for run in RUNS
            },
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

        expected_run_rows = (
            expected_window_counts[run]
        )

        if len(run_rows) != expected_run_rows:
            raise RuntimeError(
                f"Run {run} contains {len(run_rows)} "
                f"rows in the summary input, "
                f"but expected {expected_run_rows}."
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


def save_csv_rows(
    rows,
    fieldnames,
    output_path,
):
    if len(rows) == 0:
        raise ValueError(
            f"No rows were provided for {output_path.name}."
        )

    if len(fieldnames) == 0:
        raise ValueError(
            f"No field names were provided for "
            f"{output_path.name}."
        )

    for row_index, row in enumerate(rows):
        missing_fields = [
            fieldname
            for fieldname in fieldnames
            if fieldname not in row
        ]

        extra_fields = [
            fieldname
            for fieldname in row
            if fieldname not in fieldnames
        ]

        if missing_fields:
            raise RuntimeError(
                f"Row {row_index} for "
                f"{output_path.name} is missing fields: "
                f"{missing_fields}"
            )

        if extra_fields:
            raise RuntimeError(
                f"Row {row_index} for "
                f"{output_path.name} contains "
                f"unexpected fields: {extra_fields}"
            )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    with open(
        output_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        saved_fieldnames = reader.fieldnames
        saved_rows = list(reader)

    if saved_fieldnames != fieldnames:
        raise RuntimeError(
            f"Saved CSV header mismatch for "
            f"{output_path.name}."
        )

    if len(saved_rows) != len(rows):
        raise RuntimeError(
            f"Saved CSV row-count mismatch for "
            f"{output_path.name}: expected "
            f"{len(rows)}, found {len(saved_rows)}."
        )

    return output_path


def save_window_feature_csv(
    feature_rows,
):
    fieldnames = [
        "subject",
        "run",
        "condition",
        "configuration_id",
        "window_length_sec",
        "step_size_sec",
        "outer_window_overlap_fraction",
        "welch_segment_count",
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

    return save_csv_rows(
        rows=feature_rows,
        fieldnames=fieldnames,
        output_path=WINDOW_FEATURE_CSV_PATH,
    )


def save_condition_summary_csv(
    condition_summary_rows,
):
    fieldnames = [
        "subject",
        "configuration_id",
        "run",
        "condition",
        "n_windows",
        "window_length_sec",
        "step_size_sec",
        "outer_window_overlap_fraction",
        "welch_segment_count",
        "feature_name",
        "feature_unit",
        "median",
        "q25",
        "q75",
        "iqr",
        "iqr_over_median",
        "mean",
        "standard_deviation_population",
        "minimum",
        "q05",
        "q95",
        "maximum",
    ]

    return save_csv_rows(
        rows=condition_summary_rows,
        fieldnames=fieldnames,
        output_path=CONDITION_SUMMARY_CSV_PATH,
    )


def save_configuration_comparison_csv(
    configuration_comparison_rows,
):
    fieldnames = [
        "subject",
        "configuration_id",
        "eyes_open_n_windows",
        "eyes_closed_n_windows",
        "eyes_open_median",
        "eyes_closed_median",
        "median_ratio_ec_over_eo",
        "g90_ec_q05_minus_eo_q95",
        "grange_ec_min_minus_eo_max",
        "pairwise_ordering_fraction",
        "pairwise_greater_count",
        "pairwise_tie_count",
        "pairwise_lower_count",
        "total_pair_count",
    ]

    return save_csv_rows(
        rows=configuration_comparison_rows,
        fieldnames=fieldnames,
        output_path=(
            CONFIGURATION_COMPARISON_CSV_PATH
        ),
    )


def build_metadata(
    feature_rows,
    condition_summary_rows,
    configuration_comparison_rows,
    shared_window_validation,
    configuration_run_validation,
):
    if len(feature_rows) == 0:
        raise ValueError(
            "Feature rows are required to build metadata."
        )

    sampling_frequency_values = {
        round(
            float(row["n_samples"])
            / float(row["window_length_sec"]),
            12,
        )
        for row in feature_rows
    }

    if len(sampling_frequency_values) != 1:
        raise RuntimeError(
            "Feature rows imply inconsistent "
            "sampling frequencies: "
            f"{sorted(sampling_frequency_values)}"
        )

    sampling_frequency_hz = float(
        next(iter(sampling_frequency_values))
    )

    configuration_records = []

    for configuration in CONFIGURATIONS:
        configuration_id = configuration[
            "configuration_id"
        ]

        validation_matches = [
            row
            for row in configuration_run_validation
            if row["configuration_id"]
            == configuration_id
        ]

        if len(validation_matches) != len(RUNS):
            raise RuntimeError(
                "Expected one structure-validation "
                "row per run for "
                f"{configuration_id}, but found "
                f"{len(validation_matches)}."
            )

        first_validation_row = (
            validation_matches[0]
        )

        window_counts_by_run = {
            str(row["run"]): int(
                row["n_windows"]
            )
            for row in validation_matches
        }

        first_available_time_sec = float(
            configuration["window_length_sec"]
        )

        configuration_records.append({
            "configuration_id": configuration_id,
            "window_length_sec": float(
                configuration[
                    "window_length_sec"
                ]
            ),
            "step_size_sec": float(
                configuration[
                    "step_size_sec"
                ]
            ),
            "first_available_time_sec": (
                first_available_time_sec
            ),
            "outer_window_overlap_fraction": float(
                first_validation_row[
                    "outer_window_overlap_fraction"
                ]
            ),
            "welch_segment_count": int(
                first_validation_row[
                    "welch_segment_count"
                ]
            ),
            "window_counts_by_run": (
                window_counts_by_run
            ),
        })

    selected_baseline_matches = [
        record
        for record in configuration_records
        if record["configuration_id"]
        == SELECTED_BASELINE_CONFIGURATION_ID
    ]

    if len(selected_baseline_matches) != 1:
        raise RuntimeError(
            "Expected exactly one selected "
            "baseline configuration record for "
            f"{SELECTED_BASELINE_CONFIGURATION_ID}, "
            f"but found "
            f"{len(selected_baseline_matches)}."
        )

    selected_baseline_record = (
        selected_baseline_matches[0]
    )

    metadata = {
        "session": 14,
        "analysis_name": (
            "EEGBCI posterior-alpha "
            "window-parameter comparison"
        ),
        "dataset": {
            "name": "PhysioNet EEG Motor Movement/"
            "Imagery Dataset",
            "mne_dataset_name": "EEGBCI",
            "subject": SUBJECT,
            "runs": RUNS,
            "run_conditions": {
                str(run): RUN_LABELS[run]
                for run in RUNS
            },
            "sampling_frequency_hz": (
                sampling_frequency_hz
            ),
            "target_annotation": (
                TARGET_ANNOTATION
            ),
        },
        "analysis_scope": {
            "window_length_comparison": [
                "win-1s_step-1s",
                "win-2s_step-1s",
                "win-4s_step-1s",
            ],
            "step_size_comparison": [
                "win-2s_step-0p5s",
                "win-2s_step-1s",
                "win-2s_step-2s",
            ],
            "window_inclusion_rule": (
                "Only windows fully contained "
                "within the target annotation "
                "interval were included."
            ),
        },
        "preprocessing": {
            "filter_low_hz": FILTER_LOW_HZ,
            "filter_high_hz": FILTER_HIGH_HZ,
            "filter_scope": (
                "The continuous run was filtered "
                "before outer-window extraction."
            ),
            "posterior_channels": (
                POSTERIOR_CHANNELS
            ),
        },
        "welch": {
            "window": "hann",
            "n_per_seg_samples": (
                WELCH_N_PER_SEG
            ),
            "n_overlap_samples": (
                WELCH_N_OVERLAP
            ),
            "n_fft_samples": WELCH_N_FFT,
            "detrend": "constant",
            "return_onesided": True,
            "scaling": "density",
            "average": "mean",
            "psd_frequency_min_hz": (
                PSD_MIN_HZ
            ),
            "psd_frequency_max_hz": (
                PSD_MAX_HZ
            ),
        },
        "feature": {
            "name": FEATURE_NAME,
            "unit": FEATURE_UNIT,
            "alpha_band_hz": {
                "lower_inclusive": (
                    ALPHA_BAND[0]
                ),
                "upper_exclusive": (
                    ALPHA_BAND[1]
                ),
            },
            "channel_operation": (
                "Mean PSD across the six posterior "
                "channels at each frequency."
            ),
            "frequency_operation": (
                "Mean of the posterior-channel mean "
                "PSD across 8 <= f < 13 Hz."
            ),
            "calculation_scale": (
                "Raw PSD values were used for all "
                "summary and comparison metrics."
            ),
        },
        "configurations": (
            configuration_records
        ),
        "selected_baseline_configuration": {
            "version": (
                SELECTED_BASELINE_VERSION
            ),
            "configuration_id": (
                selected_baseline_record[
                    "configuration_id"
                ]
            ),
            "window_length_sec": (
                selected_baseline_record[
                    "window_length_sec"
                ]
            ),
            "step_size_sec": (
                selected_baseline_record[
                    "step_size_sec"
                ]
            ),
            "first_available_time_sec": (
                selected_baseline_record[
                    "first_available_time_sec"
                ]
            ),
            "outer_window_overlap_fraction": (
                selected_baseline_record[
                    "outer_window_overlap_fraction"
                ]
            ),
            "welch_segment_count": (
                selected_baseline_record[
                    "welch_segment_count"
                ]
            ),
            "intended_use": (
                "Baseline feature-update "
                "configuration for the Session 15 "
                "offline decision-rule analysis."
            ),
            "selection_basis": [
                (
                    "The 2 s window provided lower "
                    "relative within-run variability "
                    "than the 1 s window while "
                    "retaining shorter temporal "
                    "integration than the 4 s window."
                ),
                (
                    "The 1 s step provided an "
                    "intermediate update cadence with "
                    "50% outer-window overlap, between "
                    "the denser 0.5 s step and the "
                    "sparser non-overlapping 2 s step."
                ),
                (
                    "The configuration retained "
                    "positive central-range separation "
                    "between the two analyzed "
                    "recordings."
                ),
            ],
        },
        "condition_summary_metrics": {
            "median": (
                "Middle window-feature value."
            ),
            "q25": "25th percentile.",
            "q75": "75th percentile.",
            "iqr": "Q75 minus Q25.",
            "iqr_over_median": (
                "IQR divided by the median; "
                "relative within-recording "
                "variability."
            ),
            "mean": "Arithmetic mean.",
            "standard_deviation_population": (
                "Population standard deviation "
                "with ddof=0."
            ),
            "minimum": "Minimum window value.",
            "q05": "5th percentile.",
            "q95": "95th percentile.",
            "maximum": "Maximum window value.",
        },
        "configuration_comparison_metrics": {
            "median_ratio_ec_over_eo": (
                "Eyes-closed median divided by "
                "eyes-open median."
            ),
            "g90_ec_q05_minus_eo_q95": (
                "EC Q05 minus EO Q95. Positive "
                "values indicate separation of "
                "the central 90% ranges."
            ),
            "grange_ec_min_minus_eo_max": (
                "EC minimum minus EO maximum. "
                "Positive values indicate complete "
                "min-max separation."
            ),
            "pairwise_ordering_fraction": (
                "P(EC > EO) + 0.5 * P(EC = EO) "
                "across all cross-condition "
                "window pairs."
            ),
        },
        "validation": {
            "total_feature_row_count": len(
                feature_rows
            ),
            "condition_summary_row_count": len(
                condition_summary_rows
            ),
            "configuration_comparison_row_count": len(
                configuration_comparison_rows
            ),
            "configuration_run_structure": (
                configuration_run_validation
            ),
            "shared_window_feature_consistency": (
                shared_window_validation
            ),
            "shared_window_relative_tolerance": (
                SHARED_WINDOW_RTOL
            ),
            "shared_window_absolute_tolerance": (
                SHARED_WINDOW_ATOL
            ),
        },
        "interpretation_boundaries": {
            "recording_scope": (
                "The results describe one eyes-open "
                "baseline run and one eyes-closed "
                "baseline run from one subject."
            ),
            "condition_effect": (
                "The analysis does not establish a "
                "repeated-trial or cross-subject "
                "condition effect."
            ),
            "window_dependence": (
                "Overlapping outer windows are not "
                "independent observations."
            ),
            "step_size": (
                "A smaller step size increases update "
                "density and data reuse, not the "
                "amount of independent information."
            ),
            "window_length": (
                "The window-length comparison also "
                "changes first availability, outer "
                "overlap, and Welch segment count."
            ),
            "visualization_scale": (
                "A logarithmic axis may be used for "
                "figures, but metrics are calculated "
                "from raw PSD values."
            ),
        },

        "output_files": {
            "window_feature_csv": (
                WINDOW_FEATURE_CSV_PATH.name
            ),
            "condition_summary_csv": (
                CONDITION_SUMMARY_CSV_PATH.name
            ),
            "configuration_comparison_csv": (
                CONFIGURATION_COMPARISON_CSV_PATH.name
            ),
            "local_decomposition_csv": (
                LOCAL_DECOMPOSITION_CSV_PATH.name
            ),
            "metadata_json": (
                METADATA_JSON_PATH.name
            ),
            "window_length_figure": (
                WINDOW_LENGTH_FIGURE_PATH.name
            ),
            "step_size_figure": (
                STEP_SIZE_FIGURE_PATH.name
            ),
        },
        "output_provenance": {
            "window_feature_csv": (
                "09_eegbci_window_parameter_"
                "comparison.py"
            ),
            "condition_summary_csv": (
                "09_eegbci_window_parameter_"
                "comparison.py"
            ),
            "configuration_comparison_csv": (
                "09_eegbci_window_parameter_"
                "comparison.py"
            ),
            "local_decomposition_csv": (
                "09b_eegbci_local_window_"
                "decomposition.py"
            ),
            "metadata_json": (
                "09_eegbci_window_parameter_"
                "comparison.py"
            ),
            "window_length_figure": (
                "09_eegbci_window_parameter_"
                "comparison.py"
            ),
            "step_size_figure": (
                "09c_eegbci_step_size_"
                "comparison_figure.py"
            ),
        },
    }

    return metadata

def save_metadata_json(
    metadata,
):
    with open(
        METADATA_JSON_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    with open(
        METADATA_JSON_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        saved_metadata = json.load(file)

    if saved_metadata.get("session") != 14:
        raise RuntimeError(
            "Saved metadata session value "
            "does not equal 14."
        )

    saved_validation = saved_metadata.get(
        "validation",
        {},
    )

    expected_feature_row_count = metadata[
        "validation"
    ]["total_feature_row_count"]

    saved_feature_row_count = (
        saved_validation.get(
            "total_feature_row_count"
        )
    )

    if (
        saved_feature_row_count
        != expected_feature_row_count
    ):
        raise RuntimeError(
            "Saved metadata feature-row count "
            "does not match the expected value."
        )

    if len(
        saved_metadata.get(
            "configurations",
            [],
        )
    ) != len(CONFIGURATIONS):
        raise RuntimeError(
            "Saved metadata configuration count "
            "does not match the configured count."
        )

    saved_baseline = saved_metadata.get(
        "selected_baseline_configuration",
        {},
    )

    if (
        saved_baseline.get("configuration_id")
        != SELECTED_BASELINE_CONFIGURATION_ID
    ):
        raise RuntimeError(
            "Saved metadata does not contain "
            "the expected selected baseline "
            "configuration."
        )

    saved_output_files = saved_metadata.get(
        "output_files",
        {},
    )

    if (
        saved_output_files.get(
            "local_decomposition_csv"
        )
        != LOCAL_DECOMPOSITION_CSV_PATH.name
    ):
        raise RuntimeError(
            "Saved metadata contains an "
            "unexpected local-decomposition "
            "CSV filename."
        )

    if (
        saved_output_files.get(
            "step_size_figure"
        )
        != STEP_SIZE_FIGURE_PATH.name
    ):
        raise RuntimeError(
            "Saved metadata contains an "
            "unexpected step-size figure "
            "filename."
        )

    return METADATA_JSON_PATH


def get_sorted_feature_rows(
    feature_rows,
    configuration_id,
    run,
):
    selected_rows = sorted(
        [
            row
            for row in feature_rows
            if (
                row["configuration_id"]
                == configuration_id
                and row["run"] == run
            )
        ],
        key=lambda row: row[
            "window_center_sec"
        ],
    )

    if len(selected_rows) == 0:
        raise RuntimeError(
            "No feature rows were found for "
            f"{configuration_id}, run {run}."
        )

    return selected_rows


def save_window_length_comparison_figure(
    feature_rows,
):
    figure, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(12, 14),
    )

    time_series_panels = [
        (
            axes[0],
            EYES_OPEN_RUN,
            "A. Eyes-open window-level time series",
        ),
        (
            axes[1],
            EYES_CLOSED_RUN,
            "B. Eyes-closed window-level time series",
        ),
    ]

    for axis, run, panel_title in (
        time_series_panels
    ):
        for configuration_id in (
            WINDOW_LENGTH_COMPARISON_IDS
        ):
            selected_rows = (
                get_sorted_feature_rows(
                    feature_rows=feature_rows,
                    configuration_id=(
                        configuration_id
                    ),
                    run=run,
                )
            )

            window_center_times = np.asarray(
                [
                    row["window_center_sec"]
                    for row in selected_rows
                ],
                dtype=float,
            )

            feature_values = np.asarray(
                [
                    row[
                        "posterior_alpha_mean_psd"
                    ]
                    for row in selected_rows
                ],
                dtype=float,
            )

            axis.plot(
                window_center_times,
                feature_values,
                marker="o",
                markersize=2.5,
                linewidth=1.1,
                label=(
                    CONFIGURATION_DISPLAY_LABELS[
                        configuration_id
                    ]
                ),
            )

        axis.set_yscale("log")

        axis.set_ylabel(
            "Posterior alpha mean PSD\n(V²/Hz, log axis)"
        )

        axis.set_title(panel_title)

        axis.grid(
            visible=True,
            which="both",
            alpha=0.25,
        )

        axis.legend()

    axes[1].set_xlabel(
        "Window center time (s)"
    )

    distribution_axis = axes[2]

    configuration_positions = np.arange(
        len(WINDOW_LENGTH_COMPARISON_IDS),
        dtype=float,
    )

    eyes_open_positions = (
        configuration_positions - 0.18
    )

    eyes_closed_positions = (
        configuration_positions + 0.18
    )

    eyes_open_distributions = []
    eyes_closed_distributions = []

    eyes_open_point_x = []
    eyes_open_point_y = []

    eyes_closed_point_x = []
    eyes_closed_point_y = []

    for configuration_index, configuration_id in (
        enumerate(WINDOW_LENGTH_COMPARISON_IDS)
    ):
        eyes_open_rows = (
            get_sorted_feature_rows(
                feature_rows=feature_rows,
                configuration_id=(
                    configuration_id
                ),
                run=EYES_OPEN_RUN,
            )
        )

        eyes_closed_rows = (
            get_sorted_feature_rows(
                feature_rows=feature_rows,
                configuration_id=(
                    configuration_id
                ),
                run=EYES_CLOSED_RUN,
            )
        )

        eyes_open_values = np.asarray(
            [
                row[
                    "posterior_alpha_mean_psd"
                ]
                for row in eyes_open_rows
            ],
            dtype=float,
        )

        eyes_closed_values = np.asarray(
            [
                row[
                    "posterior_alpha_mean_psd"
                ]
                for row in eyes_closed_rows
            ],
            dtype=float,
        )

        eyes_open_distributions.append(
            eyes_open_values
        )

        eyes_closed_distributions.append(
            eyes_closed_values
        )

        eyes_open_offsets = np.linspace(
            -0.055,
            0.055,
            len(eyes_open_values),
        )

        eyes_closed_offsets = np.linspace(
            -0.055,
            0.055,
            len(eyes_closed_values),
        )

        eyes_open_point_x.extend(
            eyes_open_positions[
                configuration_index
            ]
            + eyes_open_offsets
        )

        eyes_open_point_y.extend(
            eyes_open_values
        )

        eyes_closed_point_x.extend(
            eyes_closed_positions[
                configuration_index
            ]
            + eyes_closed_offsets
        )

        eyes_closed_point_y.extend(
            eyes_closed_values
        )

    distribution_axis.boxplot(
        eyes_open_distributions,
        positions=eyes_open_positions,
        widths=0.28,
        showfliers=False,
        manage_ticks=False,
    )

    distribution_axis.boxplot(
        eyes_closed_distributions,
        positions=eyes_closed_positions,
        widths=0.28,
        showfliers=False,
        manage_ticks=False,
    )

    distribution_axis.scatter(
        eyes_open_point_x,
        eyes_open_point_y,
        marker="o",
        s=11,
        alpha=0.45,
        label="Eyes open",
    )

    distribution_axis.scatter(
        eyes_closed_point_x,
        eyes_closed_point_y,
        marker="x",
        s=13,
        alpha=0.45,
        label="Eyes closed",
    )

    distribution_axis.set_yscale("log")

    distribution_axis.set_xticks(
        configuration_positions
    )

    distribution_axis.set_xticklabels(
        [
            "1 s window",
            "2 s window",
            "4 s window",
        ]
    )

    distribution_axis.set_xlabel(
        "Outer-window configuration "
        "(step fixed at 1 s)"
    )

    distribution_axis.set_ylabel(
        "Posterior alpha mean PSD\n(V²/Hz, log axis)"
    )

    distribution_axis.set_title(
        "C. Window-level feature distributions"
    )

    distribution_axis.grid(
        visible=True,
        which="both",
        axis="y",
        alpha=0.25,
    )

    distribution_axis.legend()

    figure.suptitle(
        "Session 14: Window-Length Configuration "
        "Comparison",
        fontsize=15,
    )

    figure.text(
        0.5,
        0.012,
        (
            "Raw PSD values are displayed on a "
            "log-scaled axis. Overlapping windows "
            "are not independent observations."
        ),
        ha="center",
        fontsize=9,
    )

    figure.tight_layout(
        rect=(0.0, 0.035, 1.0, 0.965)
    )

    figure.savefig(
        WINDOW_LENGTH_FIGURE_PATH,
        dpi=180,
    )

    plt.close(figure)

    if not WINDOW_LENGTH_FIGURE_PATH.exists():
        raise RuntimeError(
            "Window-length comparison figure "
            "was not created."
        )

    if (
        WINDOW_LENGTH_FIGURE_PATH.stat().st_size
        == 0
    ):
        raise RuntimeError(
            "Window-length comparison figure "
            "is empty."
        )

    return WINDOW_LENGTH_FIGURE_PATH


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
        n_per_seg=WELCH_N_PER_SEG,
        n_overlap=WELCH_N_OVERLAP,
        n_fft=WELCH_N_FFT,
        psd_min_hz=PSD_MIN_HZ,
        psd_max_hz=PSD_MAX_HZ,
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
        calculate_welch_segment_count(
            window_length_samples=(
                first_window_data.shape[1]
            )
        )
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
        n_per_seg=WELCH_N_PER_SEG,
        n_overlap=WELCH_N_OVERLAP,
        n_fft=WELCH_N_FFT,
        psd_min_hz=PSD_MIN_HZ,
        psd_max_hz=PSD_MAX_HZ,
    )

    posterior_alpha_mean_psd = (
        extract_mean_band_psd(
            psd_data=psd_data,
            freqs=freqs,
            band_low_hz=ALPHA_BAND[0],
            band_high_hz=ALPHA_BAND[1],
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
    window_length_sec,
    step_size_sec,
):
    if not PRINT_DETAILED_DIAGNOSTICS:
        return

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
        window_length_sec,
        "s",
    )

    print(
        "Step size:",
        step_size_sec,
        "s",
    )

    outer_window_overlap_fraction = (
        calculate_outer_window_overlap_fraction(
            window_length_sec=window_length_sec,
            step_size_sec=step_size_sec,
        )
    )

    print(
        "Outer-window overlap fraction:",
        f"{outer_window_overlap_fraction:.2f}",
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


def build_window_feature_map(
    feature_rows,
    configuration_id,
):
    configuration_rows = [
        row
        for row in feature_rows
        if row["configuration_id"]
        == configuration_id
    ]

    if len(configuration_rows) == 0:
        raise RuntimeError(
            "No feature rows were found for "
            f"configuration {configuration_id}."
        )

    feature_map = {}

    for row in configuration_rows:
        window_key = (
            int(row["run"]),
            int(row["start_sample"]),
            int(row["stop_sample"]),
        )

        if window_key in feature_map:
            raise RuntimeError(
                "Duplicate window key found for "
                f"configuration {configuration_id}: "
                f"{window_key}"
            )

        feature_map[window_key] = float(
            row["posterior_alpha_mean_psd"]
        )

    return feature_map


def validate_shared_window_features(
    feature_rows,
):
    comparison_pairs = [
        (
            "win-2s_step-1s",
            "win-2s_step-0p5s",
        ),
        (
            "win-2s_step-2s",
            "win-2s_step-1s",
        ),
        (
            "win-2s_step-2s",
            "win-2s_step-0p5s",
        ),
    ]

    required_configuration_ids = {
        configuration_id
        for comparison_pair in comparison_pairs
        for configuration_id in comparison_pair
    }

    feature_maps = {
        configuration_id: (
            build_window_feature_map(
                feature_rows=feature_rows,
                configuration_id=(
                    configuration_id
                ),
            )
        )
        for configuration_id
        in required_configuration_ids
    }

    validation_results = []

    for (
        left_configuration_id,
        right_configuration_id,
    ) in comparison_pairs:
        left_feature_map = feature_maps[
            left_configuration_id
        ]

        right_feature_map = feature_maps[
            right_configuration_id
        ]

        shared_window_keys = sorted(
            set(left_feature_map.keys())
            & set(right_feature_map.keys())
        )

        expected_shared_count = min(
            len(left_feature_map),
            len(right_feature_map),
        )

        if (
            len(shared_window_keys)
            != expected_shared_count
        ):
            raise RuntimeError(
                "Shared-window count mismatch for "
                f"{left_configuration_id} and "
                f"{right_configuration_id}: "
                f"expected {expected_shared_count}, "
                f"found {len(shared_window_keys)}."
            )

        left_values = np.array(
            [
                left_feature_map[window_key]
                for window_key
                in shared_window_keys
            ],
            dtype=float,
        )

        right_values = np.array(
            [
                right_feature_map[window_key]
                for window_key
                in shared_window_keys
            ],
            dtype=float,
        )

        close_mask = np.isclose(
            left_values,
            right_values,
            rtol=SHARED_WINDOW_RTOL,
            atol=SHARED_WINDOW_ATOL,
        )

        mismatch_count = int(
            np.count_nonzero(~close_mask)
        )

        absolute_differences = np.abs(
            left_values - right_values
        )

        max_absolute_difference = float(
            absolute_differences.max()
        )

        if mismatch_count != 0:
            raise RuntimeError(
                "Shared-window feature mismatch for "
                f"{left_configuration_id} and "
                f"{right_configuration_id}: "
                f"{mismatch_count} mismatches, "
                "maximum absolute difference "
                f"{max_absolute_difference:.12e}."
            )

        validation_results.append({
            "left_configuration_id": (
                left_configuration_id
            ),
            "right_configuration_id": (
                right_configuration_id
            ),
            "shared_window_count": len(
                shared_window_keys
            ),
            "mismatch_count": mismatch_count,
            "max_absolute_difference": (
                max_absolute_difference
            ),
        })

    return validation_results


def build_configuration_run_validation_rows(
    feature_rows,
):
    validation_rows = []

    for configuration in CONFIGURATIONS:
        configuration_id = configuration[
            "configuration_id"
        ]

        configured_window_length_sec = float(
            configuration["window_length_sec"]
        )

        configured_step_size_sec = float(
            configuration["step_size_sec"]
        )

        configured_overlap_fraction = (
            calculate_outer_window_overlap_fraction(
                window_length_sec=(
                    configured_window_length_sec
                ),
                step_size_sec=(
                    configured_step_size_sec
                ),
            )
        )

        for run in RUNS:
            run_rows = sorted(
                [
                    row
                    for row in feature_rows
                    if (
                        row["configuration_id"]
                        == configuration_id
                        and row["run"] == run
                    )
                ],
                key=lambda row: row["window_index"],
            )

            if len(run_rows) == 0:
                raise RuntimeError(
                    "No feature rows found for "
                    f"{configuration_id}, run {run}."
                )

            actual_window_indices = [
                int(row["window_index"])
                for row in run_rows
            ]

            expected_window_indices = list(
                range(len(run_rows))
            )

            if (
                actual_window_indices
                != expected_window_indices
            ):
                raise RuntimeError(
                    "Window indices are not continuous "
                    f"for {configuration_id}, run {run}."
                )

            if not all(
                np.isclose(
                    float(row["window_length_sec"]),
                    configured_window_length_sec,
                )
                for row in run_rows
            ):
                raise RuntimeError(
                    "Window-length inconsistency for "
                    f"{configuration_id}, run {run}."
                )

            if not all(
                np.isclose(
                    float(row["step_size_sec"]),
                    configured_step_size_sec,
                )
                for row in run_rows
            ):
                raise RuntimeError(
                    "Step-size inconsistency for "
                    f"{configuration_id}, run {run}."
                )

            if not all(
                np.isclose(
                    float(
                        row[
                            "outer_window_overlap_fraction"
                        ]
                    ),
                    configured_overlap_fraction,
                )
                for row in run_rows
            ):
                raise RuntimeError(
                    "Outer-window overlap inconsistency "
                    f"for {configuration_id}, run {run}."
                )

            first_row = run_rows[0]
            last_row = run_rows[-1]

            expected_welch_segment_count = (
                calculate_welch_segment_count(
                    window_length_samples=int(
                        first_row["n_samples"]
                    )
                )
            )

            if not all(
                int(row["welch_segment_count"])
                == expected_welch_segment_count
                for row in run_rows
            ):
                raise RuntimeError(
                    "Welch-segment-count inconsistency "
                    f"for {configuration_id}, run {run}."
                )

            validation_rows.append({
                "configuration_id": configuration_id,
                "run": run,
                "condition": RUN_LABELS[run],
                "n_windows": len(run_rows),
                "window_length_sec": (
                    configured_window_length_sec
                ),
                "step_size_sec": (
                    configured_step_size_sec
                ),
                "outer_window_overlap_fraction": (
                    configured_overlap_fraction
                ),
                "welch_segment_count": (
                    expected_welch_segment_count
                ),
                "first_window_start_sec": float(
                    first_row["window_start_sec"]
                ),
                "first_window_center_sec": float(
                    first_row["window_center_sec"]
                ),
                "last_window_center_sec": float(
                    last_row["window_center_sec"]
                ),
                "last_window_end_sec": float(
                    last_row["window_end_sec"]
                ),
            })

    expected_validation_row_count = (
        len(CONFIGURATIONS) * len(RUNS)
    )

    if (
        len(validation_rows)
        != expected_validation_row_count
    ):
        raise RuntimeError(
            "Expected "
            f"{expected_validation_row_count} "
            "configuration-run validation rows, "
            f"but created {len(validation_rows)}."
        )

    return validation_rows


def print_configuration_run_validation_table(
    validation_rows,
):
    print("\n########################################")
    print("Configuration-run structure validation")

    print(
        f"{'Configuration':<22}"
        f"{'Run':>5}"
        f"{'N':>6}"
        f"{'Win':>7}"
        f"{'Step':>7}"
        f"{'Overlap':>10}"
        f"{'Welch':>8}"
        f"{'Centers':>16}"
        f"{'Last end':>10}"
    )

    for row in validation_rows:
        configuration_id = row[
            "configuration_id"
        ]

        run = row["run"]
        n_windows = row["n_windows"]

        window_length_sec = row[
            "window_length_sec"
        ]

        step_size_sec = row[
            "step_size_sec"
        ]

        overlap_fraction = row[
            "outer_window_overlap_fraction"
        ]

        welch_segment_count = row[
            "welch_segment_count"
        ]

        center_range = (
            f"{row['first_window_center_sec']:.1f}"
            "-"
            f"{row['last_window_center_sec']:.1f}"
        )

        last_window_end_sec = row[
            "last_window_end_sec"
        ]

        print(
            f"{configuration_id:<22}"
            f"{run:>5d}"
            f"{n_windows:>6d}"
            f"{window_length_sec:>7.1f}"
            f"{step_size_sec:>7.1f}"
            f"{overlap_fraction:>10.2f}"
            f"{welch_segment_count:>8d}"
            f"{center_range:>16}"
            f"{last_window_end_sec:>10.1f}"
        )


def run_configuration(configuration):
    configuration_id = configuration[
        "configuration_id"
    ]

    window_length_sec = float(
        configuration["window_length_sec"]
    )

    step_size_sec = float(
        configuration["step_size_sec"]
    )

    all_feature_rows = []
    expected_window_counts = {}

    print("\n########################################")
    print("Configuration:", configuration_id)

    print(
        "Configured window length:",
        window_length_sec,
        "s",
    )

    print(
        "Configured step size:",
        step_size_sec,
        "s",
    )

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
            interval_start_sec=t0_onset,
            interval_end_sec=t0_end,
            sfreq=float(raw.info["sfreq"]),
            n_samples=int(raw.n_times),
            window_length_sec=window_length_sec,
            step_size_sec=step_size_sec,
        )

        expected_window_counts[run] = len(
            window_bounds
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
            configuration_id=configuration_id,
            window_length_sec=window_length_sec,
            step_size_sec=step_size_sec,
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
            window_length_sec=window_length_sec,
            step_size_sec=step_size_sec,
            window_length_samples=window_length_samples,
            step_size_samples=step_size_samples,
            window_validation=window_validation,
            welch_validation=welch_validation,
            alpha_validation=alpha_validation,
        )

    expected_total_rows = sum(
        expected_window_counts.values()
    )

    if len(all_feature_rows) != expected_total_rows:
        raise RuntimeError(
            f"Expected {expected_total_rows} total "
            f"feature rows, but generated "
            f"{len(all_feature_rows)}."
        )

    summary = build_summary(
        feature_rows=all_feature_rows,
        expected_window_counts=(
            expected_window_counts
        ),
        configuration_id=configuration_id,
        window_length_sec=window_length_sec,
        step_size_sec=step_size_sec,
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

    print(
        f"\nConfiguration completed: "
        f"{configuration_id}"
    )

    return all_feature_rows, summary


def build_condition_summary_rows(
    feature_rows,
):
    summary_rows = []

    for configuration in CONFIGURATIONS:
        configuration_id = configuration[
            "configuration_id"
        ]

        window_length_sec = float(
            configuration["window_length_sec"]
        )

        step_size_sec = float(
            configuration["step_size_sec"]
        )

        overlap_fraction = (
            calculate_outer_window_overlap_fraction(
                window_length_sec=window_length_sec,
                step_size_sec=step_size_sec,
            )
        )

        for run in RUNS:
            condition_rows = [
                row
                for row in feature_rows
                if (
                    row["configuration_id"]
                    == configuration_id
                    and row["run"] == run
                )
            ]

            if len(condition_rows) == 0:
                raise RuntimeError(
                    "No feature rows found for "
                    f"{configuration_id}, run {run}."
                )

            feature_values = np.asarray(
                [
                    row[
                        "posterior_alpha_mean_psd"
                    ]
                    for row in condition_rows
                ],
                dtype=float,
            )

            if feature_values.ndim != 1:
                raise RuntimeError(
                    "Expected a one-dimensional "
                    "feature array for "
                    f"{configuration_id}, run {run}."
                )

            if len(feature_values) != len(
                condition_rows
            ):
                raise RuntimeError(
                    "Feature-value count does not "
                    "match the condition-row count."
                )

            if not np.isfinite(
                feature_values
            ).all():
                raise ValueError(
                    "Non-finite feature values found "
                    f"for {configuration_id}, "
                    f"run {run}."
                )

            if np.any(feature_values < 0):
                raise ValueError(
                    "Negative PSD feature values found "
                    f"for {configuration_id}, "
                    f"run {run}."
                )

            (
                q05,
                q25,
                median,
                q75,
                q95,
            ) = np.quantile(
                feature_values,
                [0.05, 0.25, 0.50, 0.75, 0.95],
                method="linear",
            )

            minimum = float(
                np.min(feature_values)
            )

            maximum = float(
                np.max(feature_values)
            )

            mean = float(
                np.mean(feature_values)
            )

            standard_deviation_population = float(
                np.std(
                    feature_values,
                    ddof=0,
                )
            )

            q05 = float(q05)
            q25 = float(q25)
            median = float(median)
            q75 = float(q75)
            q95 = float(q95)

            iqr = float(q75 - q25)

            if median <= 0:
                raise RuntimeError(
                    "IQR-to-median ratio is undefined "
                    "because the median is not positive "
                    f"for {configuration_id}, "
                    f"run {run}."
                )

            iqr_over_median = float(
                iqr / median
            )

            quantile_order = [
                minimum,
                q05,
                q25,
                median,
                q75,
                q95,
                maximum,
            ]

            if any(
                left_value > right_value
                for left_value, right_value
                in zip(
                    quantile_order[:-1],
                    quantile_order[1:],
                )
            ):
                raise RuntimeError(
                    "Summary values are not in "
                    "ascending quantile order for "
                    f"{configuration_id}, run {run}."
                )

            welch_segment_count = int(
                condition_rows[0][
                    "welch_segment_count"
                ]
            )

            summary_rows.append({
                "subject": SUBJECT,
                "configuration_id": (
                    configuration_id
                ),
                "run": int(run),
                "condition": RUN_LABELS[run],
                "n_windows": int(
                    len(feature_values)
                ),
                "window_length_sec": (
                    window_length_sec
                ),
                "step_size_sec": step_size_sec,
                "outer_window_overlap_fraction": (
                    overlap_fraction
                ),
                "welch_segment_count": (
                    welch_segment_count
                ),
                "feature_name": FEATURE_NAME,
                "feature_unit": FEATURE_UNIT,
                "median": median,
                "q25": q25,
                "q75": q75,
                "iqr": iqr,
                "iqr_over_median": (
                    iqr_over_median
                ),
                "mean": mean,
                "standard_deviation_population": (
                    standard_deviation_population
                ),
                "minimum": minimum,
                "q05": q05,
                "q95": q95,
                "maximum": maximum,
            })

    expected_summary_row_count = (
        len(CONFIGURATIONS) * len(RUNS)
    )

    if (
        len(summary_rows)
        != expected_summary_row_count
    ):
        raise RuntimeError(
            "Expected "
            f"{expected_summary_row_count} "
            "condition-summary rows, but created "
            f"{len(summary_rows)}."
        )

    summarized_window_count = sum(
        row["n_windows"]
        for row in summary_rows
    )

    if summarized_window_count != len(
        feature_rows
    ):
        raise RuntimeError(
            "Condition summaries account for "
            f"{summarized_window_count} windows, "
            f"but {len(feature_rows)} feature rows "
            "were provided."
        )

    return summary_rows


def build_configuration_comparison_rows(
    feature_rows,
    condition_summary_rows,
):
    comparison_rows = []

    for configuration in CONFIGURATIONS:
        configuration_id = configuration[
            "configuration_id"
        ]

        eyes_open_summary_matches = [
            row
            for row in condition_summary_rows
            if (
                row["configuration_id"]
                == configuration_id
                and row["run"] == EYES_OPEN_RUN
            )
        ]

        eyes_closed_summary_matches = [
            row
            for row in condition_summary_rows
            if (
                row["configuration_id"]
                == configuration_id
                and row["run"] == EYES_CLOSED_RUN
            )
        ]

        if len(eyes_open_summary_matches) != 1:
            raise RuntimeError(
                "Selected baseline configuration must "
                "match exactly one configuration record. "
                f"ID: {SELECTED_BASELINE_CONFIGURATION_ID}, "
                f"matches found: "
                f"{len(selected_baseline_matches)}."
            )

        if len(eyes_closed_summary_matches) != 1:
            raise RuntimeError(
                "Expected exactly one eyes-closed "
                "summary row for "
                f"{configuration_id}, but found "
                f"{len(eyes_closed_summary_matches)}."
            )

        eyes_open_summary = (
            eyes_open_summary_matches[0]
        )

        eyes_closed_summary = (
            eyes_closed_summary_matches[0]
        )

        eyes_open_values = np.asarray(
            [
                row[
                    "posterior_alpha_mean_psd"
                ]
                for row in feature_rows
                if (
                    row["configuration_id"]
                    == configuration_id
                    and row["run"]
                    == EYES_OPEN_RUN
                )
            ],
            dtype=float,
        )

        eyes_closed_values = np.asarray(
            [
                row[
                    "posterior_alpha_mean_psd"
                ]
                for row in feature_rows
                if (
                    row["configuration_id"]
                    == configuration_id
                    and row["run"]
                    == EYES_CLOSED_RUN
                )
            ],
            dtype=float,
        )

        if len(eyes_open_values) == 0:
            raise RuntimeError(
                "No eyes-open feature values found "
                f"for {configuration_id}."
            )

        if len(eyes_closed_values) == 0:
            raise RuntimeError(
                "No eyes-closed feature values found "
                f"for {configuration_id}."
            )

        if not np.isfinite(
            eyes_open_values
        ).all():
            raise ValueError(
                "Non-finite eyes-open feature values "
                f"found for {configuration_id}."
            )

        if not np.isfinite(
            eyes_closed_values
        ).all():
            raise ValueError(
                "Non-finite eyes-closed feature values "
                f"found for {configuration_id}."
            )

        eyes_open_median = float(
            eyes_open_summary["median"]
        )

        eyes_closed_median = float(
            eyes_closed_summary["median"]
        )

        if eyes_open_median <= 0:
            raise RuntimeError(
                "EC-to-EO median ratio is undefined "
                "because the EO median is not positive "
                f"for {configuration_id}."
            )

        median_ratio_ec_over_eo = float(
            eyes_closed_median
            / eyes_open_median
        )

        g90 = float(
            eyes_closed_summary["q05"]
            - eyes_open_summary["q95"]
        )

        grange = float(
            eyes_closed_summary["minimum"]
            - eyes_open_summary["maximum"]
        )

        pairwise_differences = (
            eyes_closed_values[:, np.newaxis]
            - eyes_open_values[np.newaxis, :]
        )

        greater_count = int(
            np.count_nonzero(
                pairwise_differences > 0
            )
        )

        tie_count = int(
            np.count_nonzero(
                pairwise_differences == 0
            )
        )

        lower_count = int(
            np.count_nonzero(
                pairwise_differences < 0
            )
        )

        total_pair_count = int(
            pairwise_differences.size
        )

        if (
            greater_count
            + tie_count
            + lower_count
            != total_pair_count
        ):
            raise RuntimeError(
                "Pairwise comparison counts do not "
                f"sum correctly for {configuration_id}."
            )

        pairwise_ordering_fraction = float(
            (
                greater_count
                + 0.5 * tie_count
            )
            / total_pair_count
        )

        if not (
            0.0
            <= pairwise_ordering_fraction
            <= 1.0
        ):
            raise RuntimeError(
                "Pairwise ordering fraction is "
                "outside the valid range for "
                f"{configuration_id}."
            )

        comparison_rows.append({
            "subject": SUBJECT,
            "configuration_id": (
                configuration_id
            ),
            "eyes_open_n_windows": int(
                len(eyes_open_values)
            ),
            "eyes_closed_n_windows": int(
                len(eyes_closed_values)
            ),
            "eyes_open_median": (
                eyes_open_median
            ),
            "eyes_closed_median": (
                eyes_closed_median
            ),
            "median_ratio_ec_over_eo": (
                median_ratio_ec_over_eo
            ),
            "g90_ec_q05_minus_eo_q95": g90,
            "grange_ec_min_minus_eo_max": (
                grange
            ),
            "pairwise_ordering_fraction": (
                pairwise_ordering_fraction
            ),
            "pairwise_greater_count": (
                greater_count
            ),
            "pairwise_tie_count": tie_count,
            "pairwise_lower_count": (
                lower_count
            ),
            "total_pair_count": (
                total_pair_count
            ),
        })

    if len(comparison_rows) != len(
        CONFIGURATIONS
    ):
        raise RuntimeError(
            "Expected "
            f"{len(CONFIGURATIONS)} "
            "configuration-comparison rows, "
            f"but created {len(comparison_rows)}."
        )

    return comparison_rows

def print_configuration_comparison_table(
    comparison_rows,
):
    print("\n########################################")
    print("EO-EC configuration comparison")

    print(
        f"{'Configuration':<22}"
        f"{'EO N':>6}"
        f"{'EC N':>6}"
        f"{'EO median':>14}"
        f"{'EC median':>14}"
        f"{'EC/EO':>10}"
        f"{'G90':>14}"
        f"{'Grange':>14}"
        f"{'Ordering':>11}"
    )

    for row in comparison_rows:
        configuration_id = row[
            "configuration_id"
        ]

        eyes_open_n_windows = row[
            "eyes_open_n_windows"
        ]

        eyes_closed_n_windows = row[
            "eyes_closed_n_windows"
        ]

        eyes_open_median = row[
            "eyes_open_median"
        ]

        eyes_closed_median = row[
            "eyes_closed_median"
        ]

        median_ratio = row[
            "median_ratio_ec_over_eo"
        ]

        g90 = row[
            "g90_ec_q05_minus_eo_q95"
        ]

        grange = row[
            "grange_ec_min_minus_eo_max"
        ]

        ordering_fraction = row[
            "pairwise_ordering_fraction"
        ]

        print(
            f"{configuration_id:<22}"
            f"{eyes_open_n_windows:>6d}"
            f"{eyes_closed_n_windows:>6d}"
            f"{eyes_open_median:>14.4e}"
            f"{eyes_closed_median:>14.4e}"
            f"{median_ratio:>10.3f}"
            f"{g90:>14.4e}"
            f"{grange:>14.4e}"
            f"{ordering_fraction:>11.4f}"
        )

    print("\nInterpretation:")
    print(
        "G90 > 0: central 90% ranges are separated."
    )
    print(
        "Grange > 0: complete min-max ranges "
        "are separated."
    )
    print(
        "Ordering near 1: EC is greater than EO "
        "for most cross-condition window pairs."
    )

    print(
        "Configuration comparison row count:",
        len(comparison_rows),
    )


def print_condition_summary_table(
    summary_rows,
):
    print("\n########################################")
    print("Condition-level feature summary")
    print(
        "SD uses population standard deviation "
        "(ddof=0)."
    )

    print("\nCentral value and robust variability")

    print(
        f"{'Configuration':<22}"
        f"{'Run':>5}"
        f"{'N':>6}"
        f"{'Median':>14}"
        f"{'Q25':>14}"
        f"{'Q75':>14}"
        f"{'IQR':>14}"
        f"{'IQR/Med':>10}"
    )

    for row in summary_rows:
        configuration_id = row[
            "configuration_id"
        ]

        run = row["run"]
        n_windows = row["n_windows"]
        median = row["median"]
        q25 = row["q25"]
        q75 = row["q75"]
        iqr = row["iqr"]

        iqr_over_median = row[
            "iqr_over_median"
        ]

        print(
            f"{configuration_id:<22}"
            f"{run:>5d}"
            f"{n_windows:>6d}"
            f"{median:>14.4e}"
            f"{q25:>14.4e}"
            f"{q75:>14.4e}"
            f"{iqr:>14.4e}"
            f"{iqr_over_median:>10.3f}"
        )

    print("\nMean, standard deviation, and range")

    print(
        f"{'Configuration':<22}"
        f"{'Run':>5}"
        f"{'Mean':>14}"
        f"{'SD':>14}"
        f"{'Minimum':>14}"
        f"{'Q05':>14}"
        f"{'Q95':>14}"
        f"{'Maximum':>14}"
    )

    for row in summary_rows:
        configuration_id = row[
            "configuration_id"
        ]

        run = row["run"]
        mean = row["mean"]

        standard_deviation_population = row[
            "standard_deviation_population"
        ]

        minimum = row["minimum"]
        q05 = row["q05"]
        q95 = row["q95"]
        maximum = row["maximum"]

        print(
            f"{configuration_id:<22}"
            f"{run:>5d}"
            f"{mean:>14.4e}"
            f"{standard_deviation_population:>14.4e}"
            f"{minimum:>14.4e}"
            f"{q05:>14.4e}"
            f"{q95:>14.4e}"
            f"{maximum:>14.4e}"
        )

    print("\nInterpretation:")
    print(
        "IQR: width of the middle 50% of window "
        "feature values; smaller means tighter "
        "within-condition concentration."
    )
    print(
        "IQR/Median: IQR relative to the median "
        "feature magnitude; smaller means lower "
        "relative variability."
    )

    print(
        "\nCondition summary row count:",
        len(summary_rows),
    )


def main():
    combined_feature_rows = []
    configuration_summaries = {}

    for configuration in CONFIGURATIONS:
        configuration_id = configuration[
            "configuration_id"
        ]

        feature_rows, summary = (
            run_configuration(
                configuration=configuration
            )
        )

        combined_feature_rows.extend(
            feature_rows
        )

        configuration_summaries[
            configuration_id
        ] = summary

    shared_window_validation = (
        validate_shared_window_features(
            feature_rows=combined_feature_rows
        )
    )

    print("\n########################################")
    print("Shared-window feature validation")

    for validation_result in (
        shared_window_validation
    ):
        print(
            validation_result[
                "left_configuration_id"
            ],
            "vs",
            validation_result[
                "right_configuration_id"
            ],
        )

        print(
            "Shared window count:",
            validation_result[
                "shared_window_count"
            ],
        )

        print(
            "Mismatch count:",
            validation_result[
                "mismatch_count"
            ],
        )

        max_absolute_difference = (
            validation_result[
                "max_absolute_difference"
            ]
        )

        print(
            "Maximum absolute difference:",
            f"{max_absolute_difference:.12e}",
        )

    configuration_run_validation = (
        build_configuration_run_validation_rows(
            feature_rows=combined_feature_rows
        )
    )

    print_configuration_run_validation_table(
        validation_rows=(
            configuration_run_validation
        )
    )

    condition_summary_rows = (
        build_condition_summary_rows(
            feature_rows=combined_feature_rows
        )
    )

    print_condition_summary_table(
        summary_rows=condition_summary_rows
    )

    configuration_comparison_rows = (
        build_configuration_comparison_rows(
            feature_rows=combined_feature_rows,
            condition_summary_rows=(
                condition_summary_rows
            ),
        )
    )

    print_configuration_comparison_table(
        comparison_rows=(
            configuration_comparison_rows
        )
    )

    print("\n########################################")
    print(
        "Configuration count:",
        len(CONFIGURATIONS),
    )

    print(
        "Combined feature row count:",
        len(combined_feature_rows),
    )

    print(
        "Completed configurations:",
        list(configuration_summaries.keys()),
    )

    if SAVE_OUTPUTS:
        window_feature_csv_path = (
            save_window_feature_csv(
                feature_rows=(
                    combined_feature_rows
                )
            )
        )

        condition_summary_csv_path = (
            save_condition_summary_csv(
                condition_summary_rows=(
                    condition_summary_rows
                )
            )
        )

        configuration_comparison_csv_path = (
            save_configuration_comparison_csv(
                configuration_comparison_rows=(
                    configuration_comparison_rows
                )
            )
        )

        metadata = build_metadata(
            feature_rows=combined_feature_rows,
            condition_summary_rows=(
                condition_summary_rows
            ),
            configuration_comparison_rows=(
                configuration_comparison_rows
            ),
            shared_window_validation=(
                shared_window_validation
            ),
            configuration_run_validation=(
                configuration_run_validation
            ),
        )

        metadata_json_path = (
            save_metadata_json(
                metadata=metadata
            )
        )

        window_length_figure_path = (
            save_window_length_comparison_figure(
                feature_rows=(
                    combined_feature_rows
                )
            )
        )

        print("\nSaved Session 14 outputs:")

        print(
            "Window feature CSV:",
            window_feature_csv_path,
        )

        print(
            "Condition summary CSV:",
            condition_summary_csv_path,
        )

        print(
            "Configuration comparison CSV:",
            configuration_comparison_csv_path,
        )

        print(
            "Metadata JSON:",
            metadata_json_path,
        )

        print(
            "Window-length figure:",
            window_length_figure_path,
        )

    else:
        print(
            "Combined output saving skipped: "
            "SAVE_OUTPUTS is False."
        )


if __name__ == "__main__":
    main()


