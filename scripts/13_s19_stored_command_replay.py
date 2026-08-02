"""Validate the frozen Session 16 command stream and execute Session 19 replay stages.

The selected execution mode controls hardware access and command transmission.
"""

import csv
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

from bci_robot.serial_client import SerialClient
from bci_robot.serial_protocol import (
    AckMessage,
    ReadyMessage,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SESSION16_RESULTS_DIR = PROJECT_ROOT / "results" / "session-16"

SOURCE_STREAM_CSV_PATH = (
    SESSION16_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_decision-rule-v0.1-stream.csv"
    )
)

FREEZE_RECORD_JSON_PATH = (
    SESSION16_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_decision-rule-v0.1.json"
    )
)

SESSION19_RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
    / "session-19"
)

REPLAY_EVENT_LOG_CSV_PATH = (
    SESSION19_RESULTS_DIR
    / "session19_source-linked_replay_event_log.csv"
)

REPLAY_SUMMARY_CSV_PATH = (
    SESSION19_RESULTS_DIR
    / "session19_recording_replay_summary.csv"
)

EXPECTED_RULE_ID = "thr-gap-mid__smooth-none__dwell-2"
EXPECTED_CONFIGURATION_ID = "win-2s_step-1s"
EXPECTED_THRESHOLD_ID = "threshold_gap_midpoint"
EXPECTED_SMOOTHING_ID = "smooth-none"
EXPECTED_DWELL_UPDATES = 2
EXPECTED_DECISION_STEP_SEC = 1.0
FLOAT_ABS_TOL = 1e-9

COMMAND_TO_SERIAL = {
    "CMD_OPEN": "OPEN",
    "CMD_CLOSE": "CLOSE",
    "CMD_STOP": "STOP",
}

EXPECTED_PROTOCOL_VERSION = "S18_V0.1"
EXPECTED_STARTUP_MODE = "STOP"
EXPECTED_STARTUP_ANGLE_DEG = 90

PORT = "COM4"
BAUD_RATE = 9600
READY_TIMEOUT_S = 3.0
RESPONSE_TIMEOUT_S = 1.0
READ_TIMEOUT_S = 0.1

STARTUP_SETTLE_WAIT_S = 1.0
POST_REPLAY_OBSERVATION_WAIT_S = 1.0

ACTUATOR_MIN_ANGLE_DEG = 60
ACTUATOR_MAX_ANGLE_DEG = 120

EXECUTION_MODE = "validation_only"

VALID_EXECUTION_MODES = {
    "validation_only",
    "ready_smoke_test",
    "actual_replay_run1",
    "actual_replay_run2",
    "actual_replay_all",
}

DIRECTIONAL_MODES = {
    "OPEN",
    "CLOSE",
}

REQUIRED_COLUMNS = {
    "rule_id",
    "subject",
    "run",
    "condition",
    "configuration_id",
    "window_index",
    "window_start_sec",
    "window_end_sec",
    "decision_time_sec",
    "threshold_id",
    "smoothing_id",
    "dwell_updates",
    "initial_command_confirmed",
    "active_switch_confirmed",
    "command_state",
}


@dataclass(frozen=True)
class ReplayEvent:
    source_event_id: str
    subject: int
    run: int
    condition: str
    window_index: int
    source_decision_time_sec: float
    scheduled_replay_elapsed_sec: float
    command_state: str
    serial_command: str
    expected_ack_result: str
    expected_actuator_mode: str
    selection_reason: str


@dataclass(frozen=True)
class SchedulerDryRunResult:
    source_event_id: str
    subject: int
    run: int
    scheduled_replay_elapsed_sec: float
    actual_replay_elapsed_sec: float
    schedule_offset_ms: float
    serial_command: str
    expected_ack_result: str
    expected_actuator_mode: str


@dataclass(frozen=True)
class ReplayRunPlan:
    replay_run_id: str
    subject: int
    run: int
    condition: str
    expected_protocol_version: str
    expected_startup_mode: str
    expected_startup_angle_deg: int
    events: tuple[ReplayEvent, ...]


@dataclass(frozen=True)
class ReadySmokeTestResult:
    replay_run_id: str
    protocol_version: str
    actuator_mode: str
    commanded_angle_deg: int
    serial_event_count: int
    tx_command_count: int
    status: str


@dataclass(frozen=True)
class ActualReplayEventResult:
    replay_run_id: str
    subject: int
    run: int
    condition: str
    source_event_id: str
    window_index: int
    command_state: str
    selection_reason: str
    command_seq: int
    source_decision_time_sec: float
    scheduled_replay_elapsed_sec: float
    actual_tx_elapsed_sec: float
    ack_received_elapsed_sec: float
    ack_round_trip_ms: float
    schedule_offset_ms: float
    serial_command: str
    expected_ack_result: str
    observed_ack_result: str
    expected_actuator_mode: str
    observed_actuator_mode: str
    observed_commanded_angle_deg: int
    status: str


@dataclass(frozen=True)
class ActualReplayRunResult:
    replay_run_id: str
    subject: int
    run: int
    condition: str
    ready_protocol_version: str
    ready_actuator_mode: str
    ready_commanded_angle_deg: int
    planned_event_count: int
    completed_event_count: int
    pass_count: int
    fail_count: int
    max_abs_schedule_offset_ms: float
    final_observed_actuator_mode: str
    final_observed_commanded_angle_deg: int
    startup_settle_wait_s: float
    post_replay_observation_wait_s: float
    status: str
    event_results: tuple[ActualReplayEventResult, ...]


def determine_expected_ack_result(
    current_mode: str,
    serial_command: str,
) -> str:
    """
    Determine the expected Session 18 ACK result
    from the current expected actuator mode and
    the next serial command.
    """

    valid_modes = {
        "STOP",
        "OPEN",
        "CLOSE",
    }

    if current_mode not in valid_modes:
        raise ValueError(
            "Unexpected current actuator mode: "
            f"{current_mode!r}"
        )

    if serial_command not in valid_modes:
        raise ValueError(
            "Unexpected serial command: "
            f"{serial_command!r}"
        )

    if serial_command == current_mode:
        return "DUPLICATE"

    if (
        current_mode in DIRECTIONAL_MODES
        and serial_command in DIRECTIONAL_MODES
    ):
        return "REVERSED"

    return "APPLIED"


