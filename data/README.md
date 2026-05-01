# Data

This directory stores information about EEG and related experimental data used in this project.

Large raw data files are not committed to this repository.

## Directory Structure

- `raw/`: Original data files
- `interim/`: Intermediate working files
- `processed/`: Cleaned or analysis-ready data

## Data Policy

- Raw EEG data should be kept unchanged.
- Large data files should not be uploaded to GitHub.
- Sensitive or personally identifiable data should not be committed.
- Public dataset sources, download instructions, subject IDs, and run numbers should be documented here.

## Planned Public Dataset

### PhysioNet EEG Motor Movement/Imagery Dataset

Planned use:

- raw EEG signal inspection
- channel and sampling-rate check
- eyes-open / eyes-closed comparison
- alpha reactivity analysis
- alpha and beta power visualization

## Notes

When a dataset is used, record the following information:

- dataset name
- source URL
- download date
- subject ID
- run or session number
- sampling frequency
- channel names
- file format
- preprocessing steps
