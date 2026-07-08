# Milestone 03 Report: Session 09–12

## 1. Overview

This report summarizes the third milestone of the EEG-BCI robot control project.

Sessions 09–12 focused on moving from offline public EEG analysis toward OpenBCI-based self-recorded acquisition. In Milestone 02, the project established a working public EEG analysis workflow using public EEG data, filtering, PSD, band-power extraction, and eyes-open / eyes-closed comparison. Milestone 03 tested whether that workflow could begin transferring to OpenBCI Cyton self-recording.

The main outcome of this milestone is that the OpenBCI connection path and BrainFlow acquisition infrastructure were partly confirmed, but stable self-recorded acquisition was not established. The unresolved bottleneck is now treated as acquisition / contact / reference stability risk.

The project should continue through a hybrid route:

```text
OpenBCI self-recording
= troubleshooting / optional validation track

public EEG replay-control
= main analysis / control track

Arduino
= independent control-output track
```

The replay-control track will use public EEG-derived feature streams for command generation. Self-recorded OpenBCI data can be added later if acquisition stability is recovered.

## 2. Period Covered

| Item | Description |
|---|---|
| Milestone | Milestone 03 |
| Sessions covered | Session 09–12 |
| Period | 2026.06.20 – 2026.07.08 |
| Current phase | OpenBCI acquisition setup, BrainFlow acquisition infrastructure, and acquisition troubleshooting |
| Next phase | Public EEG replay-control pipeline and Arduino minimum-demo sprint |

## 3. Sessions Covered

| Session | Date | Main Focus | Main Output |
|---|---|---|---|
| Session 09 | 2026.06.20 | OpenBCI Cyton structure, electrode mapping, reference / BIAS role, safety checklist, initial posterior montage preparation | Setup documents and recording readiness criteria |
| Session 10 | 2026.06.21–06.23 | OpenBCI GUI installation, Cyton connection, initial posterior dry-comb troubleshooting, forehead flat-electrode diagnostics | GUI / Cyton / COM3 live-stream path confirmed; forehead flat-electrode baseline confirmed; posterior dry-comb unresolved |
| Session 11 | 2026.07.04–07.05 | BrainFlow acquisition pipeline, synthetic board test, actual Cyton acquisition, raw save, metadata, readback verification | BrainFlow synthetic and actual Cyton acquisition infrastructure verified using known-good forehead montage |
| Session 12 | 2026.07.06–07.08 | Posterior contact-assisted acquisition, forehead baseline recovery, SRB / BIAS checks, controlled acquisition-stability check | Stable acquisition baseline not recovered; OpenBCI inquiry and route revision needed |

## 4. Project Direction After Milestone 03

The project has moved from public EEG analysis into OpenBCI-based acquisition setup.

The following connection path was confirmed:

```text
OpenBCI Cyton
→ USB dongle
→ COM3
→ OpenBCI GUI live stream
```

The BrainFlow acquisition infrastructure was also confirmed under a simplified forehead montage:

```text
Cyton
→ COM3
→ BrainFlow
→ raw CSV save
→ local metadata JSON
→ readback summary
```

However, the project did not establish stable posterior acquisition or a stable recovered forehead acquisition baseline by the end of Session 12.

The key transition after this milestone is:

```text
planned self-recorded EEG experiment
→ acquisition stability risk identified
→ project route revised into parallel tracks
```

The next block should not wait for OpenBCI acquisition stability before continuing analysis and control development.

The revised direction is:

```text
public EEG dataset
→ sliding-window feature extraction
→ feature time series
→ threshold / smoothing / dwell-time logic
→ command stream
→ Arduino actuator test
```

OpenBCI self-recording remains part of the project, but it should no longer be the only path for forward progress.

## 5. Key Technical Outcomes

### 5.1 OpenBCI setup and safety documentation were prepared

Session 09 prepared the OpenBCI acquisition stage before body-connected recording.

The main setup elements were documented:

```text
Cyton board
active channels
SRB / SRB2 reference
BIAS
USB dongle
battery power
OpenBCI EEG Headband Kit
initial posterior montage candidate
recording safety checklist
metadata requirements
```

