"""Session 21 Phase 2A-3 feature-to-command event trace."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DECISION_STREAM_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_rule-grid_decision-stream.csv"
)

OUTPUT_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_phase2a_feature-command-trace.csv"
)

OUTPUT_FIGURE_PATH = (
    PROJECT_ROOT
    / "figures"
    / "session-21"
    / "phase2a"
    / "session21_phase2a_feature-command-trace.png"
)

SUBJECT = 1
RUN = 1
CONDITION = "baseline_eyes_open"
CONFIGURATION_ID = "win-2s_step-1s"
THRESHOLD_ID = "threshold_gap_midpoint"
EXPECTED_THRESHOLD_VALUE = 1.3987182661955795e-10
FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

SMOOTHING_IDS = (
    "smooth-none",
    "smooth-median3",
)

SMOOTHING_LABELS = {
    "smooth-none": "Unsmoothed feature",
    "smooth-median3": "Causal median-3 feature",
}

DWELL_VALUES = (1, 2, 3)

RULE_IDS = {
    ("smooth-none", 1):
        "thr-gap-mid__smooth-none__dwell-1",
    ("smooth-none", 2):
        "thr-gap-mid__smooth-none__dwell-2",
    ("smooth-none", 3):
        "thr-gap-mid__smooth-none__dwell-3",
    ("smooth-median3", 1):
        "thr-gap-mid__smooth-median3__dwell-1",
    ("smooth-median3", 2):
        "thr-gap-mid__smooth-median3__dwell-2",
    ("smooth-median3", 3):
        "thr-gap-mid__smooth-median3__dwell-3",
}

EXPECTED_ROWS_PER_RULE = 59
EXPECTED_SELECTED_RULE_ROWS = 6 * EXPECTED_ROWS_PER_RULE
EXPECTED_DECISION_STEP_SEC = 1.0

TRACE_START_TIME_SEC = 23.0
TRACE_END_TIME_SEC = 30.0
EVENT_WINDOW_START_SEC = 24.0
EVENT_WINDOW_END_SEC = 26.0
EVENT_DECISION_TIME_SEC = 26.0

RTOL = 1e-12
ATOL = 1e-15

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
}

OUTPUT_COLUMNS = [
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
    "processed_feature_available",
    "processed_feature_value",
    "threshold_id",
    "threshold_value",
    "threshold_relative_margin",
    "threshold_relative_margin_percent",
    "evidence_state",
    "evidence_episode_index",
    "evidence_episode_update_count",
    "evidence_episode_start_time_sec",
    "evidence_episode_end_time_sec",
    "evidence_episode_nominal_span_sec",
    "dwell_updates",
    "candidate_evidence_state",
    "candidate_count",
    "active_evidence_state",
    "initial_command_confirmed",
    "active_switch_confirmed",
    "command_state",
    "is_selected_24_26_window",
]

EVIDENCE_Y = {
    "LOW_ALPHA": 0,
    "HIGH_ALPHA": 1,
    "UNAVAILABLE": -1,
}

COMMAND_Y = {
    "CMD_STOP": -1,
    "CMD_OPEN": 0,
    "CMD_CLOSE": 1,
}


def parse_bool(value, field_name):
    if value == "True":
        return True
    if value == "False":
        return False

    raise ValueError(
        f"Unexpected boolean value for {field_name}: {value!r}"
    )


def parse_optional_float(value):
    if value == "":
        return None
    return float(value)


def read_csv_rows(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            raise RuntimeError(
                "Decision-stream CSV is missing columns: "
                f"{sorted(missing)}"
            )

        return list(reader)


def write_csv_rows(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def load_selected_rule_rows():
    source_rows = read_csv_rows(DECISION_STREAM_CSV_PATH)
    selected_rule_ids = set(RULE_IDS.values())

    selected = []

    for source in source_rows:
        if source["rule_id"] not in selected_rule_ids:
            continue

        if int(source["subject"]) != SUBJECT:
            continue
        if int(source["run"]) != RUN:
            continue
        if source["condition"] != CONDITION:
            continue
        if source["configuration_id"] != CONFIGURATION_ID:
            continue

        row = {
            "rule_id": source["rule_id"],
            "subject": int(source["subject"]),
            "run": int(source["run"]),
            "condition": source["condition"],
            "configuration_id": source["configuration_id"],
            "window_index": int(source["window_index"]),
            "window_start_sec": float(source["window_start_sec"]),
            "window_end_sec": float(source["window_end_sec"]),
            "decision_time_sec": float(source["decision_time_sec"]),
            "feature_name": source["feature_name"],
            "feature_unit": source["feature_unit"],
            "raw_feature_value": float(
                source["raw_feature_value"]
            ),
            "smoothing_id": source["smoothing_id"],
            "smoothed_available": parse_bool(
                source["smoothed_available"],
                "smoothed_available",
            ),
            "smoothed_feature_value": parse_optional_float(
                source["smoothed_feature_value"]
            ),
            "threshold_id": source["threshold_id"],
            "threshold_value": float(source["threshold_value"]),
            "evidence_state": source["evidence_state"],
            "dwell_updates": int(source["dwell_updates"]),
            "candidate_evidence_state": (
                source["candidate_evidence_state"]
            ),
            "candidate_count": int(source["candidate_count"]),
            "active_evidence_state": (
                source["active_evidence_state"]
            ),
            "initial_command_confirmed": parse_bool(
                source["initial_command_confirmed"],
                "initial_command_confirmed",
            ),
            "active_switch_confirmed": parse_bool(
                source["active_switch_confirmed"],
                "active_switch_confirmed",
            ),
            "command_state": source["command_state"],
        }

        selected.append(row)

    if len(selected) != EXPECTED_SELECTED_RULE_ROWS:
        raise RuntimeError(
            f"Expected {EXPECTED_SELECTED_RULE_ROWS} selected rows, "
            f"found {len(selected)}."
        )

    return selected


def validate_selected_rule_rows(rows):
    grouped = defaultdict(list)

    for row in rows:
        grouped[row["rule_id"]].append(row)

        if row["feature_name"] != FEATURE_NAME:
            raise RuntimeError("Unexpected feature name.")
        if row["feature_unit"] != FEATURE_UNIT:
            raise RuntimeError("Unexpected feature unit.")
        if row["threshold_id"] != THRESHOLD_ID:
            raise RuntimeError("Unexpected threshold ID.")

        if not np.isclose(
            row["threshold_value"],
            EXPECTED_THRESHOLD_VALUE,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError("Gap-midpoint threshold mismatch.")

        expected_rule_id = RULE_IDS[
            (row["smoothing_id"], row["dwell_updates"])
        ]
        if row["rule_id"] != expected_rule_id:
            raise RuntimeError(
                "Rule ID does not match smoothing/dwell tuple."
            )

    if set(grouped) != set(RULE_IDS.values()):
        raise RuntimeError("Selected rule set is incomplete.")

    for rule_id, rule_rows in grouped.items():
        rule_rows.sort(
            key=lambda row: row["window_index"]
        )

        if len(rule_rows) != EXPECTED_ROWS_PER_RULE:
            raise RuntimeError(
                f"Unexpected row count for {rule_id}: "
                f"{len(rule_rows)}"
            )

        indices = [
            row["window_index"] for row in rule_rows
        ]
        if indices != list(range(EXPECTED_ROWS_PER_RULE)):
            raise RuntimeError(
                f"Window-index mismatch for {rule_id}."
            )

        times = np.asarray(
            [
                row["decision_time_sec"]
                for row in rule_rows
            ],
            dtype=float,
        )

        if not np.allclose(
            np.diff(times),
            EXPECTED_DECISION_STEP_SEC,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError(
                f"Unexpected decision-time step for {rule_id}."
            )

    validate_cross_dwell_processing(grouped)

    return grouped


def validate_cross_dwell_processing(grouped):
    for smoothing_id in SMOOTHING_IDS:
        reference_rule = RULE_IDS[(smoothing_id, 1)]
        reference_rows = grouped[reference_rule]

        for dwell in (2, 3):
            comparison_rule = RULE_IDS[
                (smoothing_id, dwell)
            ]
            comparison_rows = grouped[comparison_rule]

            for ref, comp in zip(
                reference_rows,
                comparison_rows,
            ):
                if ref["window_index"] != comp["window_index"]:
                    raise RuntimeError(
                        "Cross-dwell window alignment mismatch."
                    )

                if not np.isclose(
                    ref["raw_feature_value"],
                    comp["raw_feature_value"],
                    rtol=RTOL,
                    atol=ATOL,
                ):
                    raise RuntimeError(
                        "Raw feature differs across dwell values."
                    )

                if (
                    ref["smoothed_available"]
                    != comp["smoothed_available"]
                ):
                    raise RuntimeError(
                        "Smoothing availability differs across dwell."
                    )

                if ref["smoothed_feature_value"] is None:
                    if comp["smoothed_feature_value"] is not None:
                        raise RuntimeError(
                            "Processed feature availability mismatch."
                        )
                else:
                    if comp["smoothed_feature_value"] is None:
                        raise RuntimeError(
                            "Processed feature availability mismatch."
                        )

                    if not np.isclose(
                        ref["smoothed_feature_value"],
                        comp["smoothed_feature_value"],
                        rtol=RTOL,
                        atol=ATOL,
                    ):
                        raise RuntimeError(
                            "Processed feature differs across dwell."
                        )

                if ref["evidence_state"] != comp["evidence_state"]:
                    raise RuntimeError(
                        "Evidence differs across dwell values."
                    )

    no_smoothing_rows = grouped[
        RULE_IDS[("smooth-none", 1)]
    ]

    for row in no_smoothing_rows:
        if not row["smoothed_available"]:
            raise RuntimeError(
                "No-smoothing feature must always be available."
            )

        if row["smoothed_feature_value"] is None:
            raise RuntimeError(
                "No-smoothing processed feature is missing."
            )

        if not np.isclose(
            row["raw_feature_value"],
            row["smoothed_feature_value"],
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError(
                "No-smoothing processed feature does not "
                "match unsmoothed feature."
            )


def build_evidence_episode_annotations(rule_rows):
    annotations = {}
    episode_index = -1
    episode_start_index = 0

    for index in range(1, len(rule_rows) + 1):
        boundary = (
            index == len(rule_rows)
            or (
                rule_rows[index]["evidence_state"]
                != rule_rows[index - 1]["evidence_state"]
            )
        )

        if not boundary:
            continue

        episode_index += 1
        episode_rows = rule_rows[
            episode_start_index:index
        ]
        update_count = len(episode_rows)
        start_time = episode_rows[0]["decision_time_sec"]
        end_time = episode_rows[-1]["decision_time_sec"]
        nominal_span = (
            (update_count - 1)
            * EXPECTED_DECISION_STEP_SEC
        )

        for row in episode_rows:
            annotations[row["window_index"]] = {
                "evidence_episode_index": episode_index,
                "evidence_episode_update_count": update_count,
                "evidence_episode_start_time_sec": start_time,
                "evidence_episode_end_time_sec": end_time,
                "evidence_episode_nominal_span_sec": nominal_span,
            }

        episode_start_index = index

    if len(annotations) != len(rule_rows):
        raise RuntimeError(
            "Evidence-episode annotation count mismatch."
        )

    return annotations


def build_trace_rows(grouped):
    output_rows = []

    for smoothing_id in SMOOTHING_IDS:
        for dwell in DWELL_VALUES:
            rule_id = RULE_IDS[(smoothing_id, dwell)]
            rule_rows = grouped[rule_id]
            episode_annotations = (
                build_evidence_episode_annotations(
                    rule_rows
                )
            )

            for row in rule_rows:
                time_sec = row["decision_time_sec"]

                if not (
                    TRACE_START_TIME_SEC
                    <= time_sec
                    <= TRACE_END_TIME_SEC
                ):
                    continue

                processed_available = bool(
                    row["smoothed_available"]
                )
                processed_value = (
                    row["smoothed_feature_value"]
                    if processed_available
                    else None
                )

                if processed_available:
                    if processed_value is None:
                        raise RuntimeError(
                            "Available processed feature is missing."
                        )
                    margin = (
                        processed_value
                        - row["threshold_value"]
                    ) / row["threshold_value"]
                    margin_percent = 100.0 * margin
                else:
                    margin = None
                    margin_percent = None

                annotation = episode_annotations[
                    row["window_index"]
                ]

                output_rows.append({
                    "rule_id": rule_id,
                    "subject": row["subject"],
                    "run": row["run"],
                    "condition": row["condition"],
                    "configuration_id": (
                        row["configuration_id"]
                    ),
                    "window_index": row["window_index"],
                    "window_start_sec": (
                        row["window_start_sec"]
                    ),
                    "window_end_sec": row["window_end_sec"],
                    "decision_time_sec": time_sec,
                    "feature_name": row["feature_name"],
                    "feature_unit": row["feature_unit"],
                    "raw_feature_value": (
                        row["raw_feature_value"]
                    ),
                    "smoothing_id": smoothing_id,
                    "processed_feature_available": (
                        processed_available
                    ),
                    "processed_feature_value": processed_value,
                    "threshold_id": row["threshold_id"],
                    "threshold_value": row["threshold_value"],
                    "threshold_relative_margin": margin,
                    "threshold_relative_margin_percent": (
                        margin_percent
                    ),
                    "evidence_state": row["evidence_state"],
                    **annotation,
                    "dwell_updates": dwell,
                    "candidate_evidence_state": (
                        row["candidate_evidence_state"]
                    ),
                    "candidate_count": row["candidate_count"],
                    "active_evidence_state": (
                        row["active_evidence_state"]
                    ),
                    "initial_command_confirmed": (
                        row["initial_command_confirmed"]
                    ),
                    "active_switch_confirmed": (
                        row["active_switch_confirmed"]
                    ),
                    "command_state": row["command_state"],
                    "is_selected_24_26_window": (
                        np.isclose(
                            row["window_start_sec"],
                            EVENT_WINDOW_START_SEC,
                            rtol=RTOL,
                            atol=ATOL,
                        )
                        and np.isclose(
                            row["window_end_sec"],
                            EVENT_WINDOW_END_SEC,
                            rtol=RTOL,
                            atol=ATOL,
                        )
                    ),
                })

    expected_trace_times = int(
        (
            TRACE_END_TIME_SEC
            - TRACE_START_TIME_SEC
        )
        / EXPECTED_DECISION_STEP_SEC
    ) + 1
    expected_trace_rows = (
        len(RULE_IDS)
        * expected_trace_times
    )

    if len(output_rows) != expected_trace_rows:
        raise RuntimeError(
            f"Expected {expected_trace_rows} trace rows, "
            f"found {len(output_rows)}."
        )

    selected_event_rows = [
        row
        for row in output_rows
        if row["is_selected_24_26_window"]
    ]

    if len(selected_event_rows) != len(RULE_IDS):
        raise RuntimeError(
            "Selected 24-26 s event is not represented "
            "once per selected rule."
        )

    return output_rows


def load_saved_trace_rows():
    if not OUTPUT_CSV_PATH.exists():
        raise FileNotFoundError(OUTPUT_CSV_PATH)

    with open(
        OUTPUT_CSV_PATH,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != OUTPUT_COLUMNS:
            raise RuntimeError(
                "Reloaded trace schema does not match "
                "the expected schema."
            )

        rows = list(reader)

    if not rows:
        raise RuntimeError("Reloaded trace output is empty.")

    return rows


def filter_saved_rows(
    rows,
    smoothing_id,
    dwell,
):
    selected = [
        row
        for row in rows
        if (
            row["smoothing_id"] == smoothing_id
            and int(row["dwell_updates"]) == dwell
        )
    ]

    selected.sort(
        key=lambda row: float(row["decision_time_sec"])
    )

    return selected


def save_trace_figure(saved_rows):
    figure, axes = plt.subplots(
        nrows=6,
        ncols=2,
        figsize=(14, 15),
        sharex=True,
    )

    for column, smoothing_id in enumerate(
        SMOOTHING_IDS
    ):
        representative_rows = filter_saved_rows(
            saved_rows,
            smoothing_id,
            1,
        )

        times = np.asarray(
            [
                float(row["decision_time_sec"])
                for row in representative_rows
            ],
            dtype=float,
        )
        processed_values = np.asarray(
            [
                float(row["processed_feature_value"])
                for row in representative_rows
            ],
            dtype=float,
        )
        threshold_values = np.asarray(
            [
                float(row["threshold_value"])
                for row in representative_rows
            ],
            dtype=float,
        )
        margins_percent = np.asarray(
            [
                float(
                    row[
                        "threshold_relative_margin_percent"
                    ]
                )
                for row in representative_rows
            ],
            dtype=float,
        )
        evidence_values = np.asarray(
            [
                EVIDENCE_Y[row["evidence_state"]]
                for row in representative_rows
            ],
            dtype=float,
        )

        feature_axis = axes[0, column]
        feature_axis.plot(
            times,
            processed_values,
            marker="o",
            label=SMOOTHING_LABELS[smoothing_id],
        )
        feature_axis.plot(
            times,
            threshold_values,
            linestyle="--",
            label="Gap midpoint",
        )
        feature_axis.set_ylabel("PSD (V²/Hz)")
        feature_axis.set_title(
            SMOOTHING_LABELS[smoothing_id]
        )
        feature_axis.grid(alpha=0.25)
        feature_axis.legend(fontsize=9)

        margin_axis = axes[1, column]
        margin_axis.plot(
            times,
            margins_percent,
            marker="o",
        )
        margin_axis.axhline(
            0.0,
            linestyle="--",
        )
        margin_axis.set_ylabel(
            "Threshold-relative margin (%)"
        )
        margin_axis.grid(alpha=0.25)

        evidence_axis = axes[2, column]
        evidence_axis.step(
            times,
            evidence_values,
            where="post",
        )
        evidence_axis.set_yticks([0, 1])
        evidence_axis.set_yticklabels(
            ["LOW", "HIGH"]
        )
        evidence_axis.set_ylabel("Evidence")
        evidence_axis.grid(alpha=0.25)

        for row_offset, dwell in enumerate(
            DWELL_VALUES,
            start=3,
        ):
            command_rows = filter_saved_rows(
                saved_rows,
                smoothing_id,
                dwell,
            )
            command_times = np.asarray(
                [
                    float(row["decision_time_sec"])
                    for row in command_rows
                ],
                dtype=float,
            )
            command_values = np.asarray(
                [
                    COMMAND_Y[row["command_state"]]
                    for row in command_rows
                ],
                dtype=float,
            )

            command_axis = axes[
                row_offset,
                column,
            ]
            command_axis.step(
                command_times,
                command_values,
                where="post",
            )
            command_axis.set_yticks(
                [-1, 0, 1]
            )
            command_axis.set_yticklabels(
                ["STOP", "OPEN", "CLOSE"]
            )
            command_axis.set_ylabel(
                f"Dwell {dwell}"
            )
            command_axis.grid(alpha=0.25)

        for row_index in range(6):
            axis = axes[row_index, column]
            axis.axvline(
                EVENT_DECISION_TIME_SEC,
                linestyle=":",
                linewidth=1.0,
            )
            axis.set_xlim(
                TRACE_START_TIME_SEC,
                TRACE_END_TIME_SEC,
            )

    for axis in axes[-1, :]:
        axis.set_xlabel("Decision time (s)")

    figure.suptitle(
        "Session 21 Phase 2A-3: "
        "Run 1 Feature-to-Command Event Trace "
        "(Gap Midpoint)",
        fontsize=15,
    )
    figure.tight_layout(
        rect=(0.0, 0.0, 1.0, 0.97)
    )

    OUTPUT_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    figure.savefig(
        OUTPUT_FIGURE_PATH,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(figure)

    if (
        not OUTPUT_FIGURE_PATH.exists()
        or OUTPUT_FIGURE_PATH.stat().st_size == 0
    ):
        raise RuntimeError(
            "Feature-to-command trace figure "
            "was not saved correctly."
        )


def print_event_summary(saved_rows):
    print(
        "\nSelected 24-26 s event "
        f"(decision time {EVENT_DECISION_TIME_SEC:.1f} s):"
    )

    for smoothing_id in SMOOTHING_IDS:
        rows = filter_saved_rows(
            saved_rows,
            smoothing_id,
            1,
        )
        event_rows = [
            row
            for row in rows
            if row["is_selected_24_26_window"] == "True"
        ]

        if len(event_rows) != 1:
            raise RuntimeError(
                "Expected one event row per smoothing mode."
            )

        event = event_rows[0]

        print(
            f"\n{SMOOTHING_LABELS[smoothing_id]}:"
        )
        print(
            "  processed feature = "
            f"{float(event['processed_feature_value']):.8g}"
        )
        print(
            "  margin = "
            f"{float(event['threshold_relative_margin_percent']):+.2f}%"
        )
        print(
            "  evidence = "
            f"{event['evidence_state']}"
        )
        print(
            "  evidence episode updates = "
            f"{int(event['evidence_episode_update_count'])}"
        )

        for dwell in DWELL_VALUES:
            dwell_rows = filter_saved_rows(
                saved_rows,
                smoothing_id,
                dwell,
            )
            dwell_event_rows = [
                row
                for row in dwell_rows
                if row[
                    "is_selected_24_26_window"
                ] == "True"
            ]

            if len(dwell_event_rows) != 1:
                raise RuntimeError(
                    "Expected one dwell event row."
                )

            dwell_event = dwell_event_rows[0]

            print(
                f"  dwell {dwell}: "
                f"candidate_count={int(dwell_event['candidate_count'])}, "
                f"switch_confirmed="
                f"{dwell_event['active_switch_confirmed']}, "
                f"command={dwell_event['command_state']}"
            )


def main():
    selected_rows = load_selected_rule_rows()
    grouped = validate_selected_rule_rows(
        selected_rows
    )

    trace_rows = build_trace_rows(grouped)

    write_csv_rows(
        OUTPUT_CSV_PATH,
        trace_rows,
    )

    saved_rows = load_saved_trace_rows()
    save_trace_figure(saved_rows)
    print_event_summary(saved_rows)

    print("\n========================================")
    print("Session 21 Phase 2A-3 execution: PASS")
    print(
        f"Selected full-stream rows: "
        f"{len(selected_rows)}"
    )
    print(
        f"Event-trace rows: {len(saved_rows)}"
    )
    print(
        "Selected rules: 6 "
        "(2 smoothing modes × 3 dwell values)"
    )
    print(
        "Threshold: threshold_gap_midpoint"
    )
    print(
        "CSV: "
        f"{OUTPUT_CSV_PATH.relative_to(PROJECT_ROOT)}"
    )
    print(
        "Figure: "
        f"{OUTPUT_FIGURE_PATH.relative_to(PROJECT_ROOT)}"
    )
    print("========================================")


if __name__ == "__main__":
    main()
