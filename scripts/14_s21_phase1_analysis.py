"""Session 21 Phase 1 analysis and validation entry point."""

from __future__ import annotations

import csv
import json
import platform
import subprocess
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from bci_robot.session21_phase1 import (
    ATOL,
    REFERENCE_RULE_ID,
    RTOL,
    SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC,
    SMOOTHING_ID_MEDIAN3,
    SMOOTHING_ID_NONE,
    build_causal_median3_rows,
    build_command_episode_rows,
    build_no_smoothing_rows,
    build_rule_configurations,
    build_rule_rows_by_rule,
    build_rule_run_summary_rows,
    build_temporal_variability_rows,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "session-21"
FIGURE_DIR = PROJECT_ROOT / "figures" / "session-21"

SOURCE_FEATURE_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-14"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_window-features.csv"
    )
)

SOURCE_CONDITION_SUMMARY_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-14"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_condition-summary.csv"
    )
)

SESSION15_DECISION_STREAM_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-15"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-decision-stream.csv"
    )
)

SESSION15_COMMAND_EPISODE_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-15"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-command-episodes.csv"
    )
)

SESSION15_RULE_RUN_SUMMARY_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-15"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-rule-run-summary.csv"
    )
)

SESSION15_METADATA_JSON_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-15"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-decision-rule-metadata.json"
    )
)

DECISION_STREAM_CSV_PATH = (
    RESULT_DIR / "session21_rule-grid_decision-stream.csv"
)
COMMAND_EPISODE_CSV_PATH = (
    RESULT_DIR / "session21_rule-grid_command-episodes.csv"
)
RULE_GRID_SUMMARY_CSV_PATH = (
    RESULT_DIR / "session21_rule-grid_summary.csv"
)
TEMPORAL_VARIABILITY_CSV_PATH = (
    RESULT_DIR
    / "session21_feature-temporal-variability-summary.csv"
)
METADATA_JSON_PATH = (
    RESULT_DIR / "session21_analysis_metadata.json"
)

RULE_GRID_FIGURE_PATH = (
    FIGURE_DIR / "session21_rule-grid-command-behavior.png"
)
TEMPORAL_VARIABILITY_FIGURE_PATH = (
    FIGURE_DIR
    / "session21_feature-temporal-variability.png"
)

IMPLEMENTATION_PLAN_PATH = (
    PROJECT_ROOT
    / "research-agent"
    / "results"
    / "pilot-001"
    / "session21_implementation_plan_v0.1.md"
)

IMPLEMENTATION_SOURCE_PATHS = (
    "src/bci_robot/session21_phase1.py",
    "scripts/14_s21_phase1_analysis.py",
)

SUBJECT = 1
RUNS = (1, 2)
RUN_CONDITIONS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}
FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"
BASELINE_CONFIGURATION_ID = "win-2s_step-1s"

CONFIGURATION_IDS = (
    "win-1s_step-1s",
    "win-2s_step-0p5s",
    "win-2s_step-1s",
    "win-2s_step-2s",
    "win-4s_step-1s",
)

EXPECTED_WINDOW_COUNTS_PER_RUN = {
    "win-1s_step-1s": 60,
    "win-2s_step-0p5s": 117,
    "win-2s_step-1s": 59,
    "win-2s_step-2s": 30,
    "win-4s_step-1s": 57,
}

FIXED_THRESHOLDS_BY_SUBJECT = {
    1: {
        "threshold_eo_q95": 8.270509057516904e-11,
        "threshold_gap_midpoint": 1.3987182661955795e-10,
        "threshold_ec_q05": 2.365528862351009e-10,
    }
}

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

RULE_GRID_SUMMARY_COLUMNS = [
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
    "recording_duration_sec",
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
    "low_evidence_fraction",
    "high_evidence_fraction",
    "evidence_transition_count",
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
    "stop_duration_sec",
    "open_duration_sec",
    "close_duration_sec",
    "stop_duration_fraction",
    "open_duration_fraction",
    "close_duration_fraction",
]

TEMPORAL_VARIABILITY_COLUMNS = [
    "subject",
    "run",
    "condition",
    "configuration_id",
    "window_length_sec",
    "step_size_sec",
    "outer_window_overlap_fraction",
    "welch_segment_count",
    "feature_name",
    "feature_unit",
    "n_features",
    "n_differences",
    "relative_iqr",
    "successive_difference_sd_population",
    "median_absolute_successive_change",
    "comparison_role",
]


SOURCE_REQUIRED_COLUMNS = {
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
    FEATURE_NAME,
}