The initial intended montage used a small number of active channels:

```text
Ch1 / N1P
= approximate posterior-left headband position

Ch2 / N2P
= approximate posterior-right headband position

SRB / SRB2 reference
= one earclip

BIAS
= opposite earclip
```

This established the principle that OpenBCI data should be interpreted together with setup metadata: electrode, position, channel, reference, BIAS connection, and recording condition.

### 5.2 GUI / Cyton / COM3 connection and BrainFlow infrastructure were confirmed

Session 10 confirmed the OpenBCI GUI connection path on Windows 11. The GUI detected the CYTON live data source, manual COM3 connection succeeded, the Time Series widget showed live traces, and accelerometer values were visible.

Session 11 moved from GUI-level checks to programmatic acquisition with BrainFlow. BrainFlow's synthetic board verified the save / readback workflow without hardware variables, and the actual Cyton test used the known-good Ch1 forehead flat-electrode montage from Session 10.

The actual BrainFlow run completed this path:

```text
Cyton
→ COM3
→ BrainFlow
→ raw CSV save
→ local metadata JSON save
→ raw CSV readback
→ readback summary JSON
```

This verified acquisition infrastructure and file handling. Posterior acquisition quality, alpha reactivity, focus estimation, and robot-control readiness were not evaluated in this step.

### 5.3 Posterior dry-comb and contact-assisted acquisition remained unstable

The initial posterior dry-comb setup in Session 10 remained Railed / Near Railed. Forehead flat-electrode diagnostics showed that Ch1 and Ch2 could produce Not Railed signals under easier skin-contact conditions, which reduced the likelihood that the main issue was the GUI connection, COM3 path, Cyton live stream, or basic Ch1 / Ch2 channel path.

The remaining Session 10 bottleneck was posterior dry-comb scalp contact through hair.

Session 12 tested a revised posterior contact strategy using Ten20 conductive paste / gel and OpenBCI gold cup electrodes. One attempt showed temporary improvement to a Not Railed Ch1 condition after Ten20 reapplication and improved hair separation, but the condition was not repeatably stable.

The result supports gold cup + Ten20 as a potentially useful contact-assisted direction, while showing that the current posterior placement / fixation / contact condition was not stable enough for recording.

### 5.4 Forehead baseline recovery also remained unstable after Session 12

After posterior instability, Session 12 returned to forehead control and baseline recovery checks.

The known-good Ch1 forehead flat-electrode baseline from Session 10 was not reproduced at the end of the initial Session 12 block. The 2026-07-07 continuation then attempted to recover a stable forehead acquisition baseline after a full reset.

Ch1 forehead baseline was not recovered. Ch2 showed partial responsiveness under some conditions, especially around the left-forehead flat-electrode setup and SRB assembly B, but the improvement was not stable.

The observed pattern was:

```text
temporary Not Railed or partial responsiveness
→ time-dependent drift
→ Near Railed or Railed state
```

Session 12-C narrowed the test to one fixed condition:

```text
Ch2 / N2P
white snap cable
flat D
left forehead contact position
SRB assembly B
BIAS assembly B
fixed observation window
```

C00 confirmed that the GUI / Cyton / COM3 live-stream path was active after full reset. C01 started in a Near Railed state and eventually drifted to Railed 100% / 0.00 uVrms.

Together, the continuation and controlled check did not recover a stable acquisition baseline. This provided the stopping point for Session 12 hardware testing.

### 5.5 Acquisition risk led to a hybrid project route

By the end of Session 12, the project had enough evidence to treat OpenBCI self-recorded acquisition as an active risk.

Current status:

```text
confirmed:
- OpenBCI GUI / Cyton / COM3 live-stream path
- BrainFlow acquisition / save / readback infrastructure
- Session 10 forehead flat-electrode baseline under the original known-good condition

not confirmed:
- stable posterior acquisition
- stable recovered forehead baseline after Session 12 continuation
- self-recorded eyes-open / eyes-closed alpha reactivity
- feature-analysis-ready self-recorded OpenBCI dataset
```

