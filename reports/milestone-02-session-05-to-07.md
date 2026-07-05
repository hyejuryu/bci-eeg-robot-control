# Milestone 02 Report: Session 05–07

## 1. Overview

This report summarizes the second milestone of the EEG-BCI robot control project.

Sessions 05–07 focused on moving from conceptual understanding to actual EEG signal analysis.

In Milestone 01, the main goal was to understand EEG as an indirect, noisy, population-level signal and to avoid overinterpreting EEG features as direct measurements of mental states.

In Milestone 02, the goal was to build the first working analysis pipeline:

```text
raw or synthetic signal
→ data structure inspection
→ frequency-domain analysis
→ band power extraction
→ condition comparison
→ figure and result export
```

At this stage, the project still did not aim to control a robot directly.

Instead, the goal was to confirm that EEG-like signals and public EEG data could be loaded, inspected, transformed into frequency-domain features, and interpreted within a limited experimental context.

## 2. Period Covered

| Item | Description |
|---|---|
| Milestone | Milestone 02 |
| Sessions covered | Session 05–07 |
| Period | 2026.05.09 – 2026.05.24 |
| Current phase | Python environment setup and public EEG dataset analysis |
| Next phase | OpenBCI Cyton setup, data acquisition preparation, and hardware validation |

## 3. Sessions Covered

| Session | Date | Main Focus | Main Output |
|---|---|---|---|
| Session 05 | 2026.05.09–10 | Python analysis environment setup, synthetic EEG-like signal, Welch PSD, alpha/beta band power smoke test | Reproducible environment files, synthetic signal PSD script, figures, PSD summary |
| Session 06 | 2026.05.16–17 | EEGBCI public dataset loading, raw EEG structure inspection, time-domain waveform visualization | Raw EEG metadata summaries and first waveform figures |
| Session 07 | 2026.05.23–24 | Band-pass filtering, posterior channel selection, Welch PSD, alpha/beta band power, eyes-open vs eyes-closed comparison | PSD figures, band power CSV files, alpha reactivity result |

## 4. Project Direction After Milestone 02

The project has now moved from conceptual framing to the first executable EEG analysis workflow.

The current analysis pipeline is:

```text
environment setup
→ synthetic signal test
→ public EEG loading
→ raw EEG inspection
→ band-pass filtering
→ Welch PSD
→ alpha/beta band power
→ condition comparison
→ figure and CSV export
```

This milestone confirms that the project can now handle EEG data as structured numerical data rather than only as a theoretical concept.

The key transition is:

```text
EEG as a concept
→ EEG as time-series data
→ EEG as frequency-domain features
→ EEG as condition-dependent measurements
```

The next phase should not jump directly into robot control.

Before real-time control, the project should first verify whether the same basic alpha reactivity workflow can be reproduced with OpenBCI Cyton recordings.

## 5. Key Technical Outcomes

### 5.1 A reproducible Python analysis environment was established

Session 05 focused on setting up a Python-based EEG analysis environment.

The following tools and files were organized:

- Conda environment
- `environment.yml`
- `requirements.txt`
- environment check script
- MNE
- NumPy
- SciPy
- Pandas
- Matplotlib
- JupyterLab

This was not just a setup step.

For EEG analysis, the software environment is part of the research record. Package versions, environment structure, and script execution behavior can affect reproducibility.

The project now has a basic structure for recording both the analysis code and the execution environment.

### 5.2 Synthetic signal analysis worked as a pipeline smoke test

Before using real EEG data, a synthetic EEG-like signal was created.

The signal contained:

```text
10 Hz alpha-like component
20 Hz beta-like component
random noise
```

This signal was not interpreted as real EEG.

Its purpose was to test whether the code could detect known frequency components and calculate band power correctly.

The synthetic signal analysis confirmed the following workflow:

```text
time-series signal
→ Welch PSD
→ alpha/beta band definition
→ band power calculation
→ figure export
```

