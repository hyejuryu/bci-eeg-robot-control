# Session 21 Phase 1 — Frozen Implementation Plan v0.1

* **Session:** 21
* **Scope:** Phase 1A and Phase 1B
* **Status:** FROZEN / APPROVED FOR IMPLEMENTATION
* **Upstream specification:** Session 21 Analysis Specification v0.1
* **Implementation stage:** Code not yet written

## 1. Purpose

This implementation plan translates the frozen Session 21 Analysis Specification v0.1 into a reproducible implementation built on the existing Session 14–16 analysis structure.

Phase 1 contains two analyses:

```text
Phase 1A
Complete 18-Rule Decision-Rule Parameter Grid

Phase 1B
Temporal Feature-Variability Analysis
```

The implementation reuses the existing feature artifacts and decision-rule semantics and adds the Session 21 parameter-grid orchestration, summary measures, temporal-variability metrics, validation, metadata, and figures.

---

# 2. Reuse Boundary

## 2.1 Session 14 Feature Artifact

Primary source:

```text
results/session-14/
eegbci_subject-001_runs-01-02_
posterior-alpha_window-features.csv
```

The following existing configurations are used:

```text
win-1s_step-1s
win-2s_step-0p5s
win-2s_step-1s
win-2s_step-2s
win-4s_step-1s
```

The implementation **MUST** use the saved Session 14 feature values.

Raw EEG features **MUST NOT** be regenerated for Session 21 Phase 1.

The existing Session 14 relative-IQR values provide reproduction references for Phase 1B.

## 2.2 Session 15 Decision-Rule Implementation

The implementation retains the existing Session 15 behavior for:

* threshold classification;
* `smooth-none`;
* causal `smooth-median3`;
* median-3 `UNAVAILABLE` warm-up;
* dwell-1, dwell-2, and dwell-3;
* recording-boundary state reset;
* LOW/HIGH evidence-to-command mapping;
* command-episode construction;
* short-active-episode definition; and
* existing per-rule/run summary semantics.

## 2.3 Shared Decision-Rule Module

Shared logic is provided by:

```text
src/bci_robot/decision_rule.py
```

Session 21 **MUST** reuse the existing threshold-classification and dwell state-machine semantics.

Session 21 **MUST NOT** change the methodological behavior of `src/bci_robot/decision_rule.py` as part of this implementation.

Session 21-specific configuration construction, orchestration, summary extension, validation, metadata, and output generation are implemented outside the shared decision-rule semantics.

If implementation cannot proceed without changing the shared methodological behavior, that change falls outside this frozen implementation plan.

---

# 3. Phase 1A — Complete 18-Rule Grid

## 3.1 Fixed Input

```text
Subject:
1

Runs:
1, 2

Conditions:
Run 1 — baseline eyes open
Run 2 — baseline eyes closed

Feature:
posterior_alpha_mean_psd

Configuration:
win-2s_step-1s
```

Expected selected input:

```text
59 updates per run
118 feature rows total
```

## 3.2 Thresholds

The existing Session 15 thresholds are retained:

```text
threshold_eo_q95
8.270509057516904e-11

threshold_gap_midpoint
1.3987182661955795e-10

threshold_ec_q05
2.365528862351009e-10
```

These threshold values **MUST** be used without recalibration.

## 3.3 Parameter Grid

The Phase 1A grid is:

```text
3 thresholds
×
2 smoothing modes
×
3 dwell values
=
18 rules
```

Smoothing:

```text
smooth-none
smooth-median3
```

Dwell:

```text
dwell-1
dwell-2
dwell-3
```

The eight Session 15 rule identifiers **MUST** retain their existing identities.

The remaining ten configurations use the same deterministic naming convention.

Reference configuration:

```text
threshold_gap_midpoint
smooth-none
dwell-2
```

---

# 4. Phase 1A Summary Definitions

## 4.1 Evidence Fractions

LOW and HIGH evidence fractions use only updates with available LOW/HIGH evidence as the denominator.

[
f_{\mathrm{LOW}}
================

\frac{N_{\mathrm{LOW}}}
{N_{\mathrm{LOW}}+N_{\mathrm{HIGH}}}
]

