# Research Agent Pilot 001 — Frozen Analysis Specification

- **Project:** bci-eeg-robot-control
- **Research session:** Session 21
- **Pilot:** Research Agent Pilot 001
- **Status:** FROZEN / AUTHORIZED FOR EXECUTION
- **Approval:** Human-approved
- **Authorized scope:** Phase 1 only
- **Frozen date:** 2026-08-08
- **Governing protocol:** `research-agent/docs/operating_protocol_v0.1.md`


## 1. Research Context

Session 21 returns to parameter-sensitivity analysis after completion of the minimum offline EEG-derived replay-control pipeline in Sessions 17–20.

The session-level objective is:

> Compare command behavior across candidate window length, step size, threshold, smoothing, and dwell settings, while extending the existing posterior-alpha variability analysis with temporal successive-change measures.

Session 15 evaluated eight selected decision-rule configurations using the `win-2s_step-1s` feature stream. The complete 3-threshold × 2-smoothing × 3-dwell grid was deferred for later parameter analysis.

Session 21 Phase 1 consists of:

```text
A. Complete Decision-Rule Parameter Grid
   [PRIMARY]

B. Temporal Feature-Variability Analysis
   [SUPPORTING]

→ Agent Report
→ Human Review
→ Possible Phase 2 proposal
```

Phase 2 is not authorized under this specification.

---

# 2. Phase 1A — Complete Decision-Rule Parameter Grid

## 2.1 Objective

Complete the decision-rule parameter grid deferred in Session 15 and characterize command behavior across threshold, smoothing, and dwell combinations using the same input feature stream.

## 2.2 Fixed Input

```text
Dataset:
PhysioNet EEGBCI

Subject:
1

Recordings:
Run 1 — baseline eyes open
Run 2 — baseline eyes closed

Feature:
posterior_alpha_mean_psd

Window:
2.0 s

Step:
1.0 s

Configuration:
win-2s_step-1s
```

Use the existing Session 14 feature values.

## 2.3 Parameter Grid

### Threshold

```text
threshold_eo_q95
threshold_gap_midpoint
threshold_ec_q05
```

Use the existing Session 15 threshold values without recalibration.

### Smoothing

```text
smooth-none
smooth-median3
```

Median-3 retains the existing causal definition:

```text
median(
    current update,
    previous update,
    two-updates-back
)
```

### Dwell

```text
dwell-1
dwell-2
dwell-3
```

Retain the existing consecutive-update confirmation definition.

### Complete Grid

[
3 \times 2 \times 3 = 18
]

decision-rule configurations.

Reproduce the eight configurations already evaluated in Session 15 and generate the remaining ten configurations.

## 2.4 Reference Configuration

```text
threshold_gap_midpoint
smooth-none
dwell-2
```

This is the Session 16 frozen reference configuration.

## 2.5 Outcome Measures

Reuse existing Session 15 definitions where available.

### Evidence behavior

* LOW/HIGH evidence count and fraction
* evidence transition count
* unconfirmed candidate update count

### Command behavior

* first active command
* first active command time
* initial STOP duration
* active OPEN↔CLOSE switch count
* command episode count
* short active command episode count
* shortest active episode duration
* longest active episode duration
* OPEN/CLOSE/STOP occupancy

Short active command episode:

```text
duration <= 2.0 s
```

## 2.6 Pre-Specified Descriptive Comparisons

Summarize the grid by individual factors and the following factor-combination patterns:

```text
threshold × dwell
smoothing × dwell
threshold × smoothing
```

These are descriptive comparisons across the predefined configurations, not inferential interaction tests.

---

# 3. Phase 1B — Temporal Feature-Variability Analysis

## 3.1 Objective

Extend the Session 14 posterior-alpha variability analysis with successive-change measures.

## 3.2 Source Feature Configurations

Use the existing Session 14 feature streams:

```text
win-1s_step-1s
win-2s_step-0p5s
win-2s_step-1s
win-2s_step-2s
win-4s_step-1s
```

## 3.3 Distributional Variability

Retain the existing Session 14 relative-IQR measure:

[
\text{Relative IQR}
===================

\frac{Q_{75}-Q_{25}}
{\operatorname{median}(x)}
]

## 3.4 Successive-Change Metrics

For chronologically ordered feature values:

[
\Delta x_t=x_t-x_{t-1}
]

### Spectral-Feature Volatility

[
V_x=SD(\Delta x_t)
]

Implementation:

```text
population SD
ddof = 0
```

This metric adapts the successive spectral-power volatility formulation used by Yu et al. (2024).

### Median Absolute Successive Change

[
M_\Delta=
\operatorname{median}(|\Delta x_t|)
]

Use this as a project-defined robust companion statistic describing the typical magnitude of successive feature changes.

Interpret the two measures jointly when describing broadly elevated successive variation versus variability influenced by relatively rare large excursions.

## 3.5 Primary Comparison

Primary cross-window comparison:

```text
win-1s_step-1s
win-2s_step-1s
win-4s_step-1s
```

The common 1 s step keeps the elapsed interval between successive feature estimates constant.

Calculate successive-change metrics for the 0.5 s and 2 s step configurations for descriptive record purposes, but do not directly rank raw volatility across different step sizes.

