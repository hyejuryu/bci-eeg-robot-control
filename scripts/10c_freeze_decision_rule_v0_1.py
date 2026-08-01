"""
Freeze the selected Session 15 decision rule as v0.1.

This script reads existing Session 15 outputs.
It does not recalculate EEG features, thresholds,
smoothing, evidence states, or command states.
"""

import csv
import json
import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SESSION15_RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "session-15"
)

SESSION16_RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "session-16"
)

SOURCE_DECISION_STREAM_CSV_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "decision-stream.csv"
    )
)

SOURCE_COMMAND_EPISODE_CSV_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "command-episodes.csv"
    )
)

SOURCE_RULE_RUN_SUMMARY_CSV_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "rule-run-summary.csv"
    )
)

SOURCE_METADATA_JSON_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "decision-rule-metadata.json"
    )
)

FROZEN_DECISION_STREAM_CSV_PATH = (
    SESSION16_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_"
        "decision-rule-v0.1-stream.csv"
    )
)

FROZEN_CONFIG_JSON_PATH = (
    SESSION16_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_"
        "decision-rule-v0.1.json"
    )
)

FREEZE_VERSION = "v0.1"
FREEZE_DATE = "2026-07-30"
FREEZE_STATUS = "frozen"

SELECTED_RULE_ID = (
    "thr-gap-mid__smooth-none__dwell-2"
)

EXPECTED_THRESHOLD_ID = (
    "threshold_gap_midpoint"
)

EXPECTED_SMOOTHING_ID = "smooth-none"
EXPECTED_DWELL_UPDATES = 2

EXPECTED_RECORDING_COUNT = 2
EXPECTED_ROWS_PER_RECORDING = 59

EXPECTED_SELECTED_STREAM_ROW_COUNT = (
    EXPECTED_RECORDING_COUNT
    * EXPECTED_ROWS_PER_RECORDING
)

EXPECTED_SELECTED_EPISODE_ROW_COUNT = 4

EXPECTED_SELECTED_SUMMARY_ROW_COUNT = (
    EXPECTED_RECORDING_COUNT
)

EXPECTED_BEHAVIOR_BY_RECORDING = {
    (1, 1): {
        "condition": "baseline_eyes_open",
        "first_active_command_time_sec": 3.0,
        "first_active_command": "CMD_OPEN",
        "final_command_state": "CMD_OPEN",
        "active_switch_count": 0,
        "unconfirmed_candidate_update_count": 1,
        "unconfirmed_candidate_times_sec": "26.0",
        "low_evidence_count": 58,
        "high_evidence_count": 1,
        "active_command": "CMD_OPEN",
    },
    (1, 2): {
        "condition": "baseline_eyes_closed",
        "first_active_command_time_sec": 3.0,
        "first_active_command": "CMD_CLOSE",
        "final_command_state": "CMD_CLOSE",
        "active_switch_count": 0,
        "unconfirmed_candidate_update_count": 0,
        "unconfirmed_candidate_times_sec": "",
        "low_evidence_count": 0,
        "high_evidence_count": 59,
        "active_command": "CMD_CLOSE",
    },
}

EXPECTED_RUN_START_TIME_SEC = 0.0
EXPECTED_FIRST_ACTIVE_TIME_SEC = 3.0
EXPECTED_RUN_END_TIME_SEC = 60.0

FLOAT_ABS_TOL = 1e-12

REQUIRED_DECISION_STREAM_COLUMNS = {
    "rule_id",
    "subject",
    "run",
    "window_index",
    "threshold_id",
    "smoothing_id",
    "dwell_updates",
}

REQUIRED_COMMAND_EPISODE_COLUMNS = {
    "rule_id",
    "subject",
    "run",
    "episode_index",
    "threshold_id",
    "smoothing_id",
    "dwell_updates",
}

REQUIRED_RULE_RUN_SUMMARY_COLUMNS = {
    "rule_id",
    "subject",
    "run",
    "threshold_id",
    "smoothing_id",
    "dwell_updates",
}

REQUIRED_METADATA_KEYS = {
    "recording_scope",
    "rule_set",
    "outputs",
    "threshold_specification",
    "state_mapping",
}


def validate_source_paths():
    """
    Confirm that all required Session 15
    source artifacts exist and are non-empty.
    """

    source_paths = [
        SOURCE_DECISION_STREAM_CSV_PATH,
        SOURCE_COMMAND_EPISODE_CSV_PATH,
        SOURCE_RULE_RUN_SUMMARY_CSV_PATH,
        SOURCE_METADATA_JSON_PATH,
    ]

    for source_path in source_paths:
        if not source_path.exists():
            raise FileNotFoundError(
                "Required Session 15 source "
                "artifact was not found:\n"
                f"{source_path}"
            )

        if source_path.stat().st_size == 0:
            raise RuntimeError(
                "Required Session 15 source "
                "artifact is empty:\n"
                f"{source_path}"
            )

    return source_paths


def load_csv_rows(
    csv_path,
    required_columns,
):
    """
    Load one CSV and validate its header.
    """

    with open(
        csv_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "CSV has no header:\n"
                f"{csv_path}"
            )

        missing_columns = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:
            raise RuntimeError(
                "CSV is missing required "
                f"columns: {sorted(missing_columns)}\n"
                f"{csv_path}"
            )

        rows = list(reader)

    if not rows:
        raise RuntimeError(
            "CSV contains no data rows:\n"
            f"{csv_path}"
        )

    return list(reader.fieldnames), rows