def parse_bool(value: str, field_name: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False

    raise ValueError(
        f"Unexpected boolean value for {field_name}: {value!r}"
    )


def clean_timing_value(
    value: float,
    decimal_places: int = 3,
) -> float:
    """
    Round a host-side timing value for stable
    terminal and CSV representation.

    Negative zero is normalized to positive zero.
    """

    rounded_value = round(
        value,
        decimal_places,
    )

    if rounded_value == 0.0:
        return 0.0

    return rounded_value


def load_and_validate_freeze_record() -> dict:
    if not FREEZE_RECORD_JSON_PATH.exists():
        raise FileNotFoundError(
            "Freeze record JSON was not found:\n"
            f"{FREEZE_RECORD_JSON_PATH}"
        )

    with FREEZE_RECORD_JSON_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        freeze_record = json.load(file)

    top_level_checks = {
        "artifact_type": "decision_rule_freeze",
        "decision_rule_version": "v0.1",
        "freeze_status": "frozen",
    }

    for field_name, expected_value in top_level_checks.items():
        actual_value = freeze_record.get(field_name)
        if actual_value != expected_value:
            raise RuntimeError(
                f"Freeze record mismatch for {field_name}: "
                f"{actual_value!r} vs {expected_value!r}."
            )

    selected_rule = freeze_record["selected_rule"]
    selected_checks = {
        "rule_id": selected_rule["rule_id"],
        "threshold_id": selected_rule["threshold"]["threshold_id"],
        "smoothing_id": selected_rule["smoothing"]["smoothing_id"],
        "dwell_updates": selected_rule["dwell"]["dwell_updates"],
    }
    expected_selected = {
        "rule_id": EXPECTED_RULE_ID,
        "threshold_id": EXPECTED_THRESHOLD_ID,
        "smoothing_id": EXPECTED_SMOOTHING_ID,
        "dwell_updates": EXPECTED_DWELL_UPDATES,
    }

    if selected_checks != expected_selected:
        raise RuntimeError(
            "Selected rule does not match the Session 19 input "
            f"specification:\n{selected_checks}"
        )

    return freeze_record


def load_and_validate_stream(
    freeze_record: dict,
) -> list[dict]:
    if not SOURCE_STREAM_CSV_PATH.exists():
        raise FileNotFoundError(
            "Frozen decision stream was not found:\n"
            f"{SOURCE_STREAM_CSV_PATH}"
        )

    with SOURCE_STREAM_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "Frozen decision stream has no header."
            )

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing_columns:
            raise RuntimeError(
                "Frozen decision stream is missing required columns: "
                f"{sorted(missing_columns)}"
            )

        source_rows = list(reader)

    frozen_output = freeze_record["frozen_output"]["decision_stream_csv"]

    if len(source_rows) != int(frozen_output["row_count"]):
        raise RuntimeError(
            "CSV row count does not match the freeze record."
        )

    if len(reader.fieldnames) != int(frozen_output["column_count"]):
        raise RuntimeError(
            "CSV column count does not match the freeze record."
        )

    fixed_values = {
        "rule_id": EXPECTED_RULE_ID,
        "configuration_id": EXPECTED_CONFIGURATION_ID,
        "threshold_id": EXPECTED_THRESHOLD_ID,
        "smoothing_id": EXPECTED_SMOOTHING_ID,
        "dwell_updates": str(EXPECTED_DWELL_UPDATES),
    }

    for field_name, expected_value in fixed_values.items():
        observed_values = {
            row[field_name] for row in source_rows
        }
        if observed_values != {expected_value}:
            raise RuntimeError(
                f"Unexpected values in {field_name}: "
                f"{sorted(observed_values)}"
            )

    parsed_rows = []
    seen_keys = set()

    for source_row in source_rows:
        command_state = source_row["command_state"]
        if command_state not in COMMAND_TO_SERIAL:
            raise ValueError(
                f"Unexpected command_state: {command_state!r}"
            )

        row = {
            "subject": int(source_row["subject"]),
            "run": int(source_row["run"]),
            "condition": source_row["condition"],
            "window_index": int(source_row["window_index"]),
            "window_start_sec": float(source_row["window_start_sec"]),
            "window_end_sec": float(source_row["window_end_sec"]),
            "decision_time_sec": float(source_row["decision_time_sec"]),
            "initial_command_confirmed": parse_bool(
                source_row["initial_command_confirmed"],
                "initial_command_confirmed",
            ),
            "active_switch_confirmed": parse_bool(
                source_row["active_switch_confirmed"],
                "active_switch_confirmed",
            ),
            "command_state": command_state,
        }

        row_key = (
            row["subject"],
            row["run"],
            row["window_index"],
        )
        if row_key in seen_keys:
            raise RuntimeError(
                f"Duplicate source row key: {row_key}"
            )
        seen_keys.add(row_key)

        if not math.isclose(
            row["decision_time_sec"],
            row["window_end_sec"],
            rel_tol=0.0,
            abs_tol=FLOAT_ABS_TOL,
        ):
            raise RuntimeError(
                "decision_time_sec does not match window_end_sec "
                f"for {row_key}."
            )

        parsed_rows.append(row)

    expected_order = sorted(
        parsed_rows,
        key=lambda row: (
            row["subject"],
            row["run"],
            row["window_index"],
        ),
    )
    if parsed_rows != expected_order:
        raise RuntimeError(
            "Frozen stream row order is not subject, run, window_index."
        )

    return parsed_rows


