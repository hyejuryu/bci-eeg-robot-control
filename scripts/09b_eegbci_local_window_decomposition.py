# Session 14 supplementary local analysis.
# Decomposes a selected interval into overlapping
# one-second Welch segments and compares the
# reconstructed multi-second features with the
# saved Session 14 main-pipeline outputs.

import csv
from pathlib import Path

import mne
import numpy as np
from mne.datasets import eegbci

from bci_robot.eeg_features import (
    compute_welch_psd,
    extract_mean_band_psd,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

WINDOW_FEATURE_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-14"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_window-features.csv"
    )
)

LOCAL_DECOMPOSITION_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-14"
    / (
        "eegbci_subject-001_run-01_"
        "posterior-alpha_local-decomposition_"
        "center-25s.csv"
    )
)

SUBJECT = 1

RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

LOCAL_DIAGNOSTIC_RUN = 1
LOCAL_DIAGNOSTIC_CENTER_SEC = 25.0

FILTER_LOW_HZ = 1.0
FILTER_HIGH_HZ = 40.0

TARGET_ANNOTATION = "T0"

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

COMPARISON_RTOL = 1e-12
COMPARISON_ATOL = 0.0


def load_raw(run):
    file_path = eegbci.load_data(
        SUBJECT,
        [run],
    )[0]

    raw = mne.io.read_raw_edf(
        file_path,
        preload=True,
        verbose=False,
    )

    return raw


