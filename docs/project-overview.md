# EEG Feature Analysis and Replay-Based Robot Control
_Last updated: 2026.07.12_

> The project direction was revised after Session 12. See the [Project Timeline Revision](timeline-revision-2026-07-12.md).

## Summary

This project develops and evaluates a reproducible pipeline that converts public EEG recordings into window-level feature time series, decision-rule outputs, and Arduino actuator commands.

The primary focus is how EEG feature variability and decision-rule parameters affect command switching, stability, and latency.

Public EEG replay-control is the primary development track. OpenBCI self-recording remains a separate, support-guided validation track until stable acquisition is established.

## Background and Motivation

EEG is an indirect and variable population-level signal. A condition-level average may show a spectral difference, but it does not describe how the feature changes over time or how it behaves when used as a control input.

Threshold-based control introduces an additional issue. Small changes in a continuous feature value can produce discrete command-state changes, particularly when the feature remains near the threshold.

The project therefore focuses on the following sequence:

```text
EEG time series
→ window-level feature variability
→ threshold-crossing behavior
→ command-state dynamics
→ actuator response
```

EEG is used as the first case for studying time-series variability, threshold sensitivity, and control stability across signal-processing and actuator layers.

## Project Goal

The project has two main goals:

1. Build a replay-based pipeline that converts public EEG recordings into actuator commands.
2. Evaluate how feature-processing and decision-rule parameters affect command stability and latency.

The current pipeline is intended to support later integration of self-recorded EEG if stable OpenBCI acquisition becomes available.

## Research Questions

1. Can public EEG recordings be converted into reproducible window-level feature time series?
2. How do window length and step size affect feature variability and temporal resolution?
3. How do threshold, smoothing, dwell time, hysteresis, and related decision rules affect command switching, fragmentation, and latency?
4. Can stored EEG-derived command streams be transmitted consistently through the Python–Arduino–actuator path?

## Current Project Tracks

### Track A. Public EEG Replay-Control

This is the primary analysis and control-development track.

```text
public EEG
→ preprocessing
→ sliding-window feature extraction
→ feature time series
→ decision rule
→ command state stream
```

### Track B. Arduino Actuator Output

This track establishes the command-transmission and actuator path.

```text
command state stream
→ Python serial communication
→ Arduino
→ servo or simple actuator
→ response log
```

### Track C. OpenBCI Self-Recording

This is an optional validation track.

```text
support-guided diagnostic
→ stable acquisition check
→ optional self-recorded data integration
```

Further OpenBCI hardware testing will resume when a specific diagnostic procedure is available.

## System Overview

The primary system consists of two connected layers.

### EEG Feature and Decision Layer

```text
public EEG recording
→ data loading
→ preprocessing
→ posterior channel selection
→ sliding-window feature extraction
→ feature time series
→ threshold or stateful decision rule
→ command log
```

Posterior alpha power from defined eyes-open and eyes-closed recordings is used as the initial feature workflow.

Feature definitions may be revised after examining window-level variability, distribution overlap, and control behavior.

### Command and Actuator Layer

```text
command log
→ Python replay
→ serial command
→ Arduino command parsing
→ actuator response
→ communication and response log
```

The two layers are developed separately before end-to-end replay integration.

## Methods

The revised project proceeds through the following stages:

1. Reuse the existing public EEG loading and preprocessing workflow.
2. Divide recordings into sliding time windows and calculate a spectral feature for each window.
3. Export and inspect the resulting feature time series, including within-condition variability, between-condition overlap, and window-to-window changes.
4. Develop and compare initial decision rules using thresholding, smoothing, dwell time, and other stateful control methods where relevant.
5. Generate and log command state streams from the EEG-derived feature time series.
6. Transmit stored command streams through Python–Arduino serial communication and record actuator responses.
7. Evaluate command switching, short command bursts, latency, and sensitivity to feature-processing and decision-rule parameters.
8. Conduct a focused analysis of how feature variability and proximity to decision thresholds relate to control stability.

## Current Status

The following work has been completed:

* Python EEG analysis environment setup
* public EEG loading and raw-data inspection
* filtering, Welch PSD, and alpha/beta band-power calculation
* posterior eyes-open versus eyes-closed alpha-reactivity sanity check
* OpenBCI GUI / Cyton / COM3 connection verification
* BrainFlow acquisition, save, metadata, and readback infrastructure
* OpenBCI acquisition-stability troubleshooting through Session 12

Stable self-recorded acquisition was not established by the end of Session 12.

The current development sequence therefore begins with public EEG feature replay and Arduino output integration.

## Tools and Hardware

### Analysis and Software

* Python
* MNE-Python
* NumPy
* SciPy
* Pandas
* Matplotlib
* BrainFlow
* Git and GitHub

### Hardware

* Arduino
* servo motor or simple robotic actuator
* OpenBCI Cyton for optional acquisition validation

Arduino or robot hardware remains disconnected during body-connected EEG acquisition.

## Expected Outputs

* reproducible public EEG loading and preprocessing workflow
* sliding-window EEG feature pipeline
* window-level feature data and time-series figures
* feature and command logs
* threshold and stateful decision-rule comparison
* Python–Arduino serial interface
* replay-based actuator demonstration
* command-stability and latency analysis
* focused analysis of feature variability and threshold sensitivity
* project v1 report and documented extension scope

## Interpretation and Scope

The initial EEG analysis uses defined eyes-open and eyes-closed conditions. Alpha or beta power is not treated as a direct measure of attention or focus.

The actuator demonstration uses replayed feature and command streams derived from public EEG recordings. It is not a real-time self-recorded BCI demonstration.

Self-recorded OpenBCI integration remains conditional on stable acquisition and analysis-ready signal quality.

## Project Relevance

The project examines how a variable biological feature stream interacts with threshold-based and stateful decision rules.

Its main contribution is the separation and evaluation of:

```text
signal acquisition
feature extraction
decision logic
command transmission
actuator response
```

This structure allows acquisition risk, feature variability, control stability, and hardware behavior to be investigated as related but distinct system components.

## Related Documents

* [Initial Project Timeline](timeline.md)
* [Project Timeline Revision After Session 12](timeline-revision-2026-07-12.md)
* [Milestone 01 Report](../reports/milestone-01-session-01-to-03.md)
* [Milestone 02 Report](../reports/milestone-02-session-05-to-07.md)
* [Milestone 03 Report](../reports/milestone-03-session-09-to-12.md)
