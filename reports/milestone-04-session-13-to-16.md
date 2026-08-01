# Milestone 04 — Window-Level EEG Feature-to-Command Pipeline and Decision Rule v0.1

## 1. Overview

Milestone 04 developed the public EEG analysis track from a condition-level spectral comparison into a window-level offline feature-to-command pipeline.

The work progressed through the following stages:

```text
time-resolved command objective
→ posterior-alpha feature stream
→ observed temporal variability and partial EO–EC range overlap
→ temporal-parameter comparison
→ threshold, smoothing, and dwell comparison
→ provisional decision-rule candidate
→ reusable implementation and regression check
→ decision rule v0.1 formalization
```

Session 13 generated a reproducible time-ordered posterior-alpha feature stream to support command generation at successive time points. The resulting stream showed within-recording variability and partial overlap between the observed EO and EC feature ranges. These observations provided the basis for the temporal-parameter comparison in Session 14 and the decision-rule comparison in Session 15.

Session 14 compared outer-window length and step size and selected a `2 s window / 1 s step` configuration. Session 15 evaluated eight predefined threshold, smoothing, and dwell configurations and retained one provisional candidate. Session 16 used the milestone buffer to refactor repeated scientific logic, confirm preservation of the existing outputs after implementation changes, and formalize the selected candidate as decision rule v0.1.

The milestone produced two downstream interface artifacts:

```text
decision-rule-v0.1.json
decision-rule-v0.1-stream.csv
```

The JSON records the selected configuration and its source provenance. The CSV contains the corresponding stored command stream for later serial replay and actuator integration.

---

## 2. Period Covered

| Item               | Description                                                                   |
| ------------------ | ----------------------------------------------------------------------------- |
| Milestone          | Milestone 04                                                                  |
| Sessions covered   | Sessions 13–16                                                                |
| Actual work period | 2026-07-12 to 2026-08-01                                                      |
| Primary phase      | Window-level EEG feature-to-command analysis                                  |
| Final status       | Completed                                                                     |
| Next phase         | Serial communication, stored-command replay, and initial actuator integration |

---

## 3. Sessions Covered

| Session    | Main focus                                            | Main outcome                                        |
| ---------- | ----------------------------------------------------- | --------------------------------------------------- |
| Session 13 | Sliding-window posterior-alpha feature extraction     | Time-ordered window-level feature stream            |
| Session 14 | Window-length and step-size comparison                | Selection of the `2 s / 1 s` temporal configuration |
| Session 15 | Offline threshold, smoothing, and dwell comparison    | Provisional decision-rule candidate                 |
| Session 16 | Refactoring, regression check, and v0.1 formalization | Reusable modules and frozen replay artifacts        |

Session 16 does not have a separate weekly note. Its work is recorded in this milestone report, the related commits, and the decision-rule freeze artifacts.

---

## 4. Analysis Context and Fixed Definitions

### 4.1 Dataset and Recordings

| Item               | Setting                                                                   |
| ------------------ | ------------------------------------------------------------------------- |
| Dataset            | PhysioNet EEG Motor Movement/Imagery Dataset, accessed through MNE EEGBCI |
| Subject            | Subject 1                                                                 |
| Run 1              | Baseline eyes open                                                        |
| Run 2              | Baseline eyes closed                                                      |
| Sampling frequency | 160 Hz                                                                    |
| Target interval    | T0 annotation                                                             |
| Analyzed interval  | Windows fully contained within the first 60 s                             |

The two recordings were processed separately and provided the feature distributions used for the temporal-parameter and decision-rule analyses.

### 4.2 Preprocessing and Feature Definition

Continuous recordings were band-pass filtered from 1 to 40 Hz before outer-window extraction.

The posterior channels were:

```text
Po3., Poz., Po4., O1.., Oz.., O2..
```

For each outer window:

1. Welch PSD was calculated independently for each posterior channel.
2. PSD was averaged across the six posterior channels at each frequency.
3. The posterior mean PSD was averaged over the 8–12 Hz frequency bins.

