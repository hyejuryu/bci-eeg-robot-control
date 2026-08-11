"""
Deterministic Session 21 Phase 1 analysis logic.

This module reuses the frozen threshold and dwell semantics from
bci_robot.decision_rule. It does not load project files, write outputs,
or recalibrate thresholds.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from bci_robot.decision_rule import (
    CLOSE_COMMAND_STATE,
    DwellDecisionState,
    HIGH_EVIDENCE_STATE,
    LOW_EVIDENCE_STATE,
    OPEN_COMMAND_STATE,
    STOP_COMMAND_STATE,
    UNAVAILABLE_EVIDENCE_STATE,
    classify_threshold_state,
    update_dwell_decision,
)


SMOOTHING_ID_NONE = "smooth-none"
SMOOTHING_ID_MEDIAN3 = "smooth-median3"
MEDIAN3_WINDOW_UPDATES = 3
SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC = 2.0

THRESHOLD_IDS = (
    "threshold_eo_q95",
    "threshold_gap_midpoint",
    "threshold_ec_q05",
)

THRESHOLD_RULE_PREFIX = {
    "threshold_eo_q95": "thr-eo-q95",
    "threshold_gap_midpoint": "thr-gap-mid",
    "threshold_ec_q05": "thr-ec-q05",
}

SMOOTHING_IDS = (
    SMOOTHING_ID_NONE,
    SMOOTHING_ID_MEDIAN3,
)

DWELL_VALUES = (1, 2, 3)

REFERENCE_RULE_ID = "thr-gap-mid__smooth-none__dwell-2"

PRIMARY_COMMON_STEP_CONFIGURATION_IDS = {
    "win-1s_step-1s",
    "win-2s_step-1s",
    "win-4s_step-1s",
}

RTOL = 1e-12
ATOL = 1e-15


def build_rule_configurations():
    """Build the frozen 3 x 2 x 3 Session 21 rule grid."""

    configurations = []

    for threshold_id in THRESHOLD_IDS:
        threshold_prefix = THRESHOLD_RULE_PREFIX[
            threshold_id
        ]

        for smoothing_id in SMOOTHING_IDS:
            for dwell_updates in DWELL_VALUES:
                rule_id = (
                    f"{threshold_prefix}__"
                    f"{smoothing_id}__"
                    f"dwell-{dwell_updates}"
                )

                configurations.append({
                    "rule_id": rule_id,
                    "threshold_id": threshold_id,
                    "smoothing_id": smoothing_id,
                    "dwell_updates": dwell_updates,
                })

    rule_ids = [
        configuration["rule_id"]
        for configuration in configurations
    ]

    tuples = [
        (
            configuration["threshold_id"],
            configuration["smoothing_id"],
            configuration["dwell_updates"],
        )
        for configuration in configurations
    ]

    if len(configurations) != 18:
        raise RuntimeError(
            "The Session 21 rule grid must contain exactly 18 rules."
        )

    if len(set(rule_ids)) != 18:
        raise RuntimeError(
            "The Session 21 rule grid contains duplicate rule IDs."
        )

    if len(set(tuples)) != 18:
        raise RuntimeError(
            "The Session 21 rule grid contains duplicate factor tuples."
        )

    if REFERENCE_RULE_ID not in set(rule_ids):
        raise RuntimeError(
            "The frozen reference rule is missing from the rule grid."
        )

    return configurations


def group_rows_by_recording(rows):
    """Group rows by subject and run and sort by window index."""

    grouped_rows = defaultdict(list)

    for row in rows:
        key = (
            int(row["subject"]),
            int(row["run"]),
        )
        grouped_rows[key].append(row)

    for grouped in grouped_rows.values():
        grouped.sort(
            key=lambda row: int(row["window_index"])
        )

    return dict(grouped_rows)


def build_no_smoothing_rows(selected_rows):
    """Represent raw features using the common processed-row schema."""

    processed_rows = []

    for row in selected_rows:
        output_row = dict(row)
        output_row["smoothing_id"] = SMOOTHING_ID_NONE
        output_row["smoothed_available"] = True
        output_row["smoothed_feature_value"] = float(
            row["posterior_alpha_mean_psd"]
        )
        processed_rows.append(output_row)

    if len(processed_rows) != len(selected_rows):
        raise RuntimeError(
            "No-smoothing row count does not match input row count."
        )

    return processed_rows


def build_causal_median3_rows(selected_rows):
    """Apply the frozen causal three-update median per recording."""

    grouped_rows = group_rows_by_recording(
        selected_rows
    )
    processed_rows = []

    for rows in grouped_rows.values():
        raw_values = np.asarray(
            [
                float(row["posterior_alpha_mean_psd"])
                for row in rows
            ],
            dtype=float,
        )

        for index, row in enumerate(rows):
            output_row = dict(row)
            output_row["smoothing_id"] = (
                SMOOTHING_ID_MEDIAN3
            )

            if index < MEDIAN3_WINDOW_UPDATES - 1:
                output_row["smoothed_available"] = False
                output_row["smoothed_feature_value"] = None
            else:
                source_values = raw_values[
                    index - MEDIAN3_WINDOW_UPDATES + 1:
                    index + 1
                ]
                output_row["smoothed_available"] = True
                output_row["smoothed_feature_value"] = float(
                    np.median(source_values)
                )

            processed_rows.append(output_row)

    if len(processed_rows) != len(selected_rows):
        raise RuntimeError(
            "Median-3 row count does not match input row count."
        )

    return processed_rows


def build_dwell_decision_rows(
    processed_rows,
    thresholds_by_subject,
    threshold_id,
    dwell_updates,
    rule_id,
):
    """Apply one frozen threshold/dwell configuration."""

    if not processed_rows:
        raise RuntimeError(
            "No processed feature rows were supplied."
        )

    grouped_rows = group_rows_by_recording(
        processed_rows
    )
    decision_rows = []

    for (subject, run), rows in sorted(
        grouped_rows.items()
    ):
        if subject not in thresholds_by_subject:
            raise RuntimeError(
                f"No fixed thresholds were found for subject {subject}."
            )

        if threshold_id not in thresholds_by_subject[subject]:
            raise RuntimeError(
                f"Unknown threshold ID for subject {subject}: "
                f"{threshold_id}"
            )

        smoothing_ids = {
            row["smoothing_id"]
            for row in rows
        }

        if len(smoothing_ids) != 1:
            raise RuntimeError(
                "A recording contains multiple smoothing IDs."
            )

        smoothing_id = next(iter(smoothing_ids))
        threshold_value = float(
            thresholds_by_subject[subject][threshold_id]
        )
        decision_state = DwellDecisionState()

        for row in rows:
            smoothed_available = bool(
                row["smoothed_available"]
            )
            smoothed_feature_value = row[
                "smoothed_feature_value"
            ]

            if not smoothed_available:
                if smoothed_feature_value is not None:
                    raise RuntimeError(
                        "An unavailable processed row contains a value."
                    )
                evidence_state = UNAVAILABLE_EVIDENCE_STATE
            else:
                if smoothed_feature_value is None:
                    raise RuntimeError(
                        "An available processed row has no value."
                    )
                evidence_state = classify_threshold_state(
                    processed_feature_value=smoothed_feature_value,
                    threshold_value=threshold_value,
                )

            dwell_result = update_dwell_decision(
                state=decision_state,
                evidence_state=evidence_state,
                dwell_updates=dwell_updates,
            )

            decision_rows.append({
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": row["condition"],
                "configuration_id": row["configuration_id"],
                "window_index": int(row["window_index"]),
                "window_start_sec": float(row["window_start_sec"]),
                "window_end_sec": float(row["window_end_sec"]),
                "decision_time_sec": float(row["window_end_sec"]),
                "feature_name": row["feature_name"],
                "feature_unit": row["feature_unit"],
                "raw_feature_value": float(
                    row["posterior_alpha_mean_psd"]
                ),
                "smoothing_id": smoothing_id,
                "smoothed_available": smoothed_available,
                "smoothed_feature_value": smoothed_feature_value,
                "threshold_id": threshold_id,
                "threshold_value": threshold_value,
                "evidence_state": evidence_state,
                "dwell_updates": int(dwell_updates),
                "candidate_evidence_state": (
                    dwell_result.candidate_evidence_state
                ),
                "candidate_count": int(
                    dwell_result.candidate_count
                ),
                "active_evidence_state": (
                    dwell_result.active_evidence_state
                ),
                "initial_command_confirmed": bool(
                    dwell_result.initial_command_confirmed
                ),
                "active_switch_confirmed": bool(
                    dwell_result.active_switch_confirmed
                ),
                "command_state": dwell_result.command_state,
            })

    if len(decision_rows) != len(processed_rows):
        raise RuntimeError(
            "Decision-row count does not match processed-row count."
        )

    return decision_rows


def build_rule_rows_by_rule(
    processed_rows_by_smoothing,
    thresholds_by_subject,
    rule_configurations,
):
    """Build decision streams for the complete frozen rule grid."""

    rows_by_rule = {}

    for configuration in rule_configurations:
        rule_id = configuration["rule_id"]
        smoothing_id = configuration["smoothing_id"]

        if rule_id in rows_by_rule:
            raise RuntimeError(
                f"Duplicate rule ID: {rule_id}"
            )

        if smoothing_id not in processed_rows_by_smoothing:
            raise RuntimeError(
                f"Missing processed stream for {smoothing_id}."
            )

        rows_by_rule[rule_id] = build_dwell_decision_rows(
            processed_rows=(
                processed_rows_by_smoothing[smoothing_id]
            ),
            thresholds_by_subject=thresholds_by_subject,
            threshold_id=configuration["threshold_id"],
            dwell_updates=configuration["dwell_updates"],
            rule_id=rule_id,
        )

    if len(rows_by_rule) != len(rule_configurations):
        raise RuntimeError(
            "Generated rule count does not match configuration count."
        )

    return rows_by_rule


def build_command_episode_rows(
    rule_rows_by_rule,
    rule_configurations,
):
    """Convert decision streams into the frozen command-episode schema."""

    episode_rows = []
    seen_keys = set()

    for configuration in rule_configurations:
        rule_id = configuration["rule_id"]
        grouped_rows = group_rows_by_recording(
            rule_rows_by_rule[rule_id]
        )

        for (subject, run), rows in sorted(
            grouped_rows.items()
        ):
            initialization_indices = [
                index
                for index, row in enumerate(rows)
                if row["initial_command_confirmed"]
            ]

            if len(initialization_indices) != 1:
                raise RuntimeError(
                    "Each rule/run stream must contain exactly one "
                    "initial command confirmation."
                )

            first_active_index = initialization_indices[0]
            first_active_row = rows[first_active_index]

            if first_active_row["command_state"] == STOP_COMMAND_STATE:
                raise RuntimeError(
                    "Initial confirmation must produce an active command."
                )

            if any(
                row["command_state"] != STOP_COMMAND_STATE
                for row in rows[:first_active_index]
            ):
                raise RuntimeError(
                    "An active command occurred before initialization."
                )

            if any(
                row["command_state"] == STOP_COMMAND_STATE
                for row in rows[first_active_index:]
            ):
                raise RuntimeError(
                    "CMD_STOP occurred after initial confirmation."
                )

            for index in range(
                first_active_index + 1,
                len(rows),
            ):
                command_changed = (
                    rows[index]["command_state"]
                    != rows[index - 1]["command_state"]
                )
                if command_changed != bool(
                    rows[index]["active_switch_confirmed"]
                ):
                    raise RuntimeError(
                        "Command transition and active-switch flag disagree."
                    )

            run_start_time_sec = float(
                rows[0]["window_start_sec"]
            )
            run_end_time_sec = float(
                rows[-1]["window_end_sec"]
            )
            first_active_time_sec = float(
                first_active_row["decision_time_sec"]
            )

            initial_stop_rows = rows[:first_active_index]

            if initial_stop_rows:
                first_stop_window_index = int(
                    initial_stop_rows[0]["window_index"]
                )
                last_stop_window_index = int(
                    initial_stop_rows[-1]["window_index"]
                )
                first_stop_decision_time = float(
                    initial_stop_rows[0]["decision_time_sec"]
                )
                last_stop_decision_time = float(
                    initial_stop_rows[-1]["decision_time_sec"]
                )
            else:
                first_stop_window_index = None
                last_stop_window_index = None
                first_stop_decision_time = None
                last_stop_decision_time = None

            base_fields = {
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": rows[0]["condition"],
                "configuration_id": rows[0]["configuration_id"],
                "feature_name": rows[0]["feature_name"],
                "feature_unit": rows[0]["feature_unit"],
                "smoothing_id": rows[0]["smoothing_id"],
                "threshold_id": rows[0]["threshold_id"],
                "threshold_value": float(
                    rows[0]["threshold_value"]
                ),
                "dwell_updates": int(
                    rows[0]["dwell_updates"]
                ),
            }

            episode_index = 0
            key = (rule_id, subject, run, episode_index)
            if key in seen_keys:
                raise RuntimeError(
                    f"Duplicate episode key: {key}"
                )
            seen_keys.add(key)

            episode_rows.append({
                **base_fields,
                "episode_index": episode_index,
                "command_state": STOP_COMMAND_STATE,
                "episode_start_time_sec": run_start_time_sec,
                "episode_end_time_sec": first_active_time_sec,
                "episode_duration_sec": (
                    first_active_time_sec - run_start_time_sec
                ),
                "decision_update_count": len(initial_stop_rows),
                "first_window_index": first_stop_window_index,
                "last_window_index": last_stop_window_index,
                "first_decision_time_sec": first_stop_decision_time,
                "last_decision_time_sec": last_stop_decision_time,
                "start_event": "run_start",
                "end_event": "initial_command_confirmed",
                "is_initial_stop_episode": True,
                "ended_at_run_boundary": False,
            })

            active_episode_start_index = first_active_index
            active_episode_start_event = (
                "initial_command_confirmed"
            )

            for index in range(
                first_active_index + 1,
                len(rows),
            ):
                if (
                    rows[index]["command_state"]
                    == rows[index - 1]["command_state"]
                ):
                    continue

                episode_index += 1
                active_rows = rows[
                    active_episode_start_index:index
                ]
                start_time = float(
                    active_rows[0]["decision_time_sec"]
                )
                end_time = float(
                    rows[index]["decision_time_sec"]
                )

                key = (rule_id, subject, run, episode_index)
                if key in seen_keys:
                    raise RuntimeError(
                        f"Duplicate episode key: {key}"
                    )
                seen_keys.add(key)

                episode_rows.append({
                    **base_fields,
                    "episode_index": episode_index,
                    "command_state": active_rows[0]["command_state"],
                    "episode_start_time_sec": start_time,
                    "episode_end_time_sec": end_time,
                    "episode_duration_sec": end_time - start_time,
                    "decision_update_count": len(active_rows),
                    "first_window_index": int(
                        active_rows[0]["window_index"]
                    ),
                    "last_window_index": int(
                        active_rows[-1]["window_index"]
                    ),
                    "first_decision_time_sec": float(
                        active_rows[0]["decision_time_sec"]
                    ),
                    "last_decision_time_sec": float(
                        active_rows[-1]["decision_time_sec"]
                    ),
                    "start_event": active_episode_start_event,
                    "end_event": "active_switch_confirmed",
                    "is_initial_stop_episode": False,
                    "ended_at_run_boundary": False,
                })

                active_episode_start_index = index
                active_episode_start_event = (
                    "active_switch_confirmed"
                )

            episode_index += 1
            final_rows = rows[active_episode_start_index:]
            final_start_time = float(
                final_rows[0]["decision_time_sec"]
            )

            key = (rule_id, subject, run, episode_index)
            if key in seen_keys:
                raise RuntimeError(
                    f"Duplicate episode key: {key}"
                )
            seen_keys.add(key)

            episode_rows.append({
                **base_fields,
                "episode_index": episode_index,
                "command_state": final_rows[0]["command_state"],
                "episode_start_time_sec": final_start_time,
                "episode_end_time_sec": run_end_time_sec,
                "episode_duration_sec": (
                    run_end_time_sec - final_start_time
                ),
                "decision_update_count": len(final_rows),
                "first_window_index": int(
                    final_rows[0]["window_index"]
                ),
                "last_window_index": int(
                    final_rows[-1]["window_index"]
                ),
                "first_decision_time_sec": float(
                    final_rows[0]["decision_time_sec"]
                ),
                "last_decision_time_sec": float(
                    final_rows[-1]["decision_time_sec"]
                ),
                "start_event": active_episode_start_event,
                "end_event": "run_end",
                "is_initial_stop_episode": False,
                "ended_at_run_boundary": True,
            })

            recording_episodes = [
                row
                for row in episode_rows
                if (
                    row["rule_id"] == rule_id
                    and row["subject"] == subject
                    and row["run"] == run
                )
            ]
            active_switch_count = sum(
                bool(row["active_switch_confirmed"])
                for row in rows
            )

            if len(recording_episodes) != 2 + active_switch_count:
                raise RuntimeError(
                    "Command-episode count does not match switch structure."
                )

    if not episode_rows:
        raise RuntimeError(
            "No command episodes were generated."
        )

    return episode_rows


def count_available_evidence_transitions(rows):
    """Count adjacent LOW<->HIGH changes; ignore UNAVAILABLE transitions."""

    transition_count = 0

    for previous_row, current_row in zip(
        rows[:-1],
        rows[1:],
    ):
        previous_state = previous_row["evidence_state"]
        current_state = current_row["evidence_state"]

        if previous_state not in {
            LOW_EVIDENCE_STATE,
            HIGH_EVIDENCE_STATE,
        }:
            continue

        if current_state not in {
            LOW_EVIDENCE_STATE,
            HIGH_EVIDENCE_STATE,
        }:
            continue

        if previous_state != current_state:
            transition_count += 1

    return transition_count


def build_rule_run_summary_rows(
    rule_rows_by_rule,
    command_episode_rows,
    rule_configurations,
    step_size_sec=1.0,
):
    """Build frozen Session 21 per-rule/run summary measures."""

    episodes_by_key = defaultdict(list)

    for episode in command_episode_rows:
        key = (
            episode["rule_id"],
            int(episode["subject"]),
            int(episode["run"]),
        )
        episodes_by_key[key].append(episode)

    summary_rows = []
    seen_keys = set()

    for configuration in rule_configurations:
        rule_id = configuration["rule_id"]
        grouped_rows = group_rows_by_recording(
            rule_rows_by_rule[rule_id]
        )

        for (subject, run), rows in sorted(
            grouped_rows.items()
        ):
            summary_key = (rule_id, subject, run)
            if summary_key in seen_keys:
                raise RuntimeError(
                    f"Duplicate summary key: {summary_key}"
                )
            seen_keys.add(summary_key)

            initialization_rows = [
                row
                for row in rows
                if row["initial_command_confirmed"]
            ]
            if len(initialization_rows) != 1:
                raise RuntimeError(
                    "Each rule/run must contain one initial confirmation."
                )

            first_active_row = initialization_rows[0]
            available_rows = [
                row
                for row in rows
                if bool(row["smoothed_available"])
            ]
            if not available_rows:
                raise RuntimeError(
                    "No available processed feature rows were found."
                )

            unavailable_count = sum(
                row["evidence_state"]
                == UNAVAILABLE_EVIDENCE_STATE
                for row in rows
            )
            low_count = sum(
                row["evidence_state"] == LOW_EVIDENCE_STATE
                for row in rows
            )
            high_count = sum(
                row["evidence_state"] == HIGH_EVIDENCE_STATE
                for row in rows
            )
            available_count = low_count + high_count

            if available_count <= 0:
                raise RuntimeError(
                    "Available evidence denominator must be positive."
                )

            if unavailable_count + available_count != len(rows):
                raise RuntimeError(
                    "Evidence-state counts do not reconcile."
                )

            stop_count = sum(
                row["command_state"] == STOP_COMMAND_STATE
                for row in rows
            )
            open_count = sum(
                row["command_state"] == OPEN_COMMAND_STATE
                for row in rows
            )
            close_count = sum(
                row["command_state"] == CLOSE_COMMAND_STATE
                for row in rows
            )

            if stop_count + open_count + close_count != len(rows):
                raise RuntimeError(
                    "Command-state counts do not reconcile."
                )

            active_switch_rows = [
                row
                for row in rows
                if row["active_switch_confirmed"]
            ]
            active_switch_times = [
                float(row["decision_time_sec"])
                for row in active_switch_rows
            ]

            candidate_rows = [
                row
                for row in rows
                if (
                    row["command_state"] != STOP_COMMAND_STATE
                    and int(row["candidate_count"]) > 0
                    and not row["initial_command_confirmed"]
                    and not row["active_switch_confirmed"]
                )
            ]
            candidate_times = [
                float(row["decision_time_sec"])
                for row in candidate_rows
            ]

            episodes = sorted(
                episodes_by_key[summary_key],
                key=lambda row: int(row["episode_index"]),
            )
            if not episodes:
                raise RuntimeError(
                    f"No episodes found for {summary_key}."
                )

            expected_indices = list(range(len(episodes)))
            actual_indices = [
                int(row["episode_index"])
                for row in episodes
            ]
            if actual_indices != expected_indices:
                raise RuntimeError(
                    "Episode indices are not consecutive."
                )

            for previous_episode, next_episode in zip(
                episodes[:-1],
                episodes[1:],
            ):
                if not np.isclose(
                    float(previous_episode["episode_end_time_sec"]),
                    float(next_episode["episode_start_time_sec"]),
                    rtol=RTOL,
                    atol=ATOL,
                ):
                    raise RuntimeError(
                        "Command episodes are not temporally contiguous."
                    )

            initial_stop_episodes = [
                episode
                for episode in episodes
                if episode["is_initial_stop_episode"]
            ]
            if len(initial_stop_episodes) != 1:
                raise RuntimeError(
                    "Each rule/run requires one initial STOP episode."
                )

            active_episodes = [
                episode
                for episode in episodes
                if not episode["is_initial_stop_episode"]
            ]
            if not active_episodes:
                raise RuntimeError(
                    "Each rule/run requires active command episodes."
                )

            run_start_time_sec = float(
                rows[0]["window_start_sec"]
            )
            run_end_time_sec = float(
                rows[-1]["window_end_sec"]
            )
            recording_duration_sec = (
                run_end_time_sec - run_start_time_sec
            )

            if recording_duration_sec <= 0.0:
                raise RuntimeError(
                    "Recording duration must be positive."
                )

            duration_by_state = {
                STOP_COMMAND_STATE: 0.0,
                OPEN_COMMAND_STATE: 0.0,
                CLOSE_COMMAND_STATE: 0.0,
            }

            for episode in episodes:
                duration_by_state[
                    episode["command_state"]
                ] += float(episode["episode_duration_sec"])

            duration_sum = sum(duration_by_state.values())
            if not np.isclose(
                duration_sum,
                recording_duration_sec,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "Command durations do not cover the recording."
                )

            first_active_time_sec = float(
                first_active_row["decision_time_sec"]
            )
            initial_stop_duration_sec = (
                first_active_time_sec - run_start_time_sec
            )

            active_episode_durations = [
                float(episode["episode_duration_sec"])
                for episode in active_episodes
            ]
            short_active_episodes = [
                episode
                for episode in active_episodes
                if float(episode["episode_duration_sec"])
                <= SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC + ATOL
            ]

            summary_rows.append({
                "rule_id": rule_id,
                "subject": subject,
                "run": run,
                "condition": rows[0]["condition"],
                "configuration_id": rows[0]["configuration_id"],
                "feature_name": rows[0]["feature_name"],
                "feature_unit": rows[0]["feature_unit"],
                "smoothing_id": rows[0]["smoothing_id"],
                "threshold_id": rows[0]["threshold_id"],
                "threshold_value": float(rows[0]["threshold_value"]),
                "dwell_updates": int(rows[0]["dwell_updates"]),
                "nominal_confirmation_span_sec": (
                    (int(rows[0]["dwell_updates"]) - 1)
                    * float(step_size_sec)
                ),
                "run_start_time_sec": run_start_time_sec,
                "run_end_time_sec": run_end_time_sec,
                "recording_duration_sec": recording_duration_sec,
                "decision_update_count": len(rows),
                "first_decision_time_sec": float(
                    rows[0]["decision_time_sec"]
                ),
                "last_decision_time_sec": float(
                    rows[-1]["decision_time_sec"]
                ),
                "unavailable_evidence_count": unavailable_count,
                "first_processed_feature_time_sec": float(
                    available_rows[0]["decision_time_sec"]
                ),
                "initial_stop_update_count": stop_count,
                "initial_stop_duration_sec": initial_stop_duration_sec,
                "first_active_command_time_sec": first_active_time_sec,
                "first_active_command": first_active_row["command_state"],
                "final_command_state": rows[-1]["command_state"],
                "low_evidence_count": low_count,
                "high_evidence_count": high_count,
                "low_evidence_fraction": low_count / available_count,
                "high_evidence_fraction": high_count / available_count,
                "evidence_transition_count": (
                    count_available_evidence_transitions(rows)
                ),
                "cmd_stop_count": stop_count,
                "cmd_open_count": open_count,
                "cmd_close_count": close_count,
                "active_switch_count": len(active_switch_rows),
                "active_switch_times_sec": ";".join(
                    f"{time_sec:.1f}"
                    for time_sec in active_switch_times
                ),
                "unconfirmed_candidate_update_count": len(
                    candidate_rows
                ),
                "unconfirmed_candidate_times_sec": ";".join(
                    f"{time_sec:.1f}"
                    for time_sec in candidate_times
                ),
                "command_episode_count": len(episodes),
                "active_command_episode_count": len(active_episodes),
                "short_active_episode_max_duration_sec": (
                    SHORT_ACTIVE_EPISODE_MAX_DURATION_SEC
                ),
                "short_active_command_episode_count": len(
                    short_active_episodes
                ),
                "shortest_active_episode_duration_sec": min(
                    active_episode_durations
                ),
                "longest_active_episode_duration_sec": max(
                    active_episode_durations
                ),
                "stop_duration_sec": duration_by_state[
                    STOP_COMMAND_STATE
                ],
                "open_duration_sec": duration_by_state[
                    OPEN_COMMAND_STATE
                ],
                "close_duration_sec": duration_by_state[
                    CLOSE_COMMAND_STATE
                ],
                "stop_duration_fraction": (
                    duration_by_state[STOP_COMMAND_STATE]
                    / recording_duration_sec
                ),
                "open_duration_fraction": (
                    duration_by_state[OPEN_COMMAND_STATE]
                    / recording_duration_sec
                ),
                "close_duration_fraction": (
                    duration_by_state[CLOSE_COMMAND_STATE]
                    / recording_duration_sec
                ),
            })

    if len(summary_rows) != 36:
        raise RuntimeError(
            "The Session 21 rule/run summary must contain 36 rows."
        )

    return summary_rows


def build_temporal_variability_rows(
    feature_rows,
    expected_configuration_ids,
):
    """Calculate frozen Phase 1B temporal-variability metrics."""

    grouped_rows = defaultdict(list)

    for row in feature_rows:
        key = (
            row["configuration_id"],
            int(row["run"]),
        )
        grouped_rows[key].append(row)

    summary_rows = []

    for configuration_id in expected_configuration_ids:
        for run in (1, 2):
            key = (configuration_id, run)
            if key not in grouped_rows:
                raise RuntimeError(
                    f"Missing Phase 1B input group: {key}"
                )

            rows = sorted(
                grouped_rows[key],
                key=lambda row: int(row["window_index"]),
            )
            feature_values = np.asarray(
                [
                    float(row["posterior_alpha_mean_psd"])
                    for row in rows
                ],
                dtype=float,
            )

            if not np.isfinite(feature_values).all():
                raise ValueError(
                    f"Non-finite Phase 1B features for {key}."
                )

            if np.any(feature_values <= 0.0):
                raise ValueError(
                    f"Non-positive Phase 1B PSD feature for {key}."
                )

            differences = np.diff(feature_values)
            if len(differences) != len(feature_values) - 1:
                raise RuntimeError(
                    f"Difference count mismatch for {key}."
                )

            if not np.isfinite(differences).all():
                raise ValueError(
                    f"Non-finite successive differences for {key}."
                )

            q25, median, q75 = np.quantile(
                feature_values,
                [0.25, 0.50, 0.75],
                method="linear",
            )
            if median <= 0.0:
                raise RuntimeError(
                    f"Relative IQR denominator is not positive for {key}."
                )

            relative_iqr = float(
                (q75 - q25) / median
            )
            volatility = float(
                np.std(differences, ddof=0)
            )
            median_absolute_change = float(
                np.median(np.abs(differences))
            )

            first_row = rows[0]
            summary_rows.append({
                "subject": int(first_row["subject"]),
                "run": run,
                "condition": first_row["condition"],
                "configuration_id": configuration_id,
                "window_length_sec": float(
                    first_row["window_length_sec"]
                ),
                "step_size_sec": float(
                    first_row["step_size_sec"]
                ),
                "outer_window_overlap_fraction": float(
                    first_row["outer_window_overlap_fraction"]
                ),
                "welch_segment_count": int(
                    first_row["welch_segment_count"]
                ),
                "feature_name": first_row["feature_name"],
                "feature_unit": first_row["feature_unit"],
                "n_features": len(feature_values),
                "n_differences": len(differences),
                "relative_iqr": relative_iqr,
                "successive_difference_sd_population": volatility,
                "median_absolute_successive_change": (
                    median_absolute_change
                ),
                "comparison_role": (
                    "primary_common_step_1s"
                    if configuration_id
                    in PRIMARY_COMMON_STEP_CONFIGURATION_IDS
                    else "descriptive_cross_step"
                ),
            })

    if len(summary_rows) != 10:
        raise RuntimeError(
            "The Phase 1B summary must contain exactly 10 rows."
        )

    return summary_rows
