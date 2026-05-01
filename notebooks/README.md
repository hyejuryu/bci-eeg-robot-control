# Notebooks

This directory contains Jupyter notebooks for exploratory analysis.

Notebooks are used for trying ideas, inspecting data, visualizing signals, and writing analysis notes alongside code.

## Purpose

Notebooks are for exploration, not final production code.

Use notebooks to:

- inspect EEG data structure
- check channel names and sampling rate
- visualize raw signals
- test filtering and spectral analysis
- compare experimental conditions
- write intermediate observations

## Difference from Scripts

- `notebooks/`: exploratory, interactive, and explanatory
- `scripts/`: cleaned and reproducible execution code
- `src/`: reusable functions and modules

## Naming Convention

Use session numbers and short descriptions.

Examples:

- `session-05-environment-test.ipynb`
- `session-06-load-public-eeg.ipynb`
- `session-07-filtering-psd-practice.ipynb`
- `session-08-alpha-beta-visualization.ipynb`

## Rule

If an analysis becomes stable and should be repeated, move the core logic into `scripts/` or `src/`.
