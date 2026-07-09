# Milestone 03 Report: Session 09–12

## 1. Overview

This report summarizes the third milestone of the EEG-BCI robot control project.

Sessions 09–12 focused on moving from offline public EEG analysis toward OpenBCI Cyton acquisition setup and initial self-recorded acquisition checks. In Milestone 02, the project established a working public EEG analysis workflow using public EEG data, filtering, PSD, band-power extraction, and eyes-open / eyes-closed comparison. Milestone 03 tested whether that workflow could begin transferring to OpenBCI-based acquisition.

The OpenBCI GUI connection path and BrainFlow acquisition / save / readback infrastructure were confirmed at the connection and file-handling level. However, stable self-recorded acquisition was not established. The unresolved bottleneck is now treated as acquisition / contact / reference stability risk.

After this milestone, OpenBCI self-recording remains an optional, support-guided track, while public EEG replay-control and Arduino minimum-demo work move earlier in the project.

## 2. Period Covered

| Item             | Description                                                                                    |
| ---------------- | ---------------------------------------------------------------------------------------------- |
| Milestone        | Milestone 03                                                                                   |
| Sessions covered | Session 09–12                                                                                  |
| Period           | 2026.06.20 – 2026.07.08                                                                        |
| Current phase    | OpenBCI setup, BrainFlow acquisition infrastructure, and acquisition-stability troubleshooting |
| Next phase       | Public EEG replay-control pipeline and Arduino minimum-demo sprint                             |

## 3. Sessions Covered

| Session    | Date             | Main Focus                                                                                                                        | Main Output                                                                                                                                                |
| ---------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Session 09 | 2026.06.20       | OpenBCI Cyton structure, electrode mapping, reference / BIAS role, safety checklist, and initial posterior montage preparation    | Setup documents and recording readiness criteria                                                                                                           |
| Session 10 | 2026.06.21–06.23 | OpenBCI GUI installation, Cyton connection, initial posterior dry-comb troubleshooting, and forehead flat-electrode diagnostics   | GUI / Cyton / COM3 live-stream path confirmed; forehead flat-electrode control confirmed under simplified contact condition; posterior dry-comb unresolved |
| Session 11 | 2026.07.04–07.05 | BrainFlow acquisition pipeline, synthetic board test, actual Cyton acquisition, raw save, metadata, and readback verification     | BrainFlow synthetic and actual Cyton acquisition infrastructure verified using the Session 10 forehead control condition                                   |
| Session 12 | 2026.07.06–07.08 | Posterior contact-assisted acquisition, forehead baseline recovery, SRB / BIAS checks, and controlled acquisition-stability check | Stable acquisition baseline not recovered; OpenBCI inquiry and route revision needed                                                                       |

## 4. Project Direction After Milestone 03

The project has moved from public EEG analysis into OpenBCI-based acquisition setup.

The following connection path was confirmed:

```text
OpenBCI Cyton
→ USB dongle
→ COM3
→ OpenBCI GUI live stream
```