Additional self-guided hardware swapping is unlikely to be the most productive use of the next project block unless OpenBCI support suggests a specific test.

The next project block should proceed through public EEG replay-control and Arduino minimum-demo work while preparing an OpenBCI forum/support inquiry.

## 6. Decisions Made After Milestone 03

### 6.1 Adopt a hybrid project route

The project should continue through a hybrid route rather than depending on self-recorded OpenBCI acquisition as the only path.

The revised structure is:

```text
OpenBCI self-recording
= troubleshooting / optional validation track

public EEG replay-control
= main analysis / control track

Arduino
= independent control-output track
```

The replay-control track will use public EEG-derived feature streams for command generation. Self-recorded OpenBCI data can be added later if acquisition stability is recovered.

### 6.2 Move public EEG replay-control and Arduino minimum-demo work earlier

The original plan placed Arduino basics and Python-Arduino communication after the self-recorded EEG experiment block.

After Session 12, Arduino work should begin earlier.

The compressed minimum route is:

```text
public EEG feature time series
→ threshold / smoothing / dwell-time rule
→ command stream
→ Python-Arduino serial command
→ servo / gripper response
→ plot, log, and short demo video
```

This keeps the project moving even if OpenBCI acquisition remains unresolved.

### 6.3 Pause further self-guided OpenBCI troubleshooting unless a specific support-guided test is available

Session 12 produced enough evidence for an OpenBCI forum/support inquiry.

The next OpenBCI hardware step should be based on a specific recommendation, such as a reference / BIAS check, impedance check, channel setting check, lead check, or board-specific diagnostic.

Without that guidance, further electrode and cable swapping is likely to consume project time without improving the analysis or control architecture.

## 7. Outputs Produced

### Setup and troubleshooting documents

- [`docs/setup/openbci-equipment-inventory.md`](../docs/setup/openbci-equipment-inventory.md)
- [`docs/setup/cyton-board-map-v0.1.md`](../docs/setup/cyton-board-map-v0.1.md)
- [`docs/setup/alpha-reactivity-montage-v0.1.md`](../docs/setup/alpha-reactivity-montage-v0.1.md)
- [`docs/setup/eeg-recording-safety-environment-checklist.md`](../docs/setup/eeg-recording-safety-environment-checklist.md)
- [`docs/setup/openbci-gui-install-and-connection-log-v0.1.md`](../docs/setup/openbci-gui-install-and-connection-log-v0.1.md)
- [`docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md)
- [`docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md`](../docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md)
- [`docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md)

### Scripts and results

- [`scripts/05_brainflow_synthetic_pipeline_check.py`](../scripts/05_brainflow_synthetic_pipeline_check.py)
- [`scripts/06_brainflow_cyton_record_session11.py`](../scripts/06_brainflow_cyton_record_session11.py)
- [`scripts/07_brainflow_cyton_record_session12_posterior_contact_assisted.py`](../scripts/07_brainflow_cyton_record_session12_posterior_contact_assisted.py)
- [`results/session-11/2026-07-04_122240_s11_brainflow-synthetic_readback_summary.json`](../results/session-11/2026-07-04_122240_s11_brainflow-synthetic_readback_summary.json)
- [`results/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_readback_summary.json`](../results/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_readback_summary.json)

The actual Session 11 Cyton raw recording and local metadata were generated locally and kept out of GitHub:

```text
data/raw/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_raw.csv
data/raw/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_metadata.json
```

Session 12 folders were also prepared:

- [`data/raw/session-12/README.md`](../data/raw/session-12/README.md)
- [`results/session-12/README.md`](../results/session-12/README.md)

### Representative figures

Representative Session 10 figures:

