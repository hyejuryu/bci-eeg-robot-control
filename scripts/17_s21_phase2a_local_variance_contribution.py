"""Session 21 Phase 2A-2 local successive-change variance contribution."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
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

PHASE1_TEMPORAL_SUMMARY_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_feature-temporal-variability-summary.csv"
)

OUTPUT_CSV_PATH = (
    PROJECT_ROOT
    / "results"
    / "session-21"
    / "session21_phase2a_local-variance-contribution.csv"
)

OUTPUT_FIGURE_PATH = (
    PROJECT_ROOT
    / "figures"
    / "session-21"
    / "phase2a"
    / "session21_phase2a_local-variance-contribution.png"
)

SUBJECT = 1
RUN = 1
CONDITION = "baseline_eyes_open"
CONFIGURATION_ID = "win-2s_step-1s"
FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

EXPECTED_SOURCE_ROW_COUNT = 646
EXPECTED_FEATURE_COUNT = 59
EXPECTED_DIFFERENCE_COUNT = 58

SELECTED_WINDOW_START_SEC = 24.0
SELECTED_WINDOW_END_SEC = 26.0

RTOL = 1e-12
ATOL = 1e-15

SOURCE_REQUIRED_COLUMNS = {
    "subject",
    "run",
    "condition",
    "configuration_id",
    "window_index",
    "window_start_sec",
    "window_end_sec",
    "feature_name",
    "feature_unit",
    FEATURE_NAME,
}

PHASE1_REQUIRED_COLUMNS = {
    "subject",
    "run",
    "condition",
    "configuration_id",
    "n_features",
    "n_differences",
    "successive_difference_sd_population",
    "comparison_role",
}

OUTPUT_COLUMNS = [
    "subject",
    "run",
    "condition",
    "configuration_id",
    "feature_name",
    "feature_unit",
    "difference_index",
    "from_window_index",
    "to_window_index",
    "from_window_start_sec",
    "from_window_end_sec",
    "to_window_start_sec",
    "to_window_end_sec",
    "difference_time_sec",
    "from_feature_value",
    "to_feature_value",
    "successive_difference",
    "absolute_successive_difference",
    "mean_successive_difference",
    "centered_successive_difference",
    "squared_deviation_from_mean",
    "variance_contribution_fraction",
    "variance_contribution_percent",
    "absolute_difference_rank",
    "variance_contribution_rank",
    "selected_event_change",
    "selected_event_relation",
]


def read_csv_rows(path):
    if not path.exists():
        raise FileNotFoundError(path)

    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise RuntimeError(f"CSV has no header: {path}")
        return list(reader), list(reader.fieldnames)


def write_csv_rows(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="raise",
        )
        writer.writeheader()
        writer.writerows(rows)


def assert_float_close(actual, expected, label):
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


def load_target_feature_rows():
    raw_rows, fieldnames = read_csv_rows(
        SOURCE_FEATURE_CSV_PATH
    )

    missing = SOURCE_REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise RuntimeError(
            "Session 14 feature CSV is missing columns: "
            f"{sorted(missing)}"
        )

    if len(raw_rows) != EXPECTED_SOURCE_ROW_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_ROW_COUNT} Session 14 rows, "
            f"found {len(raw_rows)}."
        )

    selected = []

    for row in raw_rows:
        if (
            int(row["subject"]) != SUBJECT
            or int(row["run"]) != RUN
            or row["condition"] != CONDITION
            or row["configuration_id"] != CONFIGURATION_ID
        ):
            continue

        if row["feature_name"] != FEATURE_NAME:
            raise RuntimeError("Unexpected feature name.")
        if row["feature_unit"] != FEATURE_UNIT:
            raise RuntimeError("Unexpected feature unit.")

        selected.append({
            "subject": int(row["subject"]),
            "run": int(row["run"]),
            "condition": row["condition"],
            "configuration_id": row["configuration_id"],
            "window_index": int(row["window_index"]),
            "window_start_sec": float(row["window_start_sec"]),
            "window_end_sec": float(row["window_end_sec"]),
            "feature_name": row["feature_name"],
            "feature_unit": row["feature_unit"],
            FEATURE_NAME: float(row[FEATURE_NAME]),
        })

    selected.sort(key=lambda row: row["window_index"])

    if len(selected) != EXPECTED_FEATURE_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_FEATURE_COUNT} target feature rows, "
            f"found {len(selected)}."
        )

    indices = [row["window_index"] for row in selected]
    if indices != list(range(EXPECTED_FEATURE_COUNT)):
        raise RuntimeError(
            "Target feature window indices are incomplete."
        )

    end_times = np.asarray(
        [row["window_end_sec"] for row in selected],
        dtype=float,
    )
    feature_values = np.asarray(
        [row[FEATURE_NAME] for row in selected],
        dtype=float,
    )

    if not np.isfinite(end_times).all():
        raise RuntimeError("Target window times contain non-finite values.")
    if not np.isfinite(feature_values).all():
        raise RuntimeError("Target feature values contain non-finite values.")
    if np.any(feature_values <= 0.0):
        raise RuntimeError("Target PSD feature values must be positive.")
    if np.any(np.diff(end_times) <= 0.0):
        raise RuntimeError("Target feature rows are not chronological.")

    event_rows = [
        row
        for row in selected
        if np.isclose(
            row["window_start_sec"],
            SELECTED_WINDOW_START_SEC,
            rtol=RTOL,
            atol=ATOL,
        )
        and np.isclose(
            row["window_end_sec"],
            SELECTED_WINDOW_END_SEC,
            rtol=RTOL,
            atol=ATOL,
        )
    ]

    if len(event_rows) != 1:
        raise RuntimeError(
            "Expected exactly one pre-identified 24-26 s feature window."
        )

    event_index = event_rows[0]["window_index"]

    if event_index <= 0 or event_index >= len(selected) - 1:
        raise RuntimeError(
            "Selected event window must have both neighboring windows."
        )

    return selected, event_index


def load_phase1_reference():
    rows, fieldnames = read_csv_rows(
        PHASE1_TEMPORAL_SUMMARY_CSV_PATH
    )

    missing = PHASE1_REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise RuntimeError(
            "Phase 1 temporal summary is missing columns: "
            f"{sorted(missing)}"
        )

    matching = [
        row
        for row in rows
        if (
            int(row["subject"]) == SUBJECT
            and int(row["run"]) == RUN
            and row["condition"] == CONDITION
            and row["configuration_id"] == CONFIGURATION_ID
        )
    ]

    if len(matching) != 1:
        raise RuntimeError(
            "Expected exactly one Phase 1 reference row."
        )

    reference = matching[0]

    if int(reference["n_features"]) != EXPECTED_FEATURE_COUNT:
        raise RuntimeError(
            "Phase 1 reference feature count is inconsistent."
        )
    if int(reference["n_differences"]) != EXPECTED_DIFFERENCE_COUNT:
        raise RuntimeError(
            "Phase 1 reference difference count is inconsistent."
        )
    if reference["comparison_role"] != "primary_common_step_1s":
        raise RuntimeError(
            "Target Phase 1 condition is not a primary common-step row."
        )

    return reference


def descending_ranks(values):
    order = np.argsort(-np.asarray(values, dtype=float))
    ranks = np.empty(len(order), dtype=int)

    for rank, index in enumerate(order, start=1):
        ranks[index] = rank

    return ranks


def build_contribution_rows(feature_rows, event_index):
    feature_values = np.asarray(
        [row[FEATURE_NAME] for row in feature_rows],
        dtype=float,
    )
    differences = np.diff(feature_values)

    if len(differences) != EXPECTED_DIFFERENCE_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_DIFFERENCE_COUNT} differences, "
            f"found {len(differences)}."
        )

    mean_difference = float(np.mean(differences))
    volatility = float(np.std(differences, ddof=0))
    centered = differences - mean_difference
    squared_deviations = np.square(centered)
    total_squared_deviation = float(np.sum(squared_deviations))

    if total_squared_deviation <= 0.0:
        raise RuntimeError(
            "Total successive-difference squared deviation "
            "must be positive."
        )

    contribution_fractions = (
        squared_deviations / total_squared_deviation
    )
    absolute_differences = np.abs(differences)

    abs_ranks = descending_ranks(absolute_differences)
    contribution_ranks = descending_ranks(
        contribution_fractions
    )

    output_rows = []

    for difference_index in range(len(differences)):
        from_row = feature_rows[difference_index]
        to_row = feature_rows[difference_index + 1]

        enters_selected_window = (
            to_row["window_index"] == event_index
        )
        exits_selected_window = (
            from_row["window_index"] == event_index
        )

        if enters_selected_window:
            relation = "enter_selected_24_26_window"
        elif exits_selected_window:
            relation = "exit_selected_24_26_window"
        else:
            relation = "other"

        selected_event_change = (
            enters_selected_window or exits_selected_window
        )

        output_rows.append({
            "subject": SUBJECT,
            "run": RUN,
            "condition": CONDITION,
            "configuration_id": CONFIGURATION_ID,
            "feature_name": FEATURE_NAME,
            "feature_unit": FEATURE_UNIT,
            "difference_index": difference_index,
            "from_window_index": from_row["window_index"],
            "to_window_index": to_row["window_index"],
            "from_window_start_sec": from_row["window_start_sec"],
            "from_window_end_sec": from_row["window_end_sec"],
            "to_window_start_sec": to_row["window_start_sec"],
            "to_window_end_sec": to_row["window_end_sec"],
            "difference_time_sec": to_row["window_end_sec"],
            "from_feature_value": from_row[FEATURE_NAME],
            "to_feature_value": to_row[FEATURE_NAME],
            "successive_difference": float(
                differences[difference_index]
            ),
            "absolute_successive_difference": float(
                absolute_differences[difference_index]
            ),
            "mean_successive_difference": mean_difference,
            "centered_successive_difference": float(
                centered[difference_index]
            ),
            "squared_deviation_from_mean": float(
                squared_deviations[difference_index]
            ),
            "variance_contribution_fraction": float(
                contribution_fractions[difference_index]
            ),
            "variance_contribution_percent": float(
                100.0 * contribution_fractions[difference_index]
            ),
            "absolute_difference_rank": int(
                abs_ranks[difference_index]
            ),
            "variance_contribution_rank": int(
                contribution_ranks[difference_index]
            ),
            "selected_event_change": selected_event_change,
            "selected_event_relation": relation,
        })

    if len(output_rows) != EXPECTED_DIFFERENCE_COUNT:
        raise RuntimeError(
            "Contribution-row count does not match difference count."
        )

    selected_rows = [
        row
        for row in output_rows
        if row["selected_event_change"]
    ]

    if len(selected_rows) != 2:
        raise RuntimeError(
            "Expected exactly two successive changes associated with "
            "the selected 24-26 s feature window."
        )

    if not np.isclose(
        sum(
            row["variance_contribution_fraction"]
            for row in output_rows
        ),
        1.0,
        rtol=RTOL,
        atol=ATOL,
    ):
        raise RuntimeError(
            "Variance-contribution fractions do not sum to one."
        )

    return (
        output_rows,
        selected_rows,
        volatility,
        mean_difference,
        total_squared_deviation,
    )


def validate_against_phase1(volatility, reference):
    assert_float_close(
        volatility,
        reference["successive_difference_sd_population"],
        "Phase 1 Run 1 2 s-window SD(Δx) reproduction",
    )


def validate_saved_rows(rows):
    if len(rows) != EXPECTED_DIFFERENCE_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_DIFFERENCE_COUNT} reloaded rows, "
            f"found {len(rows)}."
        )

    selected_count = sum(
        row["selected_event_change"] == "True"
        for row in rows
    )
    if selected_count != 2:
        raise RuntimeError(
            "Reloaded output does not contain exactly two "
            "selected event changes."
        )

    fractions = np.asarray(
        [
            float(row["variance_contribution_fraction"])
            for row in rows
        ],
        dtype=float,
    )

    if not np.isfinite(fractions).all():
        raise RuntimeError(
            "Reloaded contribution fractions contain non-finite values."
        )

    if not np.isclose(
        np.sum(fractions),
        1.0,
        rtol=RTOL,
        atol=ATOL,
    ):
        raise RuntimeError(
            "Reloaded variance-contribution fractions do not sum to one."
        )


def save_figure(rows):
    times = np.asarray(
        [float(row["difference_time_sec"]) for row in rows],
        dtype=float,
    )
    abs_changes = np.asarray(
        [
            float(row["absolute_successive_difference"])
            for row in rows
        ],
        dtype=float,
    )
    contributions = np.asarray(
        [
            float(row["variance_contribution_percent"])
            for row in rows
        ],
        dtype=float,
    )
    selected_mask = np.asarray(
        [row["selected_event_change"] == "True" for row in rows],
        dtype=bool,
    )

    figure, axes = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(12, 8),
        sharex=True,
    )

    axes[0].plot(
        times,
        abs_changes,
        marker="o",
        markersize=3,
        linewidth=1.1,
        label="|Δx|",
    )
    axes[0].scatter(
        times[selected_mask],
        abs_changes[selected_mask],
        marker="s",
        s=60,
        label="24–26 s event-associated changes",
    )
    axes[0].set_ylabel("|Δx| (V²/Hz)")
    axes[0].set_title(
        "A. Absolute successive changes"
    )
    axes[0].grid(alpha=0.25)
    axes[0].legend()

    axes[1].plot(
        times,
        contributions,
        marker="o",
        markersize=3,
        linewidth=1.1,
        label="Variance contribution",
    )
    axes[1].scatter(
        times[selected_mask],
        contributions[selected_mask],
        marker="s",
        s=60,
        label="24–26 s event-associated changes",
    )
    axes[1].set_xlabel(
        "Successive-change destination time (s)"
    )
    axes[1].set_ylabel(
        "Contribution to successive-difference variance (%)"
    )
    axes[1].set_title(
        "B. Per-change contribution to recording-level variance"
    )
    axes[1].grid(alpha=0.25)
    axes[1].legend()

    selected_percent = float(
        np.sum(contributions[selected_mask])
    )
    axes[1].text(
        0.02,
        0.95,
        (
            "Selected two changes: "
            f"{selected_percent:.1f}% of total variance contribution"
        ),
        transform=axes[1].transAxes,
        va="top",
    )

    figure.suptitle(
        "Session 21 Phase 2A-2: "
        "Run 1 Local Successive-Change Variance Contribution",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))

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
            "Local variance-contribution figure was not saved correctly."
        )


def print_selected_event_summary(
    selected_rows,
    volatility,
    mean_difference,
    total_squared_deviation,
):
    selected_fraction = sum(
        row["variance_contribution_fraction"]
        for row in selected_rows
    )

    print("\nSelected 24-26 s event-associated changes:")
    for row in selected_rows:
        print(
            f"{row['selected_event_relation']}: "
            f"time={row['difference_time_sec']:.1f}s, "
            f"dx={row['successive_difference']:.8g}, "
            f"|dx| rank={row['absolute_difference_rank']}, "
            f"variance rank={row['variance_contribution_rank']}, "
            f"contribution={row['variance_contribution_percent']:.2f}%"
        )

    print(
        "Combined selected-event variance contribution: "
        f"{100.0 * selected_fraction:.2f}%"
    )
    print(f"Recording SD(dx), ddof=0: {volatility:.8g}")
    print(f"Mean(dx): {mean_difference:.8g}")
    print(
        "Total centered squared-deviation sum: "
        f"{total_squared_deviation:.8g}"
    )


def main():
    feature_rows, event_index = load_target_feature_rows()
    phase1_reference = load_phase1_reference()

    (
        contribution_rows,
        selected_rows,
        volatility,
        mean_difference,
        total_squared_deviation,
    ) = build_contribution_rows(
        feature_rows,
        event_index,
    )

    validate_against_phase1(
        volatility,
        phase1_reference,
    )

    write_csv_rows(
        OUTPUT_CSV_PATH,
        contribution_rows,
        OUTPUT_COLUMNS,
    )

    reloaded_rows, reloaded_fieldnames = read_csv_rows(
        OUTPUT_CSV_PATH
    )

    if reloaded_fieldnames != OUTPUT_COLUMNS:
        raise RuntimeError(
            "Reloaded output schema differs from expected schema."
        )

    validate_saved_rows(reloaded_rows)
    save_figure(reloaded_rows)

    print_selected_event_summary(
        selected_rows,
        volatility,
        mean_difference,
        total_squared_deviation,
    )

    print("\n========================================")
    print("Session 21 Phase 2A-2 execution: PASS")
    print(f"Target feature rows: {len(feature_rows)}")
    print(f"Successive differences: {len(contribution_rows)}")
    print("Phase 1 SD(dx) reproduction: PASS")
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