def group_and_validate_recordings(
    rows: list[dict],
) -> dict[tuple[int, int], list[dict]]:
    grouped_rows: dict[tuple[int, int], list[dict]] = {}

    for row in rows:
        key = (row["subject"], row["run"])
        grouped_rows.setdefault(key, []).append(row)

    for key, recording_rows in grouped_rows.items():
        conditions = {
            row["condition"] for row in recording_rows
        }
        if len(conditions) != 1:
            raise RuntimeError(
                f"Multiple conditions were found for {key}."
            )

        window_indices = [
            row["window_index"] for row in recording_rows
        ]
        if window_indices != list(range(len(recording_rows))):
            raise RuntimeError(
                f"Invalid window-index sequence for {key}."
            )

        decision_times = [
            row["decision_time_sec"] for row in recording_rows
        ]
        for previous_time, current_time in zip(
            decision_times[:-1],
            decision_times[1:],
        ):
            if not math.isclose(
                current_time - previous_time,
                EXPECTED_DECISION_STEP_SEC,
                rel_tol=0.0,
                abs_tol=FLOAT_ABS_TOL,
            ):
                raise RuntimeError(
                    f"Unexpected decision-time step for {key}."
                )

    return grouped_rows


def build_replay_plan(
    grouped_rows: dict[tuple[int, int], list[dict]],
) -> list[ReplayEvent]:
    replay_events = []

    for (subject, run), recording_rows in sorted(
        grouped_rows.items()
    ):
        selected_rows = []

        for index, row in enumerate(recording_rows):
            if index == 0:
                selected_rows.append(
                    (row, "recording_first_row")
                )
            elif (
                row["command_state"]
                != recording_rows[index - 1]["command_state"]
            ):
                selected_rows.append(
                    (row, "command_state_change")
                )

        first_source_time_sec = selected_rows[0][0][
            "decision_time_sec"
        ]

        expected_mode = EXPECTED_STARTUP_MODE

        for row, selection_reason in selected_rows:
            serial_command = COMMAND_TO_SERIAL[
                row["command_state"]
            ]

            expected_ack_result = (
                determine_expected_ack_result(
                    current_mode=expected_mode,
                    serial_command=serial_command,
                )
            )

            expected_actuator_mode = (
                serial_command
            )

            replay_events.append(
                ReplayEvent(
                    source_event_id=(
                        f"S{subject:03d}-R{run:02d}-"
                        f"W{row['window_index']:03d}"
                    ),
                    subject=subject,
                    run=run,
                    condition=row["condition"],
                    window_index=row["window_index"],
                    source_decision_time_sec=row[
                        "decision_time_sec"
                    ],
                    scheduled_replay_elapsed_sec=(
                        row["decision_time_sec"]
                        - first_source_time_sec
                    ),
                    command_state=row["command_state"],
                    serial_command=serial_command,
                    expected_ack_result=(
                        expected_ack_result
                    ),
                    expected_actuator_mode=(
                        expected_actuator_mode
                    ),
                    selection_reason=selection_reason,
                )
            )

            expected_mode = (
                expected_actuator_mode
            )

    return replay_events


def validate_replay_plan(
    replay_events: list[ReplayEvent],
    freeze_record: dict,
) -> None:
    behavior_by_recording = {
        (int(item["subject"]), int(item["run"])): item
        for item in freeze_record["validated_behavior_by_recording"]
    }

    freeze_recording_keys = set(
        behavior_by_recording
    )

    replay_recording_keys = {
        (event.subject, event.run)
        for event in replay_events
    }

    if replay_recording_keys != freeze_recording_keys:
        missing_recordings = (
            freeze_recording_keys
            - replay_recording_keys
        )

        unexpected_recordings = (
            replay_recording_keys
            - freeze_recording_keys
        )

        raise RuntimeError(
            "Replay/freeze recording-key mismatch: "
            f"missing={sorted(missing_recordings)}; "
            f"unexpected={sorted(unexpected_recordings)}."
        )

    for key, behavior in behavior_by_recording.items():
        events = [
            event
            for event in replay_events
            if (event.subject, event.run) == key
        ]

        expected_count = 2 + int(behavior["active_switch_count"])
        if len(events) != expected_count:
            raise RuntimeError(
                f"Unexpected replay-event count for {key}: "
                f"{len(events)} vs {expected_count}."
            )

        if events[0].command_state != "CMD_STOP":
            raise RuntimeError(
                f"First replay event is not CMD_STOP for {key}."
            )

        if events[1].command_state != behavior[
            "first_active_command"
        ]:
            raise RuntimeError(
                f"First active command mismatch for {key}."
            )

        if not math.isclose(
            events[0].scheduled_replay_elapsed_sec,
            0.0,
            rel_tol=0.0,
            abs_tol=FLOAT_ABS_TOL,
        ):
            raise RuntimeError(
                f"First replay event is not scheduled at 0 s for {key}."
            )

        expected_mode = (
            EXPECTED_STARTUP_MODE
        )

        for event in events:
            recalculated_result = (
                determine_expected_ack_result(
                    current_mode=expected_mode,
                    serial_command=(
                        event.serial_command
                    ),
                )
            )

            if (
                event.expected_ack_result
                != recalculated_result
            ):
                raise RuntimeError(
                    "Expected ACK result mismatch "
                    f"for {event.source_event_id}: "
                    f"{event.expected_ack_result} "
                    f"vs {recalculated_result}."
                )

            if (
                event.expected_actuator_mode
                != event.serial_command
            ):
                raise RuntimeError(
                    "Expected actuator mode does "
                    "not match the serial command "
                    f"for {event.source_event_id}."
                )

            expected_mode = (
                event.expected_actuator_mode
            )