- [`figures/session-10/troubleshooting/2026-06-21_s10_attempt-02_posterior_ch1-ch2_comb-dry_initial_railed-nonflat.png`](../figures/session-10/troubleshooting/2026-06-21_s10_attempt-02_posterior_ch1-ch2_comb-dry_initial_railed-nonflat.png)
- [`figures/session-10/troubleshooting/2026-06-23_s10_attempt-20_ch1-n1p_black_flatA_forehead_baseline-repeat_not-railed.png`](../figures/session-10/troubleshooting/2026-06-23_s10_attempt-20_ch1-n1p_black_flatA_forehead_baseline-repeat_not-railed.png)
- [`figures/session-10/troubleshooting/2026-06-23_s10_attempt-21_ch1-n1p_black_comb-dry_posterior-hair-parted_final-railed.png`](../figures/session-10/troubleshooting/2026-06-23_s10_attempt-21_ch1-n1p_black_comb-dry_posterior-hair-parted_final-railed.png)

Representative Session 12 figures:

- [`figures/session-12/contact-assisted/2026-07-06_s12_attempt-02_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_not-railed.png`](../figures/session-12/contact-assisted/2026-07-06_s12_attempt-02_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_not-railed.png)
- [`figures/session-12/contact-assisted/2026-07-06_s12_attempt-05_ch1-n1p_black-flatA_forehead-baseline_railed.png`](../figures/session-12/contact-assisted/2026-07-06_s12_attempt-05_ch1-n1p_black-flatA_forehead-baseline_railed.png)
- [`figures/session-12/contact-assisted/2026-07-07_s12_attempt-b13_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB-swapped_not-railed.png`](../figures/session-12/contact-assisted/2026-07-07_s12_attempt-b13_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB-swapped_not-railed.png)
- [`figures/session-12/contact-assisted/2026-07-07_s12_attempt-b15c_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_contact-repeat_drift-to-railed.png`](../figures/session-12/contact-assisted/2026-07-07_s12_attempt-b15c_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_contact-repeat_drift-to-railed.png)
- [`figures/session-12/contact-assisted/2026-07-08_s12_attempt-c00_full-reset_gui-com3-live-stream_board-only.png`](../figures/session-12/contact-assisted/2026-07-08_s12_attempt-c00_full-reset_gui-com3-live-stream_board-only.png)
- [`figures/session-12/contact-assisted/2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_railed_100.png`](../figures/session-12/contact-assisted/2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_railed_100.png)

### Data boundary

No BrainFlow recording was performed in Session 12.

No feature-analysis-ready self-recorded EEG dataset was produced in Session 12.

No PSD, band-power, alpha reactivity, focus-state, or robot-control result was generated from self-recorded OpenBCI data.

## 8. Open Questions

The following questions remain open after Milestone 03.

### 8.1 OpenBCI acquisition stability

- Is the current instability mainly related to SRB / BIAS contact, active electrode contact, lead / cable assembly, GUI / channel state, or board / session state?
- Would impedance checking or another OpenBCI-supported diagnostic help narrow the acquisition problem?
- Which Session 10–12 evidence files should be sent to OpenBCI forum/support?

### 8.2 Public EEG replay-control design

- How should public EEG data be loaded into a common feature-stream format for replay-control?
- Which dataset should be used first for the replay-control sprint?
- How should sliding-window alpha / beta features be converted into command states?

### 8.3 Time-series variability and control stability

- How do window length, overlap, smoothing, dwell time, and refractory period affect command stability?
- How should false-trigger-like events be estimated from public EEG feature time series?
- How should latency be defined for replayed feature-to-command transitions?

### 8.4 Arduino command and actuator layer

- What is the minimum Arduino actuator setup needed for a July demo?
- Should the first actuator output use one servo, one gripper action, or a simpler open / close / stop command set?
- What command log format should connect EEG-derived feature states to Arduino actions?

## 9. Risks Identified

| Risk | Description | Current response |
|---|---|---|
| Acquisition instability | Stable self-recorded OpenBCI baseline was not recovered in Session 12 | Treat OpenBCI self-recording as troubleshooting / optional validation track |
| Posterior / contact instability | Posterior dry-comb and contact-assisted posterior setup did not become repeatably stable | Do not proceed to posterior alpha testing without stable GUI-level acquisition |
| Reference / BIAS uncertainty | SRB / BIAS changes affected the signal but did not establish stable acquisition | Prepare OpenBCI inquiry with documented attempts |
| Overcommitting to hardware troubleshooting | Additional self-guided hardware swapping could consume the next block | Continue hardware tests only if support response suggests a specific test |
| Premature threshold control | Thresholds may be unstable if based on averages rather than feature time series | Analyze sliding-window features, variability, latency, and false-trigger-like events before setting control rules |

