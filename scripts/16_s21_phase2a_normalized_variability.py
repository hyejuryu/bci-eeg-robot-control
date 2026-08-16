"""Session 21 Phase 2A-1 normalized temporal-variability analysis."""

from __future__ import annotations

import csv
from collections import defaultdict
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
    / "session21_phase2a_normalized-variability-summary.csv"
)

OUTPUT_FIGURE_PATH = (
    PROJECT_ROOT
    / "figures"
    / "session-21"
    / "phase2a"
    / "session21_phase2a_normalized-variability.png"
)

OUTPUT_DIAGNOSTIC_FIGURE_PATH = (
    PROJECT_ROOT
    / "figures"
    / "session-21"
    / "phase2a"
    / "diagnostics"
    / (
        "session21_phase2a_"
        "normalized-successive-change-metric-comparison.png"
    )
)

SUBJECT = 1
RUNS = (1, 2)
RUN_CONDITIONS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}

RUN_DISPLAY_LABELS = {
    1: "Run 1 — baseline eyes open",
    2: "Run 2 — baseline eyes closed",
}
FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

CONFIGURATION_IDS = (
    "win-1s_step-1s",
    "win-2s_step-0p5s",
    "win-2s_step-1s",
    "win-2s_step-2s",
    "win-4s_step-1s",
)

PRIMARY_CONFIGURATION_IDS = (
    "win-1s_step-1s",
    "win-2s_step-1s",
    "win-4s_step-1s",
)

EXPECTED_WINDOW_COUNTS_PER_RUN = {
    "win-1s_step-1s": 60,
    "win-2s_step-0p5s": 117,
    "win-2s_step-1s": 59,
    "win-2s_step-2s": 30,
    "win-4s_step-1s": 57,
}

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

PHASE1_REQUIRED_COLUMNS = {
    "subject",
    "run",
    "condition",
    "configuration_id",
    "n_features",
    "n_differences",
    "successive_difference_sd_population",
    "median_absolute_successive_change",
    "comparison_role",
}

OUTPUT_COLUMNS = [
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
    "feature_median",
    "mean_successive_difference",
    "successive_difference_sd_population",
    "median_absolute_successive_change",
    "mssd",
    "rms_squared",
    "nmssd",
    "normalized_median_absolute_successive_change",
    "comparison_role",
]

RTOL = 1e-12
ATOL = 1e-15


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


def convert_source_rows(raw_rows, fieldnames):
    missing = SOURCE_REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise RuntimeError(
            "Session 14 feature CSV is missing columns: "
            f"{sorted(missing)}"
        )

    converted = []

    for raw in raw_rows:
        converted.append({
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
        })

    return converted


def validate_source_rows(rows):
    expected_total = 2 * sum(
        EXPECTED_WINDOW_COUNTS_PER_RUN.values()
    )

    if len(rows) != expected_total:
        raise RuntimeError(
            f"Expected {expected_total} Session 14 feature rows, "
            f"found {len(rows)}."
        )

    grouped = defaultdict(list)

    for row in rows:
        if row["subject"] != SUBJECT:
            raise RuntimeError("Unexpected subject in Session 14 source.")
        if row["run"] not in RUNS:
            raise RuntimeError("Unexpected run in Session 14 source.")
        if row["condition"] != RUN_CONDITIONS[row["run"]]:
            raise RuntimeError("Run/condition mapping mismatch.")
        if row["configuration_id"] not in CONFIGURATION_IDS:
            raise RuntimeError(
                f"Unexpected configuration: {row['configuration_id']}"
            )
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
            raise ValueError("Posterior-alpha PSD feature must be positive.")

        grouped[
            (row["configuration_id"], row["run"])
        ].append(row)

    expected_keys = {
        (configuration_id, run)
        for configuration_id in CONFIGURATION_IDS
        for run in RUNS
    }

    if set(grouped) != expected_keys:
        raise RuntimeError(
            "Session 14 configuration/run groups do not match "
            "the expected 10 groups."
        )

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
                    f"Non-chronological rows for "
                    f"{configuration_id}, run {run}."
                )

    return grouped