def build_replay_run_plans(
    replay_events: list[ReplayEvent],
) -> list[ReplayRunPlan]:
    """
    Group replay events into independent
    per-recording execution plans.
    """

    recording_keys = sorted({
        (event.subject, event.run)
        for event in replay_events
    })

    run_plans = []

    for subject, run in recording_keys:
        events = tuple(
            sorted(
                [
                    event
                    for event in replay_events
                    if (
                        event.subject == subject
                        and event.run == run
                    )
                ],
                key=lambda event: (
                    event.scheduled_replay_elapsed_sec
                ),
            )
        )

        if not events:
            raise RuntimeError(
                "No replay events were found for "
                f"Subject {subject}, Run {run}."
            )

        conditions = {
            event.condition
            for event in events
        }

        if len(conditions) != 1:
            raise RuntimeError(
                "Multiple conditions were found in "
                f"the replay plan for Subject "
                f"{subject}, Run {run}."
            )

        run_plans.append(
            ReplayRunPlan(
                replay_run_id=(
                    f"S19-S{subject:03d}-R{run:02d}"
                ),
                subject=subject,
                run=run,
                condition=next(iter(conditions)),
                expected_protocol_version=(
                    EXPECTED_PROTOCOL_VERSION
                ),
                expected_startup_mode=(
                    EXPECTED_STARTUP_MODE
                ),
                expected_startup_angle_deg=(
                    EXPECTED_STARTUP_ANGLE_DEG
                ),
                events=events,
            )
        )

    return run_plans


def validate_replay_run_plans(
    run_plans: list[ReplayRunPlan],
) -> None:
    """
    Validate recording-level execution
    boundaries and startup expectations.
    """

    if not run_plans:
        raise RuntimeError(
            "No replay run plans were created."
        )

    replay_run_ids = [
        plan.replay_run_id
        for plan in run_plans
    ]

    if len(replay_run_ids) != len(
        set(replay_run_ids)
    ):
        raise RuntimeError(
            "Duplicate replay_run_id values "
            "were created."
        )

    for plan in run_plans:
        if (
            plan.expected_protocol_version
            != EXPECTED_PROTOCOL_VERSION
        ):
            raise RuntimeError(
                "Unexpected protocol version in "
                f"{plan.replay_run_id}."
            )

        if (
            plan.expected_startup_mode
            != EXPECTED_STARTUP_MODE
        ):
            raise RuntimeError(
                "Unexpected startup mode in "
                f"{plan.replay_run_id}."
            )

        if (
            plan.expected_startup_angle_deg
            != EXPECTED_STARTUP_ANGLE_DEG
        ):
            raise RuntimeError(
                "Unexpected startup angle in "
                f"{plan.replay_run_id}."
            )

        if not plan.events:
            raise RuntimeError(
                "Replay run contains no events: "
                f"{plan.replay_run_id}."
            )

        first_event = plan.events[0]

        if not math.isclose(
            first_event.scheduled_replay_elapsed_sec,
            0.0,
            rel_tol=0.0,
            abs_tol=FLOAT_ABS_TOL,
        ):
            raise RuntimeError(
                "First event is not scheduled "
                "at replay time zero for "
                f"{plan.replay_run_id}."
            )

        if first_event.serial_command != "STOP":
            raise RuntimeError(
                "First serial command is not STOP "
                f"for {plan.replay_run_id}."
            )

        for event in plan.events:
            if (
                event.subject != plan.subject
                or event.run != plan.run
                or event.condition != plan.condition
            ):
                raise RuntimeError(
                    "A replay event does not match "
                    "its recording-level plan: "
                    f"{event.source_event_id}."
                )


def print_replay_plan(
    rows: list[dict],
    replay_events: list[ReplayEvent],
) -> None:
    recording_keys = sorted({
        (row["subject"], row["run"]) for row in rows
    })

    print("\n========================================")
    print("Session 19 Step 1: Replay-plan validation")
    print("Source row count:", len(rows))
    print("Recording count:", len(recording_keys))
    print("Selected replay event count:", len(replay_events))

    for key in recording_keys:
        recording_rows = [
            row
            for row in rows
            if (row["subject"], row["run"]) == key
        ]
        events = [
            event
            for event in replay_events
            if (event.subject, event.run) == key
        ]

        print("\n----------------------------------------")
        print(f"Subject {key[0]}, Run {key[1]}")
        print("Condition:", recording_rows[0]["condition"])
        print("Source row count:", len(recording_rows))
        print("Selected event count:", len(events))
        print(
            "Omitted stable row count:",
            len(recording_rows) - len(events),
        )

        for event in events:
            print(
                f"{event.scheduled_replay_elapsed_sec:>4.1f} s"
                f" | source={event.source_decision_time_sec:>4.1f} s"
                f" | {event.source_event_id}"
                f" | {event.command_state}"
                f" -> {event.serial_command}"
                " | expected_ack="
                f"{event.expected_ack_result}"
                "/"
                f"{event.expected_actuator_mode}"
                f" | {event.selection_reason}"
            )

    print("\nReplay-plan validation completed.")
    print(
        "No serial port was opened during "
        "replay-plan validation."
    )


def run_scheduler_dry_run(
    replay_events: list[ReplayEvent],
) -> list[SchedulerDryRunResult]:
    """
    Execute the replay timing plan without
    opening a serial port.

    Each recording receives an independent
    monotonic-clock origin.
    """

    results = []

    recording_keys = sorted({
        (event.subject, event.run)
        for event in replay_events
    })

    print("\n========================================")
    print(
        "Session 19 Step 2: "
        "Monotonic scheduler dry run"
    )

    for subject, run in recording_keys:
        recording_events = sorted(
            [
                event
                for event in replay_events
                if (
                    event.subject == subject
                    and event.run == run
                )
            ],
            key=lambda event: (
                event.scheduled_replay_elapsed_sec
            ),
        )

        if not recording_events:
            raise RuntimeError(
                "No replay events were found for "
                f"Subject {subject}, Run {run}."
            )

        replay_start_monotonic = (
            time.monotonic()
        )

        print("\n----------------------------------------")
        print(
            f"Subject {subject}, Run {run}"
        )

        for event in recording_events:
            target_monotonic = (
                replay_start_monotonic
                + event.scheduled_replay_elapsed_sec
            )

            remaining_sec = (
                target_monotonic
                - time.monotonic()
            )

            if remaining_sec > 0.0:
                time.sleep(
                    remaining_sec
                )

            actual_replay_elapsed_sec = (
                time.monotonic()
                - replay_start_monotonic
            )

            schedule_offset_ms = (
                (
                    actual_replay_elapsed_sec
                    - event.scheduled_replay_elapsed_sec
                )
                * 1000.0
            )

            result = SchedulerDryRunResult(
                source_event_id=(
                    event.source_event_id
                ),
                subject=subject,
                run=run,
                scheduled_replay_elapsed_sec=(
                    event.scheduled_replay_elapsed_sec
                ),
                actual_replay_elapsed_sec=(
                    actual_replay_elapsed_sec
                ),
                schedule_offset_ms=(
                    schedule_offset_ms
                ),
                serial_command=(
                    event.serial_command
                ),
                expected_ack_result=(
                    event.expected_ack_result
                ),
                expected_actuator_mode=(
                    event.expected_actuator_mode
                ),
            )

            results.append(
                result
            )

            print(
                "scheduled="
                f"{result.scheduled_replay_elapsed_sec:>5.3f} s"
                " | actual="
                f"{result.actual_replay_elapsed_sec:>5.3f} s"
                " | offset="
                f"{result.schedule_offset_ms:+8.3f} ms"
                f" | {result.source_event_id}"
                " | would_send="
                f"{result.serial_command}"
                " | expected_ack="
                f"{result.expected_ack_result}"
                "/"
                f"{result.expected_actuator_mode}"
            )

    if len(results) != len(
        replay_events
    ):
        raise RuntimeError(
            "Scheduler dry-run result count "
            "does not match the replay-event count: "
            f"{len(results)} vs {len(replay_events)}."
        )

    print(
        "\nScheduler dry run completed."
    )

    print(
        "No serial port was opened."
    )

    return results