| Welch parameter |            Setting |
| --------------- | -----------------: |
| Segment length  | 160 samples, 1.0 s |
| Segment overlap |  80 samples, 0.5 s |
| FFT length      |        160 samples |
| Window          |               Hann |
| Detrending      |           Constant |
| Scaling         |        PSD density |
| Feature band    | (8 \leq f < 13) Hz |

The resulting feature was:

```text
posterior_alpha_mean_psd
```

with the unit `V²/Hz`. Raw PSD values were used in calculations. Logarithmic axes were used only for visualization.

---

## 5. Key Technical Outcomes

### 5.1 Window-Level Posterior-Alpha Feature Stream

Session 13 converted the previous full-recording posterior-alpha analysis into a time-ordered feature stream.

Each 2 s window produced one posterior-alpha feature value. With a 1 s step, each recording produced 59 values, resulting in 118 rows in total.

| Recording            |       Mean |     Median | Population SD |    Minimum |    Maximum |
| -------------------- | ---------: | ---------: | ------------: | ---------: | ---------: |
| Baseline eyes open   | 4.4892e-11 | 3.9962e-11 |    2.8878e-11 | 1.5902e-11 | 2.2325e-10 |
| Baseline eyes closed | 5.4975e-10 | 5.0383e-10 |    2.5234e-10 | 1.6049e-10 | 1.2661e-09 |

The ratio between the recording-level means of the window features was approximately:

```text
eyes closed / eyes open = 12.25
```

The recording-level mean, median, and range were calculated only as descriptive summaries of the 59 window values. The time-ordered window-level stream, rather than these summary statistics, was the representation required for command generation at successive time points.

The window-level analysis showed variation within each recording. EO values were generally lower and EC values were generally higher, but the observed ranges partially overlapped:

```text
eyes-open maximum:   2.2325e-10 V²/Hz
eyes-closed minimum: 1.6049e-10 V²/Hz
```

The observed temporal variability and partial range overlap motivated the Session 14 comparison of window and step parameters and the Session 15 analysis of threshold, smoothing, and dwell configurations.

### 5.2 Temporal-Parameter Comparison

Session 14 compared outer-window lengths of 1, 2, and 4 s with the step fixed at 1 s.

| Window / step | Welch segments | EO IQR / median | EC IQR / median | Central 90% gap |
| ------------- | -------------: | --------------: | --------------: | --------------: |
| 1 s / 1 s     |              1 |           0.790 |           0.844 |      9.9715e-11 |
| 2 s / 1 s     |              3 |           0.498 |           0.691 |      1.5385e-10 |
| 4 s / 1 s     |              7 |           0.515 |           0.595 |      1.8029e-10 |

The 1 s window retained the highest relative within-recording variability. The 4 s window integrated the broadest temporal interval and produced the largest central 90% gap among the tested configurations, but required the longest interval before the first estimate became available.

The 2 s window provided intermediate temporal support with lower relative variability than the 1 s configuration.

Step sizes of 0.5, 1, and 2 s were then compared with the window length fixed at 2 s.

| Step size | Outer-window overlap | Outputs per recording |
| --------- | -------------------: | --------------------: |
| 0.5 s     |                  75% |                   117 |
| 1.0 s     |                  50% |                    59 |
| 2.0 s     |                   0% |                    30 |

Identical 2 s intervals produced identical feature values across the step-size configurations. Step size changed the positions and density of feature updates rather than the estimator applied to a shared interval.

The 0.5 s step provided additional intermediate updates but increased overlap between consecutive estimates. The 2 s step removed outer-window overlap but reduced the number of updates.

### 5.3 Selected Temporal Configuration

The following configuration was retained for the offline decision-rule analysis:

```text
Configuration ID: win-2s_step-1s
Window length: 2.0 s
Step size: 1.0 s
Outer-window overlap: 50%
Welch segments per feature: 3
First feature availability: 2.0 s
Windows per recording: 59
```

The configuration was selected as an intermediate engineering baseline between the higher local variability of the 1 s window and the broader temporal integration of the 4 s window. The 1 s step also provided an intermediate update density between the 0.5 and 2 s alternatives.