The BrainFlow acquisition infrastructure was also confirmed under a simplified forehead control condition:

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
→ analysis / control development no longer blocked by self-recording
```

The revised direction is:

```text
public EEG dataset
→ sliding-window feature extraction
→ feature time series
→ threshold / smoothing / dwell-time logic
→ command stream
→ Arduino actuator test
```

The next block will focus on a replay-based feature-to-command-to-actuator pipeline.

OpenBCI self-recording remains part of the project, but further hardware testing should be guided by a specific diagnostic recommendation.

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

The active electrode positions were treated as approximate headband positions, not exact 10–20 O1 / O2 positions.

This established the principle that OpenBCI data should be interpreted together with setup metadata: electrode, position, channel, reference, BIAS connection, and recording condition.

### 5.2 GUI / Cyton / COM3 connection and BrainFlow infrastructure were confirmed

Session 10 confirmed the OpenBCI GUI connection path on Windows 11. The GUI detected the CYTON live data source, manual COM3 connection succeeded, the Time Series widget showed live traces, and accelerometer values were visible.

Session 11 moved from GUI-level checks to programmatic acquisition with BrainFlow. BrainFlow's synthetic board verified the save / readback workflow without hardware variables. The actual Cyton test then used the Session 10 forehead flat-electrode control condition to test the acquisition path without returning to the unresolved posterior contact problem.

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

This step was limited to acquisition infrastructure and file-handling verification.

### 5.3 Posterior dry-comb and contact-assisted acquisition remained unstable

The initial posterior dry-comb setup in Session 10 remained Railed / Near Railed. Forehead flat-electrode diagnostics showed that Ch1 and Ch2 could produce Not Railed signals under easier skin-contact conditions. This reduced the likelihood that the main issue was the GUI connection, COM3 path, Cyton live stream, or basic Ch1 / Ch2 channel path.

The remaining Session 10 bottleneck was posterior dry-comb scalp contact through hair.

Session 12 tested a revised posterior contact strategy using Ten20 conductive paste / gel and OpenBCI gold cup electrodes. S12-A02 showed temporary improvement to a Not Railed Ch1 condition after Ten20 reapplication and improved hair separation. However, S12-A03 returned to Near Railed under a similar posterior condition, and the forehead gold cup control also remained Near Railed.

This suggests that improved hair separation and Ten20 reapplication can temporarily improve posterior contact, but Session 12 did not establish gold cup + Ten20 as a repeatably stable acquisition method under the tested conditions.

### 5.4 Forehead baseline recovery also remained unstable after Session 12

After posterior instability, Session 12 returned to forehead control and baseline recovery checks.

The Session 10 forehead flat-electrode control condition was not reproduced at the end of the initial Session 12 block. The 2026-07-07 continuation then attempted to recover a stable forehead acquisition baseline after a full reset.

B00 confirmed that the GUI / Cyton / COM3 live-stream path remained active. However, B01–B07 did not recover Ch1 responsiveness. Ch2 showed partial responsiveness under some conditions, especially around the left-forehead flat-electrode setup and SRB assembly B, but the improvement was not stable.

The observed pattern was:

```text
temporary Not Railed or partial responsiveness
→ time-dependent drift
→ Near Railed or Railed state
```

B11 and B13 showed temporary Ch2 improvement. B14–B15 showed drift from an initially improved state toward Near Railed or Railed. B17 and B18 also showed that unintended channel activity could appear under the current GUI / session state.

Session 12-C then narrowed the test to one fixed condition:

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

### 5.5 Acquisition risk was separated from analysis / control progress

By the end of Session 12, the project had enough evidence to treat OpenBCI self-recorded acquisition as an active risk.

Current status:

```text
confirmed:
- OpenBCI GUI / Cyton / COM3 live-stream path
- BrainFlow acquisition / save / readback workflow
- Session 10 forehead flat-electrode control under its original condition