def print_replay_run_plans(
    run_plans: list[ReplayRunPlan],
) -> None:
    """
    Print recording-level execution boundaries
    without opening a serial port.
    """

    print("\n========================================")
    print(
        "Session 19 Step 3: "
        "Recording execution boundaries"
    )

    print(
        "Replay run count:",
        len(run_plans),
    )

    for plan in run_plans:
        print("\n----------------------------------------")

        print(
            "Replay run ID:",
            plan.replay_run_id,
        )

        print(
            "Source recording:",
            f"Subject {plan.subject}, "
            f"Run {plan.run}",
        )

        print(
            "Condition:",
            plan.condition,
        )

        print(
            "Expected READY:",
            (
                f"{plan.expected_protocol_version},"
                f"{plan.expected_startup_mode},"
                f"{plan.expected_startup_angle_deg}"
            ),
        )

        print(
            "Fresh SerialClient per recording:",
            "required",
        )

        print(
            "Replay event count:",
            len(plan.events),
        )

        print(
            "Replay events:",
            " -> ".join(
                event.serial_command
                for event in plan.events
            ),
        )

    print(
        "\nRecording execution-boundary "
        "validation completed."
    )

    print(
        "No serial port was opened during "
        "execution-boundary validation."
    )


def run_ready_smoke_tests(
    run_plans: list[ReplayRunPlan],
) -> list[ReadySmokeTestResult]:
    """
    Open one fresh serial connection per
    recording and validate the startup READY
    message without transmitting commands.
    """

    results = []

    print("\n========================================")
    print(
        "Session 19 Step 4: "
        "READY startup smoke test"
    )

    for plan in run_plans:
        print("\n----------------------------------------")
        print(
            "Opening serial for:",
            plan.replay_run_id,
        )

        client = SerialClient(
            port=PORT,
            baud_rate=BAUD_RATE,
            response_timeout_s=(
                RESPONSE_TIMEOUT_S
            ),
            read_timeout_s=READ_TIMEOUT_S,
        )

        try:
            client.open()

            ready_message = client.wait_ready(
                timeout_s=READY_TIMEOUT_S,
                case_id=(
                    f"{plan.replay_run_id}-READY"
                ),
            )

            if not isinstance(
                ready_message,
                ReadyMessage,
            ):
                raise RuntimeError(
                    "Startup response is not a "
                    "ReadyMessage."
                )

            if len(client.events) != 1:
                raise RuntimeError(
                    "Expected exactly one serial "
                    "event after READY, but observed "
                    f"{len(client.events)} for "
                    f"{plan.replay_run_id}."
                )

            ready_event = client.events[0]

            tx_command_count = sum(
                1
                for event in client.events
                if (
                    event.direction == "TX"
                    and event.message_type
                    == "COMMAND"
                )
            )

            checks = [
                (
                    ready_message.protocol_version
                    == plan.expected_protocol_version
                ),
                (
                    ready_message.actuator_mode
                    == plan.expected_startup_mode
                ),
                (
                    ready_message.commanded_angle_deg
                    == plan.expected_startup_angle_deg
                ),
                ready_event.direction == "RX",
                ready_event.message_type == "READY",
                ready_event.command_seq == 0,
                tx_command_count == 0,
            ]

            status = (
                "PASS"
                if all(checks)
                else "FAIL"
            )

            result = ReadySmokeTestResult(
                replay_run_id=(
                    plan.replay_run_id
                ),
                protocol_version=(
                    ready_message.protocol_version
                ),
                actuator_mode=(
                    ready_message.actuator_mode
                ),
                commanded_angle_deg=(
                    ready_message.commanded_angle_deg
                ),
                serial_event_count=len(
                    client.events
                ),
                tx_command_count=(
                    tx_command_count
                ),
                status=status,
            )

            results.append(result)

            print(
                "READY observed:",
                (
                    f"{result.protocol_version},"
                    f"{result.actuator_mode},"
                    f"{result.commanded_angle_deg}"
                ),
            )

            print(
                "Serial event count:",
                result.serial_event_count,
            )

            print(
                "TX command count:",
                result.tx_command_count,
            )

            print(
                "Status:",
                result.status,
            )

            if result.status != "PASS":
                raise RuntimeError(
                    "READY startup validation "
                    "failed for "
                    f"{plan.replay_run_id}."
                )

        finally:
            client.close()

            print(
                "Serial port closed:",
                plan.replay_run_id,
            )

    if len(results) != len(run_plans):
        raise RuntimeError(
            "READY smoke-test result count "
            "does not match the replay-run "
            f"count: {len(results)} vs "
            f"{len(run_plans)}."
        )

    print(
        "\nREADY startup smoke test completed."
    )

    print(
        "No replay command was transmitted."
    )

    return results


