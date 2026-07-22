# Session 14 supplementary figure script.
# Generates the step-size comparison figure from
# the saved window-level feature CSV.
#
# This script does not reload or preprocess raw EEG.

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


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

STEP_SIZE_COMPARISON_FIGURE_PATH = (
    PROJECT_ROOT
    / "figures"
    / "session-14"
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_step-size-comparison.png"
    )
)

EYES_OPEN_RUN = 1
EYES_CLOSED_RUN = 2

RUN_LABELS = {
    EYES_OPEN_RUN: "baseline_eyes_open",
    EYES_CLOSED_RUN: "baseline_eyes_closed",
}

STEP_SIZE_COMPARISON_IDS = [
    "win-2s_step-0p5s",
    "win-2s_step-1s",
    "win-2s_step-2s",
]

EXPECTED_WINDOWS_PER_RUN = {
    "win-2s_step-0p5s": 117,
    "win-2s_step-1s": 59,
    "win-2s_step-2s": 30,
}

EXPECTED_STEP_SIZE_SEC = {
    "win-2s_step-0p5s": 0.5,
    "win-2s_step-1s": 1.0,
    "win-2s_step-2s": 2.0,
}

EXPECTED_OVERLAP_FRACTION = {
    "win-2s_step-0p5s": 0.75,
    "win-2s_step-1s": 0.50,
    "win-2s_step-2s": 0.00,
}

STEP_SIZE_PLOT_STYLES = {
    "win-2s_step-0p5s": {
        "marker": ".",
        "markersize": 3.0,
        "linewidth": 0.9,
        "alpha": 0.65,
        "linestyle": "-",
        "zorder": 1,
    },
    "win-2s_step-1s": {
        "marker": "o",
        "markersize": 3.2,
        "linewidth": 1.1,
        "alpha": 0.85,
        "linestyle": "-",
        "zorder": 2,
    },
    "win-2s_step-2s": {
        "marker": "s",
        "markersize": 3.8,
        "linewidth": 1.0,
        "alpha": 0.95,
        "linestyle": "--",
        "zorder": 3,
    },
}
FLOAT_ATOL = 1e-12


def load_window_feature_rows():
    required_fields = {
        "run",
        "configuration_id",
        "window_length_sec",
        "step_size_sec",
        "outer_window_overlap_fraction",
        "window_center_sec",
        "posterior_alpha_mean_psd",
    }

    if not WINDOW_FEATURE_CSV_PATH.exists():
        raise FileNotFoundError(
            "Window-feature CSV was not found: "
            f"{WINDOW_FEATURE_CSV_PATH}"
        )

    with open(
        WINDOW_FEATURE_CSV_PATH,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "Window-feature CSV has no header."
            )

        missing_fields = (
            required_fields
            - set(reader.fieldnames)
        )

        if missing_fields:
            raise RuntimeError(
                "Window-feature CSV is missing "
                f"required fields: "
                f"{sorted(missing_fields)}"
            )

        feature_rows = []

        for row in reader:
            feature_rows.append({
                "run": int(
                    row["run"]
                ),
                "configuration_id": (
                    row["configuration_id"]
                ),
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
                "window_center_sec": float(
                    row["window_center_sec"]
                ),
                "posterior_alpha_mean_psd": float(
                    row[
                        "posterior_alpha_mean_psd"
                    ]
                ),
            })

    if len(feature_rows) == 0:
        raise RuntimeError(
            "Window-feature CSV contains no rows."
        )

    return feature_rows


def select_step_size_rows(
    feature_rows,
    configuration_id,
    run,
):
    selected_rows = [
        row
        for row in feature_rows
        if (
            row["configuration_id"]
            == configuration_id
            and row["run"] == run
        )
    ]

    selected_rows.sort(
        key=lambda row: row[
            "window_center_sec"
        ]
    )

    if len(selected_rows) == 0:
        raise RuntimeError(
            "No rows were found for "
            f"{configuration_id}, run {run}."
        )

    return selected_rows


