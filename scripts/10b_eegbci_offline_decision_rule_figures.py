# Session 15 decision-rule figures.

import csv
import json
from collections import defaultdict
from pathlib import Path
from matplotlib.patches import Patch

import numpy as np
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]

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

METADATA_JSON_PATH = (
    SESSION15_RESULTS_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha_offline-"
        "decision-rule-metadata.json"
    )
)

SESSION15_FIGURE_DIR = (
    PROJECT_ROOT
    / "figures"
    / "session-15"
)

FEATURE_THRESHOLD_FIGURE_PATH = (
    SESSION15_FIGURE_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha-raw-median3-"
        "thresholds.png"
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

COMMAND_STATE_FIGURE_PATH = (
    SESSION15_FIGURE_DIR
    / (
        "eegbci_subject-001_runs-01-02_"
        "posterior-alpha-representative-"
        "command-states.png"
    )
)

RAW_RULE_ID = (
    "thr-gap-mid__smooth-none__dwell-1"
)

MEDIAN3_RULE_ID = (
    "thr-gap-mid__smooth-median3__dwell-1"
)

SMOOTHING_ID_NONE = "smooth-none"
SMOOTHING_ID_MEDIAN3 = "smooth-median3"

STOP_COMMAND_STATE = "CMD_STOP"
OPEN_COMMAND_STATE = "CMD_OPEN"
CLOSE_COMMAND_STATE = "CMD_CLOSE"

FEATURE_NAME = "posterior_alpha_mean_psd"
FEATURE_UNIT = "V^2/Hz"

RTOL = 1e-12
ATOL = 1e-15

REQUIRED_DECISION_COLUMNS = [
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
]

REQUIRED_EPISODE_COLUMNS = [
    "rule_id",
    "subject",
    "run",
    "condition",
    "configuration_id",
    "smoothing_id",
    "threshold_id",
    "threshold_value",
    "dwell_updates",
    "episode_index",
    "command_state",
    "episode_start_time_sec",
    "episode_end_time_sec",
    "episode_duration_sec",
    "start_event",
    "end_event",
    "is_initial_stop_episode",
    "ended_at_run_boundary",
]

REPRESENTATIVE_COMMAND_RULES = [
    {
        "rule_id": (
            "thr-gap-mid__smooth-none__dwell-1"
        ),
        "label": "No smoothing, dwell 1",
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 1,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-none__dwell-2"
        ),
        "label": "No smoothing, dwell 2",
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 2,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-none__dwell-3"
        ),
        "label": "No smoothing, dwell 3",
        "smoothing_id": SMOOTHING_ID_NONE,
        "dwell_updates": 3,
    },
    {
        "rule_id": (
            "thr-gap-mid__smooth-median3__dwell-1"
        ),
        "label": "Causal median-3, dwell 1",
        "smoothing_id": SMOOTHING_ID_MEDIAN3,
        "dwell_updates": 1,
    },
]


def parse_boolean(
    value,
):
    """
    Convert a CSV boolean string to bool.
    """

    if value == "True":
        return True

    if value == "False":
        return False

    raise ValueError(
        "Unexpected boolean value: "
        f"{value}"
    )


def parse_optional_float(
    value,
):
    """
    Convert a numeric CSV value to float.

    An empty field is returned as None.
    """

    if value == "":
        return None

    return float(value)