def run_single_recording_actual_replay(
    run_plans: list[ReplayRunPlan],
    target_subject: int,
    target_run: int,
) -> ActualReplayRunResult:
    """
    Execute the stored-command replay for one
    explicitly selected source recording.

    Startup settling and post-replay observation
    are outside the source replay clock.
    """

    matching_plans = [
        plan
        for plan in run_plans
        if (
            plan.subject == target_subject
            and plan.run == target_run
        )
    ]

    if len(matching_plans) != 1:
        raise RuntimeError(
            "Expected exactly one replay plan "
            f"for Subject {target_subject}, "
            f"Run {target_run}, but found "
            f"{len(matching_plans)}."
        )

    plan = matching_plans[0]
    results = []

    print("\n========================================")
    print(
        "Session 19 actual replay: "
        f"Subject {plan.subject}, "
        f"Run {plan.run}"
    )

    print(
        "Replay run ID:",
        plan.replay_run_id,
    )

    print(
        "Source recording:",
        f"Subject {plan.subject}, Run {plan.run}",
    )

    print(
        "Expected events:",
        " -> ".join(
            event.serial_command
            for event in plan.events
        ),
    )

    client = SerialClient(
        port=PORT,
        baud_rate=BAUD_RATE,
        response_timeout_s=RESPONSE_TIMEOUT_S,
        read_timeout_s=READ_TIMEOUT_S,
    )

    try:
        client.open()

        ready_message = client.wait_ready(
            timeout_s=READY_TIMEOUT_S,
            case_id=(
                f"{plan.replay_run_id}-READY"
            ),
        )

        ready_checks = [
            (
                ready_message.protocol_version
                == plan.expected_protocol_version
            ),
            (
                ready_message.actuator_mode
                == plan.expected_startup_mode
            ),
            (
                ready_message.commanded_angle_deg
                == plan.expected_startup_angle_deg
            ),
        ]

        if not all(ready_checks):
            raise RuntimeError(
                "READY validation failed for "
                f"{plan.replay_run_id}: "
                f"{ready_message}."
            )

        print(
            "READY validated:",
            (
                f"{ready_message.protocol_version},"
                f"{ready_message.actuator_mode},"
                f"{ready_message.commanded_angle_deg}"
            ),
        )

        print(
            "Startup settle wait:",
            f"{STARTUP_SETTLE_WAIT_S:.3f} s",
        )

        time.sleep(
            STARTUP_SETTLE_WAIT_S
        )

        replay_start_monotonic = (
            time.monotonic()
        )

        replay_start_client_elapsed_ms = (
            (
                replay_start_monotonic
                - client.run_start_monotonic
            )
            * 1000.0
        )

        for event_index, event in enumerate(
            plan.events
        ):
            target_monotonic = (
                replay_start_monotonic
                + event.scheduled_replay_elapsed_sec
            )

            remaining_sec = (
                target_monotonic
                - time.monotonic()
            )

            if remaining_sec > 0.0:
                time.sleep(
                    remaining_sec
                )

            command_seq = (
                client.next_command_seq
            )

            if (
                event_index == 0
                and command_seq != 1
            ):
                raise RuntimeError(
                    "The first replay command "
                    "sequence is not 1."
                )

            response = client.send_command(
                event.serial_command,
                case_id=event.source_event_id,
            )

            if not isinstance(
                response,
                AckMessage,
            ):
                raise RuntimeError(
                    "Replay command returned a "
                    "non-ACK response for "
                    f"{event.source_event_id}: "
                    f"{response}."
                )

            matching_tx_events = [
                serial_event
                for serial_event in client.events
                if (
                    serial_event.direction == "TX"
                    and serial_event.message_type
                    == "COMMAND"
                    and serial_event.command_seq
                    == command_seq
                    and serial_event.case_id
                    == event.source_event_id
                )
            ]

            if len(matching_tx_events) != 1:
                raise RuntimeError(
                    "Expected exactly one matching "
                    "TX event for "
                    f"{event.source_event_id}, "
                    f"but found "
                    f"{len(matching_tx_events)}."
                )

            tx_event = matching_tx_events[0]

            matching_ack_events = [
                serial_event
                for serial_event in client.events
                if (
                    serial_event.direction == "RX"
                    and serial_event.message_type
                    == "ACK"
                    and serial_event.command_seq
                    == command_seq
                    and serial_event.case_id
                    == event.source_event_id
                )
            ]

            if len(matching_ack_events) != 1:
                raise RuntimeError(
                    "Expected exactly one matching "
                    "ACK event for "
                    f"{event.source_event_id}, "
                    f"but found "
                    f"{len(matching_ack_events)}."
                )

            ack_event = matching_ack_events[0]

            raw_actual_tx_elapsed_sec = (
                (
                    tx_event.host_elapsed_ms
                    - replay_start_client_elapsed_ms
                )
                / 1000.0
            )

            raw_ack_received_elapsed_sec = (
                (
                    ack_event.host_elapsed_ms
                    - replay_start_client_elapsed_ms
                )
                / 1000.0
            )

            raw_ack_round_trip_ms = (
                ack_event.host_elapsed_ms
                - tx_event.host_elapsed_ms
            )

            raw_schedule_offset_ms = (
                (
                    raw_actual_tx_elapsed_sec
                    - event.scheduled_replay_elapsed_sec
                )
                * 1000.0
            )

            actual_tx_elapsed_sec = (
                clean_timing_value(
                    raw_actual_tx_elapsed_sec
                )
            )

            ack_received_elapsed_sec = (
                clean_timing_value(
                    raw_ack_received_elapsed_sec
                )
            )

            ack_round_trip_ms = (
                clean_timing_value(
                    raw_ack_round_trip_ms
                )
            )

            schedule_offset_ms = (
                clean_timing_value(
                    raw_schedule_offset_ms
                )
            )

            ack_result_ok = (
                response.result
                == event.expected_ack_result
            )

            actuator_mode_ok = (
                response.actuator_mode
                == event.expected_actuator_mode
            )

            if event_index == 0:
                commanded_angle_ok = (
                    response.commanded_angle_deg
                    == EXPECTED_STARTUP_ANGLE_DEG
                )
            else:
                commanded_angle_ok = (
                    ACTUATOR_MIN_ANGLE_DEG
                    <= response.commanded_angle_deg
                    <= ACTUATOR_MAX_ANGLE_DEG
                )

            status = (
                "PASS"
                if (
                    ack_result_ok
                    and actuator_mode_ok
                    and commanded_angle_ok
                )
                else "FAIL"
            )

            result = ActualReplayEventResult(
                replay_run_id=(
                    plan.replay_run_id
                ),
                subject=plan.subject,
                run=plan.run,
                condition=plan.condition,
                source_event_id=(
                    event.source_event_id
                ),
                window_index=(
                    event.window_index
                ),
                command_state=(
                    event.command_state
                ),
                selection_reason=(
                    event.selection_reason
                ),
                command_seq=command_seq,
                source_decision_time_sec=(
                    event.source_decision_time_sec
                ),
                scheduled_replay_elapsed_sec=(
                    event.scheduled_replay_elapsed_sec
                ),
                actual_tx_elapsed_sec=(
                    actual_tx_elapsed_sec
                ),
                ack_received_elapsed_sec=(
                    ack_received_elapsed_sec
                ),
                ack_round_trip_ms=(
                    ack_round_trip_ms
                ),
                schedule_offset_ms=(
                    schedule_offset_ms
                ),
                serial_command=(
                    event.serial_command
                ),
                expected_ack_result=(
                    event.expected_ack_result
                ),
                observed_ack_result=(
                    response.result
                ),
                expected_actuator_mode=(
                    event.expected_actuator_mode
                ),
                observed_actuator_mode=(
                    response.actuator_mode
                ),
                observed_commanded_angle_deg=(
                    response.commanded_angle_deg
                ),
                status=status,
            )

            results.append(
                result
            )

            print(
                "scheduled="
                f"{result.scheduled_replay_elapsed_sec:>5.3f} s"
                " | actual_tx="
                f"{result.actual_tx_elapsed_sec:>5.3f} s"
                " | offset="
                f"{result.schedule_offset_ms:+8.3f} ms"
                " | ack_rx="
                f"{result.ack_received_elapsed_sec:>5.3f} s"
                " | rtt="
                f"{result.ack_round_trip_ms:>7.3f} ms"
                f" | seq={result.command_seq}"
                f" | {result.source_event_id}"
                f" | command={result.serial_command}"
                " | ack="
                f"{result.observed_ack_result}"
                "/"
                f"{result.observed_actuator_mode}"
                "/"
                f"{result.observed_commanded_angle_deg}"
                f" | status={result.status}"
            )

            if result.status != "PASS":
                raise RuntimeError(
                    "Actual replay validation "
                    "failed for "
                    f"{result.source_event_id}."
                )

        print(
            "Post-replay observation wait:",
            f"{POST_REPLAY_OBSERVATION_WAIT_S:.3f} s",
        )

        time.sleep(
            POST_REPLAY_OBSERVATION_WAIT_S
        )

    finally:
        client.close()

        print(
            "Serial port closed:",
            plan.replay_run_id,
        )

    if len(results) != len(plan.events):
        raise RuntimeError(
            "Actual replay result count does "
            "not match the planned event count: "
            f"{len(results)} vs "
            f"{len(plan.events)}."
        )

    pass_count = sum(
        result.status == "PASS"
        for result in results
    )

    fail_count = (
        len(results)
        - pass_count
    )

    run_status = (
        "PASS"
        if (
            len(results) == len(plan.events)
            and fail_count == 0
        )
        else "FAIL"
    )

    run_result = ActualReplayRunResult(
        replay_run_id=(
            plan.replay_run_id
        ),
        subject=plan.subject,
        run=plan.run,
        condition=plan.condition,
        ready_protocol_version=(
            ready_message.protocol_version
        ),
        ready_actuator_mode=(
            ready_message.actuator_mode
        ),
        ready_commanded_angle_deg=(
            ready_message.commanded_angle_deg
        ),
        planned_event_count=len(
            plan.events
        ),
        completed_event_count=len(
            results
        ),
        pass_count=pass_count,
        fail_count=fail_count,
        max_abs_schedule_offset_ms=max(
            abs(
                result.schedule_offset_ms
            )
            for result in results
        ),
        final_observed_actuator_mode=(
            results[-1].observed_actuator_mode
        ),
        final_observed_commanded_angle_deg=(
            results[-1]
            .observed_commanded_angle_deg
        ),
        startup_settle_wait_s=(
            STARTUP_SETTLE_WAIT_S
        ),
        post_replay_observation_wait_s=(
            POST_REPLAY_OBSERVATION_WAIT_S
        ),
        status=run_status,
        event_results=tuple(
            results
        ),
    )

    print(
        "\nActual replay completed:",
        plan.replay_run_id,
    )

    print(
        "All planned events passed:",
        run_result.status == "PASS",
    )

    return run_result


