# Session 15 offline decision-rule analysis.
# Step 1: Load and validate the saved Session 14
# baseline feature stream.

import csv
from collections import defaultdict
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_FEATURE_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-14"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_window-features.csv"
    )
)

SESSION15_RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "session-15"
)

DECISION_STREAM_CSV_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "decision-stream.csv"
    )
)

COMMAND_EPISODE_CSV_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "command-episodes.csv"
    )
)

RULE_RUN_SUMMARY_CSV_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "rule-run-summary.csv"
    )
)

# Session 15 descriptive threshold for
# counting brief active OPEN/CLOSE episodes.
SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC = 2.0

# Fixed Session 15 analysis specification.
BASELINE_CONFIGURATION_ID = "win-2s_step-1s"

BASELINE_WINDOW_LENGTH_SEC = 2.0
BASELINE_STEP_SIZE_SEC = 1.0
BASELINE_OVERLAP_FRACTION = 0.5
BASELINE_WELCH_SEGMENT_COUNT = 3

FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

FEATURE_COLUMN = "posterior_alpha_mean_psd"
DECISION_TIME_COLUMN = "window_end_sec"

EYES_OPEN_CONDITION = "baseline_eyes_open"
EYES_CLOSED_CONDITION = "baseline_eyes_closed"

QUANTILE_METHOD = "linear"

CORE_THRESHOLD_ID = "threshold_gap_midpoint"

SMOOTHING_ID_NONE = "smooth-none"

SMOOTHING_ID_MEDIAN3 = "smooth-median3"
MEDIAN3_WINDOW_UPDATES = 3

LOW_EVIDENCE_STATE = "LOW_ALPHA"
HIGH_EVIDENCE_STATE = "HIGH_ALPHA"

OPEN_COMMAND_STATE = "CMD_OPEN"
CLOSE_COMMAND_STATE = "CMD_CLOSE"
STOP_COMMAND_STATE = "CMD_STOP"

UNAVAILABLE_EVIDENCE_STATE = "UNAVAILABLE"

CORE_RULE_CONFIGURATIONS = [
    {
        "rule_id": (
            "thr-eo-q95__smooth-none__dwell-1"
        ),
        "threshold_id": "threshold_eo_q95",
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 1,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-none__dwell-1"
        ),
        "threshold_id": (
            "threshold_gap_midpoint"
        ),
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 1,
    },
    {
        "rule_id": (
            "thr-ec-q05__smooth-none__dwell-1"
        ),
        "threshold_id": "threshold_ec_q05",
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 1,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-none__dwell-2"
        ),
        "threshold_id": (
            "threshold_gap_midpoint"
        ),
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 2,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-none__dwell-3"
        ),
        "threshold_id": (
            "threshold_gap_midpoint"
        ),
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 3,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-median3__dwell-1"
        ),
        "threshold_id": (
            "threshold_gap_midpoint"
        ),
        "smoothing_id": (
            SMOOTHING_ID_MEDIAN3
        ),
        "dwell_updates": 1,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-median3__dwell-2"
        ),
        "threshold_id": (
            "threshold_gap_midpoint"
        ),
        "smoothing_id": (
            SMOOTHING_ID_MEDIAN3
        ),
        "dwell_updates": 2,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-median3__dwell-3"
        ),
        "threshold_id": (
            "threshold_gap_midpoint"
        ),
        "smoothing_id": (
            SMOOTHING_ID_MEDIAN3
        ),
        "dwell_updates": 3,
    },
]

RTOL = 1e-12
ATOL = 1e-15


REQUIRED_COLUMNS = [
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
    "feature_name",
    "feature_unit",
    FEATURE_COLUMN,
]

DECISION_STREAM_COLUMNS = [
    "rule_id",
    "subject",
    "run",
    "condition",
    "configuration_id",
    "window_index",
    "window_start_sec",
    "window_end_sec",
    "decision_time_sec",
    "feature_name",
    "feature_unit",
    "raw_feature_value",
    "smoothing_id",
    "smoothed_available",
    "smoothed_feature_value",
    "threshold_id",
    "threshold_value",
    "evidence_state",
    "dwell_updates",
    "candidate_evidence_state",
    "candidate_count",
    "active_evidence_state",
    "initial_command_confirmed",
    "active_switch_confirmed",
    "command_state",
]

COMMAND_EPISODE_COLUMNS = [
    "rule_id",
    "subject",
    "run",
    "condition",
    "configuration_id",
    "feature_name",
    "feature_unit",
    "smoothing_id",
    "threshold_id",
    "threshold_value",
    "dwell_updates",
    "episode_index",
    "command_state",
    "episode_start_time_sec",
    "episode_end_time_sec",
    "episode_duration_sec",
    "decision_update_count",
    "first_window_index",
    "last_window_index",
    "first_decision_time_sec",
    "last_decision_time_sec",
    "start_event",
    "end_event",
    "is_initial_stop_episode",
    "ended_at_run_boundary",
]

RULE_RUN_SUMMARY_COLUMNS = [
    "rule_id",
    "subject",
    "run",
    "condition",
    "configuration_id",
    "feature_name",
    "feature_unit",
    "smoothing_id",
    "threshold_id",
    "threshold_value",
    "dwell_updates",
    "nominal_confirmation_span_sec",
    "run_start_time_sec",
    "run_end_time_sec",
    "decision_update_count",
    "first_decision_time_sec",
    "last_decision_time_sec",
    "unavailable_evidence_count",
    "first_processed_feature_time_sec",
    "initial_stop_update_count",
    "initial_stop_duration_sec",
    "first_active_command_time_sec",
    "first_active_command",
    "final_command_state",
    "low_evidence_count",
    "high_evidence_count",
    "cmd_stop_count",
    "cmd_open_count",
    "cmd_close_count",
    "active_switch_count",
    "active_switch_times_sec",
    "unconfirmed_candidate_update_count",
    "unconfirmed_candidate_times_sec",
    "command_episode_count",
    "active_command_episode_count",
    "short_active_episode_max_duration_sec",
    "short_active_command_episode_count",
    "shortest_active_episode_duration_sec",
    "longest_active_episode_duration_sec",
]


