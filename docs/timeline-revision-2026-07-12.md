# Project Timeline Revision After Session 12

## 1. Revision Scope

| Item              | Description                               |
| ----------------- | ----------------------------------------- |
| Revision date     | 2026.07.12                                |
| Sessions affected | Session 13–30                             |
| Reference point   | Completion of Session 12 and Milestone 03 |
| Initial timeline  | [`timeline.md`](timeline.md)              |

This document records the timeline and project-sequence revision made after Session 12.

Sessions 1–12, their weekly notes, and completed milestone reports remain unchanged. They retain the work, outputs, understanding, and limitations recorded at the time.

## 2. Basis for Revision

### 2.1 Technical and Content Revision

The original timeline assumed the following sequence:

```text
OpenBCI acquisition stabilization
→ self-recorded eyes-open / eyes-closed experiment
→ cognitive-condition experiment
→ real-time EEG feature calculation
→ Arduino control
```

By the end of Session 12:

* the OpenBCI GUI / Cyton / COM3 connection path had been confirmed;
* the BrainFlow acquisition, save, metadata, and readback workflow had been implemented;
* stable self-recorded acquisition had not been established;
* the existing public EEG analysis pipeline remained available for further feature and control development.

The revised plan therefore uses public EEG replay-control as the primary project track. OpenBCI self-recording remains an optional, support-guided validation track.

Detailed acquisition evidence and limitations are documented in the [Milestone 03 Report](../reports/milestone-03-session-09-to-12.md).

### 2.2 Schedule Revision

The original plan assigned one session to each weekly period and placed EEG–Arduino integration after the self-recorded experiment block.

The revised schedule:

* reorganizes Sessions 13–24 around public EEG feature extraction, decision logic, Arduino integration, and control evaluation;
* uses milestone target dates while allowing individual session dates to move according to actual execution;
* defines sessions by their main question and output rather than by a fixed weekly interval;
* reserves Sessions 25–30 for one focused research cycle and project v1 documentation.

## 3. Revised Project Tracks

### Track A. Public EEG Replay-Control

```text
public EEG
→ preprocessing
→ sliding-window feature extraction
→ feature time series
→ decision rule
→ command state stream
```

This is the primary analysis and control-development track.

### Track B. Arduino Actuator Output

```text
command stream
→ Python serial communication
→ Arduino
→ servo or simple actuator
```

This track establishes the command and actuator path before integration with EEG-derived replay commands.

### Track C. OpenBCI Self-Recording

```text
support-guided diagnostic
→ stable acquisition check
→ optional self-recorded data integration
```

Further OpenBCI testing will resume when a specific diagnostic procedure is available. It is not a dependency for the revised Session 13–30 sequence.

## 4. Revised Timeline

### Phase 3A. OpenBCI Acquisition Setup

**Sessions 9–12 — completed**

**Goal:** establish the OpenBCI connection and acquisition infrastructure and assess whether stable self-recorded acquisition is available.

* Session 9: Cyton structure, electrode configuration, safety, and acquisition preparation
* Session 10: OpenBCI GUI connection and initial signal diagnostics
* Session 11: BrainFlow acquisition, save, metadata, and readback workflow
* Session 12: acquisition-stability troubleshooting and project-sequence review

**Phase outcome:** the connection and file-handling paths were confirmed. Stable self-recorded acquisition was not established.

---

### Phase 3B. Public EEG Feature and Decision Pipeline

**Sessions 13–16**
**Target completion:** 2026.07.22

**Goal:** convert existing public EEG recordings into window-level feature and offline command streams.

* **Session 13:** reuse EEGBCI data and the existing preprocessing workflow; calculate sliding-window posterior alpha features and export the feature time series and figures
* **Session 14:** examine within-condition variability and EO/EC distribution overlap; compare initial window-length and step-size candidates
* **Session 15:** implement initial threshold, smoothing, and dwell-time rules; generate an offline command state stream
* **Session 16:** milestone and buffer; review Sessions 13–15 and define the initial decision rule and feature-to-command log structure

**Minimum phase output:**

```text
public EEG recording
→ window-level feature data
→ feature time-series figure
→ initial offline decision rule
→ command state stream
```