def load_metadata(
    json_path,
):
    """
    Load and minimally validate the
    Session 15 metadata JSON.
    """

    with open(
        json_path,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    if not isinstance(metadata, dict):
        raise RuntimeError(
            "Metadata root must be a JSON object."
        )

    missing_keys = (
        REQUIRED_METADATA_KEYS
        - set(metadata)
    )

    if missing_keys:
        raise RuntimeError(
            "Metadata are missing required "
            f"top-level keys: "
            f"{sorted(missing_keys)}"
        )

    return metadata


def validate_source_row_counts(
    decision_rows,
    episode_rows,
    summary_rows,
    metadata,
):
    """
    Confirm that actual Session 15 CSV row
    counts match the saved metadata.
    """

    row_count_checks = [
        (
            "decision stream",
            len(decision_rows),
            metadata["outputs"][
                "decision_stream_csv"
            ]["row_count"],
        ),
        (
            "command episodes",
            len(episode_rows),
            metadata["outputs"][
                "command_episode_csv"
            ]["row_count"],
        ),
        (
            "rule-run summary",
            len(summary_rows),
            metadata["outputs"][
                "rule_run_summary_csv"
            ]["row_count"],
        ),
    ]

    for (
        artifact_name,
        actual_count,
        expected_count,
    ) in row_count_checks:
        if actual_count != int(
            expected_count
        ):
            raise RuntimeError(
                f"{artifact_name} row count "
                "does not match metadata: "
                f"{actual_count} vs "
                f"{expected_count}."
            )


def select_rule_rows(
    rows,
    artifact_name,
):
    """
    Select rows belonging to the frozen
    decision-rule candidate.
    """

    selected_rows = [
        row
        for row in rows
        if row["rule_id"] == SELECTED_RULE_ID
    ]

    if not selected_rows:
        available_rule_ids = sorted({
            row["rule_id"]
            for row in rows
        })

        raise RuntimeError(
            "Selected rule was not found in "
            f"{artifact_name}: "
            f"{SELECTED_RULE_ID}. "
            "Available rule IDs: "
            f"{available_rule_ids}"
        )

    return selected_rows


def validate_selected_rule_metadata(
    metadata,
):
    """
    Confirm that metadata contains exactly one
    matching selected-rule configuration.
    """

    configurations = metadata[
        "rule_set"
    ]["configurations"]

    matching_configurations = [
        configuration
        for configuration in configurations
        if (
            configuration["rule_id"]
            == SELECTED_RULE_ID
        )
    ]

    if len(matching_configurations) != 1:
        raise RuntimeError(
            "Metadata must contain exactly one "
            "selected-rule configuration, "
            f"but found "
            f"{len(matching_configurations)}."
        )

    selected_configuration = (
        matching_configurations[0]
    )

    expected_values = {
        "threshold_id": (
            EXPECTED_THRESHOLD_ID
        ),
        "smoothing_id": (
            EXPECTED_SMOOTHING_ID
        ),
        "dwell_updates": (
            EXPECTED_DWELL_UPDATES
        ),
    }

    for key, expected_value in (
        expected_values.items()
    ):
        actual_value = (
            selected_configuration[key]
        )

        if actual_value != expected_value:
            raise RuntimeError(
                "Selected-rule metadata "
                f"mismatch for {key}: "
                f"{actual_value} vs "
                f"{expected_value}."
            )

    recording_count = int(
        metadata["recording_scope"][
            "recording_count"
        ]
    )

    if recording_count != (
        EXPECTED_RECORDING_COUNT
    ):
        raise RuntimeError(
            "Metadata recording count does "
            "not match the expected value: "
            f"{recording_count} vs "
            f"{EXPECTED_RECORDING_COUNT}."
        )

    return selected_configuration


def validate_selected_rule_rows(
    selected_decision_rows,
    selected_episode_rows,
    selected_summary_rows,
):
    """
    Confirm selected-rule row counts, settings,
    recording keys, and decision-row uniqueness.
    """

    if len(selected_decision_rows) != (
        EXPECTED_SELECTED_STREAM_ROW_COUNT
    ):
        raise RuntimeError(
            "Selected decision-stream row count "
            "does not match the expected value: "
            f"{len(selected_decision_rows)} vs "
            f"{EXPECTED_SELECTED_STREAM_ROW_COUNT}."
        )

    if len(selected_episode_rows) != (
        EXPECTED_SELECTED_EPISODE_ROW_COUNT
    ):
        raise RuntimeError(
            "Selected command-episode row count "
            "does not match the expected value: "
            f"{len(selected_episode_rows)} vs "
            f"{EXPECTED_SELECTED_EPISODE_ROW_COUNT}."
        )

    if len(selected_summary_rows) != (
        EXPECTED_SELECTED_SUMMARY_ROW_COUNT
    ):
        raise RuntimeError(
            "Selected summary-row count does "
            "not match the expected value: "
            f"{len(selected_summary_rows)} vs "
            f"{EXPECTED_SELECTED_SUMMARY_ROW_COUNT}."
        )

    selected_artifacts = [
        (
            "decision stream",
            selected_decision_rows,
        ),
        (
            "command episodes",
            selected_episode_rows,
        ),
        (
            "rule-run summary",
            selected_summary_rows,
        ),
    ]

    for artifact_name, rows in (
        selected_artifacts
    ):
        for row in rows:
            if (
                row["threshold_id"]
                != EXPECTED_THRESHOLD_ID
            ):
                raise RuntimeError(
                    f"{artifact_name} contains "
                    "an unexpected threshold ID."
                )

            if (
                row["smoothing_id"]
                != EXPECTED_SMOOTHING_ID
            ):
                raise RuntimeError(
                    f"{artifact_name} contains "
                    "an unexpected smoothing ID."
                )

            if int(
                row["dwell_updates"]
            ) != EXPECTED_DWELL_UPDATES:
                raise RuntimeError(
                    f"{artifact_name} contains "
                    "an unexpected dwell value."
                )

    decision_recording_counts = {}
    seen_decision_keys = set()

    for row in selected_decision_rows:
        subject = int(row["subject"])
        run = int(row["run"])
        window_index = int(
            row["window_index"]
        )

        decision_key = (
            subject,
            run,
            window_index,
        )

        if decision_key in seen_decision_keys:
            raise RuntimeError(
                "Duplicate selected decision-row "
                f"key: {decision_key}"
            )

        seen_decision_keys.add(
            decision_key
        )

        recording_key = (
            subject,
            run,
        )

        decision_recording_counts[
            recording_key
        ] = (
            decision_recording_counts.get(
                recording_key,
                0,
            )
            + 1
        )

    if len(decision_recording_counts) != (
        EXPECTED_RECORDING_COUNT
    ):
        raise RuntimeError(
            "Selected decision stream contains "
            "an unexpected recording count."
        )

    for (
        recording_key,
        row_count,
    ) in decision_recording_counts.items():
        if row_count != (
            EXPECTED_ROWS_PER_RECORDING
        ):
            raise RuntimeError(
                "Selected decision stream has "
                "an unexpected row count for "
                f"{recording_key}: "
                f"{row_count}."
            )

    summary_recording_keys = {
        (
            int(row["subject"]),
            int(row["run"]),
        )
        for row in selected_summary_rows
    }

    if summary_recording_keys != set(
        decision_recording_counts
    ):
        raise RuntimeError(
            "Selected summary recording keys "
            "do not match the decision stream."
        )

    episode_recording_counts = {}

    for row in selected_episode_rows:
        recording_key = (
            int(row["subject"]),
            int(row["run"]),
        )

        episode_recording_counts[
            recording_key
        ] = (
            episode_recording_counts.get(
                recording_key,
                0,
            )
            + 1
        )

    if set(
        episode_recording_counts
    ) != set(
        decision_recording_counts
    ):
        raise RuntimeError(
            "Selected episode recording keys "
            "do not match the decision stream."
        )

    for (
        recording_key,
        episode_count,
    ) in episode_recording_counts.items():
        if episode_count != 2:
            raise RuntimeError(
                "Expected two command episodes "
                f"for {recording_key}, but found "
                f"{episode_count}."
            )

    return decision_recording_counts


def validate_selected_threshold(
    selected_decision_rows,
    selected_episode_rows,
    selected_summary_rows,
    metadata,
):
    """
    Confirm that all selected artifacts use the
    subject-specific midpoint threshold recorded
    in the Session 15 metadata.
    """

    threshold_records = metadata[
        "threshold_specification"
    ]["thresholds_by_subject"]

    thresholds_by_subject = {
        int(record["subject"]): float(
            record[EXPECTED_THRESHOLD_ID]
        )
        for record in threshold_records
    }

    if not thresholds_by_subject:
        raise RuntimeError(
            "No subject thresholds were found "
            "in the Session 15 metadata."
        )

    selected_artifacts = [
        selected_decision_rows,
        selected_episode_rows,
        selected_summary_rows,
    ]

    for rows in selected_artifacts:
        for row in rows:
            subject = int(row["subject"])

            if subject not in thresholds_by_subject:
                raise RuntimeError(
                    "No expected threshold was found "
                    f"for subject {subject}."
                )

            actual_threshold = float(
                row["threshold_value"]
            )

            expected_threshold = (
                thresholds_by_subject[subject]
            )

            if not math.isclose(
                actual_threshold,
                expected_threshold,
                rel_tol=0.0,
                abs_tol=FLOAT_ABS_TOL,
            ):
                raise RuntimeError(
                    "Selected threshold value does "
                    "not match metadata for "
                    f"subject {subject}: "
                    f"{actual_threshold} vs "
                    f"{expected_threshold}."
                )

    return thresholds_by_subject


def validate_selected_summary_behavior(
    selected_summary_rows,
):
    """
    Confirm the run-level behavior used to select
    the v0.1 decision rule.
    """

    summary_rows_by_recording = {
        (
            int(row["subject"]),
            int(row["run"]),
        ): row
        for row in selected_summary_rows
    }

    if set(summary_rows_by_recording) != set(
        EXPECTED_BEHAVIOR_BY_RECORDING
    ):
        raise RuntimeError(
            "Selected summary recording keys do "
            "not match the expected recordings."
        )

    for recording_key, expected in (
        EXPECTED_BEHAVIOR_BY_RECORDING.items()
    ):
        row = summary_rows_by_recording[
            recording_key
        ]

        exact_checks = {
            "condition": expected["condition"],
            "first_active_command": expected[
                "first_active_command"
            ],
            "final_command_state": expected[
                "final_command_state"
            ],
            "unconfirmed_candidate_times_sec": (
                expected[
                    "unconfirmed_candidate_times_sec"
                ]
            ),
        }

        for field_name, expected_value in (
            exact_checks.items()
        ):
            actual_value = row[field_name]

            if actual_value != expected_value:
                raise RuntimeError(
                    "Selected summary mismatch for "
                    f"{recording_key}, {field_name}: "
                    f"{actual_value!r} vs "
                    f"{expected_value!r}."
                )

        integer_checks = {
            "active_switch_count": expected[
                "active_switch_count"
            ],
            "unconfirmed_candidate_update_count": (
                expected[
                    "unconfirmed_candidate_update_count"
                ]
            ),
            "low_evidence_count": expected[
                "low_evidence_count"
            ],
            "high_evidence_count": expected[
                "high_evidence_count"
            ],
            "command_episode_count": 2,
            "active_command_episode_count": 1,
            "short_active_command_episode_count": 0,
        }

        for field_name, expected_value in (
            integer_checks.items()
        ):
            actual_value = int(
                row[field_name]
            )

            if actual_value != expected_value:
                raise RuntimeError(
                    "Selected summary mismatch for "
                    f"{recording_key}, {field_name}: "
                    f"{actual_value} vs "
                    f"{expected_value}."
                )

        actual_first_active_time = float(
            row[
                "first_active_command_time_sec"
            ]
        )

        if not math.isclose(
            actual_first_active_time,
            expected[
                "first_active_command_time_sec"
            ],
            rel_tol=0.0,
            abs_tol=FLOAT_ABS_TOL,
        ):
            raise RuntimeError(
                "First active-command time mismatch "
                f"for {recording_key}: "
                f"{actual_first_active_time}."
            )

    return summary_rows_by_recording


def validate_selected_episode_behavior(
    selected_episode_rows,
):
    """
    Confirm the expected STOP and active-command
    episode boundaries for each recording.
    """

    episode_rows_by_recording = {}

    for row in selected_episode_rows:
        recording_key = (
            int(row["subject"]),
            int(row["run"]),
        )

        episode_rows_by_recording.setdefault(
            recording_key,
            [],
        ).append(row)

    if set(episode_rows_by_recording) != set(
        EXPECTED_BEHAVIOR_BY_RECORDING
    ):
        raise RuntimeError(
            "Selected episode recording keys do "
            "not match the expected recordings."
        )

    for recording_key, expected in (
        EXPECTED_BEHAVIOR_BY_RECORDING.items()
    ):
        rows = sorted(
            episode_rows_by_recording[
                recording_key
            ],
            key=lambda row: int(
                row["episode_index"]
            ),
        )

        if len(rows) != 2:
            raise RuntimeError(
                "Expected exactly two episodes "
                f"for {recording_key}."
            )

        stop_episode = rows[0]
        active_episode = rows[1]

        if (
            stop_episode["command_state"]
            != "CMD_STOP"
        ):
            raise RuntimeError(
                "Episode zero is not CMD_STOP for "
                f"{recording_key}."
            )

        if (
            active_episode["command_state"]
            != expected["active_command"]
        ):
            raise RuntimeError(
                "Active episode command mismatch "
                f"for {recording_key}."
            )

        time_checks = [
            (
                stop_episode[
                    "episode_start_time_sec"
                ],
                EXPECTED_RUN_START_TIME_SEC,
                "STOP start",
            ),
            (
                stop_episode[
                    "episode_end_time_sec"
                ],
                EXPECTED_FIRST_ACTIVE_TIME_SEC,
                "STOP end",
            ),
            (
                active_episode[
                    "episode_start_time_sec"
                ],
                EXPECTED_FIRST_ACTIVE_TIME_SEC,
                "active start",
            ),
            (
                active_episode[
                    "episode_end_time_sec"
                ],
                EXPECTED_RUN_END_TIME_SEC,
                "active end",
            ),
        ]

        for (
            actual_text,
            expected_value,
            label,
        ) in time_checks:
            actual_value = float(
                actual_text
            )

            if not math.isclose(
                actual_value,
                expected_value,
                rel_tol=0.0,
                abs_tol=FLOAT_ABS_TOL,
            ):
                raise RuntimeError(
                    f"{label} mismatch for "
                    f"{recording_key}: "
                    f"{actual_value} vs "
                    f"{expected_value}."
                )

        if (
            stop_episode[
                "start_event"
            ]
            != "run_start"
            or stop_episode[
                "end_event"
            ]
            != "initial_command_confirmed"
        ):
            raise RuntimeError(
                "Initial STOP episode events are "
                f"unexpected for {recording_key}."
            )

        if (
            active_episode[
                "start_event"
            ]
            != "initial_command_confirmed"
            or active_episode[
                "end_event"
            ]
            != "run_end"
        ):
            raise RuntimeError(
                "Active episode events are "
                f"unexpected for {recording_key}."
            )

    return episode_rows_by_recording


def validate_run1_candidate_event(
    selected_decision_rows,
):
    """
    Confirm the single unconfirmed HIGH_ALPHA
    candidate at 26 s in Subject 1, Run 1.
    """

    candidate_rows = [
        row
        for row in selected_decision_rows
        if (
            int(row["subject"]) == 1
            and int(row["run"]) == 1
            and int(row["candidate_count"]) > 0
            and row[
                "initial_command_confirmed"
            ] == "False"
            and row[
                "active_switch_confirmed"
            ] == "False"
            and row["command_state"]
            == "CMD_OPEN"
        )
    ]

    if len(candidate_rows) != 1:
        raise RuntimeError(
            "Expected exactly one unconfirmed "
            "Run 1 switch candidate, but found "
            f"{len(candidate_rows)}."
        )

    candidate_row = candidate_rows[0]

    if not math.isclose(
        float(
            candidate_row[
                "decision_time_sec"
            ]
        ),
        26.0,
        rel_tol=0.0,
        abs_tol=FLOAT_ABS_TOL,
    ):
        raise RuntimeError(
            "The Run 1 candidate did not occur "
            "at 26.0 s."
        )

    expected_values = {
        "evidence_state": "HIGH_ALPHA",
        "candidate_evidence_state": (
            "HIGH_ALPHA"
        ),
        "active_evidence_state": "LOW_ALPHA",
        "command_state": "CMD_OPEN",
    }

    for field_name, expected_value in (
        expected_values.items()
    ):
        actual_value = candidate_row[
            field_name
        ]

        if actual_value != expected_value:
            raise RuntimeError(
                "Run 1 candidate-row mismatch "
                f"for {field_name}: "
                f"{actual_value} vs "
                f"{expected_value}."
            )

    if int(
        candidate_row["candidate_count"]
    ) != 1:
        raise RuntimeError(
            "Run 1 candidate count is not 1."
        )

    return candidate_row


def save_frozen_decision_stream(
    selected_decision_rows,
    source_columns,
    output_path,
):
    """
    Save the validated selected-rule rows
    without recalculating any decision values.

    Rows are ordered by subject, run,
    and window index.
    """

    frozen_rows = sorted(
        selected_decision_rows,
        key=lambda row: (
            int(row["subject"]),
            int(row["run"]),
            int(row["window_index"]),
        ),
    )

    if len(frozen_rows) != (
        EXPECTED_SELECTED_STREAM_ROW_COUNT
    ):
        raise RuntimeError(
            "Frozen decision-stream row count "
            "does not match the expected value: "
            f"{len(frozen_rows)} vs "
            f"{EXPECTED_SELECTED_STREAM_ROW_COUNT}."
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
            fieldnames=source_columns,
            extrasaction="raise",
        )

        writer.writeheader()
        writer.writerows(
            frozen_rows
        )

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "Frozen decision-stream CSV was "
            "not saved correctly."
        )

    with open(
        output_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != source_columns:
            raise RuntimeError(
                "Frozen decision-stream header "
                "does not match the source header."
            )

        reloaded_rows = list(reader)

    if reloaded_rows != frozen_rows:
        raise RuntimeError(
            "Reloaded frozen decision rows do "
            "not exactly match the selected "
            "source rows."
        )

    return frozen_rows


def project_relative_path(
    path,
):
    """
    Return a repository-relative POSIX path
    for portable provenance records.
    """

    return path.relative_to(
        PROJECT_ROOT
    ).as_posix()


def parse_optional_float_list(
    value,
):
    """
    Convert a semicolon-separated optional
    numeric field to a JSON-compatible list.
    """

    text = str(value).strip()

    if not text:
        return []

    return [
        float(item.strip())
        for item in text.split(";")
        if item.strip()
    ]


def build_freeze_record(
    decision_rows,
    episode_rows,
    summary_rows,
    metadata,
    selected_configuration,
    selected_decision_rows,
    selected_episode_rows,
    selected_summary_rows,
    decision_recording_counts,
    thresholds_by_subject,
    summary_rows_by_recording,
    episode_rows_by_recording,
    frozen_decision_rows,
    decision_stream_columns,
):
    """
    Build the decision-rule v0.1 freeze record
    from already validated Session 15 artifacts.
    """

    decision_rule_ids = {
        row["rule_id"]
        for row in decision_rows
    }

    episode_rule_ids = {
        row["rule_id"]
        for row in episode_rows
    }

    summary_rule_ids = {
        row["rule_id"]
        for row in summary_rows
    }

    metadata_rule_id_list = [
        configuration["rule_id"]
        for configuration in metadata[
            "rule_set"
        ]["configurations"]
    ]

    metadata_rule_ids = set(
        metadata_rule_id_list
    )

    if not metadata_rule_ids:
        raise RuntimeError(
            "No rule configurations were found "
            "in the Session 15 metadata."
        )

    if len(metadata_rule_id_list) != len(
        metadata_rule_ids
    ):
        raise RuntimeError(
            "Session 15 metadata contain "
            "duplicate rule IDs."
        )

    artifact_rule_id_sets = [
        (
            "decision-stream CSV",
            decision_rule_ids,
        ),
        (
            "command-episode CSV",
            episode_rule_ids,
        ),
        (
            "rule-run summary CSV",
            summary_rule_ids,
        ),
    ]

    for artifact_name, rule_ids in (
        artifact_rule_id_sets
    ):
        if rule_ids != metadata_rule_ids:
            missing_rule_ids = sorted(
                metadata_rule_ids - rule_ids
            )

            unexpected_rule_ids = sorted(
                rule_ids - metadata_rule_ids
            )

            raise RuntimeError(
                f"{artifact_name} rule IDs do "
                "not match metadata. "
                f"Missing: {missing_rule_ids}. "
                "Unexpected: "
                f"{unexpected_rule_ids}."
            )

    available_rule_ids = sorted(
        metadata_rule_ids
    )

    behavior_by_recording = []

    for recording_key in sorted(
        summary_rows_by_recording
    ):
        subject, run = recording_key

        summary_row = (
            summary_rows_by_recording[
                recording_key
            ]
        )

        recording_episode_rows = sorted(
            episode_rows_by_recording[
                recording_key
            ],
            key=lambda row: int(
                row["episode_index"]
            ),
        )

        behavior_by_recording.append({
            "subject": subject,
            "run": run,
            "condition": (
                summary_row["condition"]
            ),
            "decision_row_count": (
                decision_recording_counts[
                    recording_key
                ]
            ),
            "first_active_command_time_sec": (
                float(
                    summary_row[
                        "first_active_command_time_sec"
                    ]
                )
            ),
            "first_active_command": (
                summary_row[
                    "first_active_command"
                ]
            ),
            "final_command_state": (
                summary_row[
                    "final_command_state"
                ]
            ),
            "active_switch_count": (
                int(
                    summary_row[
                        "active_switch_count"
                    ]
                )
            ),
            "unconfirmed_candidate_update_count": (
                int(
                    summary_row[
                        "unconfirmed_candidate_update_count"
                    ]
                )
            ),
            "unconfirmed_candidate_times_sec": (
                parse_optional_float_list(
                    summary_row[
                        "unconfirmed_candidate_times_sec"
                    ]
                )
            ),
            "evidence_counts": {
                "LOW_ALPHA": int(
                    summary_row[
                        "low_evidence_count"
                    ]
                ),
                "HIGH_ALPHA": int(
                    summary_row[
                        "high_evidence_count"
                    ]
                ),
            },
            "command_episode_count": (
                len(recording_episode_rows)
            ),
            "command_episode_states": [
                row["command_state"]
                for row in (
                    recording_episode_rows
                )
            ],
        })

    threshold_values_by_subject = [
        {
            "subject": subject,
            "threshold_value_v2_per_hz": (
                threshold_value
            ),
        }
        for subject, threshold_value in sorted(
            thresholds_by_subject.items()
        )
    ]

    freeze_record = {
        "artifact_type": (
            "decision_rule_freeze"
        ),
        "decision_rule_version": (
            FREEZE_VERSION
        ),
        "freeze_date": FREEZE_DATE,
        "freeze_status": FREEZE_STATUS,
        "source_session": 15,
        "freeze_session": 16,
        "source_artifacts": {
            "decision_stream_csv": {
                "path": project_relative_path(
                    SOURCE_DECISION_STREAM_CSV_PATH
                ),
                "row_count": len(
                    decision_rows
                ),
            },
            "command_episode_csv": {
                "path": project_relative_path(
                    SOURCE_COMMAND_EPISODE_CSV_PATH
                ),
                "row_count": len(
                    episode_rows
                ),
            },
            "rule_run_summary_csv": {
                "path": project_relative_path(
                    SOURCE_RULE_RUN_SUMMARY_CSV_PATH
                ),
                "row_count": len(
                    summary_rows
                ),
            },
            "metadata_json": {
                "path": project_relative_path(
                    SOURCE_METADATA_JSON_PATH
                ),
            },
        },
        "selected_rule": {
            "rule_id": SELECTED_RULE_ID,
            "threshold": {
                "threshold_id": (
                    selected_configuration[
                        "threshold_id"
                    ]
                ),
                "values_by_subject": (
                    threshold_values_by_subject
                ),
            },
            "smoothing": {
                "smoothing_id": (
                    selected_configuration[
                        "smoothing_id"
                    ]
                ),
            },
            "dwell": {
                "dwell_updates": int(
                    selected_configuration[
                        "dwell_updates"
                    ]
                ),
                "applies_to": [
                    (
                        "initial_command_"
                        "confirmation"
                    ),
                    (
                        "active_command_"
                        "switch"
                    ),
                ],
            },
            "state_mapping": {
                "LOW_ALPHA": "CMD_OPEN",
                "HIGH_ALPHA": "CMD_CLOSE",
                "UNAVAILABLE": "CMD_STOP",
            },
        },
        "selection_record": {
            "candidate_set_rule_count": (
                len(available_rule_ids)
            ),
            "basis": [
                (
                    "No active command switches "
                    "occurred in either recording."
                ),
                (
                    "Run 1 contained one "
                    "unconfirmed opposing "
                    "candidate at 26.0 s."
                ),
                (
                    "The initial active command "
                    "was confirmed at 3.0 s in "
                    "both recordings."
                ),
            ],
            "scope": (
                "Selected from the eight "
                "predefined Session 15 core "
                "configurations; this is not a "
                "global parameter optimum."
            ),
        },
        "validated_behavior_by_recording": (
            behavior_by_recording
        ),
        "regression_validation": {
            "source_artifacts_exist_and_nonempty": (
                True
            ),
            "source_row_counts_match_metadata": (
                True
            ),
            "selected_configuration_matches": (
                True
            ),
            "selected_behavior_matches": True,
            "selected_decision_row_count": (
                len(selected_decision_rows)
            ),
            "selected_episode_row_count": (
                len(selected_episode_rows)
            ),
            "selected_summary_row_count": (
                len(selected_summary_rows)
            ),
            "frozen_stream_reload_exact_match": (
                frozen_decision_rows
                == sorted(
                    selected_decision_rows,
                    key=lambda row: (
                        int(row["subject"]),
                        int(row["run"]),
                        int(
                            row["window_index"]
                        ),
                    ),
                )
            ),
            "recalculated_during_freeze": {
                "eeg_features": False,
                "thresholds": False,
                "smoothing": False,
                "evidence_states": False,
                "command_states": False,
            },
        },
        "frozen_output": {
            "decision_stream_csv": {
                "path": project_relative_path(
                    FROZEN_DECISION_STREAM_CSV_PATH
                ),
                "row_count": len(
                    frozen_decision_rows
                ),
                "column_count": len(
                    decision_stream_columns
                ),
                "row_order": [
                    "subject",
                    "run",
                    "window_index",
                ],
                "source_rows_copied_without_recalculation": (
                    True
                ),
            },
            "freeze_record_json": {
                "path": project_relative_path(
                    FROZEN_CONFIG_JSON_PATH
                ),
            },
        },
    }

    if not freeze_record[
        "regression_validation"
    ][
        "frozen_stream_reload_exact_match"
    ]:
        raise RuntimeError(
            "Frozen stream does not exactly "
            "match the validated selected rows."
        )

    return freeze_record


def save_freeze_record(
    freeze_record,
    output_path,
):
    """
    Save and reload the v0.1 freeze JSON,
    then confirm exact structural equality.
    """

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            freeze_record,
            file,
            indent=2,
            ensure_ascii=False,
        )

        file.write("\n")

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "Decision-rule freeze JSON was "
            "not saved correctly."
        )

    with open(
        output_path,
        "r",
        encoding="utf-8",
    ) as file:
        reloaded_record = json.load(file)

    if reloaded_record != freeze_record:
        raise RuntimeError(
            "Reloaded freeze JSON does not "
            "match the generated freeze record."
        )

    return reloaded_record