def load_source_rows(csv_path):
    """
    Read the saved Session 14 feature CSV.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            "Source feature CSV was not found:\n"
            f"{csv_path}"
        )

    with open(
        csv_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "The source CSV has no header."
            )

        missing_columns = [
            column
            for column in REQUIRED_COLUMNS
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise RuntimeError(
                "Missing required columns: "
                f"{missing_columns}"
            )

        source_rows = list(reader)

    if not source_rows:
        raise RuntimeError(
            "The source CSV has no data rows."
        )

    return source_rows


def convert_selected_row(row):
    """
    Convert the values needed by Session 15
    from CSV strings to Python numeric types.
    """

    try:
        return {
            "subject": int(
                row["subject"]
            ),
            "run": int(
                row["run"]
            ),
            "condition": row[
                "condition"
            ],
            "configuration_id": row[
                "configuration_id"
            ],
            "window_length_sec": float(
                row["window_length_sec"]
            ),
            "step_size_sec": float(
                row["step_size_sec"]
            ),
            "outer_window_overlap_fraction": float(
                row[
                    "outer_window_overlap_fraction"
                ]
            ),
            "welch_segment_count": int(
                row["welch_segment_count"]
            ),
            "window_index": int(
                row["window_index"]
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
            "feature_name": row[
                "feature_name"
            ],
            "feature_unit": row[
                "feature_unit"
            ],
            FEATURE_COLUMN: float(
                row[FEATURE_COLUMN]
            ),
        }

    except (TypeError, ValueError) as error:
        raise ValueError(
            "A selected row contains an "
            "invalid value: "
            f"{row}"
        ) from error


def select_baseline_rows(source_rows):
    """
    Select only the configuration fixed
    for Session 15.

    No row count is assumed in advance.
    """

    selected_rows = [
        convert_selected_row(row)
        for row in source_rows
        if (
            row["configuration_id"]
            == BASELINE_CONFIGURATION_ID
        )
    ]

    if not selected_rows:
        available_configuration_ids = sorted({
            row["configuration_id"]
            for row in source_rows
        })

        raise RuntimeError(
            "The selected configuration "
            "was not found. "
            f"Selected: "
            f"{BASELINE_CONFIGURATION_ID}. "
            f"Available: "
            f"{available_configuration_ids}"
        )

    selected_rows.sort(
        key=lambda row: (
            row["subject"],
            row["run"],
            row["window_index"],
        )
    )

    return selected_rows


def validate_selected_rows(
    selected_rows,
):
    """
    Confirm that every selected row matches
    the Session 15 feature specification.

    This validates stored values.
    """

    for row in selected_rows:
        numeric_values = np.asarray(
            [
                row["window_length_sec"],
                row["step_size_sec"],
                row[
                    "outer_window_overlap_fraction"
                ],
                row["window_start_sec"],
                row["window_end_sec"],
                row["window_center_sec"],
                row[FEATURE_COLUMN],
            ],
            dtype=float,
        )

        if not np.isfinite(
            numeric_values
        ).all():
            raise ValueError(
                "A selected row contains a "
                "non-finite value: "
                f"{row}"
            )

        if row[FEATURE_COLUMN] <= 0:
            raise ValueError(
                "The saved PSD feature must "
                "be positive: "
                f"{row}"
            )

        specification_checks = [
            np.isclose(
                row["window_length_sec"],
                BASELINE_WINDOW_LENGTH_SEC,
                rtol=RTOL,
                atol=ATOL,
            ),
            np.isclose(
                row["step_size_sec"],
                BASELINE_STEP_SIZE_SEC,
                rtol=RTOL,
                atol=ATOL,
            ),
            np.isclose(
                row[
                    "outer_window_overlap_fraction"
                ],
                BASELINE_OVERLAP_FRACTION,
                rtol=RTOL,
                atol=ATOL,
            ),
            (
                row["welch_segment_count"]
                == BASELINE_WELCH_SEGMENT_COUNT
            ),
            (
                row["feature_name"]
                == FEATURE_NAME
            ),
            (
                row["feature_unit"]
                == FEATURE_UNIT
            ),
        ]

        if not all(
            specification_checks
        ):
            raise RuntimeError(
                "A selected row does not match "
                "the fixed Session 15 "
                "specification: "
                f"{row}"
            )


def group_rows_by_recording(
    selected_rows,
):
    """
    Group rows dynamically by subject and run.

    Subject count, run count, and window count
    are not fixed in advance.
    """

    grouped_rows = defaultdict(list)

    for row in selected_rows:
        group_key = (
            row["subject"],
            row["run"],
        )

        grouped_rows[
            group_key
        ].append(row)

    for rows in grouped_rows.values():
        rows.sort(
            key=lambda row: (
                row["window_index"]
            )
        )

    return dict(grouped_rows)


def validate_recording_structure(
    grouped_rows,
):
    """
    Validate the window indices and time
    structure separately for each recording.
    """

    for (
        subject,
        run,
    ), rows in grouped_rows.items():
        conditions = {
            row["condition"]
            for row in rows
        }

        if len(conditions) != 1:
            raise RuntimeError(
                "Multiple condition labels "
                "were found for "
                f"subject {subject}, "
                f"run {run}: "
                f"{conditions}"
            )

        window_indices = [
            row["window_index"]
            for row in rows
        ]

        expected_window_indices = list(
            range(len(rows))
        )

        if (
            window_indices
            != expected_window_indices
        ):
            raise RuntimeError(
                "Window indices are duplicated, "
                "missing, or out of order for "
                f"subject {subject}, "
                f"run {run}: "
                f"{window_indices}"
            )

        window_start_times = np.asarray(
            [
                row["window_start_sec"]
                for row in rows
            ],
            dtype=float,
        )

        window_end_times = np.asarray(
            [
                row["window_end_sec"]
                for row in rows
            ],
            dtype=float,
        )

        window_center_times = np.asarray(
            [
                row["window_center_sec"]
                for row in rows
            ],
            dtype=float,
        )

        calculated_window_lengths = (
            window_end_times
            - window_start_times
        )

        if not np.allclose(
            calculated_window_lengths,
            BASELINE_WINDOW_LENGTH_SEC,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError(
                "Window duration is inconsistent "
                "for "
                f"subject {subject}, "
                f"run {run}."
            )

        expected_center_times = (
            window_start_times
            + window_end_times
        ) / 2.0

        if not np.allclose(
            window_center_times,
            expected_center_times,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError(
                "Window center time is "
                "inconsistent for "
                f"subject {subject}, "
                f"run {run}."
            )

        if len(rows) >= 2:
            decision_time_differences = (
                np.diff(
                    window_end_times
                )
            )

            if not np.allclose(
                decision_time_differences,
                BASELINE_STEP_SIZE_SEC,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "Decision times do not "
                    "follow the fixed 1 s step "
                    "for "
                    f"subject {subject}, "
                    f"run {run}."
                )


def print_input_summary(
    source_rows,
    selected_rows,
    grouped_rows,
):
    """
    Print the actual input structure.

    Step 1 does not save a new result file.
    """

    print("\n========================================")
    print(
        "Session 15 Step 1: "
        "Input validation"
    )

    print(
        "Source CSV:",
        SOURCE_FEATURE_CSV_PATH,
    )

    print(
        "Source row count:",
        len(source_rows),
    )

    print(
        "Selected configuration:",
        BASELINE_CONFIGURATION_ID,
    )

    print(
        "Selected row count:",
        len(selected_rows),
    )

    print(
        "Subject/run group count:",
        len(grouped_rows),
    )

    for (
        subject,
        run,
    ), rows in sorted(
        grouped_rows.items()
    ):
        first_row = rows[0]
        last_row = rows[-1]

        feature_values = np.asarray(
            [
                row[FEATURE_COLUMN]
                for row in rows
            ],
            dtype=float,
        )

        print("\n----------------------------------------")
        print(
            "Subject:",
            subject,
        )

        print(
            "Run:",
            run,
        )

        print(
            "Condition:",
            first_row["condition"],
        )

        print(
            "Window count:",
            len(rows),
        )

        print(
            "First window:",
            f"{first_row['window_start_sec']:.1f}"
            "–"
            f"{first_row['window_end_sec']:.1f} s",
        )

        print(
            "Last window:",
            f"{last_row['window_start_sec']:.1f}"
            "–"
            f"{last_row['window_end_sec']:.1f} s",
        )

        print(
            "Decision-time range:",
            f"{first_row[DECISION_TIME_COLUMN]:.1f}"
            "–"
            f"{last_row[DECISION_TIME_COLUMN]:.1f} s",
        )

        print(
            "Feature range:",
            f"{feature_values.min():.12e}"
            "–"
            f"{feature_values.max():.12e}",
            FEATURE_UNIT,
        )

    print(
        "\nInput validation completed."
    )


def calculate_threshold_candidates(
    selected_rows,
):
    """
    Calculate three threshold candidates
    from the unsmoothed baseline features.

    Input:
        Selected Session 15 feature rows.

    Output:
        Threshold values grouped by subject.
    """

    subjects = sorted({
        row["subject"]
        for row in selected_rows
    })

    thresholds_by_subject = {}

    for subject in subjects:
        eyes_open_values = np.asarray(
            [
                row[FEATURE_COLUMN]
                for row in selected_rows
                if (
                    row["subject"] == subject
                    and row["condition"]
                    == EYES_OPEN_CONDITION
                )
            ],
            dtype=float,
        )

        eyes_closed_values = np.asarray(
            [
                row[FEATURE_COLUMN]
                for row in selected_rows
                if (
                    row["subject"] == subject
                    and row["condition"]
                    == EYES_CLOSED_CONDITION
                )
            ],
            dtype=float,
        )

        if len(eyes_open_values) == 0:
            raise RuntimeError(
                "No eyes-open feature values "
                "were found for "
                f"subject {subject}."
            )

        if len(eyes_closed_values) == 0:
            raise RuntimeError(
                "No eyes-closed feature values "
                "were found for "
                f"subject {subject}."
            )

        eyes_open_q95 = float(
            np.quantile(
                eyes_open_values,
                0.95,
                method=QUANTILE_METHOD,
            )
        )

        eyes_closed_q05 = float(
            np.quantile(
                eyes_closed_values,
                0.05,
                method=QUANTILE_METHOD,
            )
        )

        if not (
            0.0
            < eyes_open_q95
            < eyes_closed_q05
        ):
            raise RuntimeError(
                "The central threshold gap "
                "condition was not satisfied for "
                f"subject {subject}: "
                f"EO Q95={eyes_open_q95:.12e}, "
                f"EC Q05={eyes_closed_q05:.12e}."
            )

        geometric_midpoint = float(
            np.sqrt(
                eyes_open_q95
                * eyes_closed_q05
            )
        )

        if not (
            eyes_open_q95
            < geometric_midpoint
            < eyes_closed_q05
        ):
            raise RuntimeError(
                "The geometric midpoint is not "
                "between EO Q95 and EC Q05."
            )

        thresholds_by_subject[subject] = {
            "threshold_eo_q95": (
                eyes_open_q95
            ),
            "threshold_gap_midpoint": (
                geometric_midpoint
            ),
            "threshold_ec_q05": (
                eyes_closed_q05
            ),
        }

    return thresholds_by_subject


def print_threshold_summary(
    thresholds_by_subject,
):
    """
    Print the calculated raw-feature
    threshold candidates.
    """

    print("\n========================================")
    print(
        "Session 15 Step 2: "
        "Threshold candidates"
    )

    print(
        "Threshold source:",
        "unsmoothed baseline feature",
    )

    print(
        "Quantile method:",
        QUANTILE_METHOD,
    )

    for subject, thresholds in sorted(
        thresholds_by_subject.items()
    ):
        print("\n----------------------------------------")
        print("Subject:", subject)

        print(
            "EO Q95 threshold:",
            f"{thresholds['threshold_eo_q95']:.12e}",
            FEATURE_UNIT,
        )

        print(
            "Gap midpoint threshold:",
            f"{thresholds['threshold_gap_midpoint']:.12e}",
            FEATURE_UNIT,
        )

        print(
            "EC Q05 threshold:",
            f"{thresholds['threshold_ec_q05']:.12e}",
            FEATURE_UNIT,
        )

    print(
        "\nThreshold calculation completed."
    )


def build_no_smoothing_rows(
    selected_rows,
):
    """
    Standardize the unsmoothed feature stream
    using the same processed-feature fields
    as the median-3 stream.
    """

    processed_rows = []

    for row in selected_rows:
        output_row = dict(row)

        output_row["smoothing_id"] = (
            SMOOTHING_ID_NONE
        )

        output_row["smoothed_available"] = True

        output_row["smoothed_feature_value"] = (
            row[FEATURE_COLUMN]
        )

        processed_rows.append(
            output_row
        )

    if len(processed_rows) != len(
        selected_rows
    ):
        raise RuntimeError(
            "No-smoothing row count does not "
            "match the selected input-row count."
        )

    return processed_rows


def build_causal_median3_rows(
    selected_rows,
):
    """
    Calculate a causal three-update median
    feature separately for each recording.
    """

    grouped_rows = group_rows_by_recording(
        selected_rows
    )

    smoothed_rows = []

    for (
        subject,
        run,
    ), rows in sorted(
        grouped_rows.items()
    ):
        rows = sorted(
            rows,
            key=lambda row: row["window_index"],
        )

        raw_values = np.asarray(
            [
                row[FEATURE_COLUMN]
                for row in rows
            ],
            dtype=float,
        )

        for index, row in enumerate(rows):
            output_row = dict(row)

            output_row["smoothing_id"] = (
                SMOOTHING_ID_MEDIAN3
            )

            # The first two updates do not yet
            # contain three causal feature values.
            if index < (
                MEDIAN3_WINDOW_UPDATES - 1
            ):
                output_row[
                    "smoothed_available"
                ] = False

                output_row[
                    "smoothed_feature_value"
                ] = None

            else:
                source_values = raw_values[
                    index
                    - MEDIAN3_WINDOW_UPDATES
                    + 1:
                    index + 1
                ]

                smoothed_value = float(
                    np.median(source_values)
                )

                output_row[
                    "smoothed_available"
                ] = True

                output_row[
                    "smoothed_feature_value"
                ] = smoothed_value

            smoothed_rows.append(
                output_row
            )

    if len(smoothed_rows) != len(
        selected_rows
    ):
        raise RuntimeError(
            "Median-3 row count does not match "
            "the selected input-row count."
        )

    return smoothed_rows


def print_causal_median3_validation(
    smoothed_rows,
    thresholds_by_subject,
):
    """
    Validate median-3 availability and compare
    raw and smoothed midpoint evidence states.
    """

    grouped_rows = defaultdict(list)

    for row in smoothed_rows:
        group_key = (
            row["subject"],
            row["run"],
        )

        grouped_rows[group_key].append(row)

    print("\n========================================")
    print(
        "Session 15 Step 3: "
        "Causal median-3 validation"
    )

    for (
        subject,
        run,
    ), rows in sorted(
        grouped_rows.items()
    ):
        rows.sort(
            key=lambda row: row["window_index"]
        )

        threshold_value = (
            thresholds_by_subject[subject][
                CORE_THRESHOLD_ID
            ]
        )

        unavailable_rows = [
            row
            for row in rows
            if not row["smoothed_available"]
        ]

        available_rows = [
            row
            for row in rows
            if row["smoothed_available"]
        ]

        if len(unavailable_rows) != (
            MEDIAN3_WINDOW_UPDATES - 1
        ):
            raise RuntimeError(
                "Unexpected median-3 warm-up "
                f"count for subject {subject}, "
                f"run {run}."
            )

        changed_evidence_rows = []

        for row in available_rows:
            raw_state = (
                HIGH_EVIDENCE_STATE
                if row[FEATURE_COLUMN]
                >= threshold_value
                else LOW_EVIDENCE_STATE
            )

            smoothed_state = (
                HIGH_EVIDENCE_STATE
                if row[
                    "smoothed_feature_value"
                ]
                >= threshold_value
                else LOW_EVIDENCE_STATE
            )

            if raw_state != smoothed_state:
                changed_evidence_rows.append({
                    "decision_time_sec": row[
                        DECISION_TIME_COLUMN
                    ],
                    "raw_state": raw_state,
                    "smoothed_state": (
                        smoothed_state
                    ),
                    "raw_feature_value": row[
                        FEATURE_COLUMN
                    ],
                    "smoothed_feature_value": row[
                        "smoothed_feature_value"
                    ],
                })

        first_available_row = available_rows[0]

        print("\n----------------------------------------")
        print("Subject:", subject)
        print("Run:", run)
        print(
            "Condition:",
            rows[0]["condition"],
        )

        print(
            "Total update count:",
            len(rows),
        )

        print(
            "Warm-up unavailable count:",
            len(unavailable_rows),
        )

        print(
            "Smoothed available count:",
            len(available_rows),
        )

        print(
            "First smoothed decision time:",
            f"{first_available_row[DECISION_TIME_COLUMN]:.1f} s",
        )

        print(
            "Raw-vs-smoothed evidence "
            "difference count:",
            len(changed_evidence_rows),
        )

        if changed_evidence_rows:
            print(
                "Changed evidence rows:"
            )

            for changed_row in (
                changed_evidence_rows
            ):
                print(
                    "  "
                    f"t={changed_row['decision_time_sec']:.1f} s, "
                    f"{changed_row['raw_state']} "
                    "-> "
                    f"{changed_row['smoothed_state']}, "
                    "raw="
                    f"{changed_row['raw_feature_value']:.12e}, "
                    "median3="
                    f"{changed_row['smoothed_feature_value']:.12e}"
                )

        else:
            print(
                "Changed evidence rows:",
                "None",
            )

    print(
        "\nCausal median-3 validation completed."
    )


def command_from_evidence_state(
    evidence_state,
):
    """
    Map an active evidence state to its
    corresponding virtual command.
    """

    if evidence_state == LOW_EVIDENCE_STATE:
        return OPEN_COMMAND_STATE

    if evidence_state == HIGH_EVIDENCE_STATE:
        return CLOSE_COMMAND_STATE

    raise RuntimeError(
        "Cannot map an unexpected evidence "
        f"state to a command: {evidence_state}"
    )


def build_dwell_decision_rows(
    processed_rows,
    thresholds_by_subject,
    threshold_id,
    dwell_updates,
    rule_id,
):
    """
    Apply one threshold and consecutive-evidence
    dwell rule to a standardized feature stream.
    """

    if not processed_rows:
        raise RuntimeError(
            "No processed feature rows were "
            "provided for dwell processing."
        )

    if (
        not isinstance(dwell_updates, int)
        or dwell_updates < 1
    ):
        raise ValueError(
            "dwell_updates must be a positive "
            "integer."
        )

    grouped_rows = group_rows_by_recording(
        processed_rows
    )

    decision_rows = []

    for (
        subject,
        run,
    ), rows in sorted(
        grouped_rows.items()
    ):
        rows = sorted(
            rows,
            key=lambda row: row["window_index"],
        )

        if subject not in thresholds_by_subject:
            raise RuntimeError(
                "No threshold values were found "
                f"for subject {subject}."
            )

        if (
            threshold_id
            not in thresholds_by_subject[subject]
        ):
            raise RuntimeError(
                "The requested threshold was "
                "not found for "
                f"subject {subject}: "
                f"{threshold_id}"
            )

        smoothing_ids = {
            row["smoothing_id"]
            for row in rows
        }

        if len(smoothing_ids) != 1:
            raise RuntimeError(
                "A recording contains multiple "
                "smoothing IDs for "
                f"subject {subject}, "
                f"run {run}: "
                f"{smoothing_ids}"
            )

        smoothing_id = next(
            iter(smoothing_ids)
        )

        threshold_value = (
            thresholds_by_subject[subject][
                threshold_id
            ]
        )

        # The active evidence state has already
        # satisfied the dwell requirement.
        active_evidence_state = None

        # The pending state has not yet satisfied
        # the dwell requirement.
        pending_evidence_state = None
        pending_count = 0

        for row in rows:
            raw_feature_value = row[
                FEATURE_COLUMN
            ]

            smoothed_available = row[
                "smoothed_available"
            ]

            smoothed_feature_value = row[
                "smoothed_feature_value"
            ]

            initial_command_confirmed = False
            active_switch_confirmed = False

            pending_state_for_row = None
            pending_count_for_row = 0

            # An unavailable feature produces STOP
            # and does not enter the dwell machine.
            if not smoothed_available:
                if smoothed_feature_value is not None:
                    raise RuntimeError(
                        "An unavailable processed "
                        "row must not contain a "
                        "feature value."
                    )

                if (
                    active_evidence_state is not None
                    or pending_evidence_state is not None
                    or pending_count != 0
                ):
                    raise RuntimeError(
                        "An unavailable processed "
                        "row occurred after dwell "
                        "processing had started."
                    )

                evidence_state = (
                    UNAVAILABLE_EVIDENCE_STATE
                )

                command_state = (
                    STOP_COMMAND_STATE
                )

            else:
                if smoothed_feature_value is None:
                    raise RuntimeError(
                        "An available processed "
                        "row must contain a "
                        "feature value."
                    )

                if (
                    not np.isfinite(
                        smoothed_feature_value
                    )
                    or smoothed_feature_value <= 0.0
                ):
                    raise RuntimeError(
                        "The processed feature "
                        "must be finite and positive."
                    )

                if (
                    smoothed_feature_value
                    >= threshold_value
                ):
                    evidence_state = (
                        HIGH_EVIDENCE_STATE
                    )
                else:
                    evidence_state = (
                        LOW_EVIDENCE_STATE
                    )

                # No command has yet been
                # initialized.
                if active_evidence_state is None:
                    if (
                        pending_evidence_state
                        == evidence_state
                    ):
                        pending_count += 1
                    else:
                        pending_evidence_state = (
                            evidence_state
                        )
                        pending_count = 1

                    pending_state_for_row = (
                        pending_evidence_state
                    )

                    pending_count_for_row = (
                        pending_count
                    )

                    if (
                        pending_count
                        >= dwell_updates
                    ):
                        active_evidence_state = (
                            evidence_state
                        )

                        initial_command_confirmed = (
                            True
                        )

                        pending_evidence_state = None
                        pending_count = 0

                # Current evidence agrees with
                # the active command state.
                elif (
                    evidence_state
                    == active_evidence_state
                ):
                    pending_evidence_state = None
                    pending_count = 0

                # Current evidence opposes the
                # active command state.
                else:
                    if (
                        pending_evidence_state
                        == evidence_state
                    ):
                        pending_count += 1
                    else:
                        pending_evidence_state = (
                            evidence_state
                        )
                        pending_count = 1

                    pending_state_for_row = (
                        pending_evidence_state
                    )

                    pending_count_for_row = (
                        pending_count
                    )

                    if (
                        pending_count
                        >= dwell_updates
                    ):
                        active_evidence_state = (
                            evidence_state
                        )

                        active_switch_confirmed = (
                            True
                        )

                        pending_evidence_state = None
                        pending_count = 0

                if active_evidence_state is None:
                    command_state = (
                        STOP_COMMAND_STATE
                    )
                else:
                    command_state = (
                        command_from_evidence_state(
                            active_evidence_state
                        )
                    )

            decision_rows.append({
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": row["condition"],
                "configuration_id": row[
                    "configuration_id"
                ],
                "window_index": row[
                    "window_index"
                ],
                "window_start_sec": row[
                    "window_start_sec"
                ],
                "window_end_sec": row[
                    "window_end_sec"
                ],
                "decision_time_sec": row[
                    DECISION_TIME_COLUMN
                ],
                "raw_feature_value": (
                    raw_feature_value
                ),
                "smoothing_id": smoothing_id,
                "smoothed_feature_value": (
                    smoothed_feature_value
                ),
                "smoothed_available": (
                    smoothed_available
                ),
                "threshold_id": threshold_id,
                "threshold_value": (
                    threshold_value
                ),
                "evidence_state": (
                    evidence_state
                ),
                "dwell_updates": dwell_updates,
                "candidate_evidence_state": (
                    pending_state_for_row
                ),
                "candidate_count": (
                    pending_count_for_row
                ),
                "active_evidence_state": (
                    active_evidence_state
                ),
                "initial_command_confirmed": (
                    initial_command_confirmed
                ),
                "active_switch_confirmed": (
                    active_switch_confirmed
                ),
                "command_state": (
                    command_state
                ),
            })

    if len(decision_rows) != len(
        processed_rows
    ):
        raise RuntimeError(
            "Generic dwell decision-row count "
            "does not match the processed-row "
            "count."
        )

    return decision_rows


def build_core_rule_rows_by_rule(
    processed_rows_by_smoothing,
    thresholds_by_subject,
):
    """
    Build all Session 15 core rules using
    the common dwell state machine.

    Output:
        Decision rows keyed by rule ID.
    """

    rule_rows_by_rule = {}
    seen_rule_ids = set()

    for rule_config in (
        CORE_RULE_CONFIGURATIONS
    ):
        rule_id = rule_config["rule_id"]

        threshold_id = rule_config[
            "threshold_id"
        ]

        smoothing_id = rule_config[
            "smoothing_id"
        ]

        dwell_updates = rule_config[
            "dwell_updates"
        ]

        if rule_id in seen_rule_ids:
            raise RuntimeError(
                "A duplicate core rule ID was "
                f"found: {rule_id}"
            )

        seen_rule_ids.add(rule_id)

        if (
            smoothing_id
            not in processed_rows_by_smoothing
        ):
            raise RuntimeError(
                "No processed feature stream "
                "was found for smoothing ID: "
                f"{smoothing_id}"
            )

        processed_rows = (
            processed_rows_by_smoothing[
                smoothing_id
            ]
        )

        decision_rows = (
            build_dwell_decision_rows(
                processed_rows=processed_rows,
                thresholds_by_subject=(
                    thresholds_by_subject
                ),
                threshold_id=threshold_id,
                dwell_updates=dwell_updates,
                rule_id=rule_id,
            )
        )

        rule_rows_by_rule[
            rule_id
        ] = decision_rows

    if len(rule_rows_by_rule) != len(
        CORE_RULE_CONFIGURATIONS
    ):
        raise RuntimeError(
            "The generated core-rule count "
            "does not match the configuration "
            "count."
        )

    return rule_rows_by_rule


def save_decision_stream_csv(
    core_rule_rows_by_rule,
    output_path,
):
    """
    Save all Session 15 core-rule
    window-level decision rows to one CSV.

    Input:
        Decision rows keyed by rule ID.

    Output:
        One row per rule, recording, and
        feature update.
    """

    output_rows = []
    seen_row_keys = set()
    rows_per_rule = None

    for rule_config in (
        CORE_RULE_CONFIGURATIONS
    ):
        rule_id = rule_config["rule_id"]

        if (
            rule_id
            not in core_rule_rows_by_rule
        ):
            raise RuntimeError(
                "No decision rows were found "
                "for configured rule: "
                f"{rule_id}"
            )

        decision_rows = sorted(
            core_rule_rows_by_rule[
                rule_id
            ],
            key=lambda row: (
                row["subject"],
                row["run"],
                row["window_index"],
            ),
        )

        if not decision_rows:
            raise RuntimeError(
                "A configured rule contains "
                "no decision rows: "
                f"{rule_id}"
            )

        if rows_per_rule is None:
            rows_per_rule = len(
                decision_rows
            )

        elif len(decision_rows) != (
            rows_per_rule
        ):
            raise RuntimeError(
                "Core rules contain different "
                "decision-row counts: "
                f"{rule_id} has "
                f"{len(decision_rows)}, "
                f"expected {rows_per_rule}."
            )

        for row in decision_rows:
            if row["rule_id"] != rule_id:
                raise RuntimeError(
                    "A decision row has a rule ID "
                    "that does not match its "
                    "configuration: "
                    f"{row['rule_id']} vs "
                    f"{rule_id}"
                )

            row_key = (
                rule_id,
                row["subject"],
                row["run"],
                row["window_index"],
            )

            if row_key in seen_row_keys:
                raise RuntimeError(
                    "A duplicate decision-stream "
                    "row key was found: "
                    f"{row_key}"
                )

            seen_row_keys.add(
                row_key
            )

            output_rows.append({
                "rule_id": rule_id,
                "subject": row["subject"],
                "run": row["run"],
                "condition": row[
                    "condition"
                ],
                "configuration_id": row[
                    "configuration_id"
                ],
                "window_index": row[
                    "window_index"
                ],
                "window_start_sec": row[
                    "window_start_sec"
                ],
                "window_end_sec": row[
                    "window_end_sec"
                ],
                "decision_time_sec": row[
                    "decision_time_sec"
                ],
                "feature_name": FEATURE_NAME,
                "feature_unit": FEATURE_UNIT,
                "raw_feature_value": row[
                    "raw_feature_value"
                ],
                "smoothing_id": row[
                    "smoothing_id"
                ],
                "smoothed_available": row[
                    "smoothed_available"
                ],
                "smoothed_feature_value": row[
                    "smoothed_feature_value"
                ],
                "threshold_id": row[
                    "threshold_id"
                ],
                "threshold_value": row[
                    "threshold_value"
                ],
                "evidence_state": row[
                    "evidence_state"
                ],
                "dwell_updates": row[
                    "dwell_updates"
                ],
                "candidate_evidence_state": row[
                    "candidate_evidence_state"
                ],
                "candidate_count": row[
                    "candidate_count"
                ],
                "active_evidence_state": row[
                    "active_evidence_state"
                ],
                "initial_command_confirmed": row[
                    "initial_command_confirmed"
                ],
                "active_switch_confirmed": row[
                    "active_switch_confirmed"
                ],
                "command_state": row[
                    "command_state"
                ],
            })

    expected_row_count = (
        len(CORE_RULE_CONFIGURATIONS)
        * rows_per_rule
    )

    if len(output_rows) != (
        expected_row_count
    ):
        raise RuntimeError(
            "Decision-stream output-row count "
            "does not match the expected count: "
            f"{len(output_rows)} vs "
            f"{expected_row_count}"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                DECISION_STREAM_COLUMNS
            ),
            extrasaction="raise",
        )

        writer.writeheader()
        writer.writerows(
            output_rows
        )

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "The decision-stream CSV was not "
            "saved correctly."
        )

    print("\n========================================")
    print(
        "Session 15 Output 1: "
        "Decision-stream CSV"
    )

    print(
        "Output CSV:",
        output_path,
    )

    print(
        "Rule count:",
        len(CORE_RULE_CONFIGURATIONS),
    )

    print(
        "Rows per rule:",
        rows_per_rule,
    )

    print(
        "Saved row count:",
        len(output_rows),
    )

    print(
        "Saved column count:",
        len(DECISION_STREAM_COLUMNS),
    )

    return output_rows


def build_command_episode_rows(
    core_rule_rows_by_rule,
):
    """
    Convert window-level confirmed command
    states into command episodes.

    The initial CMD_STOP interval is included
    from recording start to first active-command
    confirmation, even when no decision row
    contains CMD_STOP.
    """

    episode_rows = []
    seen_episode_keys = set()

    for rule_config in (
        CORE_RULE_CONFIGURATIONS
    ):
        rule_id = rule_config["rule_id"]

        if (
            rule_id
            not in core_rule_rows_by_rule
        ):
            raise RuntimeError(
                "No decision rows were found "
                "for configured rule: "
                f"{rule_id}"
            )

        grouped_rows = group_rows_by_recording(
            core_rule_rows_by_rule[
                rule_id
            ]
        )

        for (
            subject,
            run,
        ), rows in sorted(
            grouped_rows.items()
        ):
            rows = sorted(
                rows,
                key=lambda row: (
                    row["window_index"]
                ),
            )

            if not rows:
                raise RuntimeError(
                    "No decision rows were found "
                    "for "
                    f"rule {rule_id}, "
                    f"subject {subject}, "
                    f"run {run}."
                )

            initialization_indices = [
                index
                for index, row in enumerate(rows)
                if row[
                    "initial_command_confirmed"
                ]
            ]

            if len(initialization_indices) != 1:
                raise RuntimeError(
                    "Each rule-recording stream "
                    "must contain exactly one "
                    "initial command confirmation: "
                    f"{rule_id}, "
                    f"subject {subject}, "
                    f"run {run}."
                )

            first_active_index = (
                initialization_indices[0]
            )

            first_active_row = rows[
                first_active_index
            ]

            if (
                first_active_row["command_state"]
                == STOP_COMMAND_STATE
            ):
                raise RuntimeError(
                    "The initial confirmation row "
                    "must contain an active command."
                )

            if any(
                row["command_state"]
                != STOP_COMMAND_STATE
                for row in rows[
                    :first_active_index
                ]
            ):
                raise RuntimeError(
                    "An active command occurred "
                    "before initial confirmation."
                )

            if any(
                row["command_state"]
                == STOP_COMMAND_STATE
                for row in rows[
                    first_active_index:
                ]
            ):
                raise RuntimeError(
                    "CMD_STOP occurred after "
                    "initial command confirmation."
                )

            for index in range(
                first_active_index + 1,
                len(rows),
            ):
                command_changed = (
                    rows[index]["command_state"]
                    != rows[index - 1][
                        "command_state"
                    ]
                )

                switch_confirmed = rows[index][
                    "active_switch_confirmed"
                ]

                if (
                    command_changed
                    != switch_confirmed
                ):
                    raise RuntimeError(
                        "A command transition does "
                        "not match the recorded "
                        "active-switch flag for "
                        f"{rule_id}, "
                        f"subject {subject}, "
                        f"run {run}, "
                        f"window "
                        f"{rows[index]['window_index']}."
                    )

            run_start_time_sec = rows[0][
                "window_start_sec"
            ]

            run_end_time_sec = rows[-1][
                "window_end_sec"
            ]

            first_active_time_sec = (
                first_active_row[
                    "decision_time_sec"
                ]
            )

            if not (
                run_start_time_sec
                <= first_active_time_sec
                <= run_end_time_sec
            ):
                raise RuntimeError(
                    "The first active-command time "
                    "is outside the recording "
                    "time range."
                )

            episode_index = 0

            initial_stop_rows = rows[
                :first_active_index
            ]

            if initial_stop_rows:
                first_stop_window_index = (
                    initial_stop_rows[0][
                        "window_index"
                    ]
                )

                last_stop_window_index = (
                    initial_stop_rows[-1][
                        "window_index"
                    ]
                )

                first_stop_decision_time = (
                    initial_stop_rows[0][
                        "decision_time_sec"
                    ]
                )

                last_stop_decision_time = (
                    initial_stop_rows[-1][
                        "decision_time_sec"
                    ]
                )

            else:
                first_stop_window_index = None
                last_stop_window_index = None
                first_stop_decision_time = None
                last_stop_decision_time = None

            initial_stop_duration_sec = (
                first_active_time_sec
                - run_start_time_sec
            )

            episode_key = (
                rule_id,
                subject,
                run,
                episode_index,
            )

            if episode_key in seen_episode_keys:
                raise RuntimeError(
                    "A duplicate command-episode "
                    "key was found: "
                    f"{episode_key}"
                )

            seen_episode_keys.add(
                episode_key
            )

            episode_rows.append({
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": rows[0][
                    "condition"
                ],
                "configuration_id": rows[0][
                    "configuration_id"
                ],
                "feature_name": FEATURE_NAME,
                "feature_unit": FEATURE_UNIT,
                "smoothing_id": rows[0][
                    "smoothing_id"
                ],
                "threshold_id": rows[0][
                    "threshold_id"
                ],
                "threshold_value": rows[0][
                    "threshold_value"
                ],
                "dwell_updates": rows[0][
                    "dwell_updates"
                ],
                "episode_index": (
                    episode_index
                ),
                "command_state": (
                    STOP_COMMAND_STATE
                ),
                "episode_start_time_sec": (
                    run_start_time_sec
                ),
                "episode_end_time_sec": (
                    first_active_time_sec
                ),
                "episode_duration_sec": (
                    initial_stop_duration_sec
                ),
                "decision_update_count": len(
                    initial_stop_rows
                ),
                "first_window_index": (
                    first_stop_window_index
                ),
                "last_window_index": (
                    last_stop_window_index
                ),
                "first_decision_time_sec": (
                    first_stop_decision_time
                ),
                "last_decision_time_sec": (
                    last_stop_decision_time
                ),
                "start_event": "run_start",
                "end_event": (
                    "initial_command_confirmed"
                ),
                "is_initial_stop_episode": True,
                "ended_at_run_boundary": False,
            })

            active_episode_start_index = (
                first_active_index
            )

            active_episode_start_event = (
                "initial_command_confirmed"
            )

            for index in range(
                first_active_index + 1,
                len(rows),
            ):
                if (
                    rows[index]["command_state"]
                    == rows[index - 1][
                        "command_state"
                    ]
                ):
                    continue

                episode_index += 1

                active_episode_rows = rows[
                    active_episode_start_index:
                    index
                ]

                episode_start_time_sec = (
                    active_episode_rows[0][
                        "decision_time_sec"
                    ]
                )

                episode_end_time_sec = rows[
                    index
                ]["decision_time_sec"]

                episode_duration_sec = (
                    episode_end_time_sec
                    - episode_start_time_sec
                )

                if episode_duration_sec < 0.0:
                    raise RuntimeError(
                        "A command episode has a "
                        "negative duration."
                    )

                episode_key = (
                    rule_id,
                    subject,
                    run,
                    episode_index,
                )

                if (
                    episode_key
                    in seen_episode_keys
                ):
                    raise RuntimeError(
                        "A duplicate command-"
                        "episode key was found: "
                        f"{episode_key}"
                    )

                seen_episode_keys.add(
                    episode_key
                )

                episode_rows.append({
                    "rule_id": rule_id,
                    "subject": subject,
                    "run": run,
                    "condition": rows[0][
                        "condition"
                    ],
                    "configuration_id": rows[0][
                        "configuration_id"
                    ],
                    "feature_name": FEATURE_NAME,
                    "feature_unit": FEATURE_UNIT,
                    "smoothing_id": rows[0][
                        "smoothing_id"
                    ],
                    "threshold_id": rows[0][
                        "threshold_id"
                    ],
                    "threshold_value": rows[0][
                        "threshold_value"
                    ],
                    "dwell_updates": rows[0][
                        "dwell_updates"
                    ],
                    "episode_index": (
                        episode_index
                    ),
                    "command_state": (
                        active_episode_rows[0][
                            "command_state"
                        ]
                    ),
                    "episode_start_time_sec": (
                        episode_start_time_sec
                    ),
                    "episode_end_time_sec": (
                        episode_end_time_sec
                    ),
                    "episode_duration_sec": (
                        episode_duration_sec
                    ),
                    "decision_update_count": len(
                        active_episode_rows
                    ),
                    "first_window_index": (
                        active_episode_rows[0][
                            "window_index"
                        ]
                    ),
                    "last_window_index": (
                        active_episode_rows[-1][
                            "window_index"
                        ]
                    ),
                    "first_decision_time_sec": (
                        active_episode_rows[0][
                            "decision_time_sec"
                        ]
                    ),
                    "last_decision_time_sec": (
                        active_episode_rows[-1][
                            "decision_time_sec"
                        ]
                    ),
                    "start_event": (
                        active_episode_start_event
                    ),
                    "end_event": (
                        "active_switch_confirmed"
                    ),
                    "is_initial_stop_episode": (
                        False
                    ),
                    "ended_at_run_boundary": False,
                })

                active_episode_start_index = (
                    index
                )

                active_episode_start_event = (
                    "active_switch_confirmed"
                )

            episode_index += 1

            final_episode_rows = rows[
                active_episode_start_index:
            ]

            final_episode_start_time_sec = (
                final_episode_rows[0][
                    "decision_time_sec"
                ]
            )

            final_episode_duration_sec = (
                run_end_time_sec
                - final_episode_start_time_sec
            )

            if final_episode_duration_sec < 0.0:
                raise RuntimeError(
                    "The final command episode "
                    "has a negative duration."
                )

            episode_key = (
                rule_id,
                subject,
                run,
                episode_index,
            )

            if episode_key in seen_episode_keys:
                raise RuntimeError(
                    "A duplicate command-episode "
                    "key was found: "
                    f"{episode_key}"
                )

            seen_episode_keys.add(
                episode_key
            )

            episode_rows.append({
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": rows[0][
                    "condition"
                ],
                "configuration_id": rows[0][
                    "configuration_id"
                ],
                "feature_name": FEATURE_NAME,
                "feature_unit": FEATURE_UNIT,
                "smoothing_id": rows[0][
                    "smoothing_id"
                ],
                "threshold_id": rows[0][
                    "threshold_id"
                ],
                "threshold_value": rows[0][
                    "threshold_value"
                ],
                "dwell_updates": rows[0][
                    "dwell_updates"
                ],
                "episode_index": episode_index,
                "command_state": (
                    final_episode_rows[0][
                        "command_state"
                    ]
                ),
                "episode_start_time_sec": (
                    final_episode_start_time_sec
                ),
                "episode_end_time_sec": (
                    run_end_time_sec
                ),
                "episode_duration_sec": (
                    final_episode_duration_sec
                ),
                "decision_update_count": len(
                    final_episode_rows
                ),
                "first_window_index": (
                    final_episode_rows[0][
                        "window_index"
                    ]
                ),
                "last_window_index": (
                    final_episode_rows[-1][
                        "window_index"
                    ]
                ),
                "first_decision_time_sec": (
                    final_episode_rows[0][
                        "decision_time_sec"
                    ]
                ),
                "last_decision_time_sec": (
                    final_episode_rows[-1][
                        "decision_time_sec"
                    ]
                ),
                "start_event": (
                    active_episode_start_event
                ),
                "end_event": "run_end",
                "is_initial_stop_episode": False,
                "ended_at_run_boundary": True,
            })

            recording_episode_rows = [
                row
                for row in episode_rows
                if (
                    row["rule_id"] == rule_id
                    and row["subject"] == subject
                    and row["run"] == run
                )
            ]

            active_switch_count = sum(
                row["active_switch_confirmed"]
                for row in rows
            )

            expected_episode_count = (
                2 + active_switch_count
            )

            if len(
                recording_episode_rows
            ) != expected_episode_count:
                raise RuntimeError(
                    "Command-episode count does "
                    "not match the initialization "
                    "and active-switch structure "
                    "for "
                    f"{rule_id}, "
                    f"subject {subject}, "
                    f"run {run}: "
                    f"{len(recording_episode_rows)} "
                    "vs "
                    f"{expected_episode_count}."
                )

    if not episode_rows:
        raise RuntimeError(
            "No command episodes were created."
        )

    return episode_rows


def save_command_episode_csv(
    episode_rows,
    output_path,
):
    """
    Save Session 15 command episodes
    to one CSV.
    """

    if not episode_rows:
        raise RuntimeError(
            "No command-episode rows were "
            "provided for saving."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                COMMAND_EPISODE_COLUMNS
            ),
            extrasaction="raise",
        )

        writer.writeheader()
        writer.writerows(
            episode_rows
        )

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "The command-episode CSV was not "
            "saved correctly."
        )

    rule_count = len({
        row["rule_id"]
        for row in episode_rows
    })

    rule_recording_count = len({
        (
            row["rule_id"],
            row["subject"],
            row["run"],
        )
        for row in episode_rows
    })

    print("\n========================================")
    print(
        "Session 15 Output 2: "
        "Command-episode CSV"
    )

    print(
        "Output CSV:",
        output_path,
    )

    print(
        "Rule count:",
        rule_count,
    )

    print(
        "Rule-recording count:",
        rule_recording_count,
    )

    print(
        "Saved episode count:",
        len(episode_rows),
    )

    print(
        "Saved column count:",
        len(COMMAND_EPISODE_COLUMNS),
    )


def build_rule_run_summary_rows(
    core_rule_rows_by_rule,
    command_episode_rows,
):
    """
    Summarize each Session 15 rule separately
    for each subject and run.

    Decision-stream rows provide evidence,
    candidate, and command counts.

    Episode rows provide command-duration
    measures.
    """

    episode_rows_by_key = defaultdict(list)

    for episode_row in command_episode_rows:
        episode_key = (
            episode_row["rule_id"],
            episode_row["subject"],
            episode_row["run"],
        )

        episode_rows_by_key[
            episode_key
        ].append(episode_row)

    summary_rows = []
    seen_summary_keys = set()

    for rule_config in (
        CORE_RULE_CONFIGURATIONS
    ):
        rule_id = rule_config["rule_id"]

        if (
            rule_id
            not in core_rule_rows_by_rule
        ):
            raise RuntimeError(
                "No decision rows were found "
                "for configured rule: "
                f"{rule_id}"
            )

        grouped_decision_rows = (
            group_rows_by_recording(
                core_rule_rows_by_rule[
                    rule_id
                ]
            )
        )

        for (
            subject,
            run,
        ), rows in sorted(
            grouped_decision_rows.items()
        ):
            rows = sorted(
                rows,
                key=lambda row: (
                    row["window_index"]
                ),
            )

            if not rows:
                raise RuntimeError(
                    "No decision rows were found "
                    "for "
                    f"rule {rule_id}, "
                    f"subject {subject}, "
                    f"run {run}."
                )

            summary_key = (
                rule_id,
                subject,
                run,
            )

            if summary_key in seen_summary_keys:
                raise RuntimeError(
                    "A duplicate rule-run "
                    "summary key was found: "
                    f"{summary_key}"
                )

            seen_summary_keys.add(
                summary_key
            )

            if any(
                row["rule_id"] != rule_id
                for row in rows
            ):
                raise RuntimeError(
                    "A rule-run group contains "
                    "an unexpected rule ID."
                )

            initialization_rows = [
                row
                for row in rows
                if row[
                    "initial_command_confirmed"
                ]
            ]

            if len(initialization_rows) != 1:
                raise RuntimeError(
                    "Each rule-run stream must "
                    "contain exactly one initial "
                    "command confirmation: "
                    f"{summary_key}"
                )

            first_active_row = (
                initialization_rows[0]
            )

            available_rows = [
                row
                for row in rows
                if row["smoothed_available"]
            ]

            if not available_rows:
                raise RuntimeError(
                    "No processed feature became "
                    "available for "
                    f"{summary_key}."
                )

            active_switch_rows = [
                row
                for row in rows
                if row[
                    "active_switch_confirmed"
                ]
            ]

            active_switch_times = [
                row["decision_time_sec"]
                for row in active_switch_rows
            ]

            candidate_rows = [
                row
                for row in rows
                if (
                    row["command_state"]
                    != STOP_COMMAND_STATE
                    and row[
                        "candidate_count"
                    ] > 0
                    and not row[
                        "initial_command_confirmed"
                    ]
                    and not row[
                        "active_switch_confirmed"
                    ]
                )
            ]

            candidate_times = [
                row["decision_time_sec"]
                for row in candidate_rows
            ]

            unavailable_count = sum(
                row["evidence_state"]
                == UNAVAILABLE_EVIDENCE_STATE
                for row in rows
            )

            low_count = sum(
                row["evidence_state"]
                == LOW_EVIDENCE_STATE
                for row in rows
            )

            high_count = sum(
                row["evidence_state"]
                == HIGH_EVIDENCE_STATE
                for row in rows
            )

            stop_count = sum(
                row["command_state"]
                == STOP_COMMAND_STATE
                for row in rows
            )

            open_count = sum(
                row["command_state"]
                == OPEN_COMMAND_STATE
                for row in rows
            )

            close_count = sum(
                row["command_state"]
                == CLOSE_COMMAND_STATE
                for row in rows
            )

            if (
                unavailable_count
                + low_count
                + high_count
                != len(rows)
            ):
                raise RuntimeError(
                    "Evidence-state counts do "
                    "not match the decision-row "
                    "count for "
                    f"{summary_key}."
                )

            if (
                stop_count
                + open_count
                + close_count
                != len(rows)
            ):
                raise RuntimeError(
                    "Command-state counts do not "
                    "match the decision-row count "
                    f"for {summary_key}."
                )

            episode_key = (
                rule_id,
                subject,
                run,
            )

            if (
                episode_key
                not in episode_rows_by_key
            ):
                raise RuntimeError(
                    "No command episodes were "
                    "found for "
                    f"{episode_key}."
                )

            episodes = sorted(
                episode_rows_by_key[
                    episode_key
                ],
                key=lambda row: (
                    row["episode_index"]
                ),
            )

            episode_indices = [
                row["episode_index"]
                for row in episodes
            ]

            expected_episode_indices = list(
                range(len(episodes))
            )

            if (
                episode_indices
                != expected_episode_indices
            ):
                raise RuntimeError(
                    "Command episode indices are "
                    "missing, duplicated, or out "
                    "of order for "
                    f"{episode_key}."
                )

            initial_stop_episodes = [
                episode
                for episode in episodes
                if episode[
                    "is_initial_stop_episode"
                ]
            ]

            if len(initial_stop_episodes) != 1:
                raise RuntimeError(
                    "Each rule-run summary must "
                    "contain exactly one initial "
                    "STOP episode."
                )

            initial_stop_episode = (
                initial_stop_episodes[0]
            )

            if (
                episodes[0]
                is not initial_stop_episode
            ):
                raise RuntimeError(
                    "The initial STOP episode "
                    "must be episode zero."
                )

            if (
                initial_stop_episode[
                    "command_state"
                ]
                != STOP_COMMAND_STATE
            ):
                raise RuntimeError(
                    "The initial episode must "
                    "contain CMD_STOP."
                )

            active_episodes = [
                episode
                for episode in episodes
                if not episode[
                    "is_initial_stop_episode"
                ]
            ]

            if not active_episodes:
                raise RuntimeError(
                    "No active command episode "
                    "was found for "
                    f"{episode_key}."
                )

            expected_episode_count = (
                2
                + len(active_switch_rows)
            )

            if len(episodes) != (
                expected_episode_count
            ):
                raise RuntimeError(
                    "Episode count does not "
                    "match the active-switch "
                    "structure for "
                    f"{episode_key}: "
                    f"{len(episodes)} vs "
                    f"{expected_episode_count}."
                )

            for (
                previous_episode,
                next_episode,
            ) in zip(
                episodes[:-1],
                episodes[1:],
            ):
                if not np.isclose(
                    previous_episode[
                        "episode_end_time_sec"
                    ],
                    next_episode[
                        "episode_start_time_sec"
                    ],
                    rtol=RTOL,
                    atol=ATOL,
                ):
                    raise RuntimeError(
                        "Command episodes are not "
                        "temporally contiguous for "
                        f"{episode_key}."
                    )

            run_start_time_sec = rows[0][
                "window_start_sec"
            ]

            run_end_time_sec = rows[-1][
                "window_end_sec"
            ]

            recording_duration_sec = (
                run_end_time_sec
                - run_start_time_sec
            )

            episode_duration_sum_sec = sum(
                episode[
                    "episode_duration_sec"
                ]
                for episode in episodes
            )

            if not np.isclose(
                episode_duration_sum_sec,
                recording_duration_sec,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "Episode durations do not "
                    "cover the full recording "
                    "duration for "
                    f"{episode_key}: "
                    f"{episode_duration_sum_sec} "
                    "vs "
                    f"{recording_duration_sec}."
                )

            first_active_time_sec = (
                first_active_row[
                    "decision_time_sec"
                ]
            )

            initial_stop_duration_sec = (
                first_active_time_sec
                - run_start_time_sec
            )

            if not np.isclose(
                initial_stop_episode[
                    "episode_duration_sec"
                ],
                initial_stop_duration_sec,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "The initial STOP duration "
                    "does not match the episode "
                    "record for "
                    f"{episode_key}."
                )

            if not np.isclose(
                initial_stop_episode[
                    "episode_end_time_sec"
                ],
                first_active_time_sec,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "The initial STOP episode "
                    "does not end at first active "
                    "command confirmation."
                )

            active_episode_durations = [
                episode[
                    "episode_duration_sec"
                ]
                for episode in active_episodes
            ]

            short_active_episodes = [
                episode
                for episode in active_episodes
                if (
                    episode[
                        "episode_duration_sec"
                    ]
                    <= (
                        SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC
                        + ATOL
                    )
                )
            ]

            dwell_updates = rows[0][
                "dwell_updates"
            ]

            nominal_confirmation_span_sec = (
                dwell_updates - 1
            ) * BASELINE_STEP_SIZE_SEC

            active_switch_times_text = (
                ";".join(
                    f"{time_sec:.1f}"
                    for time_sec
                    in active_switch_times
                )
            )

            candidate_times_text = (
                ";".join(
                    f"{time_sec:.1f}"
                    for time_sec
                    in candidate_times
                )
            )

            summary_rows.append({
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": rows[0][
                    "condition"
                ],
                "configuration_id": rows[0][
                    "configuration_id"
                ],
                "feature_name": FEATURE_NAME,
                "feature_unit": FEATURE_UNIT,
                "smoothing_id": rows[0][
                    "smoothing_id"
                ],
                "threshold_id": rows[0][
                    "threshold_id"
                ],
                "threshold_value": rows[0][
                    "threshold_value"
                ],
                "dwell_updates": (
                    dwell_updates
                ),
                "nominal_confirmation_span_sec": (
                    nominal_confirmation_span_sec
                ),
                "run_start_time_sec": (
                    run_start_time_sec
                ),
                "run_end_time_sec": (
                    run_end_time_sec
                ),
                "decision_update_count": len(
                    rows
                ),
                "first_decision_time_sec": rows[
                    0
                ]["decision_time_sec"],
                "last_decision_time_sec": rows[
                    -1
                ]["decision_time_sec"],
                "unavailable_evidence_count": (
                    unavailable_count
                ),
                "first_processed_feature_time_sec": (
                    available_rows[0][
                        "decision_time_sec"
                    ]
                ),
                "initial_stop_update_count": (
                    stop_count
                ),
                "initial_stop_duration_sec": (
                    initial_stop_duration_sec
                ),
                "first_active_command_time_sec": (
                    first_active_time_sec
                ),
                "first_active_command": (
                    first_active_row[
                        "command_state"
                    ]
                ),
                "final_command_state": rows[-1][
                    "command_state"
                ],
                "low_evidence_count": (
                    low_count
                ),
                "high_evidence_count": (
                    high_count
                ),
                "cmd_stop_count": (
                    stop_count
                ),
                "cmd_open_count": (
                    open_count
                ),
                "cmd_close_count": (
                    close_count
                ),
                "active_switch_count": len(
                    active_switch_rows
                ),
                "active_switch_times_sec": (
                    active_switch_times_text
                ),
                "unconfirmed_candidate_update_count": (
                    len(candidate_rows)
                ),
                "unconfirmed_candidate_times_sec": (
                    candidate_times_text
                ),
                "command_episode_count": len(
                    episodes
                ),
                "active_command_episode_count": (
                    len(active_episodes)
                ),
                "short_active_episode_max_duration_sec": (
                    SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC
                ),
                "short_active_command_episode_count": (
                    len(short_active_episodes)
                ),
                "shortest_active_episode_duration_sec": (
                    min(
                        active_episode_durations
                    )
                ),
                "longest_active_episode_duration_sec": (
                    max(
                        active_episode_durations
                    )
                ),
            })

    if not summary_rows:
        raise RuntimeError(
            "No rule-run summary rows were "
            "created."
        )

    return summary_rows


def save_rule_run_summary_csv(
    summary_rows,
    output_path,
):
    """
    Save one summary row per rule,
    subject, and run.
    """

    if not summary_rows:
        raise RuntimeError(
            "No rule-run summary rows were "
            "provided for saving."
        )

    summary_keys = [
        (
            row["rule_id"],
            row["subject"],
            row["run"],
        )
        for row in summary_rows
    ]

    if len(summary_keys) != len(
        set(summary_keys)
    ):
        raise RuntimeError(
            "Duplicate rule-run summary keys "
            "were found."
        )

    rule_count = len({
        row["rule_id"]
        for row in summary_rows
    })

    if rule_count != len(
        CORE_RULE_CONFIGURATIONS
    ):
        raise RuntimeError(
            "The rule-run summary does not "
            "contain all configured rules."
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=(
                RULE_RUN_SUMMARY_COLUMNS
            ),
            extrasaction="raise",
        )

        writer.writeheader()
        writer.writerows(
            summary_rows
        )

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "The rule-run summary CSV was "
            "not saved correctly."
        )

    print("\n========================================")
    print(
        "Session 15 Output 3: "
        "Rule-run summary CSV"
    )

    print(
        "Output CSV:",
        output_path,
    )

    print(
        "Rule count:",
        rule_count,
    )

    print(
        "Rule-recording count:",
        len(summary_rows),
    )

    print(
        "Saved summary row count:",
        len(summary_rows),
    )

    print(
        "Saved column count:",
        len(RULE_RUN_SUMMARY_COLUMNS),
    )

    print(
        "Short active episode cutoff:",
        f"{SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC:.1f} s",
    )


def print_core_rule_summary(
    decision_rows,
):
    """
    Summarize one Session 15 core
    decision rule by recording.
    """

    if not decision_rows:
        raise RuntimeError(
            "No generic dwell decision rows "
            "were provided for summary."
        )

    rule_ids = {
        row["rule_id"]
        for row in decision_rows
    }

    dwell_values = {
        row["dwell_updates"]
        for row in decision_rows
    }

    smoothing_ids = {
        row["smoothing_id"]
        for row in decision_rows
    }

    threshold_ids = {
        row["threshold_id"]
        for row in decision_rows
    }

    if len(rule_ids) != 1:
        raise RuntimeError(
            "A core-rule summary must contain "
            "exactly one rule ID."
        )

    if len(dwell_values) != 1:
        raise RuntimeError(
            "A core-rule summary must "
            "contain exactly one dwell value."
        )

    if len(smoothing_ids) != 1:
        raise RuntimeError(
            "A core-rule summary must "
            "contain exactly one smoothing ID."
        )

    if len(threshold_ids) != 1:
        raise RuntimeError(
            "A core-rule summary must "
            "contain exactly one threshold ID."
        )

    rule_id = next(iter(rule_ids))
    dwell_updates = next(iter(dwell_values))
    smoothing_id = next(iter(smoothing_ids))
    threshold_id = next(iter(threshold_ids))

    grouped_rows = defaultdict(list)

    for row in decision_rows:
        group_key = (
            row["subject"],
            row["run"],
        )

        grouped_rows[group_key].append(row)

    nominal_confirmation_span_sec = (
        dwell_updates - 1
    ) * BASELINE_STEP_SIZE_SEC

    print("\n========================================")
    print(
        "Core decision-rule summary"
    )

    print(
        "Rule ID:",
        rule_id,
    )

    print(
        "Threshold ID:",
        threshold_id,
    )

    print(
        "Smoothing ID:",
        smoothing_id,
    )

    print(
        "Dwell updates:",
        dwell_updates,
    )

    print(
        "Nominal confirmation span:",
        f"{nominal_confirmation_span_sec:.1f} s",
    )

    print(
        "Mapping:",
        "UNAVAILABLE -> CMD_STOP, "
        "LOW_ALPHA -> CMD_OPEN, "
        "HIGH_ALPHA -> CMD_CLOSE",
    )

    for (
        subject,
        run,
    ), rows in sorted(
        grouped_rows.items()
    ):
        rows.sort(
            key=lambda row: row["window_index"]
        )

        initialization_rows = [
            row
            for row in rows
            if row[
                "initial_command_confirmed"
            ]
        ]

        if len(initialization_rows) != 1:
            raise RuntimeError(
                "Each recording must contain "
                "exactly one initial command "
                "confirmation."
            )

        first_active_row = initialization_rows[0]

        first_active_index = rows.index(
            first_active_row
        )

        if any(
            row["command_state"]
            != STOP_COMMAND_STATE
            for row in rows[:first_active_index]
        ):
            raise RuntimeError(
                "An active command occurred "
                "before initialization was "
                "confirmed."
            )

        if any(
            row["command_state"]
            == STOP_COMMAND_STATE
            for row in rows[first_active_index:]
        ):
            raise RuntimeError(
                "CMD_STOP occurred after initial "
                "command confirmation."
            )

        unavailable_indices = [
            index
            for index, row in enumerate(rows)
            if (
                row["evidence_state"]
                == UNAVAILABLE_EVIDENCE_STATE
            )
        ]

        expected_unavailable_indices = list(
            range(len(unavailable_indices))
        )

        if (
            unavailable_indices
            != expected_unavailable_indices
        ):
            raise RuntimeError(
                "Unavailable evidence must occur "
                "only during initial warm-up."
            )

        available_rows = [
            row
            for row in rows
            if row["smoothed_available"]
        ]

        if not available_rows:
            raise RuntimeError(
                "No processed feature became "
                "available for "
                f"subject {subject}, "
                f"run {run}."
            )

        first_available_row = available_rows[0]

        evidence_states = [
            row["evidence_state"]
            for row in rows
        ]

        command_states = [
            row["command_state"]
            for row in rows
        ]

        unavailable_count = sum(
            state
            == UNAVAILABLE_EVIDENCE_STATE
            for state in evidence_states
        )

        low_count = sum(
            state == LOW_EVIDENCE_STATE
            for state in evidence_states
        )

        high_count = sum(
            state == HIGH_EVIDENCE_STATE
            for state in evidence_states
        )

        stop_count = sum(
            state == STOP_COMMAND_STATE
            for state in command_states
        )

        open_count = sum(
            state == OPEN_COMMAND_STATE
            for state in command_states
        )

        close_count = sum(
            state == CLOSE_COMMAND_STATE
            for state in command_states
        )

        if (
            unavailable_count
            + low_count
            + high_count
            != len(rows)
        ):
            raise RuntimeError(
                "Evidence-state counts do not "
                "match the decision-row count."
            )

        if (
            stop_count
            + open_count
            + close_count
            != len(rows)
        ):
            raise RuntimeError(
                "Command-state counts do not "
                "match the decision-row count."
            )

        active_switch_rows = [
            row
            for row in rows
            if row["active_switch_confirmed"]
        ]

        active_switch_times = [
            row["decision_time_sec"]
            for row in active_switch_rows
        ]

        pending_switch_rows = [
            row
            for row in rows
            if (
                row["command_state"]
                != STOP_COMMAND_STATE
                and row["candidate_count"] > 0
                and not row[
                    "initial_command_confirmed"
                ]
                and not row[
                    "active_switch_confirmed"
                ]
            )
        ]

        pending_switch_times = [
            row["decision_time_sec"]
            for row in pending_switch_rows
        ]

        initial_stop_duration_sec = (
            first_active_row[
                "decision_time_sec"
            ]
            - rows[0]["window_start_sec"]
        )

        print("\n----------------------------------------")
        print("Subject:", subject)
        print("Run:", run)

        print(
            "Condition:",
            rows[0]["condition"],
        )

        print(
            "Threshold:",
            f"{rows[0]['threshold_value']:.12e}",
            FEATURE_UNIT,
        )

        print(
            "Decision update count:",
            len(rows),
        )

        print(
            "Warm-up unavailable count:",
            unavailable_count,
        )

        print(
            "First processed feature time:",
            f"{first_available_row['decision_time_sec']:.1f} s",
        )

        print(
            "Initial STOP update count:",
            stop_count,
        )

        print(
            "Initial STOP duration:",
            f"{initial_stop_duration_sec:.1f} s",
        )

        print(
            "First active command time:",
            f"{first_active_row['decision_time_sec']:.1f} s",
        )

        print(
            "First active command:",
            first_active_row[
                "command_state"
            ],
        )

        print(
            "UNAVAILABLE count:",
            unavailable_count,
        )

        print(
            "LOW_ALPHA count:",
            low_count,
        )

        print(
            "HIGH_ALPHA count:",
            high_count,
        )

        print(
            "CMD_STOP count:",
            stop_count,
        )

        print(
            "CMD_OPEN count:",
            open_count,
        )

        print(
            "CMD_CLOSE count:",
            close_count,
        )

        print(
            "Active OPEN-CLOSE switch count:",
            len(active_switch_times),
        )

        if active_switch_times:
            print(
                "Active switch decision times:",
                ", ".join(
                    f"{time_sec:.1f}"
                    for time_sec
                    in active_switch_times
                ),
                "s",
            )
        else:
            print(
                "Active switch decision times:",
                "None",
            )

        print(
            "Unconfirmed switch-candidate "
            "update count:",
            len(pending_switch_times),
        )

        if pending_switch_times:
            print(
                "Unconfirmed candidate times:",
                ", ".join(
                    f"{time_sec:.1f}"
                    for time_sec
                    in pending_switch_times
                ),
                "s",
            )
        else:
            print(
                "Unconfirmed candidate times:",
                "None",
            )


def main():
    source_rows = load_source_rows(
        csv_path=SOURCE_FEATURE_CSV_PATH,
    )

    selected_rows = select_baseline_rows(
        source_rows=source_rows,
    )

    validate_selected_rows(
        selected_rows=selected_rows,
    )

    grouped_rows = group_rows_by_recording(
        selected_rows=selected_rows,
    )

    validate_recording_structure(
        grouped_rows=grouped_rows,
    )

    print_input_summary(
        source_rows=source_rows,
        selected_rows=selected_rows,
        grouped_rows=grouped_rows,
    )

    thresholds_by_subject = (
        calculate_threshold_candidates(
            selected_rows=selected_rows,
        )
    )

    print_threshold_summary(
        thresholds_by_subject=(
            thresholds_by_subject
        ),
    )

    no_smoothing_rows = (
        build_no_smoothing_rows(
            selected_rows=selected_rows,
        )
    )

    median3_rows = (
        build_causal_median3_rows(
            selected_rows=selected_rows,
        )
    )

    print_causal_median3_validation(
        smoothed_rows=median3_rows,
        thresholds_by_subject=(
            thresholds_by_subject
        ),
    )

    processed_rows_by_smoothing = {
        SMOOTHING_ID_NONE: (
            no_smoothing_rows
        ),
        SMOOTHING_ID_MEDIAN3: (
            median3_rows
        ),
    }

    core_rule_rows_by_rule = (
        build_core_rule_rows_by_rule(
            processed_rows_by_smoothing=(
                processed_rows_by_smoothing
            ),
            thresholds_by_subject=(
                thresholds_by_subject
            ),
        )
    )

    if len(core_rule_rows_by_rule) != len(
        CORE_RULE_CONFIGURATIONS
    ):
        raise RuntimeError(
            "The generated core-rule count "
            "does not match the configured "
            "core-rule count."
        )

    decision_stream_rows = (
        save_decision_stream_csv(
            core_rule_rows_by_rule=(
                core_rule_rows_by_rule
            ),
            output_path=(
                DECISION_STREAM_CSV_PATH
            ),
        )
    )

    print("\n========================================")
    print(
        "Session 15 Step 4: "
        "Core decision rules"
    )

    print(
        "Generated core rule count:",
        len(core_rule_rows_by_rule),
    )

    for rule_config in (
        CORE_RULE_CONFIGURATIONS
    ):
        rule_id = rule_config["rule_id"]

        decision_rows = (
            core_rule_rows_by_rule[
                rule_id
            ]
        )

        print_core_rule_summary(
            decision_rows=decision_rows,
        )

    decision_stream_rows = (
        save_decision_stream_csv(
            core_rule_rows_by_rule=(
                core_rule_rows_by_rule
            ),
            output_path=(
                DECISION_STREAM_CSV_PATH
            ),
        )
    )

    expected_current_row_count = (
        len(CORE_RULE_CONFIGURATIONS)
        * len(selected_rows)
    )

    if len(decision_stream_rows) != (
        expected_current_row_count
    ):
        raise RuntimeError(
            "The saved decision-stream row "
            "count does not match the rule "
            "and input-row counts."
        )

    command_episode_rows = (
        build_command_episode_rows(
            core_rule_rows_by_rule=(
                core_rule_rows_by_rule
            ),
        )
    )

    save_command_episode_csv(
        episode_rows=command_episode_rows,
        output_path=(
            COMMAND_EPISODE_CSV_PATH
        ),
    )

    rule_run_summary_rows = (
        build_rule_run_summary_rows(
            core_rule_rows_by_rule=(
                core_rule_rows_by_rule
            ),
            command_episode_rows=(
                command_episode_rows
            ),
        )
    )

    save_rule_run_summary_csv(
        summary_rows=(
            rule_run_summary_rows
        ),
        output_path=(
            RULE_RUN_SUMMARY_CSV_PATH
        ),
    )

if __name__ == "__main__":
    main()