def validate_step_size_rows(
    selected_rows,
    configuration_id,
    run,
):
    expected_n_windows = (
        EXPECTED_WINDOWS_PER_RUN[
            configuration_id
        ]
    )

    if len(selected_rows) != expected_n_windows:
        raise RuntimeError(
            f"{configuration_id}, run {run}: "
            f"expected {expected_n_windows} rows, "
            f"but found {len(selected_rows)}."
        )

    window_lengths = np.asarray(
        [
            row["window_length_sec"]
            for row in selected_rows
        ],
        dtype=float,
    )

    step_sizes = np.asarray(
        [
            row["step_size_sec"]
            for row in selected_rows
        ],
        dtype=float,
    )

    overlap_fractions = np.asarray(
        [
            row[
                "outer_window_overlap_fraction"
            ]
            for row in selected_rows
        ],
        dtype=float,
    )

    center_times = np.asarray(
        [
            row["window_center_sec"]
            for row in selected_rows
        ],
        dtype=float,
    )

    feature_values = np.asarray(
        [
            row[
                "posterior_alpha_mean_psd"
            ]
            for row in selected_rows
        ],
        dtype=float,
    )

    if not np.allclose(
        window_lengths,
        2.0,
        rtol=0.0,
        atol=FLOAT_ATOL,
    ):
        raise RuntimeError(
            f"{configuration_id}, run {run}: "
            "window length is not consistently "
            "2.0 seconds."
        )

    expected_step_size = (
        EXPECTED_STEP_SIZE_SEC[
            configuration_id
        ]
    )

    if not np.allclose(
        step_sizes,
        expected_step_size,
        rtol=0.0,
        atol=FLOAT_ATOL,
    ):
        raise RuntimeError(
            f"{configuration_id}, run {run}: "
            "step size does not match the "
            "configured value."
        )

    expected_overlap_fraction = (
        EXPECTED_OVERLAP_FRACTION[
            configuration_id
        ]
    )

    if not np.allclose(
        overlap_fractions,
        expected_overlap_fraction,
        rtol=0.0,
        atol=FLOAT_ATOL,
    ):
        raise RuntimeError(
            f"{configuration_id}, run {run}: "
            "outer-window overlap does not "
            "match the configured value."
        )

    if not np.isfinite(
        center_times
    ).all():
        raise ValueError(
            f"{configuration_id}, run {run}: "
            "window-center times contain "
            "non-finite values."
        )

    if not np.all(
        np.diff(center_times) > 0
    ):
        raise RuntimeError(
            f"{configuration_id}, run {run}: "
            "window-center times are not "
            "strictly increasing."
        )

    if not np.isfinite(
        feature_values
    ).all():
        raise ValueError(
            f"{configuration_id}, run {run}: "
            "feature values contain "
            "non-finite values."
        )

    if np.any(feature_values <= 0):
        raise ValueError(
            f"{configuration_id}, run {run}: "
            "log-scale plotting requires "
            "positive feature values."
        )

    return {
        "n_windows": len(selected_rows),
        "window_length_sec": float(
            window_lengths[0]
        ),
        "step_size_sec": float(
            step_sizes[0]
        ),
        "overlap_fraction": float(
            overlap_fractions[0]
        ),
        "first_center_sec": float(
            center_times[0]
        ),
        "last_center_sec": float(
            center_times[-1]
        ),
        "minimum_feature": float(
            np.min(feature_values)
        ),
        "maximum_feature": float(
            np.max(feature_values)
        ),
    }