def read_csv_rows(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")
        return list(reader), list(reader.fieldnames)


def parse_bool(value):
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def parse_optional_float(value):
    if value is None or str(value).strip() == "":
        return None
    return float(value)


def parse_optional_int(value):
    if value is None or str(value).strip() == "":
        return None
    return int(value)


def normalize_optional_text(value):
    if value is None:
        return ""
    return str(value)


def assert_float_close(actual, expected, label):
    if actual is None or expected is None:
        if actual is expected:
            return
        raise RuntimeError(
            f"Float presence mismatch for {label}: "
            f"{actual} vs {expected}"
        )

    if not np.isclose(
        float(actual),
        float(expected),
        rtol=RTOL,
        atol=ATOL,
    ):
        raise RuntimeError(
            f"Float mismatch for {label}: "
            f"{actual} vs {expected}"
        )


def convert_source_feature_rows(raw_rows, fieldnames):
    missing = SOURCE_REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise RuntimeError(
            f"Session 14 feature CSV is missing columns: "
            f"{sorted(missing)}"
        )

    converted = []

    for raw in raw_rows:
        row = {
            "subject": int(raw["subject"]),
            "run": int(raw["run"]),
            "condition": raw["condition"],
            "configuration_id": raw["configuration_id"],
            "window_length_sec": float(raw["window_length_sec"]),
            "step_size_sec": float(raw["step_size_sec"]),
            "outer_window_overlap_fraction": float(
                raw["outer_window_overlap_fraction"]
            ),
            "welch_segment_count": int(raw["welch_segment_count"]),
            "window_index": int(raw["window_index"]),
            "window_start_sec": float(raw["window_start_sec"]),
            "window_end_sec": float(raw["window_end_sec"]),
            "window_center_sec": float(raw["window_center_sec"]),
            "feature_name": raw["feature_name"],
            "feature_unit": raw["feature_unit"],
            FEATURE_NAME: float(raw[FEATURE_NAME]),
        }
        converted.append(row)

    return converted


def validate_source_feature_rows(rows):
    expected_total = 2 * sum(
        EXPECTED_WINDOW_COUNTS_PER_RUN.values()
    )

    if len(rows) != expected_total:
        raise RuntimeError(
            f"Expected {expected_total} Session 14 feature rows, "
            f"found {len(rows)}."
        )

    configuration_ids = {
        row["configuration_id"]
        for row in rows
    }
    if configuration_ids != set(CONFIGURATION_IDS):
        raise RuntimeError(
            "Unexpected Session 14 configuration IDs: "
            f"{sorted(configuration_ids)}"
        )

    grouped = defaultdict(list)

    for row in rows:
        if row["subject"] != SUBJECT:
            raise RuntimeError("Unexpected subject in Session 14 source.")
        if row["run"] not in RUNS:
            raise RuntimeError("Unexpected run in Session 14 source.")
        if row["condition"] != RUN_CONDITIONS[row["run"]]:
            raise RuntimeError("Run/condition mapping mismatch.")
        if row["feature_name"] != FEATURE_NAME:
            raise RuntimeError("Unexpected feature name.")
        if row["feature_unit"] != FEATURE_UNIT:
            raise RuntimeError("Unexpected feature unit.")

        numeric_values = np.asarray(
            [
                row["window_length_sec"],
                row["step_size_sec"],
                row["outer_window_overlap_fraction"],
                row["window_start_sec"],
                row["window_end_sec"],
                row["window_center_sec"],
                row[FEATURE_NAME],
            ],
            dtype=float,
        )
        if not np.isfinite(numeric_values).all():
            raise ValueError("Non-finite Session 14 source value.")
        if row[FEATURE_NAME] <= 0.0:
            raise ValueError("PSD feature must be positive.")

        grouped[
            (row["configuration_id"], row["run"])
        ].append(row)

    for configuration_id in CONFIGURATION_IDS:
        expected_count = EXPECTED_WINDOW_COUNTS_PER_RUN[
            configuration_id
        ]

        for run in RUNS:
            group = sorted(
                grouped[(configuration_id, run)],
                key=lambda row: row["window_index"],
            )
            if len(group) != expected_count:
                raise RuntimeError(
                    f"Unexpected window count for "
                    f"{configuration_id}, run {run}: "
                    f"{len(group)} vs {expected_count}"
                )

            indices = [row["window_index"] for row in group]
            if indices != list(range(expected_count)):
                raise RuntimeError(
                    f"Window-index mismatch for "
                    f"{configuration_id}, run {run}."
                )

            end_times = np.asarray(
                [row["window_end_sec"] for row in group],
                dtype=float,
            )
            if len(end_times) > 1 and np.any(
                np.diff(end_times) <= 0.0
            ):
                raise RuntimeError(
                    f"Non-chronological source rows for "
                    f"{configuration_id}, run {run}."
                )

    return {
        "source_feature_row_count": len(rows),
        "configuration_run_group_count": len(grouped),
    }


def validate_fixed_thresholds_against_session15_metadata():
    if not SESSION15_METADATA_JSON_PATH.exists():
        raise FileNotFoundError(SESSION15_METADATA_JSON_PATH)

    with open(
        SESSION15_METADATA_JSON_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    records = metadata[
        "threshold_specification"
    ]["thresholds_by_subject"]

    subject_records = [
        record
        for record in records
        if int(record["subject"]) == SUBJECT
    ]

    if len(subject_records) != 1:
        raise RuntimeError(
            "Expected exactly one Subject 1 threshold record."
        )

    record = subject_records[0]

    for threshold_id, expected_value in (
        FIXED_THRESHOLDS_BY_SUBJECT[SUBJECT].items()
    ):
        assert_float_close(
            float(record[threshold_id]),
            expected_value,
            f"Session 15 threshold {threshold_id}",
        )

    return metadata


def select_phase1a_rows(rows):
    selected = sorted(
        [
            row
            for row in rows
            if row["configuration_id"]
            == BASELINE_CONFIGURATION_ID
        ],
        key=lambda row: (
            row["subject"],
            row["run"],
            row["window_index"],
        ),
    )

    if len(selected) != 118:
        raise RuntimeError(
            f"Phase 1A requires 118 rows, found {len(selected)}."
        )

    for run in RUNS:
        if sum(row["run"] == run for row in selected) != 59:
            raise RuntimeError(
                f"Phase 1A run {run} does not contain 59 rows."
            )

    return selected


def flatten_rule_rows(rule_rows_by_rule, rule_configurations):
    rows = []

    for configuration in rule_configurations:
        rule_id = configuration["rule_id"]
        rule_rows = sorted(
            rule_rows_by_rule[rule_id],
            key=lambda row: (
                row["subject"],
                row["run"],
                row["window_index"],
            ),
        )
        rows.extend(rule_rows)

    return rows


def compare_decision_stream_reproduction(
    generated_rows,
    historical_rule_ids,
):
    reference_rows, reference_header = read_csv_rows(
        SESSION15_DECISION_STREAM_CSV_PATH
    )

    if reference_header != DECISION_STREAM_COLUMNS:
        raise RuntimeError(
            "Session 15 decision-stream schema differs from expected."
        )

    reference_map = {
        (
            row["rule_id"],
            int(row["subject"]),
            int(row["run"]),
            int(row["window_index"]),
        ): row
        for row in reference_rows
    }

    generated_historical = [
        row
        for row in generated_rows
        if row["rule_id"] in historical_rule_ids
    ]

    if len(generated_historical) != len(reference_rows):
        raise RuntimeError(
            "Historical decision-stream row count mismatch: "
            f"{len(generated_historical)} vs {len(reference_rows)}"
        )

    int_fields = {
        "subject",
        "run",
        "window_index",
        "dwell_updates",
        "candidate_count",
    }
    float_fields = {
        "window_start_sec",
        "window_end_sec",
        "decision_time_sec",
        "raw_feature_value",
        "smoothed_feature_value",
        "threshold_value",
    }
    bool_fields = {
        "smoothed_available",
        "initial_command_confirmed",
        "active_switch_confirmed",
    }

    for generated in generated_historical:
        key = (
            generated["rule_id"],
            int(generated["subject"]),
            int(generated["run"]),
            int(generated["window_index"]),
        )
        if key not in reference_map:
            raise RuntimeError(
                f"Missing Session 15 decision reference: {key}"
            )

        reference = reference_map[key]

        for field in DECISION_STREAM_COLUMNS:
            if field in int_fields:
                actual = int(generated[field])
                expected = int(reference[field])
                if actual != expected:
                    raise RuntimeError(
                        f"Decision reproduction mismatch {key} "
                        f"field={field}: {actual} vs {expected}"
                    )
            elif field in float_fields:
                actual = (
                    parse_optional_float(generated[field])
                )
                expected = parse_optional_float(reference[field])
                assert_float_close(
                    actual,
                    expected,
                    f"decision {key} {field}",
                )
            elif field in bool_fields:
                if bool(generated[field]) != parse_bool(reference[field]):
                    raise RuntimeError(
                        f"Decision reproduction mismatch {key} "
                        f"field={field}."
                    )
            else:
                if normalize_optional_text(generated[field]) != (
                    normalize_optional_text(reference[field])
                ):
                    raise RuntimeError(
                        f"Decision reproduction mismatch {key} "
                        f"field={field}: "
                        f"{generated[field]} vs {reference[field]}"
                    )

    return len(generated_historical)


def compare_episode_reproduction(
    generated_rows,
    historical_rule_ids,
):
    reference_rows, reference_header = read_csv_rows(
        SESSION15_COMMAND_EPISODE_CSV_PATH
    )

    if reference_header != COMMAND_EPISODE_COLUMNS:
        raise RuntimeError(
            "Session 15 command-episode schema differs from expected."
        )

    reference_map = {
        (
            row["rule_id"],
            int(row["subject"]),
            int(row["run"]),
            int(row["episode_index"]),
        ): row
        for row in reference_rows
    }

    generated_historical = [
        row
        for row in generated_rows
        if row["rule_id"] in historical_rule_ids
    ]

    if len(generated_historical) != len(reference_rows):
        raise RuntimeError(
            "Historical command-episode row count mismatch."
        )

    int_fields = {
        "subject",
        "run",
        "dwell_updates",
        "episode_index",
        "decision_update_count",
        "first_window_index",
        "last_window_index",
    }
    float_fields = {
        "threshold_value",
        "episode_start_time_sec",
        "episode_end_time_sec",
        "episode_duration_sec",
        "first_decision_time_sec",
        "last_decision_time_sec",
    }
    bool_fields = {
        "is_initial_stop_episode",
        "ended_at_run_boundary",
    }

    for generated in generated_historical:
        key = (
            generated["rule_id"],
            int(generated["subject"]),
            int(generated["run"]),
            int(generated["episode_index"]),
        )
        if key not in reference_map:
            raise RuntimeError(
                f"Missing Session 15 episode reference: {key}"
            )
        reference = reference_map[key]

        for field in COMMAND_EPISODE_COLUMNS:
            if field in int_fields:
                actual = parse_optional_int(generated[field])
                expected = parse_optional_int(reference[field])
                if actual != expected:
                    raise RuntimeError(
                        f"Episode reproduction mismatch {key} "
                        f"field={field}: {actual} vs {expected}"
                    )
            elif field in float_fields:
                assert_float_close(
                    parse_optional_float(generated[field]),
                    parse_optional_float(reference[field]),
                    f"episode {key} {field}",
                )
            elif field in bool_fields:
                if bool(generated[field]) != parse_bool(reference[field]):
                    raise RuntimeError(
                        f"Episode reproduction mismatch {key} "
                        f"field={field}."
                    )
            else:
                if normalize_optional_text(generated[field]) != (
                    normalize_optional_text(reference[field])
                ):
                    raise RuntimeError(
                        f"Episode reproduction mismatch {key} "
                        f"field={field}."
                    )

    return len(generated_historical)


def compare_summary_reproduction(
    generated_rows,
    historical_rule_ids,
):
    reference_rows, reference_header = read_csv_rows(
        SESSION15_RULE_RUN_SUMMARY_CSV_PATH
    )

    reference_map = {
        (
            row["rule_id"],
            int(row["subject"]),
            int(row["run"]),
        ): row
        for row in reference_rows
    }

    generated_map = {
        (
            row["rule_id"],
            int(row["subject"]),
            int(row["run"]),
        ): row
        for row in generated_rows
        if row["rule_id"] in historical_rule_ids
    }

    if len(generated_map) != len(reference_rows):
        raise RuntimeError(
            "Historical rule/run summary row count mismatch."
        )

    int_fields = {
        "subject",
        "run",
        "dwell_updates",
        "decision_update_count",
        "unavailable_evidence_count",
        "initial_stop_update_count",
        "low_evidence_count",
        "high_evidence_count",
        "cmd_stop_count",
        "cmd_open_count",
        "cmd_close_count",
        "active_switch_count",
        "unconfirmed_candidate_update_count",
        "command_episode_count",
        "active_command_episode_count",
        "short_active_command_episode_count",
    }
    float_fields = {
        "threshold_value",
        "nominal_confirmation_span_sec",
        "run_start_time_sec",
        "run_end_time_sec",
        "first_decision_time_sec",
        "last_decision_time_sec",
        "first_processed_feature_time_sec",
        "initial_stop_duration_sec",
        "first_active_command_time_sec",
        "short_active_episode_max_duration_sec",
        "shortest_active_episode_duration_sec",
        "longest_active_episode_duration_sec",
    }

    for key, reference in reference_map.items():
        if key not in generated_map:
            raise RuntimeError(
                f"Missing generated historical summary: {key}"
            )
        generated = generated_map[key]

        for field in reference_header:
            if field not in generated:
                raise RuntimeError(
                    f"Generated summary lacks historical field: {field}"
                )
            if field in int_fields:
                if int(generated[field]) != int(reference[field]):
                    raise RuntimeError(
                        f"Summary reproduction mismatch {key} "
                        f"field={field}."
                    )
            elif field in float_fields:
                assert_float_close(
                    parse_optional_float(generated[field]),
                    parse_optional_float(reference[field]),
                    f"summary {key} {field}",
                )
            else:
                if normalize_optional_text(generated[field]) != (
                    normalize_optional_text(reference[field])
                ):
                    raise RuntimeError(
                        f"Summary reproduction mismatch {key} "
                        f"field={field}: "
                        f"{generated[field]} vs {reference[field]}"
                    )

    return len(generated_map)


def get_historical_rule_ids():
    reference_rows, _ = read_csv_rows(
        SESSION15_RULE_RUN_SUMMARY_CSV_PATH
    )
    historical_rule_ids = {
        row["rule_id"]
        for row in reference_rows
    }
    if len(historical_rule_ids) != 8:
        raise RuntimeError(
            f"Expected 8 Session 15 rules, found "
            f"{len(historical_rule_ids)}."
        )
    return historical_rule_ids


def validate_complete_grid(
    rule_configurations,
    decision_rows,
    summary_rows,
):
    if len(rule_configurations) != 18:
        raise RuntimeError("Expected exactly 18 rule configurations.")

    if len(decision_rows) != 2124:
        raise RuntimeError(
            f"Expected 2,124 decision rows, found {len(decision_rows)}."
        )

    if len(summary_rows) != 36:
        raise RuntimeError(
            f"Expected 36 summary rows, found {len(summary_rows)}."
        )

    rule_ids = {
        configuration["rule_id"]
        for configuration in rule_configurations
    }

    summary_keys = {
        (
            row["rule_id"],
            int(row["run"]),
        )
        for row in summary_rows
    }

    for rule_id in rule_ids:
        for run in RUNS:
            if (rule_id, run) not in summary_keys:
                raise RuntimeError(
                    f"Missing rule/run summary: {rule_id}, run {run}"
                )

    rows_by_rule_run = defaultdict(list)
    for row in decision_rows:
        rows_by_rule_run[
            (row["rule_id"], int(row["run"]))
        ].append(row)

    for key, rows in rows_by_rule_run.items():
        if len(rows) != 59:
            raise RuntimeError(
                f"Expected 59 decision rows for {key}, "
                f"found {len(rows)}."
            )
        rows = sorted(rows, key=lambda row: row["window_index"])
        if [row["window_index"] for row in rows] != list(range(59)):
            raise RuntimeError(
                f"Decision ordering mismatch for {key}."
            )

    for row in summary_rows:
        if not np.isclose(
            float(row["low_evidence_fraction"])
            + float(row["high_evidence_fraction"]),
            1.0,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError("Evidence fractions do not sum to one.")

        if not np.isclose(
            float(row["stop_duration_fraction"])
            + float(row["open_duration_fraction"])
            + float(row["close_duration_fraction"]),
            1.0,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError("Occupancy fractions do not sum to one.")

    return {
        "rule_count": len(rule_ids),
        "summary_row_count": len(summary_rows),
        "decision_stream_row_count": len(decision_rows),
    }


def validate_temporal_reproduction(temporal_rows):
    reference_rows, _ = read_csv_rows(
        SOURCE_CONDITION_SUMMARY_CSV_PATH
    )

    reference_map = {
        (
            row["configuration_id"],
            int(row["run"]),
        ): float(row["iqr_over_median"])
        for row in reference_rows
    }

    if len(reference_map) != 10:
        raise RuntimeError(
            "Session 14 condition summary must contain 10 "
            "configuration/run references."
        )

    for row in temporal_rows:
        key = (
            row["configuration_id"],
            int(row["run"]),
        )
        if key not in reference_map:
            raise RuntimeError(
                f"Missing Session 14 relative-IQR reference: {key}"
            )
        assert_float_close(
            float(row["relative_iqr"]),
            reference_map[key],
            f"relative IQR {key}",
        )

        expected_count = EXPECTED_WINDOW_COUNTS_PER_RUN[
            row["configuration_id"]
        ]
        if int(row["n_features"]) != expected_count:
            raise RuntimeError(
                f"Temporal feature count mismatch for {key}."
            )
        if int(row["n_differences"]) != expected_count - 1:
            raise RuntimeError(
                f"Temporal difference count mismatch for {key}."
            )

    return {
        "temporal_summary_row_count": len(temporal_rows),
        "relative_iqr_reproduction_count": len(temporal_rows),
    }


def save_csv_rows(rows, columns, path):
    if not rows:
        raise RuntimeError(f"No rows supplied for {path.name}.")

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=columns,
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)

    reloaded_rows, reloaded_header = read_csv_rows(path)

    if reloaded_header != columns:
        raise RuntimeError(f"Reloaded header mismatch: {path.name}")
    if len(reloaded_rows) != len(rows):
        raise RuntimeError(f"Reloaded row-count mismatch: {path.name}")

    return reloaded_rows


def validate_reloaded_rule_grid(
    decision_rows,
    episode_rows,
    summary_rows,
):
    if len(decision_rows) != 2124:
        raise RuntimeError("Reloaded decision-stream count mismatch.")
    if len(summary_rows) != 36:
        raise RuntimeError("Reloaded rule-grid summary count mismatch.")
    if not episode_rows:
        raise RuntimeError("Reloaded command-episode table is empty.")

    summary_keys = [
        (
            row["rule_id"],
            int(row["subject"]),
            int(row["run"]),
        )
        for row in summary_rows
    ]
    if len(summary_keys) != len(set(summary_keys)):
        raise RuntimeError("Reloaded summary keys are not unique.")

    for row in summary_rows:
        for field in (
            "threshold_value",
            "low_evidence_fraction",
            "high_evidence_fraction",
            "stop_duration_fraction",
            "open_duration_fraction",
            "close_duration_fraction",
        ):
            value = float(row[field])
            if not np.isfinite(value):
                raise RuntimeError(
                    f"Non-finite reloaded summary value: {field}"
                )

    return {
        "reloaded_decision_stream_row_count": len(decision_rows),
        "reloaded_command_episode_row_count": len(episode_rows),
        "reloaded_rule_grid_summary_row_count": len(summary_rows),
    }


def validate_reloaded_temporal(rows):
    if len(rows) != 10:
        raise RuntimeError("Reloaded temporal summary count mismatch.")

    keys = [
        (row["configuration_id"], int(row["run"]))
        for row in rows
    ]
    if len(keys) != len(set(keys)):
        raise RuntimeError("Reloaded temporal keys are not unique.")

    for row in rows:
        for field in (
            "relative_iqr",
            "successive_difference_sd_population",
            "median_absolute_successive_change",
        ):
            if not np.isfinite(float(row[field])):
                raise RuntimeError(
                    f"Non-finite temporal metric: {field}"
                )

    return {
        "reloaded_temporal_summary_row_count": len(rows),
    }


def git_output(args, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"Git command failed: git {' '.join(args)}\n"
            f"{result.stderr.strip()}"
        )
    return result


def get_execution_git_provenance():
    head = git_output(["rev-parse", "HEAD"]).stdout.strip()

    for source_path in IMPLEMENTATION_SOURCE_PATHS:
        tracked = git_output(
            ["ls-files", "--error-unmatch", source_path],
            check=False,
        )
        if tracked.returncode != 0:
            raise RuntimeError(
                "Session 21 implementation source must be committed "
                f"before execution: {source_path}"
            )

        unstaged = git_output(
            ["diff", "--quiet", "--", source_path],
            check=False,
        )
        staged = git_output(
            ["diff", "--cached", "--quiet", "--", source_path],
            check=False,
        )
        if unstaged.returncode != 0 or staged.returncode != 0:
            raise RuntimeError(
                "Session 21 implementation source has uncommitted "
                f"changes: {source_path}"
            )

    status = git_output(
        ["status", "--porcelain=v1", "--untracked-files=all"]
    ).stdout

    return {
        "implementation_git_revision": head,
        "execution_git_revision": head,
        "working_tree_status_before_outputs": (
            "CLEAN" if not status.strip() else "DIRTY"
        ),
        "implementation_source_paths": list(
            IMPLEMENTATION_SOURCE_PATHS
        ),
    }


def rule_display_label(
    configuration,
    historical_rule_ids,
):
    threshold_labels = {
        "threshold_eo_q95": "EO-Q95",
        "threshold_gap_midpoint": "MID",
        "threshold_ec_q05": "EC-Q05",
    }
    smoothing_labels = {
        SMOOTHING_ID_NONE: "N",
        SMOOTHING_ID_MEDIAN3: "M3",
    }
    label = (
        f"{threshold_labels[configuration['threshold_id']]}-"
        f"{smoothing_labels[configuration['smoothing_id']]}-"
        f"D{configuration['dwell_updates']}"
    )

    if configuration["rule_id"] in historical_rule_ids:
        label += " †"

    if configuration["rule_id"] == REFERENCE_RULE_ID:
        label += "★"

    return label


def save_rule_grid_figure(
    reloaded_summary_rows,
    rule_configurations,
    historical_rule_ids,
):
    summary_map = {
        (row["rule_id"], int(row["run"])): row
        for row in reloaded_summary_rows
    }
    labels = [
        rule_display_label(
            configuration,
            historical_rule_ids,
        )
        for configuration in rule_configurations
    ]
    x = np.arange(len(rule_configurations))

    figure, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(18, 11),
        sharex="col",
    )

    for row_index, run in enumerate(RUNS):
        ordered = [
            summary_map[(configuration["rule_id"], run)]
            for configuration in rule_configurations
        ]

        stop_fraction = np.asarray(
            [float(row["stop_duration_fraction"]) for row in ordered]
        )
        open_fraction = np.asarray(
            [float(row["open_duration_fraction"]) for row in ordered]
        )
        close_fraction = np.asarray(
            [float(row["close_duration_fraction"]) for row in ordered]
        )
        switches = np.asarray(
            [int(row["active_switch_count"]) for row in ordered]
        )

        occupancy_axis = axes[row_index, 0]
        occupancy_axis.bar(x, stop_fraction, label="STOP")
        occupancy_axis.bar(
            x,
            open_fraction,
            bottom=stop_fraction,
            label="OPEN",
        )
        occupancy_axis.bar(
            x,
            close_fraction,
            bottom=stop_fraction + open_fraction,
            label="CLOSE",
        )
        occupancy_axis.set_ylim(0.0, 1.0)
        occupancy_axis.set_ylabel("Duration fraction")
        occupancy_axis.set_title(
            f"Run {run} — {RUN_CONDITIONS[run]}: command occupancy"
        )
        occupancy_axis.grid(axis="y", alpha=0.25)
        occupancy_axis.legend()

        switch_axis = axes[row_index, 1]
        switch_axis.bar(x, switches)
        switch_axis.set_ylabel("Active OPEN↔CLOSE switches")
        switch_axis.set_title(
            f"Run {run} — {RUN_CONDITIONS[run]}: active switches"
        )
        switch_axis.grid(axis="y", alpha=0.25)

    threshold_family_separators = (5.5, 11.5)
    for axis in axes.flat:
        for separator_x in threshold_family_separators:
            axis.axvline(
                separator_x,
                linestyle=":",
                linewidth=0.9,
                alpha=0.45,
                zorder=0,
            )

    for axis in axes[-1, :]:
        axis.set_xticks(x)
        axis.set_xticklabels(
            labels,
            rotation=90,
            fontsize=8,
        )
        axis.set_xlabel("Threshold–smoothing–dwell rule")

    figure.suptitle(
        "Session 21 Phase 1A: 18-Rule Command Behavior",
        fontsize=15,
    )
    figure.text(
        0.5,
        0.012,
        "† Reproduced Session 15 rule    ★ Frozen reference rule",
        ha="center",
        fontsize=9,
    )
    figure.tight_layout(rect=(0.0, 0.035, 1.0, 0.96))

    RULE_GRID_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    figure.savefig(RULE_GRID_FIGURE_PATH, dpi=180)
    plt.close(figure)

    if (
        not RULE_GRID_FIGURE_PATH.exists()
        or RULE_GRID_FIGURE_PATH.stat().st_size == 0
    ):
        raise RuntimeError("Rule-grid figure was not saved correctly.")


def save_temporal_variability_figure(reloaded_rows):
    row_map = {
        (row["configuration_id"], int(row["run"])): row
        for row in reloaded_rows
    }

    primary_ids = (
        "win-1s_step-1s",
        "win-2s_step-1s",
        "win-4s_step-1s",
    )
    primary_window_lengths = np.asarray([1.0, 2.0, 4.0])

    figure, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(13, 10),
    )

    metrics = (
        ("relative_iqr", "Relative IQR", axes[0, 0]),
        (
            "successive_difference_sd_population",
            "SD(Δx), ddof=0 (V²/Hz)",
            axes[0, 1],
        ),
        (
            "median_absolute_successive_change",
            "Median |Δx| (V²/Hz)",
            axes[1, 0],
        ),
    )

    for metric, ylabel, axis in metrics:
        for run in RUNS:
            values = [
                float(row_map[(configuration_id, run)][metric])
                for configuration_id in primary_ids
            ]
            axis.plot(
                primary_window_lengths,
                values,
                marker="o",
                label=f"Run {run}",
            )
        axis.set_xticks(primary_window_lengths)
        axis.set_xlabel("Window length (s), step fixed at 1 s")
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.25)
        axis.legend()

    descriptive_axis = axes[1, 1]
    step_ids = (
        "win-2s_step-0p5s",
        "win-2s_step-1s",
        "win-2s_step-2s",
    )
    step_values = np.asarray([0.5, 1.0, 2.0])

    for run in RUNS:
        volatility_values = [
            float(
                row_map[(configuration_id, run)][
                    "successive_difference_sd_population"
                ]
            )
            for configuration_id in step_ids
        ]
        median_change_values = [
            float(
                row_map[(configuration_id, run)][
                    "median_absolute_successive_change"
                ]
            )
            for configuration_id in step_ids
        ]
        descriptive_axis.scatter(
            step_values,
            volatility_values,
            marker="o",
            label=f"Run {run} SD(Δx)",
        )
        descriptive_axis.scatter(
            step_values,
            median_change_values,
            marker="x",
            label=f"Run {run} median |Δx|",
        )

    descriptive_axis.set_xticks(step_values)
    descriptive_axis.set_xlabel("Step size (s), 2 s window")
    descriptive_axis.set_ylabel("Successive-change magnitude (V²/Hz)")
    descriptive_axis.set_title(
        "Descriptive cross-step records — no direct ranking"
    )
    descriptive_axis.grid(alpha=0.25)
    descriptive_axis.legend(fontsize=8)

    axes[0, 0].set_title("A. Distributional variability")
    axes[0, 1].set_title("B. Temporal volatility")
    axes[1, 0].set_title("C. Robust successive change")

    figure.suptitle(
        "Session 21 Phase 1B: Temporal Feature Variability",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))

    TEMPORAL_VARIABILITY_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    figure.savefig(TEMPORAL_VARIABILITY_FIGURE_PATH, dpi=180)
    plt.close(figure)

    if (
        not TEMPORAL_VARIABILITY_FIGURE_PATH.exists()
        or TEMPORAL_VARIABILITY_FIGURE_PATH.stat().st_size == 0
    ):
        raise RuntimeError(
            "Temporal-variability figure was not saved correctly."
        )