This was important because it allowed the signal-processing pipeline to be checked before applying it to real EEG data.

### 5.3 EEGBCI raw data was loaded and inspected

Session 06 moved from synthetic signals to real public EEG data.

Using MNE-Python, EEGBCI baseline eyes-open and eyes-closed runs were loaded for Subject 1.

The raw EEG structure was inspected through:

- sampling frequency
- number of channels
- number of samples
- recording duration
- channel names
- annotations
- data shape
- time-domain waveform visualization

One key understanding from this session was that EEG is not stored as a continuous “brain wave picture.”

Inside Python, EEG is represented as numerical time-series data:

```text
channels × samples
```

For the EEGBCI data used in this milestone, the sampling frequency was 160 Hz.

This means:

```text
1 second = 160 samples
```

Therefore, plotting a 10-second waveform means selecting and visualizing about 1600 sample points.

### 5.4 Raw EEG waveform visualization is useful but insufficient

The first raw EEG waveform figures showed that EEG is noisy, irregular, and channel-dependent.

However, raw waveform visualization alone was not enough to interpret alpha or beta activity.

The project confirmed the following distinction:

```text
raw waveform visualization
≠
frequency-domain rhythm analysis
```

From raw waveform alone, it is not appropriate to claim:

```text
alpha increased
beta decreased
```

To discuss alpha or beta power, the signal must first be transformed into the frequency domain.

This finding directly connected Session 06 to Session 07.

### 5.5 The first public EEG frequency-domain pipeline was completed

Session 07 applied the first complete frequency-domain EEG analysis workflow to public EEG data.

The pipeline was:

```text
raw EEG
→ 1–40 Hz band-pass filtering
→ posterior channel selection
→ Welch PSD
→ posterior mean PSD
→ alpha/beta band power
→ eyes-open vs eyes-closed comparison
```

The analysis used Subject 1 from the EEGBCI dataset.

| Item | Value |
|---|---|
| Subject | 1 |
| Run 1 | baseline eyes open |
| Run 2 | baseline eyes closed |
| Sampling frequency | 160 Hz |
| Selected posterior channels | 6 |
| Filtering range | 1–40 Hz |
| PSD method | Welch |
| Alpha band | 8 Hz ≤ f < 13 Hz |
| Beta band | 13 Hz ≤ f ≤ 30 Hz |

The PSD result had the following structure:

```text
6 posterior channels × 500 frequency points
```

This made it clear that PSD should be understood not only as a graph, but also as a structured array with channel and frequency axes.

### 5.6 Posterior alpha reactivity was observed in the public dataset

The main result of Session 07 was that posterior alpha power was much higher in the eyes-closed condition than in the eyes-open condition.

The summary result was:

```text
eyes closed → clear posterior alpha peak around 10 Hz
eyes open   → much lower posterior alpha power
```

The calculated band power values were:

| Condition | Alpha power | Beta power | Beta/Alpha ratio |
|---|---:|---:|---:|
| baseline_eyes_open | 4.1429e-11 | 1.2779e-11 | 0.3084 |
| baseline_eyes_closed | 4.7801e-10 | 3.0087e-11 | 0.0629 |

The condition comparison was:

| Comparison | Value |
|---|---:|
| Alpha power, eyes closed / eyes open | 11.54 |
| Beta power, eyes closed / eyes open | 2.35 |
| Beta/alpha ratio, eyes closed / eyes open | 0.204 |
| Beta/alpha ratio, eyes open / eyes closed | 4.90 |

The most important result is that eyes-closed alpha power was approximately 11.5 times higher than eyes-open alpha power in this Subject 1 analysis.

This supports using eyes-open / eyes-closed alpha reactivity as a reference workflow before OpenBCI data collection.

### 5.7 Interpretation boundaries were clarified

The Session 07 result should not be interpreted as direct mental-state reading.

