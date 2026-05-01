# Source Code

This directory contains reusable source code for the project.

At the early stage of the project, most code may remain in `scripts/` or `notebooks/`.

As repeated logic emerges, it should be moved into `src/`.

## Purpose

Use `src/` for reusable functions and modules, such as:

- EEG data loading
- filtering
- band power calculation
- plotting utilities
- feature extraction
- threshold decision logic
- Arduino serial communication
- experiment logging

## Example Structure

- `bci_robot/io.py`: data loading and saving
- `bci_robot/preprocessing.py`: filtering and preprocessing
- `bci_robot/features.py`: band power and feature extraction
- `bci_robot/visualization.py`: plotting functions
- `bci_robot/control.py`: threshold decision and control logic
- `bci_robot/utils.py`: helper functions

## Difference from Scripts

- `scripts/`: executable workflows
- `src/`: reusable tools used by scripts and notebooks

## Principle

Do not move code into `src/` too early.

Only move code here when it is used repeatedly across multiple sessions or scripts.