[
f_{\mathrm{HIGH}}
=================

\frac{N_{\mathrm{HIGH}}}
{N_{\mathrm{LOW}}+N_{\mathrm{HIGH}}}
]

`UNAVAILABLE` updates **MUST NOT** be included in the LOW/HIGH fraction denominator.

They are recorded separately as:

```text
unavailable_evidence_count
```

This separates median-3 warm-up availability from the distribution of actual threshold-classified evidence.

## 4.2 Evidence Transitions

Evidence transition count represents changes between available evidence states:

```text
LOW_ALPHA → HIGH_ALPHA
HIGH_ALPHA → LOW_ALPHA
```

Transitions involving `UNAVAILABLE` **MUST NOT** contribute to `evidence_transition_count`.

Excluded transitions therefore include:

```text
UNAVAILABLE → LOW_ALPHA
UNAVAILABLE → HIGH_ALPHA
LOW_ALPHA → UNAVAILABLE
HIGH_ALPHA → UNAVAILABLE
```

`UNAVAILABLE` remains a separate smoothing-availability state.

## 4.3 Command Occupancy

Primary command occupancy is defined using elapsed command-state duration.

For each run and rule, calculate:

```text
stop_duration_sec
open_duration_sec
close_duration_sec

stop_duration_fraction
open_duration_fraction
close_duration_fraction
```

For command state (s):

[
f_s
===

\frac{\text{duration in state }s}
{\text{recording duration}}
]

Duration is derived from the existing command-episode semantics.

The state durations **MUST** reconcile with complete recording-duration coverage.

Decision-update counts and count-based fractions **MAY** be retained as diagnostic or reconciliation fields, but they are not the primary occupancy measure.

## 4.4 Run and Condition Aggregation

The primary summary unit is:

```text
rule × run × condition
```

Run 1 and Run 2 **MUST NOT** be pooled or averaged across conditions without a separate approved analysis decision.

Descriptive summaries and figures therefore retain:

```text
Run 1 — baseline eyes open
Run 2 — baseline eyes closed
```

as distinct records.

---

# 5. Phase 1A Output Measures

Existing Session 15 measures are retained where applicable.

## 5.1 Evidence Measures

* `low_evidence_count`
* `high_evidence_count`
* `unavailable_evidence_count`
* `low_evidence_fraction`
* `high_evidence_fraction`
* `evidence_transition_count`
* `unconfirmed_candidate_update_count`

## 5.2 Command Measures

* first active command
* first active command time
* initial STOP duration
* active OPEN↔CLOSE switch count
* command episode count
* short active command episode count
* shortest active episode duration
* longest active episode duration
* STOP duration and duration fraction
* OPEN duration and duration fraction
* CLOSE duration and duration fraction

The existing short-active-episode definition is retained:

```text
duration <= 2.0 s
```

---

# 6. Phase 1A Descriptive Comparisons

The complete 18-rule grid is summarized by individual factors and the following pre-specified factor-combination patterns:

```text
threshold × dwell
smoothing × dwell
threshold × smoothing
```

Comparisons remain stratified by run and condition.

These analyses are descriptive.

Inferential interaction tests **MUST NOT** be introduced under this implementation plan.

---

# 7. Phase 1B — Temporal Feature-Variability Analysis

## 7.1 Analysis Units

Phase 1B uses the five Session 14 configurations across two runs:

```text
5 configurations × 2 runs
=
10 configuration/run records
```

## 7.2 Existing Distributional Metric

Retain the Session 14 relative-IQR definition:

[
\text{Relative IQR}
===================

\frac{Q_{75}-Q_{25}}
{\operatorname{median}(x)}
]

The saved Session 14 values are used as reproduction references.

## 7.3 Successive Differences

Within each configuration and run, feature rows are ordered chronologically and:

[
\Delta x_t=x_t-x_{t-1}
]

is calculated.

Expected difference count:

```text
n_differences = n_features - 1
```

## 7.4 Spectral-Feature Volatility

[
V_x=SD(\Delta x_t)
]

Implementation:

```text
ddof = 0
```

## 7.5 Median Absolute Successive Change