## 10. Next Actions

The next block should focus on a compressed Session 13–20 sprint.

The goal is a minimum viable replay-control demo:

```text
public EEG feature time series
→ threshold / smoothing / dwell-time logic
→ command stream
→ Python-Arduino serial command
→ actuator output
→ plots, logs, and short demo video
```

### Compressed Session 13–20 sprint direction

1. Prepare OpenBCI forum/support inquiry using Session 10–12 evidence.

2. Start a public EEG replay pipeline:

   ```text
   public EEG dataset
   → loader
   → preprocessing
   → sliding-window feature extraction
   → feature time series
   ```

3. Build a replay-control decision layer:

   ```text
   feature stream
   → threshold rule
   → smoothing
   → dwell-time condition
   → refractory period
   → command state
   ```

4. Start Arduino minimum-demo work earlier than originally planned:

   ```text
   Arduino-only servo / gripper smoke test
   Python-Arduino serial command test
   open / close / stop command set
   command log
   ```

5. Produce minimum sprint outputs:

   ```text
   feature time-series plot
   command timeline plot
   threshold rule comparison table
   short Arduino replay demo video
   technical note
   GitHub README update
   ```

The following block should extend the sprint output toward threshold sensitivity, false-trigger-like event rate, latency, and command stability analysis.

## 11. Milestone Reflection

Milestone 03 did not produce a feature-analysis-ready self-recorded OpenBCI dataset.

Its main value was identifying acquisition stability as a project risk and separating that risk from analysis / control progress.

The project confirmed:

```text
OpenBCI GUI / Cyton / COM3 live stream
BrainFlow acquisition / save / readback infrastructure
attempt-level troubleshooting documentation
```

The project did not yet confirm:

```text
stable posterior acquisition
stable recovered forehead acquisition baseline after Session 12
self-recorded eyes-open / eyes-closed alpha reactivity
self-recorded EEG-based robot control
```

The next phase should focus on making the control architecture testable:

```text
feature time series
→ decision rule
→ command stream
→ actuator output
```

This keeps the project aligned with the original EEG-BCI robot control goal without allowing acquisition instability to block all progress.

## 12. Related Links

- [Session 09](../weekly-notes/session-09-260620.md)
- [Session 10](../weekly-notes/session-10-260627.md)
- [Session 11](../weekly-notes/session-11-260704.md)
- [Session 12](../weekly-notes/session-12-260706.md)
- [Milestone 02 Report](milestone-02-session-05-to-07.md)

## 13. References

### OpenBCI documentation

- [OpenBCI Documentation](https://docs.openbci.com/)
- [OpenBCI Cyton Board documentation](https://docs.openbci.com/Cyton/CytonLanding/)
- [OpenBCI Cyton Getting Started Guide](https://docs.openbci.com/GettingStarted/Boards/CytonGS/)
- [OpenBCI EEG Setup Guide](https://docs.openbci.com/GettingStarted/Biosensing-Setups/EEGSetup/)
- [OpenBCI GUI documentation](https://docs.openbci.com/Software/OpenBCISoftware/GUIDocs/)
- [OpenBCI GUI troubleshooting](https://docs.openbci.com/Troubleshooting/GUI_Troubleshooting/)

### BrainFlow documentation

- [BrainFlow Documentation](https://brainflow.readthedocs.io/)
- [BrainFlow Supported Boards](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html)
- [BrainFlow Data Format Description](https://brainflow.readthedocs.io/en/stable/DataFormatDesc.html)

### Internal setup / troubleshooting references

- [`docs/setup/openbci-gui-install-and-connection-log-v0.1.md`](../docs/setup/openbci-gui-install-and-connection-log-v0.1.md)
- [`docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md)
- [`docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md`](../docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md)
- [`docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md)