def save_replay_event_log(
    run_results: list[ActualReplayRunResult],
) -> None:
    """
    Save one source-linked row per transmitted
    replay command.
    """

    REPLAY_EVENT_LOG_CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "replay_run_id",
        "subject",
        "run",
        "condition",
        "source_event_id",
        "window_index",
        "command_state",
        "selection_reason",
        "command_seq",
        "source_decision_time_sec",
        "scheduled_replay_elapsed_sec",
        "actual_tx_elapsed_sec",
        "schedule_offset_ms",
        "ack_received_elapsed_sec",
        "ack_round_trip_ms",
        "serial_command",
        "expected_ack_result",
        "observed_ack_result",
        "expected_actuator_mode",
        "observed_actuator_mode",
        "observed_commanded_angle_deg",
        "status",
    ]

    with REPLAY_EVENT_LOG_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for run_result in run_results:
            for event in run_result.event_results:
                writer.writerow(
                    {
                        field_name: getattr(
                            event,
                            field_name,
                        )
                        for field_name in fieldnames
                    }
                )


def save_replay_summary(
    run_results: list[ActualReplayRunResult],
) -> None:
    """
    Save one summary row per source recording.
    """

    REPLAY_SUMMARY_CSV_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "replay_run_id",
        "subject",
        "run",
        "condition",
        "ready_protocol_version",
        "ready_actuator_mode",
        "ready_commanded_angle_deg",
        "planned_event_count",
        "completed_event_count",
        "pass_count",
        "fail_count",
        "max_abs_schedule_offset_ms",
        "final_observed_actuator_mode",
        "final_observed_commanded_angle_deg",
        "startup_settle_wait_s",
        "post_replay_observation_wait_s",
        "status",
    ]

    with REPLAY_SUMMARY_CSV_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for result in run_results:
            writer.writerow(
                {
                    field_name: getattr(
                        result,
                        field_name,
                    )
                    for field_name in fieldnames
                }
            )