def get_t0_interval(raw):
    t0_indices = np.where(
        raw.annotations.description
        == TARGET_ANNOTATION
    )[0]

    if len(t0_indices) != 1:
        raise ValueError(
            f"Expected exactly one "
            f"{TARGET_ANNOTATION} annotation, "
            f"but found {len(t0_indices)}."
        )

    t0_index = int(t0_indices[0])

    onset = float(
        raw.annotations.onset[t0_index]
    )

    duration = float(
        raw.annotations.duration[t0_index]
    )

    end = onset + duration

    if not np.isfinite(
        [onset, duration, end]
    ).all():
        raise ValueError(
            "T0 annotation contains a "
            "non-finite value."
        )

    if duration <= 0:
        raise ValueError(
            "T0 annotation duration must "
            "be positive."
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
            "Missing posterior channels: "
            f"{missing_channels}"
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

    if (
        posterior_channel_names
        != POSTERIOR_CHANNELS
    ):
        raise RuntimeError(
            "Posterior channel order does not "
            "match the configured order."
        )

    posterior_data = (
        raw_posterior.get_data()
    )

    if posterior_data.ndim != 2:
        raise RuntimeError(
            "Expected two-dimensional "
            "posterior EEG data."
        )

    if not np.isfinite(
        posterior_data
    ).all():
        raise ValueError(
            "Posterior EEG data contains "
            "non-finite values."
        )

    return (
        posterior_data,
        posterior_channel_names,
    )


def load_reference_feature_rows():
    required_fields = {
        "subject",
        "run",
        "configuration_id",
        "window_start_sec",
        "window_end_sec",
        "window_center_sec",
        "start_sample",
        "stop_sample",
        "n_samples",
        "posterior_alpha_mean_psd",
    }

    with open(
        WINDOW_FEATURE_CSV_PATH,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "Reference feature CSV has no header."
            )

        missing_fields = (
            required_fields
            - set(reader.fieldnames)
        )

        if missing_fields:
            raise RuntimeError(
                "Reference feature CSV is missing "
                f"fields: {sorted(missing_fields)}"
            )

        reference_rows = []

        for row in reader:
            reference_rows.append({
                "subject": int(row["subject"]),
                "run": int(row["run"]),
                "configuration_id": (
                    row["configuration_id"]
                ),
                "window_start_sec": float(
                    row["window_start_sec"]
                ),
                "window_end_sec": float(
                    row["window_end_sec"]
                ),
                "window_center_sec": float(
                    row["window_center_sec"]
                ),
                "start_sample": int(
                    row["start_sample"]
                ),
                "stop_sample": int(
                    row["stop_sample"]
                ),
                "n_samples": int(
                    row["n_samples"]
                ),
                "posterior_alpha_mean_psd": float(
                    row[
                        "posterior_alpha_mean_psd"
                    ]
                ),
            })

    if len(reference_rows) == 0:
        raise RuntimeError(
            "Reference feature CSV contains no rows."
        )

    if not all(
        np.isfinite(
            row["posterior_alpha_mean_psd"]
        )
        for row in reference_rows
    ):
        raise ValueError(
            "Reference feature CSV contains "
            "non-finite feature values."
        )

    return reference_rows


def get_reference_feature_row(
    reference_rows,
    configuration_id,
    run,
    center_sec,
):
    matching_rows = [
        row
        for row in reference_rows
        if (
            row["configuration_id"]
            == configuration_id
            and row["run"] == run
            and np.isclose(
                row["window_center_sec"],
                center_sec,
                rtol=0.0,
                atol=1e-12,
            )
        )
    ]

    if len(matching_rows) != 1:
        raise RuntimeError(
            "Expected exactly one reference row "
            f"for {configuration_id}, run {run}, "
            f"center {center_sec:.3f} s, but found "
            f"{len(matching_rows)}."
        )

    return matching_rows[0]


def build_local_decomposition(
    posterior_data,
    sfreq,
    t0_onset,
    t0_end,
    reference_rows,
    run,
    center_sec,
):
    center_sample = int(
        round(center_sec * sfreq)
    )

    one_second_samples = int(
        round(1.0 * sfreq)
    )

    two_second_samples = int(
        round(2.0 * sfreq)
    )

    four_second_samples = int(
        round(4.0 * sfreq)
    )

    two_second_start_sample = (
        center_sample
        - two_second_samples // 2
    )

    two_second_stop_sample = (
        two_second_start_sample
        + two_second_samples
    )

    four_second_start_sample = (
        center_sample
        - four_second_samples // 2
    )

    four_second_stop_sample = (
        four_second_start_sample
        + four_second_samples
    )

    t0_start_sample = int(
        round(t0_onset * sfreq)
    )

    t0_end_sample = int(
        np.floor(t0_end * sfreq)
    )

    if (
        four_second_start_sample
        < t0_start_sample
    ):
        raise ValueError(
            "The local four-second window begins "
            "before the T0 interval."
        )

    if (
        four_second_stop_sample
        > t0_end_sample
    ):
        raise ValueError(
            "The local four-second window ends "
            "after the T0 interval."
        )

    welch_segment_step_samples = (
        WELCH_N_PER_SEG
        - WELCH_N_OVERLAP
    )

    if welch_segment_step_samples <= 0:
        raise ValueError(
            "Welch segment step must be positive."
        )

    segment_rows = []

    segment_start_samples = range(
        four_second_start_sample,
        (
            four_second_stop_sample
            - WELCH_N_PER_SEG
            + 1
        ),
        welch_segment_step_samples,
    )

    for segment_index, start_sample in enumerate(
        segment_start_samples
    ):
        stop_sample = (
            start_sample
            + WELCH_N_PER_SEG
        )

        segment_data = posterior_data[
            :,
            start_sample:stop_sample,
        ]

        expected_segment_shape = (
            len(POSTERIOR_CHANNELS),
            WELCH_N_PER_SEG,
        )

        if (
            segment_data.shape
            != expected_segment_shape
        ):
            raise RuntimeError(
                f"Segment {segment_index} has shape "
                f"{segment_data.shape}, but expected "
                f"{expected_segment_shape}."
            )

        psd_data, freqs = compute_welch_psd(
            window_data=segment_data,
            sfreq=sfreq,
            n_per_seg=WELCH_N_PER_SEG,
            n_overlap=WELCH_N_OVERLAP,
            n_fft=WELCH_N_FFT,
            psd_min_hz=PSD_MIN_HZ,
            psd_max_hz=PSD_MAX_HZ,
        )

        segment_feature = (
            extract_mean_band_psd(
                psd_data=psd_data,
                freqs=freqs,
                band_low_hz=ALPHA_BAND[0],
                band_high_hz=ALPHA_BAND[1],
    )
)

        start_sec = (
            start_sample / sfreq
        )

        stop_sec = (
            stop_sample / sfreq
        )

        segment_center_sec = (
            start_sec + stop_sec
        ) / 2.0

        is_one_second_output = (
            (
                start_sample
                - t0_start_sample
            )
            % one_second_samples
            == 0
        )

        included_in_two_second_window = (
            start_sample
            >= two_second_start_sample
            and stop_sample
            <= two_second_stop_sample
        )

        included_in_four_second_window = (
            start_sample
            >= four_second_start_sample
            and stop_sample
            <= four_second_stop_sample
        )

        stored_one_second_feature = None

        if is_one_second_output:
            reference_one_second_row = (
                get_reference_feature_row(
                    reference_rows=(
                        reference_rows
                    ),
                    configuration_id=(
                        "win-1s_step-1s"
                    ),
                    run=run,
                    center_sec=(
                        segment_center_sec
                    ),
                )
            )

            stored_one_second_feature = float(
                reference_one_second_row[
                    "posterior_alpha_mean_psd"
                ]
            )

            if not np.isclose(
                segment_feature,
                stored_one_second_feature,
                rtol=COMPARISON_RTOL,
                atol=COMPARISON_ATOL,
            ):
                raise RuntimeError(
                    "Recalculated one-second "
                    "segment does not match the "
                    "stored one-second feature."
                )

        segment_rows.append({
            "segment_index": int(
                segment_index
            ),
            "start_sec": float(
                start_sec
            ),
            "stop_sec": float(
                stop_sec
            ),
            "center_sec": float(
                segment_center_sec
            ),
            "is_one_second_output": bool(
                is_one_second_output
            ),
            "included_in_two_second_window": bool(
                included_in_two_second_window
            ),

            "included_in_four_second_window": bool(
                included_in_four_second_window
            ),

            "segment_feature": float(
                segment_feature
            ),
            "stored_one_second_feature": (
                stored_one_second_feature
            ),
        })

    if len(segment_rows) != 7:
        raise RuntimeError(
            "Expected seven one-second Welch "
            "segments inside the four-second "
            f"window, but found {len(segment_rows)}."
        )

    if not all(
        row["included_in_four_second_window"]
        for row in segment_rows
    ):
        raise RuntimeError(
            "A local Welch segment falls outside "
            "the selected four-second window."
        )

    two_second_segment_values = np.asarray(
        [
            row["segment_feature"]
            for row in segment_rows
            if row[
                "included_in_two_second_window"
            ]
        ],
        dtype=float,
    )

    four_second_segment_values = np.asarray(
        [
            row["segment_feature"]
            for row in segment_rows
        ],
        dtype=float,
    )

    if len(two_second_segment_values) != 3:
        raise RuntimeError(
            "Expected three Welch segments "
            "inside the two-second window."
        )

    reconstructed_two_second_feature = float(
        np.mean(
            two_second_segment_values
        )
    )

    reconstructed_four_second_feature = float(
        np.mean(
            four_second_segment_values
        )
    )

    reference_two_second_row = (
        get_reference_feature_row(
            reference_rows=reference_rows,
            configuration_id=(
                "win-2s_step-1s"
            ),
            run=run,
            center_sec=center_sec,
        )
    )

    reference_four_second_row = (
        get_reference_feature_row(
            reference_rows=reference_rows,
            configuration_id=(
                "win-4s_step-1s"
            ),
            run=run,
            center_sec=center_sec,
        )
    )

    stored_two_second_feature = float(
        reference_two_second_row[
            "posterior_alpha_mean_psd"
        ]
    )

    stored_four_second_feature = float(
        reference_four_second_row[
            "posterior_alpha_mean_psd"
        ]
    )

    two_second_difference = float(
        reconstructed_two_second_feature
        - stored_two_second_feature
    )

    four_second_difference = float(
        reconstructed_four_second_feature
        - stored_four_second_feature
    )

    if not np.isclose(
        reconstructed_two_second_feature,
        stored_two_second_feature,
        rtol=COMPARISON_RTOL,
        atol=COMPARISON_ATOL,
    ):
        raise RuntimeError(
            "The three-segment reconstruction "
            "does not match the stored "
            "two-second feature."
        )

    if not np.isclose(
        reconstructed_four_second_feature,
        stored_four_second_feature,
        rtol=COMPARISON_RTOL,
        atol=COMPARISON_ATOL,
    ):
        raise RuntimeError(
            "The seven-segment reconstruction "
            "does not match the stored "
            "four-second feature."
        )

    local_maximum_row = max(
        segment_rows,
        key=lambda row: row[
            "segment_feature"
        ],
    )

    local_minimum_row = min(
        segment_rows,
        key=lambda row: row[
            "segment_feature"
        ],
    )

    return {
        "run": int(run),
        "condition": RUN_LABELS[run],
        "center_sec": float(center_sec),
        "segment_rows": segment_rows,
        "stored_two_second_feature": (
            stored_two_second_feature
        ),
        "reconstructed_two_second_feature": (
            reconstructed_two_second_feature
        ),
        "two_second_difference": (
            two_second_difference
        ),
        "stored_four_second_feature": (
            stored_four_second_feature
        ),
        "reconstructed_four_second_feature": (
            reconstructed_four_second_feature
        ),
        "four_second_difference": (
            four_second_difference
        ),
        "local_maximum_row": (
            local_maximum_row
        ),
        "local_minimum_row": (
            local_minimum_row
        ),
    }


def print_local_decomposition(
    diagnostic,
):
    print(
        "\n########################################"
    )

    print(
        "Local window-length decomposition"
    )

    print(
        "Run:",
        diagnostic["run"],
        diagnostic["condition"],
    )

    print(
        "Comparison center:",
        f"{diagnostic['center_sec']:.1f} s",
    )

    print(
        f"{'Segment':<13}"
        f"{'Center':>8}"
        f"{'1s output':>12}"
        f"{'In 2s':>9}"
        f"{'Segment feature':>19}"
        f"{'Stored 1s':>17}"
    )

    for row in diagnostic["segment_rows"]:
        segment_label = (
            f"{row['start_sec']:.1f}"
            "-"
            f"{row['stop_sec']:.1f}"
        )

        one_second_output_label = (
            "yes"
            if row["is_one_second_output"]
            else "no"
        )

        included_in_two_second_label = (
            "yes"
            if row[
                "included_in_two_second_window"
            ]
            else "no"
        )

        stored_one_second_feature = row[
            "stored_one_second_feature"
        ]

        if stored_one_second_feature is None:
            stored_one_second_text = "-"
        else:
            stored_one_second_text = (
                f"{stored_one_second_feature:.6e}"
            )

        segment_feature = row[
            "segment_feature"
        ]

        center_sec = row[
            "center_sec"
        ]

        print(
            f"{segment_label:<13}"
            f"{center_sec:>8.1f}"
            f"{one_second_output_label:>12}"
            f"{included_in_two_second_label:>9}"
            f"{segment_feature:>19.6e}"
            f"{stored_one_second_text:>17}"
        )

    stored_two_second_feature = diagnostic[
        "stored_two_second_feature"
    ]

    reconstructed_two_second_feature = diagnostic[
        "reconstructed_two_second_feature"
    ]

    two_second_difference = diagnostic[
        "two_second_difference"
    ]

    stored_four_second_feature = diagnostic[
        "stored_four_second_feature"
    ]

    reconstructed_four_second_feature = diagnostic[
        "reconstructed_four_second_feature"
    ]

    four_second_difference = diagnostic[
        "four_second_difference"
    ]

    print(
        "\nTwo-second window: 24.0-26.0 s"
    )

    print(
        "Stored feature:",
        f"{stored_two_second_feature:.12e}",
    )

    print(
        "Mean of three segments:",
        f"{reconstructed_two_second_feature:.12e}",
    )

    print(
        "Difference:",
        f"{two_second_difference:.12e}",
    )

    print(
        "\nFour-second window: 23.0-27.0 s"
    )

    print(
        "Stored feature:",
        f"{stored_four_second_feature:.12e}",
    )

    print(
        "Mean of seven segments:",
        f"{reconstructed_four_second_feature:.12e}",
    )

    print(
        "Difference:",
        f"{four_second_difference:.12e}",
    )

    maximum_row = diagnostic[
        "local_maximum_row"
    ]

    minimum_row = diagnostic[
        "local_minimum_row"
    ]

    print("\nLocal segment extremes")

    print(
        "Maximum:",
        f"{maximum_row['start_sec']:.1f}"
        "-"
        f"{maximum_row['stop_sec']:.1f} s,",
        f"{maximum_row['segment_feature']:.6e}",
    )

    print(
        "Minimum:",
        f"{minimum_row['start_sec']:.1f}"
        "-"
        f"{minimum_row['stop_sec']:.1f} s,",
        f"{minimum_row['segment_feature']:.6e}",
    )


def save_local_decomposition_csv(
    diagnostic,
):
    fieldnames = [
        "run",
        "condition",
        "analysis_center_sec",
        "segment_start_sec",
        "segment_end_sec",
        "segment_center_sec",
        "segment_feature",
        "is_1s_output",
        "included_in_2s_window",
        "included_in_4s_window",
        "stored_1s_feature",
    ]

    output_rows = []

    for segment_row in diagnostic[
        "segment_rows"
    ]:
        stored_one_second_feature = (
            segment_row[
                "stored_one_second_feature"
            ]
        )

        if stored_one_second_feature is None:
            stored_one_second_value = ""
        else:
            stored_one_second_value = float(
                stored_one_second_feature
            )

        output_rows.append({
            "run": diagnostic["run"],
            "condition": diagnostic[
                "condition"
            ],
            "analysis_center_sec": diagnostic[
                "center_sec"
            ],
            "segment_start_sec": segment_row[
                "start_sec"
            ],
            "segment_end_sec": segment_row[
                "stop_sec"
            ],
            "segment_center_sec": segment_row[
                "center_sec"
            ],
            "segment_feature": segment_row[
                "segment_feature"
            ],
            "is_1s_output": segment_row[
                "is_one_second_output"
            ],
            "included_in_2s_window": (
                segment_row[
                    "included_in_two_second_window"
                ]
            ),
            "included_in_4s_window": (
                segment_row[
                    "included_in_four_second_window"
                ]
            ),
            "stored_1s_feature": (
                stored_one_second_value
            ),
        })

    LOCAL_DECOMPOSITION_CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        LOCAL_DECOMPOSITION_CSV_PATH,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(output_rows)

    if not LOCAL_DECOMPOSITION_CSV_PATH.exists():
        raise RuntimeError(
            "Local decomposition CSV was "
            "not created."
        )

    if (
        LOCAL_DECOMPOSITION_CSV_PATH.stat().st_size
        == 0
    ):
        raise RuntimeError(
            "Local decomposition CSV is empty."
        )

    with open(
        LOCAL_DECOMPOSITION_CSV_PATH,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)
        saved_rows = list(reader)

        if reader.fieldnames != fieldnames:
            raise RuntimeError(
                "Saved local decomposition CSV "
                "header does not match the "
                "configured field order."
            )

    if len(saved_rows) != len(output_rows):
        raise RuntimeError(
            "Saved local decomposition CSV "
            "row count does not match the "
            "generated row count."
        )

    if len(saved_rows) != 7:
        raise RuntimeError(
            "Expected seven rows in the local "
            "decomposition CSV, but found "
            f"{len(saved_rows)}."
        )

    return LOCAL_DECOMPOSITION_CSV_PATH


def main():
    if not WINDOW_FEATURE_CSV_PATH.exists():
        raise FileNotFoundError(
            "Session 14 window-feature CSV "
            "was not found: "
            f"{WINDOW_FEATURE_CSV_PATH}"
        )

    raw = load_raw(
        LOCAL_DIAGNOSTIC_RUN
    )

    t0_onset, t0_duration, t0_end = (
        get_t0_interval(raw)
    )

    (
        posterior_data,
        posterior_channel_names,
    ) = prepare_posterior_data(raw)

    sfreq = float(
        raw.info["sfreq"]
    )

    print(
        "\n########################################"
    )

    print(
        "Session 14 local decomposition "
        "initialization"
    )

    print(
        "Run:",
        LOCAL_DIAGNOSTIC_RUN,
        RUN_LABELS[
            LOCAL_DIAGNOSTIC_RUN
        ],
    )

    print(
        "Comparison center:",
        LOCAL_DIAGNOSTIC_CENTER_SEC,
        "s",
    )

    print(
        "Sampling frequency:",
        sfreq,
        "Hz",
    )

    print(
        "Posterior channels:",
        posterior_channel_names,
    )

    print(
        "Posterior data shape:",
        posterior_data.shape,
    )

    print(
        "T0 interval:",
        f"{t0_onset:.1f}"
        "-"
        f"{t0_end:.1f} s",
    )

    print(
        "T0 duration:",
        f"{t0_duration:.1f} s",
    )

    print(
        "Reference feature CSV:",
        WINDOW_FEATURE_CSV_PATH,
    )

    print(
        "\nLocal decomposition "
        "initialization completed."
    )

    reference_rows = (
        load_reference_feature_rows()
    )

    diagnostic = build_local_decomposition(
        posterior_data=posterior_data,
        sfreq=sfreq,
        t0_onset=t0_onset,
        t0_end=t0_end,
        reference_rows=reference_rows,
        run=LOCAL_DIAGNOSTIC_RUN,
        center_sec=(
            LOCAL_DIAGNOSTIC_CENTER_SEC
        ),
    )

    print_local_decomposition(
        diagnostic=diagnostic
    )

    saved_csv_path = (
        save_local_decomposition_csv(
            diagnostic=diagnostic
        )
    )

    print(
        "\nSaved local decomposition CSV:",
        saved_csv_path,
    )

    print(
        "\nLocal decomposition "
        "validation completed."
    )


if __name__ == "__main__":
    main()