[
M_\Delta=
\operatorname{median}(|\Delta x_t|)
]

This is retained as the project-defined robust companion statistic.

## 7.6 Step-Size Comparison Restriction

The primary cross-window comparison uses:

```text
win-1s_step-1s
win-2s_step-1s
win-4s_step-1s
```

These configurations share a 1 s step.

Successive-change metrics are also calculated and stored for:

```text
win-2s_step-0p5s
win-2s_step-2s
```

Raw `SD(Δx)` or `median(|Δx|)` values across different step sizes **MUST NOT** be directly ranked as if they represented equivalent temporal increments.

The restriction reflects both:

1. different elapsed intervals represented by successive differences; and
2. different outer-window overlap structures.

The comparison restriction is recorded in Session 21 metadata.

---

# 8. Session 21 Outputs

## 8.1 Research Tables

The implementation **MUST** produce:

```text
results/session-21/
session21_rule-grid_decision-stream.csv
session21_rule-grid_command-episodes.csv
session21_rule-grid_summary.csv
session21_feature-temporal-variability-summary.csv
```

## 8.2 Metadata

The implementation **MUST** produce:

```text
results/session-21/
session21_analysis_metadata.json
```

The metadata records:

* source artifact paths;
* subject, run, and condition identifiers;
* fixed feature configuration;
* threshold identifiers and values;
* all 18 rule identifiers and factor tuples;
* evidence-fraction definition;
* evidence-transition definition;
* occupancy definition;
* run-aggregation policy;
* temporal metric definitions;
* cross-step comparison restriction;
* validation outcomes;
* software versions;
* output inventory; and
* Git provenance.

### Git Provenance

Planner-run Git HEAD values and scientific implementation/execution provenance are distinct concepts.

Planner revisions **MAY** be retained as planning provenance, for example:

```text
planner_source_git_revisions
```

The scientific metadata **MUST** record the Git revision containing the implementation used for the analysis and the Git revision at actual execution, for example:

```text
implementation_git_revision
execution_git_revision
```

If the same committed revision is used for both, the two values may be identical.

Planner-run Git HEAD values **MUST NOT** be substituted for the actual implementation or execution revision.

---

# 9. Figures

The frozen output filenames are:

```text
figures/session-21/
session21_rule-grid_command-behavior.png
session21_feature-temporal-variability.png
```

Figures are generated from saved and validated Session 21 tables rather than by independently recomputing the primary analysis.

## 9.1 Command-Behavior Figure

The figure should:

* distinguish Run 1 and Run 2;
* represent the 18-rule factor structure;
* identify the frozen reference rule; and
* present selected command-behavior measures from the validated summary.

## 9.2 Temporal-Variability Figure

The figure should:

* emphasize the common-1-s-step window-length comparison;
* visually separate the 0.5 s and 2 s step descriptive records; and
* avoid implying a direct cross-step volatility ranking.

---

# 10. Validation Plan

Existing Session 14 and Session 15 validation provides the upstream reference. Session 21 adds reproduction, extension, reconciliation, and saved-output checks.

## 10.1 Source and Selection Checks

For Phase 1A, expected selected input is:

```text
win-2s_step-1s
59 rows per run
118 rows total
```

Expected Session 14 feature counts for Phase 1B are:

```text
win-1s_step-1s      60 per run
win-2s_step-1s      59 per run
win-4s_step-1s      57 per run
win-2s_step-0p5s   117 per run
win-2s_step-2s      30 per run
```

Input identity, configuration membership, chronology, and required finite values are checked before downstream calculations.

## 10.2 Eight-Rule Reproduction

The eight historical Session 15 rules are regenerated and compared against the saved Session 15 outputs.

Comparison fields include:

* rule identifiers;
* raw feature values;
* smoothing availability;
* smoothed feature values;
* threshold identifiers and values;
* evidence states;
* candidate state and count;
* active evidence;
* confirmation flags;
* command states;
* episode boundaries and durations; and
* compatible existing summary fields.

Comparison policy:

```text
identifiers and discrete states:
exact agreement

floating-point values:
RTOL = 1e-12
ATOL = 1e-15
```