The result does not mean:

```text
eyes closed = relaxation
eyes open = focus
```

A more careful interpretation is:

```text
defined eyes-open / eyes-closed baseline conditions
→ different posterior alpha-band power
```

This distinction is important because the project should continue to avoid overinterpreting EEG features.

The current result shows that a measurable spectral feature changed between defined experimental conditions.

It does not prove psychological states directly.

### 5.8 Beta/alpha ratio should be treated as a secondary feature

The beta/alpha ratio was lower in the eyes-closed condition.

However, this happened because alpha power increased much more strongly than beta power.

The ratio result should therefore be interpreted carefully.

The project should not use beta/alpha ratio alone to infer concentration, relaxation, or attention.

Instead, beta/alpha ratio should be treated as a secondary feature that must be interpreted together with the original alpha and beta power values.

## 6. Decisions Made After Milestone 02

After reviewing Sessions 05–07, the following decisions were made.

### 6.1 OpenBCI should begin with alpha reactivity validation

Before attempting focus-based control, the first OpenBCI experiment should check whether eyes-open / eyes-closed alpha reactivity can be observed.

Initial OpenBCI validation should follow this structure:

```text
eyes open
vs.
eyes closed
→ posterior alpha power comparison
```

This will help determine whether the hardware setup, electrode placement, recording environment, and preprocessing pipeline are sufficient for basic EEG analysis.

### 6.2 Raw waveform inspection should remain part of the workflow

Raw waveform visualization should not be used for direct alpha/beta interpretation.

However, it should remain an important early step for checking:

- obvious noise
- large artifacts
- channel differences
- amplitude scale
- recording duration
- signal continuity
- possible electrode or contact problems

The project should continue to inspect raw data before applying PSD or band power analysis.

### 6.3 Frequency-domain analysis is now the core analysis path

For the next phase, the current analysis priority should be:

```text
raw EEG inspection
→ filtering
→ PSD
→ band power
→ condition comparison
```

This pipeline should be cleaned into reusable functions before real OpenBCI data collection.

Potential functions include:

- data loading function
- preprocessing function
- PSD computation function
- band power extraction function
- figure saving function

### 6.4 Threshold rules should still be postponed

Although the project now has alpha/beta power values, threshold-based robot control should still be postponed.

The current results are based on condition-level comparison, not real-time decision-making.

Before threshold design, the project needs to inspect:

- window-based feature values
- within-condition variability
- overlap between conditions
- stability across time
- false trigger risk
- latency caused by window length

A threshold should be designed from feature distributions, not from a single average value.

## 7. Outputs Produced

### Environment and setup files

- [`environment.yml`](../environment.yml)
- [`requirements.txt`](../requirements.txt)
- [`scripts/00_check_environment.py`](../scripts/00_check_environment.py)

### Scripts

- [`scripts/01_synthetic_signal_psd.py`](../scripts/01_synthetic_signal_psd.py)
- [`scripts/02_download_eegbci_test.py`](../scripts/02_download_eegbci_test.py)
- [`scripts/03_load_eegbci_inspect_raw.py`](../scripts/03_load_eegbci_inspect_raw.py)
- [`scripts/04_filter_psd_bandpower.py`](../scripts/04_filter_psd_bandpower.py)

### Results

- [`docs/weekly-notes-outputs/session-05-environment-check.txt`](../docs/weekly-notes-outputs/session-05-environment-check.txt)
- [`results/session-05/synthetic_signal_psd_summary.txt`](../results/session-05/synthetic_signal_psd_summary.txt)
- [`results/session-06/subject-001_run-01_baseline_eyes_open_raw_summary.json`](../results/session-06/subject-001_run-01_baseline_eyes_open_raw_summary.json)
- [`results/session-06/subject-001_run-02_baseline_eyes_closed_raw_summary.json`](../results/session-06/subject-001_run-02_baseline_eyes_closed_raw_summary.json)
- [`results/session-07/subject-001_alpha_beta_bandpower_summary.csv`](../results/session-07/subject-001_alpha_beta_bandpower_summary.csv)
- [`results/session-07/subject-001_bandpower_condition_comparison.csv`](../results/session-07/subject-001_bandpower_condition_comparison.csv)