### 5.4 Offline Decision-Rule Comparison and Provisional Candidate

Session 15 applied the following processing sequence to the selected feature stream:

```text
raw feature
→ optional causal smoothing
→ fixed-threshold comparison
→ evidence state
→ dwell confirmation
→ active command state
```

Evidence and command states were defined as:

```text
feature < threshold   → LOW_ALPHA   → CMD_OPEN
feature ≥ threshold   → HIGH_ALPHA  → CMD_CLOSE
unavailable feature   → UNAVAILABLE → CMD_STOP
```

Three threshold candidates were calculated from the unsmoothed feature distributions:

| Threshold    | Definition                              |                    Value |
| ------------ | --------------------------------------- | -----------------------: |
| EO Q95       | 95th percentile of Run 1                | 8.270509057517e-11 V²/Hz |
| Gap midpoint | Geometric midpoint of EO Q95 and EC Q05 | 1.398718266196e-10 V²/Hz |
| EC Q05       | 5th percentile of Run 2                 | 2.365528862351e-10 V²/Hz |

The comparison included eight predefined configurations.

| Rule                          | First active command | Run 1 switches / brief episodes | Run 2 switches / brief episodes |
| ----------------------------- | -------------------: | ------------------------------: | ------------------------------: |
| EO Q95 / none / dwell-1       |                  2 s |                           4 / 2 |                           0 / 0 |
| Midpoint / none / dwell-1     |                  2 s |                           2 / 1 |                           0 / 0 |
| EC Q05 / none / dwell-1       |                  2 s |                           0 / 0 |                           4 / 2 |
| Midpoint / none / dwell-2     |                  3 s |                           0 / 0 |                           0 / 0 |
| Midpoint / none / dwell-3     |                  4 s |                           0 / 0 |                           0 / 0 |
| Midpoint / median-3 / dwell-1 |                  4 s |                           0 / 0 |                           0 / 0 |
| Midpoint / median-3 / dwell-2 |                  5 s |                           0 / 0 |                           0 / 0 |
| Midpoint / median-3 / dwell-3 |                  6 s |                           0 / 0 |                           0 / 0 |

At the Run 1 update ending at 26 s:

```text
raw feature:      2.232459066668e-10 V²/Hz
midpoint:         1.398718266196e-10 V²/Hz
median-3 feature: 3.958809706352e-11 V²/Hz
```

The raw midpoint, dwell-1 configuration produced a one-update `CMD_CLOSE` episode. Under dwell-2, the `HIGH_ALPHA` evidence was retained in the stream, but its candidate count did not reach the required value of two. The active command therefore remained `CMD_OPEN`.

Session 15 retained the following provisional candidate for milestone review:

```text
Rule ID: thr-gap-mid__smooth-none__dwell-2
Threshold: gap midpoint
Smoothing: none
Dwell: 2 consecutive available updates
```

Dwell-2 and dwell-3 produced the same zero-switch result in the two recordings. Dwell-2 confirmed the first active command one second earlier.

### 5.5 Session 16 Refactoring, Regression Check, and v0.1 Formalization

Session 16 was used as a milestone buffer. It did not introduce an independent EEG dataset or a new comparison result. Its main tasks were to formalize the provisional candidate selected in Session 15 and to separate repeated scientific logic into reusable modules.

The shared modules were:

```text
src/bci_robot/eeg_features.py
src/bci_robot/decision_rule.py
```

The feature module contains reusable functions for:

* outer-window boundary generation;
* Welch PSD calculation; and
* mean band-PSD extraction.

The decision module contains reusable functions for:

* threshold-state classification;
* evidence-to-command mapping; and
* stateful dwell confirmation.

The modules were separated to avoid maintaining duplicate scientific calculations across scripts, preserve a consistent implementation across sessions, distinguish reusable calculations from dataset-specific loading, calibration, aggregation, and file I/O, and support later application to additional recordings and subjects.

After refactoring, the affected Session 13–15 pipelines were rerun. The existing result and figure artifacts were preserved.

Session 16 then formalized the Session 15 candidate as decision rule v0.1 and generated a frozen decision stream containing:

```text
118 decision-stream rows
Run 1: 59 rows
Run 2: 59 rows
```

The frozen CSV was saved and reloaded to confirm that it matched the selected source rows. A machine-readable JSON record was also generated to preserve the selected rule, source paths, observed behavior, freeze date, and downstream output path.

---

## 6. Follow-up Research Focus: Local Temporal Concentration and Window Aggregation

During the Session 14 window-length comparison, additional attention was given to a localized posterior-alpha increase near 25 s in the eyes-open recording.

The 24–26 s, 2 s feature contained three overlapping 1 s Welch segments:

| Welch segment | Posterior-alpha estimate |
| ------------- | -----------------------: |
| 24.0–25.0 s   |               2.5904e-11 |
| 24.5–25.5 s   |               6.3269e-10 |
| 25.0–26.0 s   |               1.1147e-11 |

The high-valued 24.5–25.5 s segment represented one of three components in the 2 s feature and one of seven components in the corresponding 4 s feature. It therefore affected the two outer-window estimates differently.

Reconstruction from the component segments reproduced the saved 2 s and 4 s feature values. This confirmed that the observed difference was connected to temporal support, segment alignment, and aggregation.

This additional analysis was not part of the original primary comparison. It is retained as a follow-up research focus for examining:

* how frequently short- and long-window estimates diverge across full recordings;
* how window support and alignment affect feature sensitivity;
* whether comparable patterns appear in additional recordings and subjects; and
* how parameter-dependent feature excursions affect threshold and command behavior.

---

## 7. Decisions Made

### 7.1 Temporal Feature Baseline

The first offline control baseline will use:

```text
window length: 2.0 s
step size: 1.0 s
```

### 7.2 Decision Rule v0.1

The first formalized decision rule is:

```text
rule_id: thr-gap-mid__smooth-none__dwell-2
threshold: threshold_gap_midpoint
smoothing: smooth-none
dwell: 2 updates

LOW_ALPHA   → CMD_OPEN
HIGH_ALPHA  → CMD_CLOSE
UNAVAILABLE → CMD_STOP
```

The corresponding frozen stream will be used as the designated input for the initial stored-command replay. The freeze JSON preserves the selected configuration and source provenance.

---

## 8. Outputs Produced

### 8.1 Reusable Modules

* [`src/bci_robot/eeg_features.py`](../src/bci_robot/eeg_features.py)
* [`src/bci_robot/decision_rule.py`](../src/bci_robot/decision_rule.py)

### 8.2 Primary Scripts

* [`scripts/08_eegbci_sliding_window_alpha.py`](../scripts/08_eegbci_sliding_window_alpha.py)
* [`scripts/09_eegbci_window_parameter_comparison.py`](../scripts/09_eegbci_window_parameter_comparison.py)
* [`scripts/09b_eegbci_local_window_decomposition.py`](../scripts/09b_eegbci_local_window_decomposition.py)
* [`scripts/09c_eegbci_step_size_comparison_figure.py`](../scripts/09c_eegbci_step_size_comparison_figure.py)
* [`scripts/10_eegbci_offline_decision_rule.py`](../scripts/10_eegbci_offline_decision_rule.py)
* [`scripts/10b_eegbci_offline_decision_rule_figures.py`](../scripts/10b_eegbci_offline_decision_rule_figures.py)
* [`scripts/10c_freeze_decision_rule_v0_1.py`](../scripts/10c_freeze_decision_rule_v0_1.py)

### 8.3 Primary Result Groups

* [`results/session-13/`](../results/session-13/): window-level posterior-alpha feature stream and descriptive summary
* [`results/session-14/`](../results/session-14/): temporal-parameter comparison and local decomposition
* [`results/session-15/`](../results/session-15/): decision stream, command episodes, rule-run summary, and metadata
* [`results/session-16/`](../results/session-16/): frozen v0.1 command stream and freeze record

### 8.4 Primary Figure Groups

* [`figures/session-13/`](../figures/session-13/): window-level posterior-alpha trajectories
* [`figures/session-14/`](../figures/session-14/): window-length and step-size comparisons
* [`figures/session-15/`](../figures/session-15/): feature-threshold and command-state comparisons