The eight historical rules **MUST** be reproduced before the ten new rules are accepted as validated Session 21 extensions.

## 10.3 Full-Grid Structural Validation

Expected Phase 1A structure:

```text
18 unique rules
10 new rules
2 runs per rule
36 rule/run summaries
59 decision updates per rule/run
2,124 decision-stream rows
```

Validation also checks:

* unique parameter tuples;
* threshold identifier/value consistency;
* chronological decision ordering;
* recording-boundary state reset; and
* finite required numeric fields.

## 10.4 Stream / Episode / Summary Reconciliation

Saved outputs are reconciled across representations.

Checks include:

* evidence counts and fractions;
* evidence transitions;
* command-state measures;
* duration-based occupancy;
* first active command and initialization timing;
* active switches;
* command episode counts;
* short active episodes;
* minimum and maximum active-episode duration; and
* complete episode-duration coverage of each recording.

## 10.5 Phase 1B Metric Validation

For every configuration/run pair, validation checks:

* chronological ordering;
* finite source features;
* expected feature count;
* exactly `n_features - 1` successive differences;
* `SD(Δx)` using `ddof=0`;
* `median(|Δx|)`; and
* reproduction of the existing Session 14 relative-IQR value.

## 10.6 Save / Reload Validation

The four CSV outputs and metadata JSON are saved and reloaded.

Reload validation checks:

* schema;
* expected row count;
* identifier uniqueness;
* required finite values; and
* metadata readability.

Figures are generated from the reloaded validated research tables.

## 10.7 Validation-Failure Reporting Boundary

Validation handling follows the frozen analysis specification.

A validation mismatch **MUST** be reported before the corresponding scientific result is reported.

This implementation plan does not introduce an additional global requirement that every Phase 1A and Phase 1B validation must pass before any otherwise valid result can be reported.

A mismatch is evaluated according to the outputs or calculations it affects, while the existing frozen scope and interpretation boundary remain unchanged.

---

# 11. Implementation Structure

A Session 21-specific analysis entry point will coordinate the two Phase 1 analyses while reusing the existing Session 14 artifacts and Session 15/16 rule semantics.

The Phase 1A implementation will add deterministic complete-grid construction and extended rule/run summaries around the existing decision-rule processing path.

The Phase 1B implementation will add successive-difference calculations to the existing configuration/run feature summary structure.

Validation logic will compare historical rule subsets against Session 15 references, check the new grid structure, reconcile derived outputs, and verify saved artifacts after reload.

Plotting will consume validated Session 21 outputs rather than acting as a second implementation of the analysis.

---

# 12. Implementation and Execution Sequence

Implementation proceeds in the following order:

1. Create the Session 21 analysis entry point and define Session 21 output paths.
2. Add deterministic construction of the complete 18-rule Phase 1A grid.
3. Extend per-rule/run summaries with the approved evidence fractions, evidence transitions, and duration-based occupancy.
4. Implement the Phase 1B successive-change summary.
5. Add reproduction, structural, reconciliation, and save/reload validation.
6. Run the eight-rule Session 15 reproduction comparison.
7. Generate the complete 18-rule Phase 1A outputs.
8. Validate and save/reload the Phase 1A decision stream, command episodes, and rule summary.
9. Run Phase 1B using the five existing Session 14 feature configurations.
10. Validate and save/reload the ten configuration/run temporal-variability records.
11. Write Session 21 metadata with actual implementation and execution Git provenance.
12. Generate both figures from reloaded validated Session 21 tables.
13. Record final validation status for each output and analysis component.

---

# 13. Scope Boundary

This frozen implementation plan authorizes only:

```text
Phase 1A
18-rule decision-rule parameter grid

Phase 1B
temporal feature-variability analysis

+
validation
metadata
required figures
```

The implementation **MUST NOT** add:

* event-level feature/command linkage analysis;
* Phase 2A follow-up analysis;
* Phase 2B window/step command extension;
* a 90-configuration cross-product;
* new threshold calibration;
* new preprocessing or feature definitions;
* new inferential statistical tests; or
* unapproved pooling of Run 1 and Run 2.

Any such change requires a separate analysis or implementation decision before execution.