def load_phase1_reference_rows():
    raw_rows, fieldnames = read_csv_rows(
        PHASE1_TEMPORAL_SUMMARY_CSV_PATH
    )

    missing = PHASE1_REQUIRED_COLUMNS - set(fieldnames)
    if missing:
        raise RuntimeError(
            "Phase 1 temporal summary is missing columns: "
            f"{sorted(missing)}"
        )

    if len(raw_rows) != 10:
        raise RuntimeError(
            f"Expected 10 Phase 1 temporal-summary rows, "
            f"found {len(raw_rows)}."
        )

    reference_map = {}

    for row in raw_rows:
        key = (
            row["configuration_id"],
            int(row["run"]),
        )

        if key in reference_map:
            raise RuntimeError(
                f"Duplicate Phase 1 temporal-summary key: {key}"
            )

        reference_map[key] = row

    expected_keys = {
        (configuration_id, run)
        for configuration_id in CONFIGURATION_IDS
        for run in RUNS
    }

    if set(reference_map) != expected_keys:
        raise RuntimeError(
            "Phase 1 temporal-summary groups do not match "
            "the expected configuration/run groups."
        )

    return reference_map


def calculate_normalized_variability_rows(grouped_rows):
    output_rows = []

    for configuration_id in CONFIGURATION_IDS:
        for run in RUNS:
            rows = sorted(
                grouped_rows[(configuration_id, run)],
                key=lambda row: row["window_index"],
            )

            feature_values = np.asarray(
                [row[FEATURE_NAME] for row in rows],
                dtype=float,
            )
            differences = np.diff(feature_values)

            if len(differences) != len(feature_values) - 1:
                raise RuntimeError(
                    f"Difference-count mismatch for "
                    f"{configuration_id}, run {run}."
                )

            feature_median = float(np.median(feature_values))
            mean_difference = float(np.mean(differences))
            volatility = float(np.std(differences, ddof=0))
            median_absolute_change = float(
                np.median(np.abs(differences))
            )
            mssd = float(np.mean(np.square(differences)))
            rms_squared = float(
                np.mean(np.square(feature_values))
            )

            if feature_median <= 0.0:
                raise RuntimeError(
                    f"Non-positive feature median for "
                    f"{configuration_id}, run {run}."
                )
            if rms_squared <= 0.0:
                raise RuntimeError(
                    f"Non-positive RMS squared for "
                    f"{configuration_id}, run {run}."
                )

            nmssd = float(mssd / rms_squared)
            normalized_median_change = float(
                median_absolute_change / feature_median
            )

            result_values = np.asarray(
                [
                    feature_median,
                    mean_difference,
                    volatility,
                    median_absolute_change,
                    mssd,
                    rms_squared,
                    nmssd,
                    normalized_median_change,
                ],
                dtype=float,
            )
            if not np.isfinite(result_values).all():
                raise RuntimeError(
                    f"Non-finite normalized-variability result for "
                    f"{configuration_id}, run {run}."
                )

            identity_value = (
                volatility**2 + mean_difference**2
            )
            assert_float_close(
                mssd,
                identity_value,
                (
                    f"MSSD identity "
                    f"{configuration_id}, run {run}"
                ),
            )

            first_row = rows[0]

            output_rows.append({
                "subject": SUBJECT,
                "run": run,
                "condition": RUN_CONDITIONS[run],
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
                "feature_name": FEATURE_NAME,
                "feature_unit": FEATURE_UNIT,
                "n_features": len(feature_values),
                "n_differences": len(differences),
                "feature_median": feature_median,
                "mean_successive_difference": mean_difference,
                "successive_difference_sd_population": volatility,
                "median_absolute_successive_change": (
                    median_absolute_change
                ),
                "mssd": mssd,
                "rms_squared": rms_squared,
                "nmssd": nmssd,
                "normalized_median_absolute_successive_change": (
                    normalized_median_change
                ),
                "comparison_role": (
                    "primary_common_step_1s"
                    if configuration_id
                    in PRIMARY_CONFIGURATION_IDS
                    else "descriptive_cross_step"
                ),
            })

    if len(output_rows) != 10:
        raise RuntimeError(
            f"Expected 10 normalized-variability rows, "
            f"found {len(output_rows)}."
        )

    return output_rows


