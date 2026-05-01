# Scripts

This directory contains executable Python scripts for reproducible analysis.

Scripts should be runnable from the command line and should perform a clear task from start to finish.

## Purpose

Use scripts for:

- environment checks
- loading public EEG datasets
- plotting raw EEG signals
- filtering data
- computing power spectra
- calculating alpha and beta power
- exporting result summaries
- testing Arduino serial communication
- running simple BCI control logic

## Difference from Notebooks

- `notebooks/`: exploratory and interactive
- `scripts/`: cleaned, repeatable, and executable
- `src/`: reusable functions and modules

## Naming Convention

Use numbered prefixes to indicate rough workflow order.

Examples:

- `00_check_environment.py`
- `01_synthetic_signal_psd.py`
- `02_load_eegbci_subject01.py`
- `03_plot_raw_eeg.py`
- `04_compute_alpha_beta_power.py`
- `05_compare_eyes_open_closed.py`

## Rule

Each script should ideally answer one clear question or perform one clear step.

Examples:

- Can the Python EEG environment run successfully?
- Can a synthetic signal be converted into a power spectrum?
- Can public EEG data be loaded?
- Can alpha and beta power be calculated?
