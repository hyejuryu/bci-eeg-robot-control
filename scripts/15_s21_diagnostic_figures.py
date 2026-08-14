"""Generate Session 21 Phase 1 diagnostic figures from validated outputs."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SESSION14_FEATURE_CSV = (
    PROJECT_ROOT
    / "results"
    / "session-14"
    / "eegbci_subject-001_runs-01-02_posterior-alpha_window-features.csv"
)

SESSION21_DECISION_STREAM_CSV = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_rule-grid_decision-stream.csv"
)

SESSION21_METADATA_JSON = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_analysis_metadata.json"
)

SESSION21_TEMPORAL_SUMMARY_CSV = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_feature-temporal-variability-summary.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "figures"
    / "session-21"
    / "diagnostics"
)

FEATURE_NAME = "posterior_alpha_mean_psd"

RUNS = (1, 2)
RUN_LABELS = {
    1: "Run 1 — baseline eyes open",
    2: "Run 2 — baseline eyes closed",
}

THRESHOLD_IDS = (
    "threshold_eo_q95",
    "threshold_gap_midpoint",
    "threshold_ec_q05",
)

THRESHOLD_LABELS = {
    "threshold_eo_q95": "EO Q95",
    "threshold_gap_midpoint": "Gap midpoint",
    "threshold_ec_q05": "EC Q05",
}

COMMAND_Y = {
    "CMD_STOP": 0,
    "CMD_OPEN": 1,
    "CMD_CLOSE": 2,
}

COMMAND_Y_TICKS = [0, 1, 2]
COMMAND_Y_LABELS = ["STOP", "OPEN", "CLOSE"]

WINDOW_CONFIGS_COMMON_STEP = (
    ("win-1s_step-1s", "1 s window"),
    ("win-2s_step-1s", "2 s window"),
    ("win-4s_step-1s", "4 s window"),
)

EXPECTED_WINDOW_COUNTS = {
    "win-1s_step-1s": 60,
    "win-2s_step-1s": 59,
    "win-4s_step-1s": 57,
}

THRESHOLD_SLICE_RULES = (
    ("thr-eo-q95__smooth-none__dwell-1", "EO Q95"),
    ("thr-gap-mid__smooth-none__dwell-1", "Gap midpoint"),
    ("thr-ec-q05__smooth-none__dwell-1", "EC Q05"),
)

SMOOTHING_SLICE_RULES = (
    ("thr-gap-mid__smooth-none__dwell-1", "No smoothing"),
    ("thr-gap-mid__smooth-median3__dwell-1", "Causal median-3"),
)

DWELL_RULES_BY_RUN = {
    1: (
        "threshold_eo_q95",
        (
            ("thr-eo-q95__smooth-none__dwell-1", "Dwell 1"),
            ("thr-eo-q95__smooth-none__dwell-2", "Dwell 2"),
            ("thr-eo-q95__smooth-none__dwell-3", "Dwell 3"),
        ),
    ),
    2: (
        "threshold_ec_q05",
        (
            ("thr-ec-q05__smooth-none__dwell-1", "Dwell 1"),
            ("thr-ec-q05__smooth-none__dwell-2", "Dwell 2"),
            ("thr-ec-q05__smooth-none__dwell-3", "Dwell 3"),
        ),
    ),
}


def read_csv_rows(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")
        return list(reader), list(reader.fieldnames)


def read_metadata():
    if not SESSION21_METADATA_JSON.exists():
        raise FileNotFoundError(SESSION21_METADATA_JSON)

    with open(SESSION21_METADATA_JSON, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    return metadata


def load_thresholds(metadata):
    try:
        thresholds = metadata["phase1a"]["fixed_thresholds_by_subject"]["1"]
    except KeyError as exc:
        raise RuntimeError(
            "Session 21 metadata does not contain fixed Subject 1 thresholds."
        ) from exc

    missing = set(THRESHOLD_IDS) - set(thresholds)
    if missing:
        raise RuntimeError(
            f"Missing threshold IDs in metadata: {sorted(missing)}"
        )

    return {
        threshold_id: float(thresholds[threshold_id])
        for threshold_id in THRESHOLD_IDS
    }


def load_session14_features():
    rows, header = read_csv_rows(SESSION14_FEATURE_CSV)

    required = {
        "subject",
        "run",
        "condition",
        "configuration_id",
        "window_index",
        "window_end_sec",
        FEATURE_NAME,
    }
    missing = required - set(header)
    if missing:
        raise RuntimeError(
            f"Session 14 feature CSV is missing columns: {sorted(missing)}"
        )

    converted = []
    for row in rows:
        converted.append({
            "subject": int(row["subject"]),
            "run": int(row["run"]),
            "condition": row["condition"],
            "configuration_id": row["configuration_id"],
            "window_index": int(row["window_index"]),
            "window_end_sec": float(row["window_end_sec"]),
            FEATURE_NAME: float(row[FEATURE_NAME]),
        })

    return converted


def load_session21_decisions():
    rows, header = read_csv_rows(SESSION21_DECISION_STREAM_CSV)

    required = {
        "rule_id",
        "run",
        "condition",
        "window_index",
        "window_start_sec",
        "decision_time_sec",
        "raw_feature_value",
        "smoothed_available",
        "smoothed_feature_value",
        "command_state",
    }
    missing = required - set(header)
    if missing:
        raise RuntimeError(
            f"Session 21 decision stream is missing columns: {sorted(missing)}"
        )

    return rows


def load_session21_temporal_summary():
    rows, header = read_csv_rows(SESSION21_TEMPORAL_SUMMARY_CSV)

    required = {
        "run",
        "configuration_id",
        "window_length_sec",
        "step_size_sec",
        "successive_difference_sd_population",
        "median_absolute_successive_change",
        "comparison_role",
    }
    missing = required - set(header)
    if missing:
        raise RuntimeError(
            "Session 21 temporal summary is missing columns: "
            f"{sorted(missing)}"
        )

    return rows


def parse_bool(value):
    normalized = str(value).strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def select_decision_rows(rows, rule_id, run):
    selected = [
        row
        for row in rows
        if row["rule_id"] == rule_id and int(row["run"]) == run
    ]
    selected.sort(key=lambda row: int(row["window_index"]))

    if len(selected) != 59:
        raise RuntimeError(
            f"Expected 59 decision rows for {rule_id}, run {run}; "
            f"found {len(selected)}."
        )

    indices = [int(row["window_index"]) for row in selected]
    if indices != list(range(59)):
        raise RuntimeError(
            f"Decision rows are not complete/ordered for {rule_id}, run {run}."
        )

    return selected


def select_feature_rows(rows, configuration_id, run):
    selected = [
        row
        for row in rows
        if (
            row["configuration_id"] == configuration_id
            and int(row["run"]) == run
        )
    ]
    selected.sort(key=lambda row: int(row["window_index"]))

    expected = EXPECTED_WINDOW_COUNTS.get(configuration_id)
    if expected is not None and len(selected) != expected:
        raise RuntimeError(
            f"Expected {expected} rows for {configuration_id}, run {run}; "
            f"found {len(selected)}."
        )

    if not selected:
        raise RuntimeError(
            f"No feature rows for {configuration_id}, run {run}."
        )

    return selected


def decision_time_and_raw(rows):
    time = np.asarray(
        [float(row["decision_time_sec"]) for row in rows],
        dtype=float,
    )
    raw = np.asarray(
        [float(row["raw_feature_value"]) for row in rows],
        dtype=float,
    )
    return time, raw


def median3_values(rows):
    values = []
    for row in rows:
        if not parse_bool(row["smoothed_available"]):
            values.append(np.nan)
        else:
            values.append(float(row["smoothed_feature_value"]))
    return np.asarray(values, dtype=float)


def command_values(rows):
    try:
        return np.asarray(
            [COMMAND_Y[row["command_state"]] for row in rows],
            dtype=int,
        )
    except KeyError as exc:
        raise RuntimeError(
            f"Unexpected command state: {exc.args[0]}"
        ) from exc


def command_timeline_with_initial_stop(rows):
    if not rows:
        raise RuntimeError("No decision rows were supplied.")

    run_start_time_sec = float(rows[0]["window_start_sec"])
    decision_times = np.asarray(
        [float(row["decision_time_sec"]) for row in rows],
        dtype=float,
    )
    commands = command_values(rows)

    timeline_times = np.concatenate(
        ([run_start_time_sec], decision_times)
    )
    timeline_commands = np.concatenate(
        ([COMMAND_Y["CMD_STOP"]], commands)
    )

    return timeline_times, timeline_commands


def configure_command_axis(axis):
    axis.set_yticks(COMMAND_Y_TICKS)
    axis.set_yticklabels(COMMAND_Y_LABELS)
    axis.set_ylim(-0.25, 2.25)
    axis.grid(alpha=0.25)


def add_threshold_lines(axis, thresholds, threshold_ids=THRESHOLD_IDS):
    line_styles = ("--", "-.", ":")
    for threshold_id, line_style in zip(threshold_ids, line_styles):
        axis.axhline(
            thresholds[threshold_id],
            linestyle=line_style,
            linewidth=1.1,
            label=THRESHOLD_LABELS[threshold_id],
        )


def save_figure(figure, filename):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / filename
    figure.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(figure)

    if not output_path.exists() or output_path.stat().st_size == 0:
        raise RuntimeError(f"Figure was not saved correctly: {output_path}")

    return output_path


def make_window_length_successive_change(feature_rows):
    figure, axes = plt.subplots(
        nrows=2,
        ncols=2,
        figsize=(15, 9),
        sharex=False,
    )

    for column, run in enumerate(RUNS):
        raw_axis = axes[0, column]
        change_axis = axes[1, column]

        for configuration_id, label in WINDOW_CONFIGS_COMMON_STEP:
            rows = select_feature_rows(
                feature_rows,
                configuration_id,
                run,
            )
            time = np.asarray(
                [row["window_end_sec"] for row in rows],
                dtype=float,
            )
            values = np.asarray(
                [row[FEATURE_NAME] for row in rows],
                dtype=float,
            )

            raw_axis.plot(
                time,
                values,
                marker="o",
                markersize=2.5,
                linewidth=1.1,
                label=label,
            )

            absolute_changes = np.abs(np.diff(values))
            change_axis.plot(
                time[1:],
                absolute_changes,
                marker="o",
                markersize=2.5,
                linewidth=1.1,
                label=label,
            )

        raw_axis.set_title(f"{RUN_LABELS[run]} — raw feature")
        raw_axis.set_ylabel("Posterior alpha mean PSD (V²/Hz)")
        raw_axis.grid(alpha=0.25)
        raw_axis.legend(fontsize=9)

        change_axis.set_title(
            f"{RUN_LABELS[run]} — absolute successive change"
        )
        change_axis.set_xlabel("Window end time (s)")
        change_axis.set_ylabel("|Δx| (V²/Hz)")
        change_axis.grid(alpha=0.25)
        change_axis.legend(fontsize=9)

    figure.suptitle(
        "Session 21 Diagnostic: Window Length and Successive Change "
        "(Step Fixed at 1 s)",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))

    return save_figure(
        figure,
        "session21_diag_window-length-successive-change.png",
    )


def make_successive_change_metric_comparison(temporal_rows):
    primary_ids = (
        "win-1s_step-1s",
        "win-2s_step-1s",
        "win-4s_step-1s",
    )

    row_map = {
        (row["configuration_id"], int(row["run"])): row
        for row in temporal_rows
        if row["configuration_id"] in primary_ids
    }

    expected_keys = {
        (configuration_id, run)
        for configuration_id in primary_ids
        for run in RUNS
    }
    if set(row_map) != expected_keys:
        missing = expected_keys - set(row_map)
        extra = set(row_map) - expected_keys
        raise RuntimeError(
            "Unexpected primary temporal-summary groups. "
            f"Missing={sorted(missing)}, extra={sorted(extra)}"
        )

    window_labels = ["1 s", "2 s", "4 s"]
    x = np.arange(len(primary_ids))
    width = 0.34

    figure, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(13, 5.5),
        sharey=False,
    )

    for axis, run in zip(axes, RUNS):
        volatility = np.asarray(
            [
                float(
                    row_map[(configuration_id, run)][
                        "successive_difference_sd_population"
                    ]
                )
                for configuration_id in primary_ids
            ],
            dtype=float,
        )
        median_change = np.asarray(
            [
                float(
                    row_map[(configuration_id, run)][
                        "median_absolute_successive_change"
                    ]
                )
                for configuration_id in primary_ids
            ],
            dtype=float,
        )

        axis.bar(
            x - width / 2,
            volatility,
            width=width,
            label="SD(Δx)",
        )
        axis.bar(
            x + width / 2,
            median_change,
            width=width,
            label="Median |Δx|",
        )

        axis.set_xticks(x)
        axis.set_xticklabels(window_labels)
        axis.set_xlabel("Window length (step fixed at 1 s)")
        axis.set_ylabel("Successive-change magnitude (V²/Hz)")
        axis.set_title(RUN_LABELS[run])
        axis.grid(axis="y", alpha=0.25)
        axis.legend()

    figure.suptitle(
        "Session 21 Diagnostic: SD(Δx) vs Median |Δx|",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))

    return save_figure(
        figure,
        "session21_diag_successive-change-metric-comparison.png",
    )


def make_threshold_command_slice(decision_rows, thresholds):
    figure, axes = plt.subplots(
        nrows=4,
        ncols=2,
        figsize=(15, 12),
        sharex="col",
    )

    for column, run in enumerate(RUNS):
        top_axis = axes[0, column]

        base_rows = select_decision_rows(
            decision_rows,
            THRESHOLD_SLICE_RULES[0][0],
            run,
        )
        time, raw = decision_time_and_raw(base_rows)

        top_axis.plot(time, raw, label="Raw feature")
        add_threshold_lines(top_axis, thresholds)
        top_axis.set_title(RUN_LABELS[run])
        top_axis.set_ylabel("PSD (V²/Hz)")
        top_axis.grid(alpha=0.25)
        top_axis.legend(fontsize=8)

        for row_index, (rule_id, label) in enumerate(
            THRESHOLD_SLICE_RULES,
            start=1,
        ):
            axis = axes[row_index, column]
            rows = select_decision_rows(
                decision_rows,
                rule_id,
                run,
            )
            command_time, commands = (
                command_timeline_with_initial_stop(rows)
            )

            axis.step(
                command_time,
                commands,
                where="post",
            )
            axis.set_ylabel(label)
            configure_command_axis(axis)

        axes[-1, column].set_xlabel("Decision time (s)")

    figure.suptitle(
        "Session 21 Diagnostic: Threshold-to-Command Slice "
        "(No Smoothing, Dwell 1)",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))

    return save_figure(
        figure,
        "session21_diag_threshold-command-slice.png",
    )


def make_smoothing_command_slice(decision_rows, thresholds):
    figure, axes = plt.subplots(
        nrows=3,
        ncols=2,
        figsize=(15, 10),
        sharex="col",
    )

    midpoint = thresholds["threshold_gap_midpoint"]

    for column, run in enumerate(RUNS):
        raw_rows = select_decision_rows(
            decision_rows,
            SMOOTHING_SLICE_RULES[0][0],
            run,
        )
        median_rows = select_decision_rows(
            decision_rows,
            SMOOTHING_SLICE_RULES[1][0],
            run,
        )

        time, raw = decision_time_and_raw(raw_rows)
        median3 = median3_values(median_rows)

        top_axis = axes[0, column]
        top_axis.plot(time, raw, label="Raw feature")
        top_axis.plot(time, median3, label="Causal median-3")
        top_axis.axhline(
            midpoint,
            linestyle="--",
            linewidth=1.1,
            label="Gap midpoint",
        )
        top_axis.set_title(RUN_LABELS[run])
        top_axis.set_ylabel("PSD (V²/Hz)")
        top_axis.grid(alpha=0.25)
        top_axis.legend(fontsize=8)

        for row_index, (rule_id, label) in enumerate(
            SMOOTHING_SLICE_RULES,
            start=1,
        ):
            axis = axes[row_index, column]
            rows = select_decision_rows(
                decision_rows,
                rule_id,
                run,
            )
            command_time, commands = (
                command_timeline_with_initial_stop(rows)
            )

            axis.step(
                command_time,
                commands,
                where="post",
            )
            axis.set_ylabel(label)
            configure_command_axis(axis)

        axes[-1, column].set_xlabel("Decision time (s)")

    figure.suptitle(
        "Session 21 Diagnostic: Smoothing-to-Command Slice "
        "(Gap Midpoint, Dwell 1)",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))

    return save_figure(
        figure,
        "session21_diag_smoothing-command-slice.png",
    )


def make_dwell_command_slice(decision_rows, thresholds):
    figure, axes = plt.subplots(
        nrows=4,
        ncols=2,
        figsize=(15, 12),
        sharex="col",
    )

    for column, run in enumerate(RUNS):
        threshold_id, dwell_rules = DWELL_RULES_BY_RUN[run]
        threshold_value = thresholds[threshold_id]

        base_rows = select_decision_rows(
            decision_rows,
            dwell_rules[0][0],
            run,
        )
        time, raw = decision_time_and_raw(base_rows)

        top_axis = axes[0, column]
        top_axis.plot(time, raw, label="Raw feature")
        top_axis.axhline(
            threshold_value,
            linestyle="--",
            linewidth=1.1,
            label=THRESHOLD_LABELS[threshold_id],
        )
        top_axis.set_title(
            f"{RUN_LABELS[run]} — {THRESHOLD_LABELS[threshold_id]}"
        )
        top_axis.set_ylabel("PSD (V²/Hz)")
        top_axis.grid(alpha=0.25)
        top_axis.legend(fontsize=8)

        for row_index, (rule_id, label) in enumerate(
            dwell_rules,
            start=1,
        ):
            axis = axes[row_index, column]
            rows = select_decision_rows(
                decision_rows,
                rule_id,
                run,
            )
            command_time, commands = (
                command_timeline_with_initial_stop(rows)
            )

            axis.step(
                command_time,
                commands,
                where="post",
            )
            axis.set_ylabel(label)
            configure_command_axis(axis)

        axes[-1, column].set_xlabel("Decision time (s)")

    figure.suptitle(
        "Session 21 Diagnostic: Dwell-to-Command Slice "
        "(No Smoothing; Run-Specific Sensitive Threshold)",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.96))

    return save_figure(
        figure,
        "session21_diag_dwell-command-slice.png",
    )


def main():
    metadata = read_metadata()
    thresholds = load_thresholds(metadata)
    feature_rows = load_session14_features()
    decision_rows = load_session21_decisions()
    temporal_rows = load_session21_temporal_summary()

    generated = [
        make_window_length_successive_change(
            feature_rows,
        ),
        make_successive_change_metric_comparison(
            temporal_rows,
        ),
        make_threshold_command_slice(
            decision_rows,
            thresholds,
        ),
        make_smoothing_command_slice(
            decision_rows,
            thresholds,
        ),
        make_dwell_command_slice(
            decision_rows,
            thresholds,
        ),
    ]

    print("\n========================================")
    print("Session 21 diagnostic figures: PASS")
    for path in generated:
        print(path.relative_to(PROJECT_ROOT))
    print("========================================")


if __name__ == "__main__":
    main()