def validate_against_phase1(output_rows, phase1_reference_map):
    reproduced = 0

    for row in output_rows:
        key = (
            row["configuration_id"],
            int(row["run"]),
        )
        reference = phase1_reference_map[key]

        if int(reference["subject"]) != SUBJECT:
            raise RuntimeError(
                f"Phase 1 subject mismatch for {key}."
            )
        if reference["condition"] != row["condition"]:
            raise RuntimeError(
                f"Phase 1 condition mismatch for {key}."
            )
        if int(reference["n_features"]) != int(row["n_features"]):
            raise RuntimeError(
                f"Phase 1 feature-count mismatch for {key}."
            )
        if int(reference["n_differences"]) != int(
            row["n_differences"]
        ):
            raise RuntimeError(
                f"Phase 1 difference-count mismatch for {key}."
            )
        if reference["comparison_role"] != row["comparison_role"]:
            raise RuntimeError(
                f"Phase 1 comparison-role mismatch for {key}."
            )

        assert_float_close(
            row["successive_difference_sd_population"],
            reference["successive_difference_sd_population"],
            f"Phase 1 SD(Δx) reproduction {key}",
        )
        assert_float_close(
            row["median_absolute_successive_change"],
            reference["median_absolute_successive_change"],
            f"Phase 1 median(|Δx|) reproduction {key}",
        )

        reproduced += 1

    if reproduced != 10:
        raise RuntimeError(
            f"Expected 10 Phase 1 reproductions, found {reproduced}."
        )

    return reproduced


def validate_saved_rows(reloaded_rows):
    if len(reloaded_rows) != 10:
        raise RuntimeError(
            f"Expected 10 reloaded rows, found {len(reloaded_rows)}."
        )

    keys = {
        (
            row["configuration_id"],
            int(row["run"]),
        )
        for row in reloaded_rows
    }

    expected_keys = {
        (configuration_id, run)
        for configuration_id in CONFIGURATION_IDS
        for run in RUNS
    }

    if keys != expected_keys:
        raise RuntimeError(
            "Reloaded normalized-variability groups are incomplete."
        )

    for row in reloaded_rows:
        numeric_fields = [
            "feature_median",
            "mean_successive_difference",
            "successive_difference_sd_population",
            "median_absolute_successive_change",
            "mssd",
            "rms_squared",
            "nmssd",
            "normalized_median_absolute_successive_change",
        ]

        values = np.asarray(
            [float(row[field]) for field in numeric_fields],
            dtype=float,
        )

        if not np.isfinite(values).all():
            raise RuntimeError(
                "Reloaded normalized-variability output contains "
                "non-finite values."
            )

        if float(row["nmssd"]) < 0.0:
            raise RuntimeError("nMSSD must be non-negative.")
        if (
            float(
                row[
                    "normalized_median_absolute_successive_change"
                ]
            )
            < 0.0
        ):
            raise RuntimeError(
                "Normalized median absolute change must be non-negative."
            )


def normalized_metric_limits(reloaded_rows):
    nmssd_values = np.asarray(
        [float(row["nmssd"]) for row in reloaded_rows],
        dtype=float,
    )
    robust_values = np.asarray(
        [
            float(
                row[
                    "normalized_median_absolute_successive_change"
                ]
            )
            for row in reloaded_rows
        ],
        dtype=float,
    )

    nmssd_max = float(np.max(nmssd_values))
    robust_max = float(np.max(robust_values))

    nmssd_upper = 1.1 * nmssd_max if nmssd_max > 0.0 else 1.0
    robust_upper = (
        1.1 * robust_max if robust_max > 0.0 else 1.0
    )

    return (0.0, nmssd_upper), (0.0, robust_upper)