def save_step_size_comparison_figure(
    feature_rows,
):
    figure, axes = plt.subplots(
        nrows=2,
        ncols=1,
        figsize=(12, 9),
        sharex=True,
    )

    panel_definitions = [
        (
            axes[0],
            EYES_OPEN_RUN,
            "A. Eyes open — Run 1",
        ),
        (
            axes[1],
            EYES_CLOSED_RUN,
            "B. Eyes closed — Run 2",
        ),
    ]

    for axis, run, panel_title in (
        panel_definitions
    ):
        for configuration_id in (
            STEP_SIZE_COMPARISON_IDS
        ):
            selected_rows = (
                select_step_size_rows(
                    feature_rows=feature_rows,
                    configuration_id=(
                        configuration_id
                    ),
                    run=run,
                )
            )

            summary = validate_step_size_rows(
                selected_rows=selected_rows,
                configuration_id=(
                    configuration_id
                ),
                run=run,
            )

            center_times = np.asarray(
                [
                    row["window_center_sec"]
                    for row in selected_rows
                ],
                dtype=float,
            )

            feature_values = np.asarray(
                [
                    row[
                        "posterior_alpha_mean_psd"
                    ]
                    for row in selected_rows
                ],
                dtype=float,
            )

            legend_label = (
                f"{summary['step_size_sec']:.1f} s step "
                f"({summary['overlap_fraction']:.0%} "
                f"overlap, "
                f"n={summary['n_windows']})"
            )

            axis.plot(
                center_times,
                feature_values,
                label=legend_label,
                **STEP_SIZE_PLOT_STYLES[
                    configuration_id
                ],
            )

        axis.set_title(
            panel_title
        )

        axis.set_ylabel(
            "Posterior alpha mean PSD\n"
            "(V²/Hz)"
        )

        axis.set_yscale(
            "log"
        )

        axis.grid(
            True,
            which="both",
            alpha=0.25,
        )

        axis.legend(
            loc="best",
            fontsize=9,
        )

    axes[1].set_xlabel(
        "Window center time (s)"
    )

    axes[1].set_xlim(
        0.0,
        60.0,
    )

    figure.suptitle(
        "Step-Size Comparison with "
        "Fixed 2 s Windows",
        fontsize=14,
    )

    figure.text(
        0.5,
        0.018,
        (
            "Raw PSD values are shown on "
            "log-scaled y-axes. Smaller steps "
            "produce denser, overlapping estimates.\n"
            "Shared 2 s windows have identical "
            "feature values; additional points "
            "represent intermediate update times."
        ),
        ha="center",
        va="bottom",
        fontsize=9,
    )

    figure.tight_layout(
        rect=(0.0, 0.075, 1.0, 0.95)
    )

    STEP_SIZE_COMPARISON_FIGURE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure.savefig(
        STEP_SIZE_COMPARISON_FIGURE_PATH,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(
        figure
    )

    if not (
        STEP_SIZE_COMPARISON_FIGURE_PATH.exists()
    ):
        raise RuntimeError(
            "Step-size comparison figure "
            "was not created."
        )

    if (
        STEP_SIZE_COMPARISON_FIGURE_PATH.stat().st_size
        == 0
    ):
        raise RuntimeError(
            "Step-size comparison figure "
            "is empty."
        )

    return STEP_SIZE_COMPARISON_FIGURE_PATH


def main():
    feature_rows = (
        load_window_feature_rows()
    )

    print(
        "\n########################################"
    )

    print(
        "Session 14 step-size figure "
        "input validation"
    )

    print(
        "Source CSV:",
        WINDOW_FEATURE_CSV_PATH,
    )

    print(
        "Total source rows:",
        len(feature_rows),
    )

    for run in [
        EYES_OPEN_RUN,
        EYES_CLOSED_RUN,
    ]:
        print(
            "\nRun:",
            run,
            RUN_LABELS[run],
        )

        for configuration_id in (
            STEP_SIZE_COMPARISON_IDS
        ):
            selected_rows = (
                select_step_size_rows(
                    feature_rows=feature_rows,
                    configuration_id=(
                        configuration_id
                    ),
                    run=run,
                )
            )

            summary = (
                validate_step_size_rows(
                    selected_rows=selected_rows,
                    configuration_id=(
                        configuration_id
                    ),
                    run=run,
                )
            )

            print(
                configuration_id,
                "| n:",
                summary["n_windows"],
                "| window:",
                f"{summary['window_length_sec']:.1f}",
                "s",
                "| step:",
                f"{summary['step_size_sec']:.1f}",
                "s",
                "| overlap:",
                f"{summary['overlap_fraction']:.0%}",
                "| centers:",
                (
                    f"{summary['first_center_sec']:.1f}"
                    "-"
                    f"{summary['last_center_sec']:.1f} s"
                ),
            )

    print(
        "\nStep-size figure input "
        "validation completed."
    )

    saved_figure_path = (
        save_step_size_comparison_figure(
            feature_rows=feature_rows
        )
    )

    print(
        "\nSaved step-size comparison figure:",
        saved_figure_path,
    )


if __name__ == "__main__":
    main()