def build_metadata(
    git_provenance,
    rule_configurations,
    source_validation,
    reproduction_validation,
    grid_validation,
    temporal_validation,
    reload_validation,
):
    return {
        "metadata_schema_version": "1.0",
        "session": {
            "session_id": 21,
            "analysis_name": "phase1_rule_grid_and_temporal_variability",
            "scope": ["Phase 1A", "Phase 1B"],
        },
        "governing_artifact": (
            IMPLEMENTATION_PLAN_PATH
            .relative_to(PROJECT_ROOT)
            .as_posix()
        ),
        "source_artifacts": {
            "session14_window_features": (
                SOURCE_FEATURE_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "session14_condition_summary": (
                SOURCE_CONDITION_SUMMARY_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "session15_decision_stream": (
                SESSION15_DECISION_STREAM_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "session15_command_episodes": (
                SESSION15_COMMAND_EPISODE_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "session15_rule_run_summary": (
                SESSION15_RULE_RUN_SUMMARY_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "session15_metadata": (
                SESSION15_METADATA_JSON_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
        },
        "recording_scope": {
            "subject": SUBJECT,
            "runs": list(RUNS),
            "conditions": {
                str(run): RUN_CONDITIONS[run]
                for run in RUNS
            },
            "run_pooling": "not_authorized",
        },
        "phase1a": {
            "feature_name": FEATURE_NAME,
            "feature_unit": FEATURE_UNIT,
            "configuration_id": BASELINE_CONFIGURATION_ID,
            "updates_per_run": 59,
            "selected_feature_row_count": 118,
            "fixed_thresholds_by_subject": {
                str(subject): thresholds
                for subject, thresholds in (
                    FIXED_THRESHOLDS_BY_SUBJECT.items()
                )
            },
            "rule_count": len(rule_configurations),
            "rule_configurations": rule_configurations,
            "reference_rule_id": REFERENCE_RULE_ID,
            "evidence_fraction_definition": (
                "LOW or HIGH count divided by LOW+HIGH available "
                "evidence count; UNAVAILABLE excluded from denominator"
            ),
            "evidence_transition_definition": (
                "Adjacent LOW_ALPHA<->HIGH_ALPHA transitions only; "
                "transitions involving UNAVAILABLE excluded"
            ),
            "occupancy_definition": (
                "elapsed command-state duration divided by complete "
                "recording duration"
            ),
            "short_active_episode_max_duration_sec": (
                SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC
            ),
        },
        "phase1b": {
            "configuration_ids": list(CONFIGURATION_IDS),
            "relative_iqr_definition": "(Q75-Q25)/median(x)",
            "successive_difference_definition": "x_t - x_(t-1)",
            "volatility_definition": "SD(successive differences), ddof=0",
            "median_absolute_successive_change_definition": (
                "median(abs(successive differences))"
            ),
            "primary_comparison_configuration_ids": [
                "win-1s_step-1s",
                "win-2s_step-1s",
                "win-4s_step-1s",
            ],
            "cross_step_restriction": (
                "Raw successive-change metrics are not directly ranked "
                "across different step sizes because temporal increments "
                "and outer-window overlap differ."
            ),
        },
        "validation": {
            "source": source_validation,
            "session15_reproduction": reproduction_validation,
            "complete_grid": grid_validation,
            "temporal_variability": temporal_validation,
            "save_reload": reload_validation,
            "figure_files_nonempty": True,
        },
        "git_provenance": git_provenance,
        "software": {
            "python_version": platform.python_version(),
            "numpy_version": np.__version__,
            "matplotlib_version": __import__("matplotlib").__version__,
        },
        "outputs": {
            "decision_stream_csv": (
                DECISION_STREAM_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "command_episode_csv": (
                COMMAND_EPISODE_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "rule_grid_summary_csv": (
                RULE_GRID_SUMMARY_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "temporal_variability_summary_csv": (
                TEMPORAL_VARIABILITY_CSV_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "metadata_json": (
                METADATA_JSON_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "rule_grid_figure": (
                RULE_GRID_FIGURE_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
            "temporal_variability_figure": (
                TEMPORAL_VARIABILITY_FIGURE_PATH
                .relative_to(PROJECT_ROOT)
                .as_posix()
            ),
        },
    }


def save_metadata(metadata):
    METADATA_JSON_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

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
            allow_nan=False,
        )
        file.write("\n")

    with open(
        METADATA_JSON_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        reloaded = json.load(file)

    if reloaded != metadata:
        raise RuntimeError("Reloaded metadata differs from saved metadata.")


def main():
    git_provenance = get_execution_git_provenance()

    raw_source_rows, source_header = read_csv_rows(
        SOURCE_FEATURE_CSV_PATH
    )
    source_rows = convert_source_feature_rows(
        raw_source_rows,
        source_header,
    )
    source_validation = validate_source_feature_rows(
        source_rows
    )

    validate_fixed_thresholds_against_session15_metadata()

    phase1a_rows = select_phase1a_rows(source_rows)
    no_smoothing_rows = build_no_smoothing_rows(
        phase1a_rows
    )
    median3_rows = build_causal_median3_rows(
        phase1a_rows
    )

    processed_rows_by_smoothing = {
        SMOOTHING_ID_NONE: no_smoothing_rows,
        SMOOTHING_ID_MEDIAN3: median3_rows,
    }

    rule_configurations = build_rule_configurations()
    rule_rows_by_rule = build_rule_rows_by_rule(
        processed_rows_by_smoothing=processed_rows_by_smoothing,
        thresholds_by_subject=FIXED_THRESHOLDS_BY_SUBJECT,
        rule_configurations=rule_configurations,
    )
    decision_rows = flatten_rule_rows(
        rule_rows_by_rule,
        rule_configurations,
    )
    command_episode_rows = build_command_episode_rows(
        rule_rows_by_rule,
        rule_configurations,
    )
    rule_grid_summary_rows = build_rule_run_summary_rows(
        rule_rows_by_rule,
        command_episode_rows,
        rule_configurations,
        step_size_sec=1.0,
    )

    historical_rule_ids = get_historical_rule_ids()
    generated_rule_ids = {
        configuration["rule_id"]
        for configuration in rule_configurations
    }
    if not historical_rule_ids.issubset(generated_rule_ids):
        raise RuntimeError(
            "The Session 21 grid does not retain all Session 15 rule IDs."
        )

    reproduction_validation = {
        "historical_rule_count": len(historical_rule_ids),
        "decision_stream_rows_reproduced": (
            compare_decision_stream_reproduction(
                decision_rows,
                historical_rule_ids,
            )
        ),
        "command_episode_rows_reproduced": (
            compare_episode_reproduction(
                command_episode_rows,
                historical_rule_ids,
            )
        ),
        "rule_run_summary_rows_reproduced": (
            compare_summary_reproduction(
                rule_grid_summary_rows,
                historical_rule_ids,
            )
        ),
        "status": "PASS",
    }

    grid_validation = validate_complete_grid(
        rule_configurations,
        decision_rows,
        rule_grid_summary_rows,
    )
    grid_validation["new_rule_count"] = (
        len(generated_rule_ids - historical_rule_ids)
    )
    if grid_validation["new_rule_count"] != 10:
        raise RuntimeError(
            "Expected exactly 10 new Session 21 rules."
        )
    grid_validation["status"] = "PASS"

    reloaded_decision_rows = save_csv_rows(
        decision_rows,
        DECISION_STREAM_COLUMNS,
        DECISION_STREAM_CSV_PATH,
    )
    reloaded_episode_rows = save_csv_rows(
        command_episode_rows,
        COMMAND_EPISODE_COLUMNS,
        COMMAND_EPISODE_CSV_PATH,
    )
    reloaded_summary_rows = save_csv_rows(
        rule_grid_summary_rows,
        RULE_GRID_SUMMARY_COLUMNS,
        RULE_GRID_SUMMARY_CSV_PATH,
    )

    rule_reload_validation = validate_reloaded_rule_grid(
        reloaded_decision_rows,
        reloaded_episode_rows,
        reloaded_summary_rows,
    )

    temporal_rows = build_temporal_variability_rows(
        source_rows,
        CONFIGURATION_IDS,
    )
    temporal_validation = validate_temporal_reproduction(
        temporal_rows
    )
    temporal_validation["status"] = "PASS"

    reloaded_temporal_rows = save_csv_rows(
        temporal_rows,
        TEMPORAL_VARIABILITY_COLUMNS,
        TEMPORAL_VARIABILITY_CSV_PATH,
    )
    temporal_reload_validation = validate_reloaded_temporal(
        reloaded_temporal_rows
    )

    save_rule_grid_figure(
        reloaded_summary_rows,
        rule_configurations,
        historical_rule_ids,
    )
    save_temporal_variability_figure(
        reloaded_temporal_rows
    )

    reload_validation = {
        **rule_reload_validation,
        **temporal_reload_validation,
        "status": "PASS",
    }

    metadata = build_metadata(
        git_provenance=git_provenance,
        rule_configurations=rule_configurations,
        source_validation=source_validation,
        reproduction_validation=reproduction_validation,
        grid_validation=grid_validation,
        temporal_validation=temporal_validation,
        reload_validation=reload_validation,
    )
    save_metadata(metadata)

    print("\n========================================")
    print("Session 21 Phase 1 execution: PASS")
    print("Implementation Git revision:", git_provenance[
        "implementation_git_revision"
    ])
    print("Decision-stream rows:", len(decision_rows))
    print("Command episodes:", len(command_episode_rows))
    print("Rule/run summaries:", len(rule_grid_summary_rows))
    print("Temporal summaries:", len(temporal_rows))
    print("Historical rules reproduced:", len(historical_rule_ids))
    print("New rules validated:", grid_validation["new_rule_count"])
    print("Metadata:", METADATA_JSON_PATH)
    print("========================================")


if __name__ == "__main__":
    main()