def save_normalized_variability_figure(reloaded_rows):
    row_map = {
        (
            row["configuration_id"],
            int(row["run"]),
        ): row
        for row in reloaded_rows
    }

    window_lengths = np.asarray(
        [1.0, 2.0, 4.0],
        dtype=float,
    )

    nmssd_ylim, robust_ylim = normalized_metric_limits(
        reloaded_rows
    )

    figure, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(13, 5.5),
    )

    nmssd_axis = axes[0]
    robust_axis = axes[1]

    for run in RUNS:
        nmssd_values = [
            float(
                row_map[(configuration_id, run)]["nmssd"]
            )
            for configuration_id in PRIMARY_CONFIGURATION_IDS
        ]
        robust_values = [
            float(
                row_map[(configuration_id, run)][
                    "normalized_median_absolute_successive_change"
                ]
            )
            for configuration_id in PRIMARY_CONFIGURATION_IDS
        ]

        nmssd_axis.plot(
            window_lengths,
            nmssd_values,
            marker="o",
            label=f"Run {run}",
        )
        robust_axis.plot(
            window_lengths,
            robust_values,
            marker="o",
            label=f"Run {run}",
        )

    nmssd_axis.set_xticks(window_lengths)
    nmssd_axis.set_xlabel(
        "Window length (s), step fixed at 1 s"
    )
    nmssd_axis.set_ylabel("nMSSD (dimensionless)")
    nmssd_axis.set_ylim(*nmssd_ylim)
    nmssd_axis.set_title(
        "A. Magnitude-normalized squared successive variability"
    )
    nmssd_axis.grid(alpha=0.25)
    nmssd_axis.legend()

    robust_axis.set_xticks(window_lengths)
    robust_axis.set_xlabel(
        "Window length (s), step fixed at 1 s"
    )
    robust_axis.set_ylabel(
        "Median |Δx| / median(x) (dimensionless)"
    )
    robust_axis.set_ylim(*robust_ylim)
    robust_axis.set_title(
        "B. Normalized robust successive change"
    )
    robust_axis.grid(alpha=0.25)
    robust_axis.legend()

    figure.suptitle(
        "Session 21 Phase 2A-1: "
        "Normalized Temporal Feature Variability",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.93))

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
            "Normalized-variability figure was not saved correctly."
        )