### 8.5 Decision Rule v0.1 Artifacts

* [`results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1-stream.csv`](../results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1-stream.csv)
* [`results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json`](../results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json)

---

## 9. Open Questions

1. What criteria should be used to select or adjust window length and step size across different recordings and subjects?
2. Which calibration strategy—feature normalization, smoothing before calibration, dataset-specific calibration, or adaptive thresholds—best supports comparable control behavior across recordings and subjects?
3. How often, and under what signal conditions, do short- and long-window feature estimates diverge substantially across full recordings and datasets?
4. What latency is added by replay scheduling, serial round-trip communication, command processing, and actuator movement?
5. Should stored-command replay transmit every sampled command state or only transmit command-state changes?

---

## 10. Risks and Uncertainties

| Risk or uncertainty                          | Current status                                                                                | Planned response                                                                                          |
| -------------------------------------------- | --------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Limited and non-independent evaluation scope | Subject 1 Runs 1–2 were used for both threshold calibration and behavior review               | Extend the analysis to additional recordings, subjects, and later held-out data                           |
| Threshold transferability                    | The v0.1 threshold is an absolute PSD value calculated from the current feature distributions | Compare normalization, calibration order, dataset-specific calibration, and adaptive-threshold strategies |
| Offline-to-hardware timing gap               | Serial round-trip and actuator movement are not included in the current command timing        | Measure latency components during Sessions 18–19                                                          |

Decision rule v0.1 is an initial stored-replay baseline. Cross-subject and online behavior remain untested.

---

## 11. Sprint Continuation: Sessions 17–20

Continue the compressed Session 13–20 sprint defined after Milestone 03.

| Session    | Focus                                               | Status    |
| ---------- | --------------------------------------------------- | --------- |
| Session 17 | Arduino–servo–gripper actuator baseline             | Completed |
| Session 18 | Python–Arduino serial communication and ACK logging | Planned   |
| Session 19 | Frozen EEG-derived command replay                   | Planned   |
| Session 20 | Initial integration, verification, and demo record  | Planned   |

The immediate integration path is:

```text
decision-rule-v0.1-stream.csv
→ Python replay
→ serial transmission
→ Arduino acknowledgement
→ actuator command
```

---

## 12. Milestone Reflection

Milestone 04 introduced the project’s first time-based EEG feature and command analysis.

It also prepared the first explicit EEG-derived command interface for later robot integration by converting the selected decision rule into a frozen replay stream and machine-readable configuration record.

During the temporal-parameter comparison, an additional research focus was identified around local temporal concentration and window aggregation. This focus will be carried into later multi-recording, multi-subject, and parameter-sensitivity analyses.

---

## 13. Related Records

* [`weekly-notes/session-13-260712.md`](../weekly-notes/session-13-260712.md)
* [`weekly-notes/session-14-260717.md`](../weekly-notes/session-14-260717.md)
* [`weekly-notes/session-15-260724.md`](../weekly-notes/session-15-260724.md)
* [`milestone-03-session-09-to-12.md`](milestone-03-session-09-to-12.md)
* [`docs/timeline-revision-2026-07-12.md`](../docs/timeline-revision-2026-07-12.md)
* [`results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json`](../results/session-16/eegbci_subject-001_runs-01-02_posterior-alpha_decision-rule-v0.1.json)

---

## 14. References

1. PhysioNet.
   [EEG Motor Movement/Imagery Dataset, version 1.0.0](https://physionet.org/content/eegmmidb/1.0.0/)

2. MNE-Python documentation.
   [`mne.datasets.eegbci.load_data`](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html)

3. SciPy documentation.
   [`scipy.signal.welch`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html)

4. Welch, P. D. (1967).
   [“The Use of Fast Fourier Transform for the Estimation of Power Spectra: A Method Based on Time Averaging over Short, Modified Periodograms.”](https://doi.org/10.1109/TAU.1967.1161901)
   *IEEE Transactions on Audio and Electroacoustics, 15*(2), 70–73.
