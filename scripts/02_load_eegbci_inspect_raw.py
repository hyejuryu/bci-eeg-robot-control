from pathlib import Path
import json

import mne
from mne.datasets import eegbci


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = PROJECT_ROOT / "results" / "session-06"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

SUBJECT = 1
RUNS = [1, 2]

RUN_LABELS = {
    1: "baseline_eyes_open",
    2: "baseline_eyes_closed",
}


def inspect_run(run):
    print(f"\n=== Run {run}: {RUN_LABELS[run]} ===")

    file_path = eegbci.load_data(subject=SUBJECT, runs=[run])[0]

    raw = mne.io.read_raw_edf(file_path, preload=True, verbose=False)

    sfreq = raw.info["sfreq"]
    n_channels = len(raw.ch_names)
    n_samples = raw.n_times
    duration_sec = raw.times[-1]
    data = raw.get_data()

    summary = {
        "subject": SUBJECT,
        "run": run,
        "condition": RUN_LABELS[run],
        "file_path": str(file_path),
        "sampling_frequency_hz": float(sfreq),
        "n_channels": int(n_channels),
        "n_samples": int(n_samples),
        "duration_seconds": float(duration_sec),
        "data_shape_channels_x_samples": list(data.shape),
        "first_10_channel_names": raw.ch_names[:10],
        "all_channel_names": raw.ch_names,
        "annotations": [
            {
                "onset": float(a["onset"]),
                "duration": float(a["duration"]),
                "description": str(a["description"]),
            }
            for a in raw.annotations
        ],
        "data_min_volts": float(data.min()),
        "data_max_volts": float(data.max()),
        "note": "MNE stores EEG data in volts. EEG plots are often shown in microvolts.",
    }

    output_path = RESULT_DIR / f"subject-001_run-{run:02d}_{RUN_LABELS[run]}_raw_summary.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("file:", file_path)
    print("sampling frequency:", sfreq)
    print("channels:", n_channels)
    print("samples:", n_samples)
    print("duration:", duration_sec)
    print("data shape:", data.shape)
    print("first 10 channels:", raw.ch_names[:10])
    print("saved:", output_path)


if __name__ == "__main__":
    for run in RUNS:
        inspect_run(run)

    print("\nSession 06 raw inspection completed.")