---

### Phase 4. Arduino and Replay-Control Integration

**Sessions 17–20**
**Target completion:** 2026.07.31

**Goal:** establish the actuator path and connect it to a stored EEG-derived command stream.

* **Session 17:** implement basic Arduino and servo control with a minimum command set
* **Session 18:** implement Python–Arduino serial communication, command parsing, acknowledgement handling, and communication logging
* **Session 19:** replay the stored EEG-derived command stream through Python serial communication and connect it to the actuator
* **Session 20:** milestone and buffer; resolve integration issues and produce the minimum feature-to-command-to-actuator demonstration and logs

**Minimum phase output:**

```text
EEG-derived command stream
→ Python replay
→ serial command
→ Arduino actuator response
```

---

### Phase 5. Control Sensitivity and Stability Evaluation

**Sessions 21–24**
**Target completion:** 2026.08.23

**Goal:** evaluate how feature-processing and decision-rule parameters affect command behavior.

* **Session 21:** compare command behavior across window length, step size, threshold, smoothing, and dwell-time candidates
* **Session 22:** examine recording dependence using another subject, run, or holdout segment
* **Session 23:** analyze threshold crossings, command switching, short command bursts, false-trigger-like events, and processing or serial latency
* **Session 24:** milestone and buffer; summarize parameter sensitivity and fix replay-control demo v1

**Minimum phase output:**

```text
parameter comparison
→ command-stability metrics
→ latency analysis
→ replay-control demo v1
```

---

### Summer Buffer and Project Documentation

**Target period:** 2026.08.24–08.31

This period is reserved for:

* project-description revision
* GitHub README updates
* completion of missing figures or demo material
* external communication material
* preparation for the academic semester

This period is not assigned a numbered session.

---

### Phase 6. Focused Research Cycle and Project v1 Completion

**Sessions 25–30**
**Target dates:** to be set after Session 24

**Goal:** complete one focused analysis cycle on EEG feature variability and threshold-based control behavior, then document project v1.

The working research direction is:

> EEG feature time-series variability and threshold-based control stability: from public EEG replay to Arduino actuator commands

* **Session 25:** document the research question and analysis scope; define feature variability, threshold proximity, command stability, and latency operationally
* **Session 26:** conduct a small analysis pilot using selected subjects or runs; check metric definitions and result-table structure
* **Session 27:** analyze relationships among feature variability, threshold crossings, and command switching
* **Session 28:** compare simple threshold, smoothing, dwell time, hysteresis, and related stateful decision rules
* **Session 29:** summarize the sensitivity–stability–latency trade-off using the main figures, tables, and result interpretation
* **Session 30:** prepare the final report draft, organize the repository and demonstration material, and define the scope and limitations of project v1

Sessions 25–30 may be conducted as a compact research cycle. Their target dates will be set after reviewing the completion status of Session 24.

## 5. Schedule Management

Milestone target dates are planned in advance.

Individual session dates may move according to actual execution. Target periods and actual run dates are recorded separately.

If a task requires additional investigation, the session count or target period may be revised without modifying completed session records.

## 6. Deferred and Optional Work

The following items remain outside the primary Session 13–30 dependency path:

* stable self-recorded EO/EC acquisition
* self-recorded posterior alpha-reactivity analysis
* self-recorded cognitive-condition experiments
* real-time OpenBCI-to-Arduino control
* additional OpenBCI hardware diagnostics without support guidance
* larger multi-subject or alternative-dataset analysis
* later nonlinear time-series extensions

These items may be added when the required acquisition condition, method, or project capacity becomes available.

## 7. Project v1 and Future Extensions

Session 30 is the planned completion point of project v1.

Work arising from OpenBCI acquisition recovery, additional datasets, laboratory research, or later time-series methods will be recorded as separate extensions. Completed milestone and session records will not be retrospectively revised using later results.

## 8. Related Documents

* [Initial Project Timeline](timeline.md)
* [Project Overview](project-overview.md)
* [Milestone 02 Report](../reports/milestone-02-session-05-to-07.md)
* [Milestone 03 Report](../reports/milestone-03-session-09-to-12.md)
