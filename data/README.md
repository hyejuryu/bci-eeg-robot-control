# Data

This directory stores and documents public EEG data and locally acquired EEG data used in this project.

Large raw data files are not committed to the repository.

## Directory Structure

- `raw/`: Original or directly acquired data files
- `interim/`: Intermediate working files
- `processed/`: Cleaned or analysis-ready data

## Data Policy

- Raw EEG data should remain unchanged after download or acquisition.
- Large raw data files should not be committed to GitHub.
- Sensitive or personally identifiable data should not be committed.
- Dataset source, subject, run, condition, sampling frequency, and file format should be documented.
- Derived results should be traceable to the corresponding script, result file, and session record.

## Public EEG Dataset

### PhysioNet EEG Motor Movement/Imagery Dataset

| Item | Value |
|---|---|
| Access method | MNE-Python `eegbci.load_data()` |
| Subject | Subject 1 |
| Runs | Run 1 and Run 2 |
| Conditions | Baseline eyes open and baseline eyes closed |
| Sampling frequency | 160 Hz |
| File format | EDF |
| Used in | Sessions 06, 07, and 13 |
| Local storage | MNE-managed local dataset directory |
| Repository handling | Dataset files are not committed |

Current uses include:

- raw EEG structure inspection
- time-domain waveform visualization
- posterior PSD and band-power comparison
- sliding-window posterior alpha feature extraction

Session-specific preprocessing and feature parameters are recorded in the corresponding scripts, result summaries, and weekly notes.

## Locally Acquired OpenBCI Data

### Session 11

Session 11 generated a short OpenBCI Cyton recording using BrainFlow.

Local-only files are stored under:

```text
data/raw/session-11/
````

The files include:

* raw BrainFlow CSV
* acquisition metadata JSON

The Session 11 recording was collected to verify the acquisition and file-handling pipeline rather than for feature-level analysis.

The repository-visible readback summary is stored under:

```text
results/session-11/
```

### Session 12

No BrainFlow recording was generated in Session 12 because a stable GUI-level acquisition condition was not established.

Session 12 contains troubleshooting documentation and screenshot evidence rather than a recorded EEG dataset.

## Required Record for New Data

When a new dataset or recording is added, document the following where applicable:

* dataset or recording name
* source or acquisition device
* download or acquisition date
* subject or participant identifier
* run or session identifier
* condition label
* sampling frequency
* channel names or channel mapping
* file format
* recording duration
* local-only and repository-visible file boundaries