def validate_saved_replay_outputs(
    run_results: list[ActualReplayRunResult],
) -> None:
    """
    Reload the saved CSV files and validate
    their row counts, identities, and statuses.
    """

    with REPLAY_EVENT_LOG_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        saved_event_rows = list(
            csv.DictReader(csv_file)
        )

    with REPLAY_SUMMARY_CSV_PATH.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        saved_summary_rows = list(
            csv.DictReader(csv_file)
        )

    expected_event_results = [
        event
        for run_result in run_results
        for event in run_result.event_results
    ]

    if len(saved_event_rows) != len(
        expected_event_results
    ):
        raise RuntimeError(
            "Saved replay-event row count "
            "does not match the executed "
            f"event count: "
            f"{len(saved_event_rows)} vs "
            f"{len(expected_event_results)}."
        )

    if len(saved_summary_rows) != len(
        run_results
    ):
        raise RuntimeError(
            "Saved summary row count does "
            "not match the replay-run count: "
            f"{len(saved_summary_rows)} vs "
            f"{len(run_results)}."
        )

    expected_source_event_ids = {
        event.source_event_id
        for event in expected_event_results
    }

    saved_source_event_ids = {
        row["source_event_id"]
        for row in saved_event_rows
    }

    if (
        saved_source_event_ids
        != expected_source_event_ids
    ):
        raise RuntimeError(
            "Saved source-event IDs do not "
            "match the executed replay events."
        )

    if any(
        row["status"] != "PASS"
        for row in saved_event_rows
    ):
        raise RuntimeError(
            "A saved replay-event row is "
            "not marked PASS."
        )

    if any(
        row["status"] != "PASS"
        for row in saved_summary_rows
    ):
        raise RuntimeError(
            "A saved replay-summary row is "
            "not marked PASS."
        )


def run_all_recordings_actual_replay(
    run_plans: list[ReplayRunPlan],
) -> list[ActualReplayRunResult]:
    """
    Execute all recording-level replay plans
    using a fresh SerialClient per recording,
    then save and reload-validate the results.
    """

    ordered_plans = sorted(
        run_plans,
        key=lambda plan: (
            plan.subject,
            plan.run,
        ),
    )

    run_results = []

    print("\n========================================")
    print(
        "Session 19 Step 7: "
        "Integrated actual replay"
    )

    print(
        "Recording replay count:",
        len(ordered_plans),
    )

    for plan in ordered_plans:
        run_result = (
            run_single_recording_actual_replay(
                run_plans=run_plans,
                target_subject=plan.subject,
                target_run=plan.run,
            )
        )

        run_results.append(
            run_result
        )

    if any(
        result.status != "PASS"
        for result in run_results
    ):
        raise RuntimeError(
            "At least one integrated replay "
            "run did not pass."
        )

    save_replay_event_log(
        run_results
    )

    save_replay_summary(
        run_results
    )

    validate_saved_replay_outputs(
        run_results
    )

    print("\n========================================")
    print(
        "Integrated replay outputs saved."
    )

    print(
        "Event log:",
        REPLAY_EVENT_LOG_CSV_PATH,
    )

    print(
        "Event row count:",
        sum(
            len(result.event_results)
            for result in run_results
        ),
    )

    print(
        "Recording summary:",
        REPLAY_SUMMARY_CSV_PATH,
    )

    print(
        "Summary row count:",
        len(run_results),
    )

    print(
        "Saved-output validation:",
        "PASS",
    )

    return run_results


def main() -> None:
    freeze_record = load_and_validate_freeze_record()
    rows = load_and_validate_stream(freeze_record)
    grouped_rows = group_and_validate_recordings(rows)
    replay_events = build_replay_plan(
        grouped_rows
    )

    validate_replay_plan(
        replay_events,
        freeze_record,
    )

    run_plans = build_replay_run_plans(
        replay_events
    )

    validate_replay_run_plans(
        run_plans
    )

    print_replay_plan(
        rows,
        replay_events,
    )

    print_replay_run_plans(
        run_plans
    )

    print(
        "\nExecution mode:",
        EXECUTION_MODE,
    )

    if EXECUTION_MODE == "validation_only":
        run_scheduler_dry_run(
            replay_events
        )

    elif EXECUTION_MODE == "ready_smoke_test":
        run_ready_smoke_tests(
            run_plans
        )

    elif EXECUTION_MODE == "actual_replay_run1":
        run_single_recording_actual_replay(
            run_plans=run_plans,
            target_subject=1,
            target_run=1,
        )

    elif EXECUTION_MODE == "actual_replay_run2":
        run_single_recording_actual_replay(
            run_plans=run_plans,
            target_subject=1,
            target_run=2,
        )

    elif EXECUTION_MODE == "actual_replay_all":
        run_all_recordings_actual_replay(
            run_plans
        )

    else:
        raise RuntimeError(
            "Unsupported execution mode: "
            f"{EXECUTION_MODE!r}. "
            "Expected one of "
            f"{sorted(VALID_EXECUTION_MODES)}."
        )

if __name__ == "__main__":
    main()