not confirmed:
- stable posterior acquisition
- stable recovered forehead acquisition baseline after Session 12
- self-recorded eyes-open / eyes-closed alpha reactivity
- feature-analysis-ready self-recorded OpenBCI dataset
```

Additional self-guided hardware swapping is unlikely to be the most productive use of the next project block unless OpenBCI support suggests a specific test.

## 6. Decisions Made After Milestone 03

### 6.1 Treat OpenBCI self-recording as a support-guided optional track

OpenBCI self-recording should remain in the project, but it should not be treated as a prerequisite for analysis / control development.

Further OpenBCI hardware testing should be based on a specific support-guided diagnostic, such as a reference / BIAS check, impedance check, channel setting check, lead check, or board-specific test.

Without that guidance, additional electrode and cable swapping is likely to consume project time without improving the analysis or control architecture.

### 6.2 Move public EEG replay-control and Arduino minimum-demo work earlier

The original plan placed Arduino basics and Python-Arduino communication after the self-recorded EEG experiment block.

After Session 12, Arduino work should begin earlier.

The compressed minimum route is:

```text
public EEG feature time series
→ threshold / smoothing / dwell-time rule
→ command stream
→ Python-Arduino serial command
→ servo / gripper or other minimal actuator response
→ plot, log, and short demo video
```

This keeps the project moving even if OpenBCI acquisition remains unresolved.

## 7. Outputs Produced

### Setup and troubleshooting documents

* [`docs/setup/openbci-equipment-inventory.md`](../docs/setup/openbci-equipment-inventory.md)
* [`docs/setup/cyton-board-map-v0.1.md`](../docs/setup/cyton-board-map-v0.1.md)
* [`docs/setup/alpha-reactivity-montage-v0.1.md`](../docs/setup/alpha-reactivity-montage-v0.1.md)
* [`docs/setup/eeg-recording-safety-environment-checklist.md`](../docs/setup/eeg-recording-safety-environment-checklist.md)
* [`docs/setup/openbci-gui-install-and-connection-log-v0.1.md`](../docs/setup/openbci-gui-install-and-connection-log-v0.1.md)
* [`docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md)
* [`docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md`](../docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md)
* [`docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md)

### Scripts and repository-visible results

* [`scripts/05_brainflow_synthetic_pipeline_check.py`](../scripts/05_brainflow_synthetic_pipeline_check.py)
* [`scripts/06_brainflow_cyton_record_session11.py`](../scripts/06_brainflow_cyton_record_session11.py)
* [`scripts/07_brainflow_cyton_record_session12_posterior_contact_assisted.py`](../scripts/07_brainflow_cyton_record_session12_posterior_contact_assisted.py)

  * Prepared for Session 12 contact-assisted acquisition, but not used for BrainFlow recording because GUI-level acquisition criteria were not met.
* [`results/session-11/2026-07-04_122240_s11_brainflow-synthetic_readback_summary.json`](../results/session-11/2026-07-04_122240_s11_brainflow-synthetic_readback_summary.json)
* [`results/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_readback_summary.json`](../results/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_readback_summary.json)

The actual Session 11 Cyton raw recording and local metadata were generated locally and kept out of GitHub:

```text
data/raw/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_raw.csv
data/raw/session-11/2026-07-05_135705_s11_brainflow-cyton-ch1-forehead_metadata.json
```

### Representative evidence files

Full attempt-level evidence is maintained in the troubleshooting logs. Representative evidence files include:

* [`figures/session-10/troubleshooting/2026-06-23_s10_attempt-20_ch1-n1p_black_flatA_forehead_baseline-repeat_not-railed.png`](../figures/session-10/troubleshooting/2026-06-23_s10_attempt-20_ch1-n1p_black_flatA_forehead_baseline-repeat_not-railed.png)
* [`figures/session-10/troubleshooting/2026-06-23_s10_attempt-21_ch1-n1p_black_comb-dry_posterior-hair-parted_final-railed.png`](../figures/session-10/troubleshooting/2026-06-23_s10_attempt-21_ch1-n1p_black_comb-dry_posterior-hair-parted_final-railed.png)
* [`figures/session-12/contact-assisted/2026-07-06_s12_attempt-02_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_not-railed.png`](../figures/session-12/contact-assisted/2026-07-06_s12_attempt-02_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_not-railed.png)
* [`figures/session-12/contact-assisted/2026-07-07_s12_attempt-b13_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB-swapped_not-railed.png`](../figures/session-12/contact-assisted/2026-07-07_s12_attempt-b13_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB-swapped_not-railed.png)
* [`figures/session-12/contact-assisted/2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_railed_100.png`](../figures/session-12/contact-assisted/2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_railed_100.png)

### Data boundary

No BrainFlow recording or feature-analysis-ready self-recorded EEG dataset was produced in Session 12; therefore, no self-recorded PSD, band-power, alpha-reactivity, focus-state, or robot-control result was generated.

## 8. Open Questions

The following questions remain open after Milestone 03.

### 8.1 OpenBCI acquisition stability

* Is the current instability mainly related to SRB / BIAS contact, active electrode contact, lead / cable assembly, GUI / channel state, or board / session state?
* Would impedance checking or another OpenBCI-supported diagnostic help narrow the acquisition problem?
* Which Session 10–12 evidence files should be sent to OpenBCI forum/support?

### 8.2 Public EEG replay-control design

* How should the existing EEGBCI workflow be converted into a sliding-window feature stream for replay-control?
* Which window length, overlap, and feature definitions should be used for the first replay-control test?
* How should replay-control outputs be logged so that replay-based control is clearly separated from self-recorded BCI claims?

### 8.3 Time-series variability and control stability

* How do window length, overlap, smoothing, dwell time, and refractory period affect command stability?
* How should false-trigger-like events be estimated from public EEG feature time series?
* How should latency be defined for replayed feature-to-command transitions?

### 8.4 Arduino command and actuator layer

* How should the Python-Arduino serial command format be defined?
* What command log format should connect EEG-derived command states to Arduino actions?

## 9. Risks Identified

| Risk                                          | Description                                                                                                                                                                               | Current response                                                                                                                                                    |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Acquisition / contact / reference instability | Stable self-recorded OpenBCI acquisition was not recovered in Session 12; posterior contact, forehead baseline recovery, SRB / BIAS condition, and time-dependent drift remain unresolved | Treat OpenBCI self-recording as a support-guided optional track and do not use self-recorded data for feature-level claims until acquisition stability is recovered |
| Overcommitting to hardware troubleshooting    | Additional self-guided hardware swapping could consume the next block without improving the analysis or control architecture                                                              | Continue OpenBCI hardware tests only if support response suggests a specific diagnostic                                                                             |
| Replay-control claim ambiguity                | Public EEG replay-control could be mistaken for real-time self-recorded BCI control                                                                                                       | Label replay-based control, self-recorded acquisition, and Arduino output as separate tracks                                                                        |
| Premature threshold control                   | Thresholds may be unstable if based on averages rather than feature time series                                                                                                           | Analyze sliding-window features, variability, latency, and false-trigger-like events before setting control rules                                                   |

## 10. Next Actions

The next block should focus on a compressed Session 13–20 sprint.

The sprint target is a replay-based feature-to-command-to-actuator demo.

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

The next phase should focus on making the control architecture testable while OpenBCI acquisition is handled through support-guided troubleshooting.

## 12. Related Links

* [Session 09](../weekly-notes/session-09-260620.md)
* [Session 10](../weekly-notes/session-10-260627.md)
* [Session 11](../weekly-notes/session-11-260704.md)
* [Session 12](../weekly-notes/session-12-260706.md)
* [Milestone 02 Report](milestone-02-session-05-to-07.md)

## 13. References

### OpenBCI documentation

* [OpenBCI Documentation](https://docs.openbci.com/)
* [OpenBCI Cyton Board documentation](https://docs.openbci.com/Cyton/CytonLanding/)
* [OpenBCI Cyton Getting Started Guide](https://docs.openbci.com/GettingStarted/Boards/CytonGS/)
* [OpenBCI EEG Setup Guide](https://docs.openbci.com/GettingStarted/Biosensing-Setups/EEGSetup/)
* [OpenBCI EEG Headband Kit Documentation](https://docs.openbci.com/AddOns/Headwear/HeadBand/)
* [OpenBCI GUI documentation](https://docs.openbci.com/Software/OpenBCISoftware/GUIDocs/)
* [OpenBCI GUI troubleshooting](https://docs.openbci.com/Troubleshooting/GUI_Troubleshooting/)

### BrainFlow documentation

* [BrainFlow Documentation](https://brainflow.readthedocs.io/)
* [BrainFlow Supported Boards](https://brainflow.readthedocs.io/en/stable/SupportedBoards.html)
* [BrainFlow Data Format Description](https://brainflow.readthedocs.io/en/stable/DataFormatDesc.html)

### Internal setup / troubleshooting references

* [`docs/setup/openbci-gui-install-and-connection-log-v0.1.md`](../docs/setup/openbci-gui-install-and-connection-log-v0.1.md)
* [`docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-initial-signal-troubleshooting-log-v0.1.md)
* [`docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md`](../docs/setup/openbci-posterior-contact-assisted-acquisition-log-v0.1.md)
* [`docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md`](../docs/setup/openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md)
