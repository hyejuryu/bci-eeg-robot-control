# Session 21 Phase 1 Checkpoint

- **Session:** 21
- **Scope:** Phase 1A — Decision-Rule Parameter Grid; Phase 1B — Temporal Feature Variability
- **Status:** Phase 1 completed; Phase 2A follow-up pending
- **Subject:** 1
- **Recordings:**
  - Run 1 — baseline eyes open
  - Run 2 — baseline eyes closed
- **Feature:** `posterior_alpha_mean_psd`

## 1. Purpose

This checkpoint records the main observations from Session 21 Phase 1 and the empirical basis for the Phase 2A follow-up.

Phase 1A evaluated command behavior across the complete 18-rule threshold–smoothing–dwell grid using the fixed `win-2s_step-1s` feature stream. Phase 1B evaluated distributional and successive-change variability across the Session 14 window/step configurations.

Run 1 and Run 2 are retained as separate recording-level observations.

## 2. Phase 1A — Decision-Rule Behavior

Command switching was concentrated in threshold families positioned near the feature distributions of the corresponding recordings.

For Run 1, the EO-Q95 family produced the largest number of active OPEN↔CLOSE switches. With no smoothing, increasing dwell from 1 to 3 updates reduced the active-switch count from 4 to 2 to 0.

For Run 2, the corresponding pattern occurred in the EC-Q05 family. With no smoothing, the active-switch count likewise decreased from 4 to 2 to 0 across dwell values 1, 2, and 3.

The dwell parameter therefore changed whether short evidence episodes propagated to confirmed command changes while the feature stream and threshold remained fixed. Increasing dwell also increased the initial command-confirmation interval.

Median-3 smoothing reduced some short feature excursions and evidence transitions, but its effect on command switching depended on threshold position and the duration of the remaining evidence episodes. It did not produce a uniform reduction in switching across the grid.

The frozen reference rule, `thr-gap-mid__smooth-none__dwell-2`, produced no active OPEN↔CLOSE switches in either recording and remained a stable reference within the evaluated grid.

## 3. Phase 1B — Temporal Feature Variability

Phase 1B used three complementary summaries:

- **Relative IQR:** `(Q75 - Q25) / median(x)`, describing distributional spread relative to feature magnitude without using temporal order.
- **Spectral-feature volatility:** `SD(Δx)`, where `Δx_t = x_t - x_(t-1)`, describing dispersion of successive feature changes. This measure was adapted from the spectral-power volatility approach of Yu et al. (2024).
- **Median absolute successive change:** `median(|Δx|)`, used here as a project-defined robust summary of typical successive-change magnitude.

The primary window-length comparison used 1 s, 2 s, and 4 s windows with step fixed at 1 s.

For Run 2, both `SD(Δx)` and `median(|Δx|)` decreased as window length increased from 1 s to 2 s to 4 s.

For Run 1, `median(|Δx|)` also decreased across the three window lengths. In contrast, `SD(Δx)` increased from approximately `3.03e-11 V²/Hz` at the 1 s window to `3.93e-11 V²/Hz` at the 2 s window, then decreased to `1.71e-11 V²/Hz` at the 4 s window.

The divergence between the two successive-change summaries indicates that typical successive-change magnitude and dispersion of successive changes captured different aspects of the same feature stream.

Diagnostic inspection identified a large local feature deviation in the Run 1 2 s-window stream around the 24–26 s window, represented at decision time 26 s, accompanied by large successive changes. This is the same local feature event previously decomposed in Session 14.

This observation motivates the hypothesis that a small number of large local successive changes contributed disproportionately to the elevated recording-level `SD(Δx)` in the Run 1 2 s condition. Their contribution was not quantified in Phase 1.

## 4. Magnitude Dependence

For the fixed `win-2s_step-1s` configuration, the median posterior-alpha feature was approximately `3.996e-11 V²/Hz` in Run 1 and `5.038e-10 V²/Hz` in Run 2. The Run 2 median was therefore approximately 12.61 times the Run 1 median.

The original-scale successive-change measures also differed substantially between the two recordings. At the same 2 s / 1 s configuration:

- `SD(Δx)` was approximately `3.93e-11 V²/Hz` in Run 1 and `2.63e-10 V²/Hz` in Run 2, a ratio of approximately 6.7.
- `median(|Δx|)` was approximately `8.66e-12 V²/Hz` in Run 1 and `1.87e-10 V²/Hz` in Run 2, a ratio of approximately 21.6.

Because both successive-change measures retain the original PSD scale, these between-recording differences cannot distinguish relative temporal variability from overall feature magnitude.

This motivates evaluation of a magnitude-normalized successive-variability measure in Phase 2A. An nMSSD-based approach, following the magnitude-normalization rationale used by Li et al. (2018), will be reviewed for its suitability to the posterior-alpha PSD feature stream before adoption.

## 5. Phase 2A Follow-up Questions

### 5.1 Contribution of large local successive changes

The Run 1 2 s-window condition showed lower `median(|Δx|)` than the 1 s condition but higher `SD(Δx)`.

The time-series diagnostic identified large local successive changes around the 24–26 s feature event. This supports a testable hypothesis that a small number of large changes contributed disproportionately to the recording-level successive-difference variance while the typical successive-change magnitude remained lower.

Phase 2A will quantify the contribution of the selected local successive changes to the total successive-difference variance for this recording.

### 5.2 Magnitude-normalized temporal variability

Run 1 and Run 2 differed substantially in both posterior-alpha feature magnitude and original-scale successive-change metrics.

Phase 2A will therefore review a magnitude-normalized successive-variability measure, with nMSSD as the primary literature-based candidate, before making a relative between-recording variability comparison.

### 5.3 Feature-to-command propagation

Phase 1A showed that threshold position, smoothing, and dwell changed whether local feature behavior propagated to a confirmed command change.

Threshold-relative position will be represented continuously as:

`m_t = (y_t - T) / T`

where `y_t` is the feature value supplied to the threshold classifier and `T` is the applied threshold.

Thus:

- `m_t = 0` indicates the threshold,
- `m_t > 0` indicates a feature value above the threshold,
- `m_t < 0` indicates a feature value below the threshold.

No categorical threshold-proximity cutoff is defined.

For selected feature events and rule conditions, Phase 2A will link the threshold-relative trajectory `m_t` with evidence duration, dwell confirmation, and the resulting command state.

## 6. Next Step

Phase 2A will address three follow-up analyses:

1. review magnitude-normalized successive variability, with nMSSD as the primary literature-based candidate;
2. quantify the contribution of the selected Run 1 local successive changes to recording-level successive-difference variance;
3. examine selected feature-to-command events using continuous threshold-relative margin `m_t`, evidence duration, dwell confirmation, and command outcome.

The concrete calculation and event-selection rules will be recorded before execution.

Cross-subject extension will be considered after the single-subject follow-up analysis structure has been completed.

## Related Project Artifacts

- `results/session-21/session21_rule-grid_summary.csv`
- `results/session-21/session21_feature-temporal-variability-summary.csv`
- `results/session-21/session21_analysis_metadata.json`
- `figures/session-21/session21_rule-grid-command-behavior.png`
- `figures/session-21/session21_feature-temporal-variability.png`
- `figures/session-21/diagnostics/`
- `scripts/14_s21_phase1_analysis.py`
- `scripts/15_s21_diagnostic_figures.py`
- `weekly-notes/session-14-260717.md`

## References

Yu, Y., Oh, Y., Kounios, J., & Beeman, M. (2024).
Electroencephalography Spectral-power Volatility Predicts Problem-solving Outcomes.
*Journal of Cognitive Neuroscience, 36*(5), 901–915.
https://doi.org/10.1162/jocn_a_02136

Li, L., Huang, G., Lin, Q., Liu, J., Zhang, S., & Zhang, Z. (2018).
Magnitude and Temporal Variability of Inter-stimulus EEG Modulate the Linear Relationship Between Laser-Evoked Potentials and Fast-Pain Perception.
*Frontiers in Neuroscience, 12*, 340.
https://doi.org/10.3389/fnins.2018.00340