### Figures

- [`figures/session-05/synthetic_signal_time_series.png`](../figures/session-05/synthetic_signal_time_series.png)
- [`figures/session-05/synthetic_signal_psd.png`](../figures/session-05/synthetic_signal_psd.png)
- [`figures/session-06/subject-001_run-01_baseline_eyes_open_first_10s.png`](../figures/session-06/subject-001_run-01_baseline_eyes_open_first_10s.png)
- [`figures/session-06/subject-001_run-02_baseline_eyes_closed_first_10s.png`](../figures/session-06/subject-001_run-02_baseline_eyes_closed_first_10s.png)
- [`figures/session-07/subject-001_run-01_baseline_eyes_open_posterior_mean_psd.png`](../figures/session-07/subject-001_run-01_baseline_eyes_open_posterior_mean_psd.png)
- [`figures/session-07/subject-001_run-02_baseline_eyes_closed_posterior_mean_psd.png`](../figures/session-07/subject-001_run-02_baseline_eyes_closed_posterior_mean_psd.png)
- [`figures/session-07/subject-001_eyes_open_vs_eyes_closed_posterior_mean_psd.png`](../figures/session-07/subject-001_eyes_open_vs_eyes_closed_posterior_mean_psd.png)
- [`figures/session-07/subject-001_alpha_beta_power_comparison.png`](../figures/session-07/subject-001_alpha_beta_power_comparison.png)

### Blog Output

