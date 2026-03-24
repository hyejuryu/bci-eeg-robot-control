# BCI-Based EEG Signal Analysis and Robot Control

## Summary
This project investigates whether attention-related EEG features can be used to control a simple robotic system in real time.

## Background and Motivation

## Research Goal
To build and evaluate a prototype system that extracts EEG features related to attention and converts them into robot control commands.

## Research Questions
1. Can meaningful EEG features be extracted from low-cost EEG hardware?
2. Do focus-related conditions produce usable differences in beta-band power?
3. Can threshold-based real-time control achieve measurable performance?

## Hypotheses

## System Overview
The system consists of the following pipeline:

EEG acquisition (OpenBCI Cyton)
→ signal preprocessing (filtering, segmentation)
→ feature extraction (beta-band power)
→ decision logic (threshold-based trigger)
→ serial communication from Python to Arduino
→ servo motor / gripper actuation

# pics

## Tools and Hardware
- OpenBCI Cyton board
- EEG electrodes and acquisition setup
- BrainFlow
- Python (NumPy, SciPy, MNE, Matplotlib)
- Arduino
- Servo motor / simple robotic gripper
- GitHub for version control and documentation
- Medium Blog

## Methods
The project proceeds in four stages:

1. Foundational study of neuroscience, EEG, and BCI
2. Offline EEG analysis using public datasets
3. Real EEG acquisition with OpenBCI
4. Real-time integration of EEG features with robot control

# Can be more specific

## Expected Outputs
- EEG analysis pipeline
- Real-time BCI prototype
- Experimental logs and visualizations
- Final report and demo materials
- GitHub repository showing the full development process

## Significance