def load_selected_decision_rows(
    csv_path,
):
    """
    Load only the raw and median-3 rule streams
    needed for the feature-threshold figure.

    Output:
        Parsed rows for two selected rule IDs.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            "Decision-stream CSV was not found:\n"
            f"{csv_path}"
        )

    selected_rule_ids = {
        RAW_RULE_ID,
        MEDIAN3_RULE_ID,
    }

    selected_rows = []
    seen_row_keys = set()

    with open(
        csv_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "Decision-stream CSV has "
                "no header."
            )

        missing_columns = [
            column
            for column in (
                REQUIRED_DECISION_COLUMNS
            )
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise RuntimeError(
                "Decision-stream CSV is missing "
                "required columns: "
                f"{missing_columns}"
            )

        for source_row in reader:
            rule_id = source_row["rule_id"]

            if rule_id not in selected_rule_ids:
                continue

            output_row = {
                "rule_id": rule_id,
                "subject": int(
                    source_row["subject"]
                ),
                "run": int(
                    source_row["run"]
                ),
                "condition": source_row[
                    "condition"
                ],
                "configuration_id": source_row[
                    "configuration_id"
                ],
                "window_index": int(
                    source_row["window_index"]
                ),
                "window_start_sec": float(
                    source_row["window_start_sec"]
                ),
                "window_end_sec": float(
                    source_row["window_end_sec"]
                ),
                "decision_time_sec": float(
                    source_row["decision_time_sec"]
                ),
                "feature_name": source_row[
                    "feature_name"
                ],
                "feature_unit": source_row[
                    "feature_unit"
                ],
                "raw_feature_value": float(
                    source_row[
                        "raw_feature_value"
                    ]
                ),
                "smoothing_id": source_row[
                    "smoothing_id"
                ],
                "smoothed_available": (
                    parse_boolean(
                        source_row[
                            "smoothed_available"
                        ]
                    )
                ),
                "smoothed_feature_value": (
                    parse_optional_float(
                        source_row[
                            "smoothed_feature_value"
                        ]
                    )
                ),
                "threshold_id": source_row[
                    "threshold_id"
                ],
                "threshold_value": float(
                    source_row[
                        "threshold_value"
                    ]
                ),
            }

            row_key = (
                output_row["rule_id"],
                output_row["subject"],
                output_row["run"],
                output_row["window_index"],
            )

            if row_key in seen_row_keys:
                raise RuntimeError(
                    "A duplicate figure-input "
                    "row key was found: "
                    f"{row_key}"
                )

            seen_row_keys.add(
                row_key
            )

            selected_rows.append(
                output_row
            )

    if not selected_rows:
        raise RuntimeError(
            "No decision rows were selected "
            "for the figure."
        )

    found_rule_ids = {
        row["rule_id"]
        for row in selected_rows
    }

    if found_rule_ids != selected_rule_ids:
        raise RuntimeError(
            "The figure input does not contain "
            "both required rule streams: "
            f"{found_rule_ids}"
        )

    selected_rows.sort(
        key=lambda row: (
            row["rule_id"],
            row["subject"],
            row["run"],
            row["window_index"],
        )
    )

    return selected_rows


def load_selected_command_episode_rows(
    csv_path,
):
    """
    Load the four representative command-rule
    episode streams used for Figure 2.
    """

    if not csv_path.exists():
        raise FileNotFoundError(
            "Command-episode CSV was not found:\n"
            f"{csv_path}"
        )

    selected_rule_ids = {
        config["rule_id"]
        for config in (
            REPRESENTATIVE_COMMAND_RULES
        )
    }

    selected_rows = []
    seen_row_keys = set()

    with open(
        csv_path,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise RuntimeError(
                "Command-episode CSV has "
                "no header."
            )

        missing_columns = [
            column
            for column in (
                REQUIRED_EPISODE_COLUMNS
            )
            if column not in reader.fieldnames
        ]

        if missing_columns:
            raise RuntimeError(
                "Command-episode CSV is missing "
                "required columns: "
                f"{missing_columns}"
            )

        for source_row in reader:
            rule_id = source_row["rule_id"]

            if rule_id not in selected_rule_ids:
                continue

            output_row = {
                "rule_id": rule_id,
                "subject": int(
                    source_row["subject"]
                ),
                "run": int(
                    source_row["run"]
                ),
                "condition": source_row[
                    "condition"
                ],
                "configuration_id": source_row[
                    "configuration_id"
                ],
                "smoothing_id": source_row[
                    "smoothing_id"
                ],
                "threshold_id": source_row[
                    "threshold_id"
                ],
                "threshold_value": float(
                    source_row[
                        "threshold_value"
                    ]
                ),
                "dwell_updates": int(
                    source_row[
                        "dwell_updates"
                    ]
                ),
                "episode_index": int(
                    source_row[
                        "episode_index"
                    ]
                ),
                "command_state": source_row[
                    "command_state"
                ],
                "episode_start_time_sec": float(
                    source_row[
                        "episode_start_time_sec"
                    ]
                ),
                "episode_end_time_sec": float(
                    source_row[
                        "episode_end_time_sec"
                    ]
                ),
                "episode_duration_sec": float(
                    source_row[
                        "episode_duration_sec"
                    ]
                ),
                "start_event": source_row[
                    "start_event"
                ],
                "end_event": source_row[
                    "end_event"
                ],
                "is_initial_stop_episode": (
                    parse_boolean(
                        source_row[
                            "is_initial_stop_episode"
                        ]
                    )
                ),
                "ended_at_run_boundary": (
                    parse_boolean(
                        source_row[
                            "ended_at_run_boundary"
                        ]
                    )
                ),
            }

            row_key = (
                output_row["rule_id"],
                output_row["subject"],
                output_row["run"],
                output_row["episode_index"],
            )

            if row_key in seen_row_keys:
                raise RuntimeError(
                    "A duplicate command-figure "
                    "episode key was found: "
                    f"{row_key}"
                )

            seen_row_keys.add(
                row_key
            )

            selected_rows.append(
                output_row
            )

    found_rule_ids = {
        row["rule_id"]
        for row in selected_rows
    }

    if found_rule_ids != selected_rule_ids:
        raise RuntimeError(
            "The command figure does not contain "
            "all representative rules: "
            f"{found_rule_ids}"
        )

    selected_rows.sort(
        key=lambda row: (
            row["subject"],
            row["run"],
            row["rule_id"],
            row["episode_index"],
        )
    )

    return selected_rows


def validate_command_figure_inputs(
    episode_rows,
):
    """
    Validate temporal continuity and rule
    specifications for Figure 2.
    """

    grouped_rows = defaultdict(list)

    for row in episode_rows:
        group_key = (
            row["rule_id"],
            row["subject"],
            row["run"],
        )

        grouped_rows[group_key].append(
            row
        )

    expected_rule_ids = {
        config["rule_id"]
        for config in (
            REPRESENTATIVE_COMMAND_RULES
        )
    }

    recording_keys = {
        (
            row["subject"],
            row["run"],
        )
        for row in episode_rows
    }

    for config in (
        REPRESENTATIVE_COMMAND_RULES
    ):
        rule_id = config["rule_id"]

        for (
            subject,
            run,
        ) in recording_keys:
            group_key = (
                rule_id,
                subject,
                run,
            )

            if group_key not in grouped_rows:
                raise RuntimeError(
                    "A representative rule is "
                    "missing a recording: "
                    f"{group_key}"
                )

            rows = sorted(
                grouped_rows[group_key],
                key=lambda row: (
                    row["episode_index"]
                ),
            )

            episode_indices = [
                row["episode_index"]
                for row in rows
            ]

            if episode_indices != list(
                range(len(rows))
            ):
                raise RuntimeError(
                    "Command episode indices are "
                    "missing or out of order for "
                    f"{group_key}."
                )

            if rows[0]["command_state"] != (
                STOP_COMMAND_STATE
            ):
                raise RuntimeError(
                    "The first command episode "
                    "must be CMD_STOP."
                )

            if not rows[0][
                "is_initial_stop_episode"
            ]:
                raise RuntimeError(
                    "Episode zero is not marked "
                    "as the initial STOP episode."
                )

            if any(
                row["command_state"]
                not in {
                    STOP_COMMAND_STATE,
                    OPEN_COMMAND_STATE,
                    CLOSE_COMMAND_STATE,
                }
                for row in rows
            ):
                raise RuntimeError(
                    "An unexpected command state "
                    "was found for Figure 2."
                )

            if any(
                row["smoothing_id"]
                != config["smoothing_id"]
                for row in rows
            ):
                raise RuntimeError(
                    "A Figure 2 rule contains an "
                    "unexpected smoothing ID."
                )

            if any(
                row["dwell_updates"]
                != config["dwell_updates"]
                for row in rows
            ):
                raise RuntimeError(
                    "A Figure 2 rule contains an "
                    "unexpected dwell value."
                )

            for (
                previous_row,
                next_row,
            ) in zip(
                rows[:-1],
                rows[1:],
            ):
                if not np.isclose(
                    previous_row[
                        "episode_end_time_sec"
                    ],
                    next_row[
                        "episode_start_time_sec"
                    ],
                    rtol=RTOL,
                    atol=ATOL,
                ):
                    raise RuntimeError(
                        "Command episodes are not "
                        "temporally contiguous for "
                        f"{group_key}."
                    )

            if not np.isclose(
                rows[0][
                    "episode_start_time_sec"
                ],
                0.0,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "The command timeline does "
                    "not begin at recording time "
                    "zero."
                )

            if not np.isclose(
                rows[-1][
                    "episode_end_time_sec"
                ],
                60.0,
                rtol=RTOL,
                atol=ATOL,
            ):
                raise RuntimeError(
                    "The command timeline does "
                    "not end at 60 s."
                )

    found_rule_ids = {
        rule_id
        for (
            rule_id,
            subject,
            run,
        ) in grouped_rows
    }

    if found_rule_ids != expected_rule_ids:
        raise RuntimeError(
            "Validated command-figure rules do "
            "not match the configured rules."
        )

    return (
        dict(grouped_rows),
        sorted(recording_keys),
    )


def save_representative_command_figure(
    grouped_episode_rows,
    recording_keys,
    output_path,
):
    """
    Save Figure 2:
    representative confirmed command-state
    episodes for four decision rules.
    """

    if not recording_keys:
        raise RuntimeError(
            "No recording keys were provided "
            "for Figure 2."
        )

    command_colors = {
        STOP_COMMAND_STATE: "0.75",
        OPEN_COMMAND_STATE: "tab:blue",
        CLOSE_COMMAND_STATE: "tab:orange",
    }

    figure_height = (
        3.4 * len(recording_keys)
    )

    fig, axes = plt.subplots(
        len(recording_keys),
        1,
        figsize=(11, figure_height),
        sharex=True,
    )

    if len(recording_keys) == 1:
        axes = [axes]

    rule_count = len(
        REPRESENTATIVE_COMMAND_RULES
    )

    bar_height = 0.64

    for ax, (
        subject,
        run,
    ) in zip(
        axes,
        recording_keys,
    ):
        y_positions = list(
            reversed(range(rule_count))
        )

        condition = None

        for y_position, config in zip(
            y_positions,
            REPRESENTATIVE_COMMAND_RULES,
        ):
            group_key = (
                config["rule_id"],
                subject,
                run,
            )

            episodes = sorted(
                grouped_episode_rows[
                    group_key
                ],
                key=lambda row: (
                    row["episode_index"]
                ),
            )

            condition = episodes[0][
                "condition"
            ]

            for episode in episodes:
                start_time = episode[
                    "episode_start_time_sec"
                ]

                duration = episode[
                    "episode_duration_sec"
                ]

                ax.broken_barh(
                    [
                        (
                            start_time,
                            duration,
                        )
                    ],
                    (
                        y_position
                        - bar_height / 2.0,
                        bar_height,
                    ),
                    facecolors=(
                        command_colors[
                            episode[
                                "command_state"
                            ]
                        ]
                    ),
                    edgecolors="white",
                    linewidth=0.8,
                )

            initial_stop_episode = episodes[0]

            first_active_time = (
                initial_stop_episode[
                    "episode_end_time_sec"
                ]
            )

            ax.text(
                first_active_time + 0.4,
                y_position,
                f"t={first_active_time:.0f} s",
                va="center",
                ha="left",
                fontsize=8,
            )

        condition_text = (
            condition
            .replace(
                "baseline_",
                "",
            )
            .replace(
                "_",
                " ",
            )
        )

        ax.set_title(
            f"Subject {subject} "
            f"— Run {run} "
            f"({condition_text})"
        )

        ax.set_yticks(
            y_positions
        )

        ax.set_yticklabels([
            config["label"]
            for config in (
                REPRESENTATIVE_COMMAND_RULES
            )
        ])

        ax.set_ylim(
            -0.7,
            rule_count - 0.3,
        )

        ax.set_xlim(
            0.0,
            60.0,
        )

        ax.grid(
            True,
            axis="x",
            alpha=0.3,
        )

        if run == 1:
            ax.axvline(
                26.0,
                color="0.25",
                linestyle="--",
                linewidth=1.0,
            )

            ax.text(
                26.4,
                rule_count - 0.45,
                "26 s raw HIGH evidence",
                fontsize=8,
                va="top",
            )

    axes[-1].set_xlabel(
        "Recording time (s)"
    )

    axes[-1].set_xticks(
        np.arange(
            0.0,
            61.0,
            10.0,
        )
    )

    legend_handles = [
        Patch(
            facecolor=command_colors[
                STOP_COMMAND_STATE
            ],
            label="CMD_STOP",
        ),
        Patch(
            facecolor=command_colors[
                OPEN_COMMAND_STATE
            ],
            label="CMD_OPEN",
        ),
        Patch(
            facecolor=command_colors[
                CLOSE_COMMAND_STATE
            ],
            label="CMD_CLOSE",
        ),
    ]

    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(
            0.5,
            0.94,
        ),
        ncol=3,
        frameon=True,
    )

    fig.suptitle(
        "Confirmed command-state episodes for "
        "representative midpoint-threshold rules",
        y=0.995,
    )

    fig.tight_layout(
        rect=(
            0.0,
            0.0,
            1.0,
            0.89,
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "The command-state figure was not "
            "saved correctly."
        )

    print("\n========================================")
    print(
        "Session 15 Figure 2: "
        "Representative command states"
    )

    print(
        "Command-episode CSV:",
        COMMAND_EPISODE_CSV_PATH,
    )

    print(
        "Output figure:",
        output_path,
    )

    print(
        "Representative rule count:",
        len(
            REPRESENTATIVE_COMMAND_RULES
        ),
    )

    print(
        "Recording panel count:",
        len(recording_keys),
    )


def load_metadata(
    json_path,
):
    """
    Load the saved Session 15 metadata JSON.
    """

    if not json_path.exists():
        raise FileNotFoundError(
            "Metadata JSON was not found:\n"
            f"{json_path}"
        )

    with open(
        json_path,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    required_keys = {
        "recording_scope",
        "feature_specification",
        "threshold_specification",
        "rule_set",
    }

    missing_keys = (
        required_keys
        - set(metadata)
    )

    if missing_keys:
        raise RuntimeError(
            "Metadata are missing required "
            "top-level keys: "
            f"{sorted(missing_keys)}"
        )

    return metadata


def group_rows_by_rule_recording(
    selected_rows,
):
    """
    Group rows by rule, subject, and run.
    """

    grouped_rows = defaultdict(list)

    for row in selected_rows:
        group_key = (
            row["rule_id"],
            row["subject"],
            row["run"],
        )

        grouped_rows[group_key].append(
            row
        )

    for rows in grouped_rows.values():
        rows.sort(
            key=lambda row: (
                row["window_index"]
            )
        )

    return dict(grouped_rows)


def get_thresholds_by_subject(
    metadata,
):
    """
    Extract the three saved threshold values
    from metadata.

    Output:
        Threshold dictionaries keyed by subject.
    """

    threshold_records = metadata[
        "threshold_specification"
    ]["thresholds_by_subject"]

    thresholds_by_subject = {}

    for record in threshold_records:
        subject = int(
            record["subject"]
        )

        if subject in thresholds_by_subject:
            raise RuntimeError(
                "Duplicate threshold metadata "
                f"for subject {subject}."
            )

        thresholds_by_subject[subject] = {
            "threshold_eo_q95": float(
                record["threshold_eo_q95"]
            ),
            "threshold_gap_midpoint": float(
                record[
                    "threshold_gap_midpoint"
                ]
            ),
            "threshold_ec_q05": float(
                record["threshold_ec_q05"]
            ),
        }

    if not thresholds_by_subject:
        raise RuntimeError(
            "No subject thresholds were found "
            "in metadata."
        )

    return thresholds_by_subject


def validate_feature_figure_inputs(
    grouped_rows,
    metadata,
    thresholds_by_subject,
):
    """
    Confirm that raw and median-3 streams
    describe the same recordings and windows.

    This prevents plotting mismatched rule rows
    as though they were paired observations.
    """

    raw_recording_keys = {
        (
            subject,
            run,
        )
        for (
            rule_id,
            subject,
            run,
        ) in grouped_rows
        if rule_id == RAW_RULE_ID
    }

    median3_recording_keys = {
        (
            subject,
            run,
        )
        for (
            rule_id,
            subject,
            run,
        ) in grouped_rows
        if rule_id == MEDIAN3_RULE_ID
    }

    if (
        raw_recording_keys
        != median3_recording_keys
    ):
        raise RuntimeError(
            "Raw and median-3 recording keys "
            "do not match."
        )

    metadata_recording_count = metadata[
        "recording_scope"
    ]["recording_count"]

    if len(raw_recording_keys) != (
        metadata_recording_count
    ):
        raise RuntimeError(
            "Figure recording count does not "
            "match metadata."
        )

    for (
        subject,
        run,
    ) in sorted(raw_recording_keys):
        raw_rows = grouped_rows[
            (
                RAW_RULE_ID,
                subject,
                run,
            )
        ]

        median3_rows = grouped_rows[
            (
                MEDIAN3_RULE_ID,
                subject,
                run,
            )
        ]

        if len(raw_rows) != len(
            median3_rows
        ):
            raise RuntimeError(
                "Raw and median-3 row counts "
                "do not match for "
                f"subject {subject}, "
                f"run {run}."
            )

        raw_window_indices = np.asarray(
            [
                row["window_index"]
                for row in raw_rows
            ],
            dtype=int,
        )

        median3_window_indices = np.asarray(
            [
                row["window_index"]
                for row in median3_rows
            ],
            dtype=int,
        )

        if not np.array_equal(
            raw_window_indices,
            median3_window_indices,
        ):
            raise RuntimeError(
                "Raw and median-3 window indices "
                "do not match for "
                f"subject {subject}, "
                f"run {run}."
            )

        raw_decision_times = np.asarray(
            [
                row["decision_time_sec"]
                for row in raw_rows
            ],
            dtype=float,
        )

        median3_decision_times = np.asarray(
            [
                row["decision_time_sec"]
                for row in median3_rows
            ],
            dtype=float,
        )

        if not np.allclose(
            raw_decision_times,
            median3_decision_times,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError(
                "Raw and median-3 decision times "
                "do not match for "
                f"subject {subject}, "
                f"run {run}."
            )

        raw_feature_values = np.asarray(
            [
                row["raw_feature_value"]
                for row in raw_rows
            ],
            dtype=float,
        )

        median3_source_values = np.asarray(
            [
                row["raw_feature_value"]
                for row in median3_rows
            ],
            dtype=float,
        )

        if not np.allclose(
            raw_feature_values,
            median3_source_values,
            rtol=RTOL,
            atol=ATOL,
        ):
            raise RuntimeError(
                "Raw source feature values "
                "differ between figure streams "
                "for "
                f"subject {subject}, "
                f"run {run}."
            )

        if any(
            row["smoothing_id"]
            != SMOOTHING_ID_NONE
            for row in raw_rows
        ):
            raise RuntimeError(
                "Unexpected smoothing ID in "
                "the raw figure stream."
            )

        if any(
            not row["smoothed_available"]
            for row in raw_rows
        ):
            raise RuntimeError(
                "A no-smoothing row is marked "
                "unavailable."
            )

        if any(
            not np.isclose(
                row["raw_feature_value"],
                row["smoothed_feature_value"],
                rtol=RTOL,
                atol=ATOL,
            )
            for row in raw_rows
        ):
            raise RuntimeError(
                "No-smoothing processed values "
                "do not match raw values."
            )

        unavailable_indices = [
            index
            for index, row in enumerate(
                median3_rows
            )
            if not row[
                "smoothed_available"
            ]
        ]

        if unavailable_indices != [0, 1]:
            raise RuntimeError(
                "Median-3 warm-up rows are "
                "not the expected initial "
                "two updates for "
                f"subject {subject}, "
                f"run {run}."
            )

        for row in median3_rows:
            if row["smoothed_available"]:
                smoothed_value = row[
                    "smoothed_feature_value"
                ]

                if (
                    smoothed_value is None
                    or not np.isfinite(
                        smoothed_value
                    )
                    or smoothed_value <= 0.0
                ):
                    raise RuntimeError(
                        "An available median-3 "
                        "value is invalid."
                    )

            elif (
                row["smoothed_feature_value"]
                is not None
            ):
                raise RuntimeError(
                    "An unavailable median-3 "
                    "row contains a value."
                )

        if subject not in (
            thresholds_by_subject
        ):
            raise RuntimeError(
                "No saved thresholds were found "
                f"for subject {subject}."
            )

    return sorted(
        raw_recording_keys
    )


def print_figure_input_summary(
    selected_rows,
    recording_keys,
    thresholds_by_subject,
):
    """
    Print the validated inputs that will be
    used for Figure 1.
    """

    print("\n========================================")
    print(
        "Session 15 Figure Step 1: "
        "Feature-figure input validation"
    )

    print(
        "Decision-stream CSV:",
        DECISION_STREAM_CSV_PATH,
    )

    print(
        "Metadata JSON:",
        METADATA_JSON_PATH,
    )

    print(
        "Selected rule count:",
        len({
            row["rule_id"]
            for row in selected_rows
        }),
    )

    print(
        "Selected row count:",
        len(selected_rows),
    )

    print(
        "Recording count:",
        len(recording_keys),
    )

    for (
        subject,
        run,
    ) in recording_keys:
        raw_row_count = sum(
            (
                row["rule_id"]
                == RAW_RULE_ID
                and row["subject"]
                == subject
                and row["run"]
                == run
            )
            for row in selected_rows
        )

        print("\n----------------------------------------")
        print("Subject:", subject)
        print("Run:", run)
        print(
            "Window count per stream:",
            raw_row_count,
        )

        thresholds = (
            thresholds_by_subject[
                subject
            ]
        )

        print(
            "EO Q95:",
            f"{thresholds['threshold_eo_q95']:.12e}",
            FEATURE_UNIT,
        )

        print(
            "Gap midpoint:",
            f"{thresholds['threshold_gap_midpoint']:.12e}",
            FEATURE_UNIT,
        )

        print(
            "EC Q05:",
            f"{thresholds['threshold_ec_q05']:.12e}",
            FEATURE_UNIT,
        )

    print(
        "\nFeature-figure input "
        "validation completed."
    )


def build_feature_figure_records(
    grouped_rows,
    recording_keys,
    thresholds_by_subject,
):
    """
    Build one plotting record per recording.

    Each record contains:
        decision times
        raw feature values
        causal median-3 values
        three threshold levels
    """

    figure_records = []

    for (
        subject,
        run,
    ) in recording_keys:
        raw_rows = grouped_rows[
            (
                RAW_RULE_ID,
                subject,
                run,
            )
        ]

        median3_rows = grouped_rows[
            (
                MEDIAN3_RULE_ID,
                subject,
                run,
            )
        ]

        decision_times_sec = np.asarray(
            [
                row["decision_time_sec"]
                for row in raw_rows
            ],
            dtype=float,
        )

        raw_feature_values = np.asarray(
            [
                row["raw_feature_value"]
                for row in raw_rows
            ],
            dtype=float,
        )

        median3_feature_values = np.asarray(
            [
                (
                    np.nan
                    if row["smoothed_feature_value"]
                    is None
                    else row[
                        "smoothed_feature_value"
                    ]
                )
                for row in median3_rows
            ],
            dtype=float,
        )

        thresholds = thresholds_by_subject[
            subject
        ]

        figure_records.append({
            "subject": subject,
            "run": run,
            "condition": raw_rows[0][
                "condition"
            ],
            "decision_times_sec": (
                decision_times_sec
            ),
            "raw_feature_values": (
                raw_feature_values
            ),
            "median3_feature_values": (
                median3_feature_values
            ),
            "threshold_eo_q95": (
                thresholds[
                    "threshold_eo_q95"
                ]
            ),
            "threshold_gap_midpoint": (
                thresholds[
                    "threshold_gap_midpoint"
                ]
            ),
            "threshold_ec_q05": (
                thresholds[
                    "threshold_ec_q05"
                ]
            ),
        })

    if not figure_records:
        raise RuntimeError(
            "No feature-figure records were "
            "created."
        )

    return figure_records


def save_feature_threshold_figure(
    figure_records,
    output_path,
):
    """
    Save Figure 1:
    raw feature, causal median-3, and
    three threshold levels for each recording.
    """

    if not figure_records:
        raise RuntimeError(
            "No figure records were provided."
        )

    positive_values = []

    for record in figure_records:
        positive_values.extend(
            value
            for value in record[
                "raw_feature_values"
            ]
            if (
                np.isfinite(value)
                and value > 0.0
            )
        )

        positive_values.extend(
            value
            for value in record[
                "median3_feature_values"
            ]
            if (
                np.isfinite(value)
                and value > 0.0
            )
        )

        positive_values.extend([
            record["threshold_eo_q95"],
            record["threshold_gap_midpoint"],
            record["threshold_ec_q05"],
        ])

    if not positive_values:
        raise RuntimeError(
            "No positive values were available "
            "for the feature figure."
        )

    y_min = min(positive_values) * 0.8
    y_max = max(positive_values) * 1.2

    figure_height = (
        4.0 * len(figure_records)
    )

    fig, axes = plt.subplots(
        len(figure_records),
        1,
        figsize=(10, figure_height),
        sharex=True,
    )

    if len(figure_records) == 1:
        axes = [axes]

    for ax, record in zip(
        axes,
        figure_records,
    ):
        ax.plot(
            record["decision_times_sec"],
            record["raw_feature_values"],
            color="tab:blue",
            label="Raw feature",
            linewidth=1.5,
        )

        ax.plot(
            record["decision_times_sec"],
            record[
                "median3_feature_values"
            ],
            color="tab:orange",
            label="Causal median-3",
            linewidth=1.7,
        )

        ax.axhline(
            record["threshold_eo_q95"],
            color="0.35",
            linestyle="--",
            linewidth=1.2,
            label="EO Q95",
        )

        ax.axhline(
            record[
                "threshold_gap_midpoint"
            ],
            color="0.35",
            linestyle="-.",
            linewidth=1.7,
            label="Gap midpoint",
        )

        ax.axhline(
            record["threshold_ec_q05"],
            color="0.35",
            linestyle=":",
            linewidth=1.5,
            label="EC Q05",
        )

        ax.set_yscale("log")
        ax.set_ylim(y_min, y_max)

        ax.set_ylabel(
            "Posterior alpha mean PSD\n"
            "(V²/Hz)"
        )

        condition_text = (
            record["condition"]
            .replace(
                "baseline_",
                "",
            )
            .replace(
                "_",
                " ",
            )
        )

        ax.set_title(
            f"Subject {record['subject']} "
            f"— Run {record['run']} "
            f"({condition_text})"
        )

        ax.grid(
            True,
            which="both",
            alpha=0.3,
        )

        # Mark the Run 1 update at which
        # midpoint-threshold evidence changes
        # from raw HIGH to median-3 LOW.
        if (
            record["run"] == 1
            and record["condition"]
            == "baseline_eyes_open"
        ):
            target_indices = np.where(
                np.isclose(
                    record[
                        "decision_times_sec"
                    ],
                    26.0,
                    rtol=RTOL,
                    atol=ATOL,
                )
            )[0]

            if len(target_indices) != 1:
                raise RuntimeError(
                    "Expected exactly one "
                    "Run 1 decision update "
                    "at 26 s."
                )

            target_index = int(
                target_indices[0]
            )

            raw_value = record[
                "raw_feature_values"
            ][target_index]

            median3_value = record[
                "median3_feature_values"
            ][target_index]

            ax.scatter(
                [26.0],
                [raw_value],
                color="tab:blue",
                s=28,
                zorder=5,
            )

            ax.scatter(
                [26.0],
                [median3_value],
                color="tab:orange",
                s=28,
                zorder=5,
            )

            ax.annotate(
                "Midpoint evidence at 26 s:\n"
                "raw HIGH → median-3 LOW",
                xy=(
                    26.0,
                    raw_value,
                ),
                xytext=(
                    31.0,
                    raw_value * 1.8,
                ),
                arrowprops={
                    "arrowstyle": "->",
                    "linewidth": 0.8,
                },
                fontsize=8,
            )

    axes[-1].set_xlabel(
        "Decision time (s)"
    )

    axes[-1].set_xlim(
        0.0,
        60.0,
    )

    axes[-1].set_xticks(
        np.arange(
            0.0,
            61.0,
            10.0,
        )
    )

    handles, labels = (
        axes[0].get_legend_handles_labels()
    )

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(
            0.5,
            0.955,
        ),
        ncol=5,
        fontsize=8,
        frameon=True,
    )

    fig.suptitle(
        "Posterior-alpha feature streams, "
        "causal median-3 smoothing, "
        "and candidate thresholds",
        y=0.995,
    )

    fig.tight_layout(
        rect=(
            0.0,
            0.0,
            1.0,
            0.90,
        )
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    if (
        not output_path.exists()
        or output_path.stat().st_size == 0
    ):
        raise RuntimeError(
            "The feature-threshold figure "
            "was not saved correctly."
        )

    print("\n========================================")
    print(
        "Session 15 Figure 1: "
        "Feature streams and thresholds"
    )

    print(
        "Output figure:",
        output_path,
    )

    print(
        "Recording panel count:",
        len(figure_records),
    )

def main():
    selected_rows = (
        load_selected_decision_rows(
            csv_path=(
                DECISION_STREAM_CSV_PATH
            ),
        )
    )

    metadata = load_metadata(
        json_path=METADATA_JSON_PATH,
    )

    grouped_rows = (
        group_rows_by_rule_recording(
            selected_rows=selected_rows,
        )
    )

    thresholds_by_subject = (
        get_thresholds_by_subject(
            metadata=metadata,
        )
    )

    recording_keys = (
        validate_feature_figure_inputs(
            grouped_rows=grouped_rows,
            metadata=metadata,
            thresholds_by_subject=(
                thresholds_by_subject
            ),
        )
    )

    print_figure_input_summary(
        selected_rows=selected_rows,
        recording_keys=recording_keys,
        thresholds_by_subject=(
            thresholds_by_subject
        ),
    )

    figure_records = (
        build_feature_figure_records(
            grouped_rows=grouped_rows,
            recording_keys=recording_keys,
            thresholds_by_subject=(
                thresholds_by_subject
            ),
        )
    )

    save_feature_threshold_figure(
        figure_records=figure_records,
        output_path=(
            FEATURE_THRESHOLD_FIGURE_PATH
        ),
    )

    selected_episode_rows = (
        load_selected_command_episode_rows(
            csv_path=(
                COMMAND_EPISODE_CSV_PATH
            ),
        )
    )

    (
        grouped_episode_rows,
        command_recording_keys,
    ) = validate_command_figure_inputs(
        episode_rows=(
            selected_episode_rows
        ),
    )

    print("\n========================================")
    print(
        "Session 15 Figure Step 2: "
        "Command-figure input validation"
    )

    print(
        "Selected rule count:",
        len(
            REPRESENTATIVE_COMMAND_RULES
        ),
    )

    print(
        "Selected episode count:",
        len(selected_episode_rows),
    )

    print(
        "Recording count:",
        len(command_recording_keys),
    )

    save_representative_command_figure(
        grouped_episode_rows=(
            grouped_episode_rows
        ),
        recording_keys=(
            command_recording_keys
        ),
        output_path=(
            COMMAND_STATE_FIGURE_PATH
        ),
    )

if __name__ == "__main__":
    main()