def main():
    source_paths = validate_source_paths()

    (
        decision_stream_columns,
        decision_rows,
    ) = load_csv_rows(
        csv_path=(
            SOURCE_DECISION_STREAM_CSV_PATH
        ),
        required_columns=(
            REQUIRED_DECISION_STREAM_COLUMNS
        ),
    )

    (
        command_episode_columns,
        episode_rows,
    ) = load_csv_rows(
        csv_path=(
            SOURCE_COMMAND_EPISODE_CSV_PATH
        ),
        required_columns=(
            REQUIRED_COMMAND_EPISODE_COLUMNS
        ),
    )

    (
        rule_run_summary_columns,
        summary_rows,
    ) = load_csv_rows(
        csv_path=(
            SOURCE_RULE_RUN_SUMMARY_CSV_PATH
        ),
        required_columns=(
            REQUIRED_RULE_RUN_SUMMARY_COLUMNS
        ),
    )

    metadata = load_metadata(
        json_path=SOURCE_METADATA_JSON_PATH,
    )

    validate_source_row_counts(
        decision_rows=decision_rows,
        episode_rows=episode_rows,
        summary_rows=summary_rows,
        metadata=metadata,
    )

    selected_decision_rows = (
        select_rule_rows(
            rows=decision_rows,
            artifact_name=(
                "decision-stream CSV"
            ),
        )
    )

    selected_episode_rows = (
        select_rule_rows(
            rows=episode_rows,
            artifact_name=(
                "command-episode CSV"
            ),
        )
    )

    selected_summary_rows = (
        select_rule_rows(
            rows=summary_rows,
            artifact_name=(
                "rule-run summary CSV"
            ),
        )
    )

    selected_configuration = (
        validate_selected_rule_metadata(
            metadata=metadata,
        )
    )

    decision_recording_counts = (
        validate_selected_rule_rows(
            selected_decision_rows=(
                selected_decision_rows
            ),
            selected_episode_rows=(
                selected_episode_rows
            ),
            selected_summary_rows=(
                selected_summary_rows
            ),
        )
    )

    thresholds_by_subject = (
        validate_selected_threshold(
            selected_decision_rows=(
                selected_decision_rows
            ),
            selected_episode_rows=(
                selected_episode_rows
            ),
            selected_summary_rows=(
                selected_summary_rows
            ),
            metadata=metadata,
        )
    )

    summary_rows_by_recording = (
        validate_selected_summary_behavior(
            selected_summary_rows=(
                selected_summary_rows
            ),
        )
    )

    episode_rows_by_recording = (
        validate_selected_episode_behavior(
            selected_episode_rows=(
                selected_episode_rows
            ),
        )
    )

    run1_candidate_row = (
        validate_run1_candidate_event(
            selected_decision_rows=(
                selected_decision_rows
            ),
        )
    )

    print("\n========================================")
    print(
        "Session 16 Step 3: "
        "Selected-rule behavior validation"
    )

    print(
        "Selected rule ID:",
        SELECTED_RULE_ID,
    )

    print(
        "Source artifact count:",
        len(source_paths),
    )

    print(
        "Source decision-stream rows:",
        len(decision_rows),
    )

    print(
        "Source command-episode rows:",
        len(episode_rows),
    )

    print(
        "Source rule-run summary rows:",
        len(summary_rows),
    )

    print(
        "Selected decision-stream rows:",
        len(selected_decision_rows),
    )

    print(
        "Selected command-episode rows:",
        len(selected_episode_rows),
    )

    print(
        "Selected rule-run summary rows:",
        len(selected_summary_rows),
    )

    print(
        "Selected threshold ID:",
        selected_configuration[
            "threshold_id"
        ],
    )

    print(
        "Selected smoothing ID:",
        selected_configuration[
            "smoothing_id"
        ],
    )

    print(
        "Selected dwell updates:",
        selected_configuration[
            "dwell_updates"
        ],
    )

    print(
        "Decision-stream column count:",
        len(decision_stream_columns),
    )

    print(
        "Command-episode column count:",
        len(command_episode_columns),
    )

    print(
        "Rule-run summary column count:",
        len(rule_run_summary_columns),
    )

    for (
        subject,
        run,
    ), row_count in sorted(
        decision_recording_counts.items()
    ):
        print(
            "Selected recording:",
            f"subject {subject}, run {run}, "
            f"rows {row_count}",
        )
    for subject, threshold_value in sorted(
        thresholds_by_subject.items()
    ):
        print(
            "Validated midpoint threshold:",
            f"subject {subject}, "
            f"{threshold_value:.12e}",
        )

    print(
        "Validated summary recordings:",
        len(summary_rows_by_recording),
    )

    print(
        "Validated episode recordings:",
        len(episode_rows_by_recording),
    )

    print(
        "Validated Run 1 candidate time:",
        run1_candidate_row[
            "decision_time_sec"
        ],
        "s",
    )
    
    print(
        "\nSelected-rule behavior "
        "validation completed."
    )

    frozen_decision_rows = (
        save_frozen_decision_stream(
            selected_decision_rows=(
                selected_decision_rows
            ),
            source_columns=(
                decision_stream_columns
            ),
            output_path=(
                FROZEN_DECISION_STREAM_CSV_PATH
            ),
        )
    )

    print("\n========================================")
    print(
        "Session 16 Step 4: "
        "Frozen decision-stream output"
    )

    print(
        "Output CSV:",
        FROZEN_DECISION_STREAM_CSV_PATH,
    )

    print(
        "Frozen rule ID:",
        SELECTED_RULE_ID,
    )

    print(
        "Saved row count:",
        len(frozen_decision_rows),
    )

    print(
        "Saved column count:",
        len(decision_stream_columns),
    )

    print(
        "\nFrozen decision-stream CSV "
        "validation completed."
    )

    freeze_record = build_freeze_record(
        decision_rows=decision_rows,
        episode_rows=episode_rows,
        summary_rows=summary_rows,
        metadata=metadata,
        selected_configuration=(
            selected_configuration
        ),
        selected_decision_rows=(
            selected_decision_rows
        ),
        selected_episode_rows=(
            selected_episode_rows
        ),
        selected_summary_rows=(
            selected_summary_rows
        ),
        decision_recording_counts=(
            decision_recording_counts
        ),
        thresholds_by_subject=(
            thresholds_by_subject
        ),
        summary_rows_by_recording=(
            summary_rows_by_recording
        ),
        episode_rows_by_recording=(
            episode_rows_by_recording
        ),
        frozen_decision_rows=(
            frozen_decision_rows
        ),
        decision_stream_columns=(
            decision_stream_columns
        ),
    )

    reloaded_freeze_record = (
        save_freeze_record(
            freeze_record=freeze_record,
            output_path=(
                FROZEN_CONFIG_JSON_PATH
            ),
        )
    )

    print("\n========================================")
    print(
        "Session 16 Step 5: "
        "Decision-rule v0.1 freeze record"
    )

    print(
        "Output JSON:",
        FROZEN_CONFIG_JSON_PATH,
    )

    print(
        "Decision-rule version:",
        reloaded_freeze_record[
            "decision_rule_version"
        ],
    )

    print(
        "Freeze status:",
        reloaded_freeze_record[
            "freeze_status"
        ],
    )

    print(
        "Validated recording count:",
        len(
            reloaded_freeze_record[
                "validated_behavior_by_recording"
            ]
        ),
    )

    print(
        "Frozen stream rows:",
        reloaded_freeze_record[
            "frozen_output"
        ][
            "decision_stream_csv"
        ][
            "row_count"
        ],
    )

    print(
        "\nDecision-rule v0.1 freeze "
        "record validation completed."
    )

if __name__ == "__main__":
    main()