- [English Medium Post 03: From Raw EEG to Alpha Power: Building My First EEG Analysis Pipeline](https://medium.com/@hyejuryuwork/from-raw-eeg-to-alpha-power-building-my-first-eeg-analysis-pipeline-866956438923)
- [`docs/blog/en/003-from-raw-eeg-to-alpha-power.md`](../docs/blog/en/003-from-raw-eeg-to-alpha-power.md)
- [`docs/blog/ko/003-raw-eeg에서-alpha-power까지.md`](../docs/blog/ko/003-raw-eeg에서-alpha-power까지.md)

## 8. Open Questions

The following questions remain open after Milestone 02.

### 8.1 PSD and parameter choice

- How do `n_fft`, `n_per_seg`, and `n_overlap` affect PSD shape, frequency spacing, and band power values?
- How different are Welch PSD results when the window length changes?
- Should PSD values be visualized in linear scale, log scale, or dB scale for later comparison?

### 8.2 Channel selection

- How sensitive is posterior alpha reactivity to channel selection?
- Would O1, Oz, and O2 alone show the same alpha peak?
- How different are the results when PO3, POz, and PO4 are included?

### 8.3 Band power calculation

- What is the practical difference between mean PSD within a band and integrated band power?
- Should future analyses use absolute power, relative power, or baseline-normalized power?
- How should beta/alpha ratio be interpreted when both alpha and beta power change?

### 8.4 OpenBCI transfer

- Can the same posterior alpha reactivity be observed using OpenBCI Cyton 8-channel recordings?
- How will electrode placement, impedance, motion artifact, and environmental noise affect alpha power estimation?
- What raw data format and sampling structure will OpenBCI / BrainFlow produce?

### 8.5 Future control design

- How should feature values be computed over sliding time windows?
- How much overlap should be used between windows?
- How should feature distributions be inspected before threshold design?
- How can false triggers be estimated before connecting the system to a robot?

## 9. Risks Identified

| Risk | Description | Current response |
|---|---|---|
| Environment inconsistency | Python package versions or Conda setup may differ across systems | Record `environment.yml`, `requirements.txt`, and environment check output |
| Synthetic signal overinterpretation | Treating synthetic signal results as real EEG findings | Use synthetic data only as a pipeline smoke test |
| Raw waveform overinterpretation | Inferring alpha or beta activity directly from time-domain waveform | Use PSD and band power for frequency-domain interpretation |
| PSD parameter sensitivity | Welch parameters may affect PSD shape and band power results | Review `n_fft`, `n_per_seg`, `n_overlap`, and frequency spacing |
| Channel selection bias | Posterior alpha result may depend on selected channels | Compare O-only channels with broader posterior channel sets |
| Ratio misinterpretation | Beta/alpha ratio may hide whether beta or alpha caused the change | Always inspect alpha and beta raw values with the ratio |
| Hardware transfer risk | Public EEG results may not transfer cleanly to OpenBCI data | Use eyes-open / eyes-closed alpha reactivity as the first hardware sanity check |
| Premature threshold control | Single condition-level values are not enough for real-time control | Inspect window-based feature distributions before setting thresholds |

## 10. Next Actions

The next block should focus on preparing for OpenBCI-based EEG acquisition while cleaning the current offline analysis workflow.

### Session 08–12 Direction

1. Refactor the current EEG analysis scripts:
   - data loading
   - preprocessing
   - PSD computation
   - band power extraction
   - figure saving

2. Finalize the alpha reactivity workflow as a reference pipeline:

```text
eyes open
vs.
eyes closed
→ posterior alpha power difference
```

3. Review Welch PSD parameters:
   - `n_fft`
   - `n_per_seg`
   - `n_overlap`
   - frequency spacing

4. Review band power calculation:
   - mean PSD
   - sum
   - integration
   - relative power
   - baseline-normalized power

5. Study OpenBCI Cyton board setup:
   - channel layout
   - electrode placement
   - reference and ground
   - impedance
   - safety
   - data format

6. Install and test OpenBCI GUI.

7. Study BrainFlow data structure and Python acquisition workflow.

8. Prepare a first OpenBCI recording protocol:

```text
eyes open baseline
eyes closed baseline
short repeated trials
raw data save
metadata save
PSD and alpha power analysis
```

9. Keep robot control postponed until the EEG acquisition and feature extraction pipeline is stable.

## 11. Milestone Reflection

Milestone 02 established the first executable EEG analysis workflow in the project.

The project moved from conceptual EEG understanding to a working analysis path:

```text
synthetic signal
→ public EEG raw data
→ time-domain inspection
→ frequency-domain PSD
→ alpha/beta band power
→ eyes-open vs eyes-closed comparison
```

The main result was a working path from raw EEG to condition-level feature comparison:

```text
raw EEG
→ structured data
→ frequency-domain feature
→ condition comparison
```

This workflow is necessary before OpenBCI data collection and robot control.

The next phase should continue to avoid direct mental-state claims unless they are tied to defined conditions and measurable EEG feature changes.

## 12. Related Links

- [Session 05](../weekly-notes/session-05-260509.md)
- [Session 06](../weekly-notes/session-06-260516.md)
- [Session 07](../weekly-notes/session-07-260523.md)

## 13. References

- [MNE-Python documentation](https://mne.tools/stable/index.html)
- [MNE EEGBCI dataset documentation](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html)
- [MNE documentation: `mne.io.read_raw_edf`](https://mne.tools/stable/generated/mne.io.read_raw_edf.html)
- [MNE documentation: `Raw.compute_psd`](https://mne.tools/stable/generated/mne.io.Raw.html#mne.io.Raw.compute_psd)
- [SciPy documentation: `scipy.signal.welch`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html)
- [PhysioNet EEG Motor Movement/Imagery Dataset](https://physionet.org/content/eegmmidb/1.0.0/)
- [NumPy documentation](https://numpy.org/doc/stable/)
- [Matplotlib documentation](https://matplotlib.org/stable/)