def save_normalized_metric_comparison_figure(reloaded_rows):
    row_map = {
        (
            row["configuration_id"],
            int(row["run"]),
        ): row
        for row in reloaded_rows
    }

    window_labels = ["1 s", "2 s", "4 s"]
    x = np.arange(len(PRIMARY_CONFIGURATION_IDS))
    width = 0.34

    all_primary_values = []

    for run in RUNS:
        for configuration_id in PRIMARY_CONFIGURATION_IDS:
            row = row_map[(configuration_id, run)]
            all_primary_values.extend(
                [
                    float(row["nmssd"]),
                    float(
                        row[
                            "normalized_median_absolute_successive_change"
                        ]
                    ),
                ]
            )

    common_upper = (
        1.1 * max(all_primary_values)
        if max(all_primary_values) > 0.0
        else 1.0
    )

    figure, axes = plt.subplots(
        nrows=1,
        ncols=2,
        figsize=(13, 5.5),
        sharey=True,
    )

    for axis, run in zip(axes, RUNS):
        nmssd_values = np.asarray(
            [
                float(
                    row_map[(configuration_id, run)]["nmssd"]
                )
                for configuration_id
                in PRIMARY_CONFIGURATION_IDS
            ],
            dtype=float,
        )
        robust_values = np.asarray(
            [
                float(
                    row_map[(configuration_id, run)][
                        "normalized_median_absolute_successive_change"
                    ]
                )
                for configuration_id
                in PRIMARY_CONFIGURATION_IDS
            ],
            dtype=float,
        )

        axis.bar(
            x - width / 2,
            nmssd_values,
            width=width,
            label="nMSSD",
        )
        axis.bar(
            x + width / 2,
            robust_values,
            width=width,
            label="Median |Δx| / median(x)",
        )

        axis.set_xticks(x)
        axis.set_xticklabels(window_labels)
        axis.set_xlabel(
            "Window length, step fixed at 1 s"
        )
        axis.set_ylim(0.0, common_upper)
        axis.set_title(RUN_DISPLAY_LABELS[run])
        axis.grid(axis="y", alpha=0.25)
        axis.legend(fontsize=9)

    axes[0].set_ylabel(
        "Normalized successive-change measure "
        "(dimensionless)"
    )

    figure.suptitle(
        "Session 21 Phase 2A-1 Diagnostic: "
        "Normalized Successive-Change Metric Comparison",
        fontsize=15,
    )
    figure.tight_layout(rect=(0.0, 0.0, 1.0, 0.94))

    OUTPUT_DIAGNOSTIC_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    figure.savefig(
        OUTPUT_DIAGNOSTIC_FIGURE_PATH,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(figure)

    if (
        not OUTPUT_DIAGNOSTIC_FIGURE_PATH.exists()
        or OUTPUT_DIAGNOSTIC_FIGURE_PATH.stat().st_size == 0
    ):
        raise RuntimeError(
            "Normalized metric-comparison figure "
            "was not saved correctly."
        )


def print_primary_results(reloaded_rows):
    row_map = {
        (
            row["configuration_id"],
            int(row["run"]),
        ): row
        for row in reloaded_rows
    }

    print("\nPrimary common-step comparison:")
    print(
        "run  configuration          nMSSD        "
        "median|dx|/median(x)"
    )

    for run in RUNS:
        for configuration_id in PRIMARY_CONFIGURATION_IDS:
            row = row_map[(configuration_id, run)]
            print(
                f"{run:<4} "
                f"{configuration_id:<22} "
                f"{float(row['nmssd']):.8g}   "
                f"{float(row['normalized_median_absolute_successive_change']):.8g}"
            )


def main():
    raw_source_rows, source_fieldnames = read_csv_rows(
        SOURCE_FEATURE_CSV_PATH
    )
    source_rows = convert_source_rows(
        raw_source_rows,
        source_fieldnames,
    )
    grouped_rows = validate_source_rows(source_rows)

    phase1_reference_map = load_phase1_reference_rows()

    output_rows = calculate_normalized_variability_rows(
        grouped_rows
    )

    reproduction_count = validate_against_phase1(
        output_rows,
        phase1_reference_map,
    )

    write_csv_rows(
        OUTPUT_CSV_PATH,
        output_rows,
        OUTPUT_COLUMNS,
    )

    reloaded_rows, reloaded_fieldnames = read_csv_rows(
        OUTPUT_CSV_PATH
    )

    if reloaded_fieldnames != OUTPUT_COLUMNS:
        raise RuntimeError(
            "Reloaded output schema differs from the expected schema."
        )

    validate_saved_rows(reloaded_rows)
    save_normalized_variability_figure(reloaded_rows)
    save_normalized_metric_comparison_figure(reloaded_rows)
    print_primary_results(reloaded_rows)

    print("\n========================================")
    print("Session 21 Phase 2A-1 execution: PASS")
    print(f"Source feature rows: {len(source_rows)}")
    print(f"Configuration/run groups: {len(grouped_rows)}")
    print(f"Phase 1 metric reproductions: {reproduction_count}")
    print(f"Normalized summary rows: {len(reloaded_rows)}")
    print(
        "CSV: "
        f"{OUTPUT_CSV_PATH.relative_to(PROJECT_ROOT)}"
    )
    print(
        "Canonical figure: "
        f"{OUTPUT_FIGURE_PATH.relative_to(PROJECT_ROOT)}"
    )
    print(
        "Diagnostic figure: "
        f"{OUTPUT_DIAGNOSTIC_FIGURE_PATH.relative_to(PROJECT_ROOT)}"
    )
    print("========================================")


if __name__ == "__main__":
    main()