Successive differences at different step sizes represent different elapsed intervals. In addition, the 2 s outer windows have different overlap structures across the existing step-size configurations. This comparison restriction follows the time-step dependence of successive-change volatility discussed by Yu et al. (2024) and the overlap structure established in Session 14.

---

# 4. Phase 1 Relationship and Reporting Order

Execute Phase 1A first, followed by Phase 1B.

Phase 1A evaluates decision-rule sensitivity using the fixed `win-2s_step-1s` feature stream.

Phase 1B characterizes temporal variability in the existing Session 14 feature streams.

Do not add an event-level linkage analysis between Phase 1A and Phase 1B during the authorized execution.

After both analyses are complete, report the results for human review.

---

# 5. Validation

Existing Session 14 feature-generation validation and Session 15 decision-rule validation remain the upstream basis for Session 21.

## 5.1 Reproduction Checks

* reproduce the eight existing Session 15 decision rules;
* verify agreement with the saved Session 15 decision streams, command episodes, and summaries;
* verify retained threshold, smoothing, and dwell definitions.

## 5.2 Extension Checks

* confirm exactly 18 unique Phase 1A rule configurations;
* confirm Run 1 and Run 2 are present for every rule;
* verify consistency among decision-stream, command-episode, and rule-summary outputs;
* verify chronological ordering and finite values for Phase 1B inputs and calculated metrics;
* reload and verify saved Session 21 outputs.

Report any validation mismatch before reporting the corresponding scientific result.

---

# 6. Required Phase 1 Outputs

## 6.1 Research Outputs

```text
results/session-21/

session21_rule-grid_decision-stream.csv
session21_rule-grid_command-episodes.csv
session21_rule-grid_summary.csv
session21_feature-temporal-variability-summary.csv
session21_analysis_metadata.json
```

## 6.2 Figures

```text
figures/session-21/

session21_rule-grid_command-behavior.png
session21_feature-temporal-variability.png
```

---

# 7. Methodological References

### Yu et al. (2024)

Yu, Y., Oh, Y., Kounios, J., & Beeman, M.
*EEG Spectral-Power Volatility Predicts Problem-Solving Outcomes.*
Journal of Cognitive Neuroscience, 36(5), 901–915.
DOI: 10.1162/jocn_a_02136.

**Use in Session 21:** methodological precedent for `SD(Δx)` as a successive spectral-power variability measure and for considering time-step dependence.

### Li et al. (2018)

Li, L., Huang, G., Lin, Q., Liu, J., Zhang, S., & Zhang, Z.
*Magnitude and Temporal Variability of Inter-stimulus EEG Modulate the Linear Relationship Between Laser-Evoked Potentials and Fast-Pain Perception.*
Frontiers in Neuroscience, 12, 340.
DOI: 10.3389/fnins.2018.00340.

**Use in Session 21:** EEG precedent for treating successive temporal variability separately from signal magnitude.

`median(|Δx|)` is a project-defined descriptive statistic.

Relevant papers and notes linking each source to its Session 21 methodological role are maintained in the Session 21 Zotero collection.

---

# 8. Possible Phase 2 — Research Context Only

## 8.1 Phase 2A — Selected Event-Level and Temporal-Variability Follow-up

Phase 2A may be proposed when a Phase 1 observation warrants more detailed feature-level investigation.

Temporal-variability analysis is a priority candidate but does not restrict the allowable methodology.

A follow-up candidate must state:

1. the triggering Phase 1 observation;
2. the research question;
3. the proposed method or metric;
4. the methodological basis or relevant literature, where applicable;
5. the information expected beyond the existing Phase 1 results.

Possible analyses may include:

```text
selected command event
→ local raw/smoothed feature trajectory
→ successive-change behavior
→ threshold position or crossing
→ evidence behavior
→ command episode
```

Alternative methods may be proposed when supported by the observed result and an explicit methodological rationale.

## 8.2 Phase 2B — Selected Window/Step Command Extension

Selected Phase 1 decision rules may later be evaluated on the existing Session 14 window/step configurations:

```text
win-1s_step-1s
win-2s_step-0p5s
win-2s_step-1s
win-2s_step-2s
win-4s_step-1s
```

Any rule selected for extension must be linked to a specific Phase 1 observation and approved before execution.

A complete 90-configuration cross-product is not part of the current plan.

---

# 9. Research-Agent Reporting and Approval Boundary

The Phase 1 agent report must separate:

```text
Observation
Validation
Uncertainty
Follow-up Candidates
```

For each follow-up candidate, report:

```text
triggering observation
research question
proposed method
methodological basis
expected added information
```

Scientific interpretation and the decision to proceed with any follow-up analysis are reserved for human review.

The agent must stop after Phase 1 reporting.

Phase 2 requires a new human approval and frozen specification.

---

# 10. Frozen State

```text
Overall S21 roadmap      CONTEXT PROVIDED

Phase 1A
18-rule parameter grid   FROZEN / AUTHORIZED

Phase 1B
temporal variability     FROZEN / AUTHORIZED

Phase 2A
event-level / temporal
follow-up                 NOT AUTHORIZED

Phase 2B
window/step extension     NOT AUTHORIZED

90-configuration grid     NOT PLANNED

Specification version     v0.1
Specification status      FROZEN
```
