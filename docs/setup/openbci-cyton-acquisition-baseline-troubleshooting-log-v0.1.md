# OpenBCI Cyton acquisition baseline troubleshooting log v0.1

## 1. Document metadata

- Session: 12 continuation
- Date: 2026-07-07
- Related sessions: Session 10??2
- Version: v0.1
- Scope: forehead baseline recovery, channel/path checks, SRB/BIAS assembly checks, and GUI-level acquisition stability
- Out of scope: posterior acquisition validation, BrainFlow recording, EEG feature interpretation, alpha reactivity, focus estimation, robot control

## 2. Purpose and scope

This document records the Session 12 continuation troubleshooting after the initial posterior contact-assisted acquisition attempts.

The initial Session 12 posterior contact-assisted test did not establish stable posterior acquisition. At the end of that block, the known-good forehead flat-electrode baseline was also not reproduced. Therefore, the continuation shifted from posterior contact testing to acquisition baseline troubleshooting.

This document focuses on whether a stable forehead acquisition baseline could be recovered before returning to posterior testing.

## 3. Starting point

Before this continuation:

```text
Session 10:
- GUI / Cyton / COM3 live stream was confirmed.
- Ch1 and Ch2 produced Not Railed forehead flat-electrode signals under simplified diagnostic conditions.
- Posterior dry-comb acquisition remained unresolved.

Session 12 initial block:
- Posterior gold cup + Ten20 attempts were not repeatably stable.
- Forehead gold cup control remained Near Railed.
- Known-good Ch1 forehead flat-electrode baseline was not reproduced at the end of the block.
```

Continuation decision:

```text
Restart from full reset.
Recover a stable forehead acquisition baseline before returning to posterior acquisition testing.
```

## 4. Attempt log

| Attempt | Setup / action | Observation | Interpretation | Next decision |
|---|---|---|---|---|
| B00 | Full reset. GUI / COM3 live stream. No body electrodes. | GUI stream and accelerometer were visible. Floating channel activity was visible. | Connection-level stream path was active. Body-contact acquisition was not tested. | Proceed to B01. |
| B01 | Ch1 / N1P, black snap cable, flat A, forehead contact, SRB left, BIAS right. | Ch1 remained Railed. | Session 10 known-good Ch1 forehead baseline was not reproduced. | Adjust active contact. |
| B02 | Same as B01 after active contact adjustment. | Ch1 remained Railed 100% / 0.00 uVrms. | Active contact adjustment did not recover the baseline. | Run Ch1 active path touch test. |
| B03 | Ch1 / N1P, black snap cable, flat A, touch test. | No Ch1 response. | The black cable + flat A + Ch1 path did not respond under the current condition. | Change electrode only. |
| B04 | Ch1 / N1P, black snap cable, flat C, touch test without forehead contact. | No response. | Flat A alone did not explain the no-response condition. | Change cable only. |
| B05 | Ch1 / N1P, white snap cable, flat C, touch test without forehead contact. | No response. | Black snap cable alone became less likely as the sole issue. | Change electrode only. |
| B06 | Ch1 / N1P, white snap cable, flat D, touch test without forehead contact. | No response. | Flat A/C alone became less likely as the sole issue. | Re-seat SRB/BIAS. |
| B07 | Ch1 / N1P, white snap cable, flat D, touch test after SRB/BIAS re-seat. | No response. | Simple SRB/BIAS re-seat did not recover Ch1 response. | Switch active channel. |
| B08 | Ch2 / N2P, white snap cable, flat D, touch test. | Touch-related transient responses appeared, but they were not channel-specific and were not consistently reproducible. | Inconclusive. The response did not confirm a clean Ch2 path. | Test Ch2 forehead baseline. |
| B09 | Ch2 / N2P, white snap cable, flat D, forehead baseline. | Ch2 was Near Railed with visible non-flat waveform. Facial movement affected the trace. | Ch2 path was not completely inactive, but stable forehead baseline was not achieved. | Adjust forehead contact. |
| B10 | Same as B09 after contact adjustment. | Ch2 remained Near Railed. | Active contact adjustment did not produce a stable Not Railed baseline. | Check alternate contact position. |
| B11 | Ch2 / N2P, white snap cable, flat D, left-forehead contact position. | Ch2 showed Not Railed. | Contact position affected the result. This suggested that the Ch2 / white / flat D path could improve under a different forehead contact condition. | Repeat same condition. |
| B12 | Same as B11, repeated after reattachment. | Ch2 returned to Near Railed. | The B11 improvement was not repeatably stable. | Test SRB assembly. |
| B13 | Ch2 / N2P, white snap cable, flat D, left forehead, SRB assembly B, original BIAS. | Ch2 showed Not Railed. | SRB assembly B improved the condition compared with earlier attempts. | Test stream restart stability. |
| B14 | Same physical setup as B13. Stream restart only. | Ch2 initially appeared Not Railed, then drifted to Near Railed over time. | SRB assembly B improved the initial state but did not establish stable baseline over time. | Repeat physical contact. |
| B15 | Same as B13 after contact repeat. | Ch2 initially appeared Not Railed, drifted to Near Railed, then reached Railed 100% / 0.00 uVrms. | Dry flat forehead contact under SRB assembly B remained time-dependent and unstable. | Test BIAS assembly. |
| B16 | Ch2 / N2P, white snap cable, flat D, left forehead, SRB assembly B, BIAS assembly swapped. | Ch2 remained Near Railed around 88%. | BIAS assembly swap did not establish a stable Not Railed baseline. | Test active gold cup + Ten20 forehead control. |
| B17 | Ch2 / N2P, black gold cup + Ten20, left forehead, SRB assembly B, BIAS assembly B. | Intended Ch2 remained Railed 100% / 0.00 uVrms. Ch3 showed visible activity despite not being the intended active channel. | Active gold cup + Ten20 forehead control did not establish usable Ch2 acquisition. Channel mapping was checked and N2P connection was confirmed. | Run no-active-electrode control. |
| B18 | Active electrode removed. SRB assembly B and BIAS assembly B remained attached. | Ch3 initially showed Near Railed-like activity, then drifted to Railed / flat. | B18 supported treating the Ch3 activity observed in B17 as unintended channel activity under the current GUI/session state. | Stop hardware testing. |

## 5. Evidence files

Evidence files are stored in:

```text
figures/session-12/contact-assisted/
```

Relevant 2026-07-07 files:

```text
2026-07-07_s12_check-b00_full-reset_gui-com3-live-stream_board-only-floating-inputs.png
2026-07-07_s12_attempt-b01_ch1-n1p_black-flatA_forehead-baseline_railed.png
2026-07-07_s12_attempt-b02_ch1-n1p_black-flatA_forehead-baseline-contact-adjusted_railed.png
2026-07-07_s12_attempt-b03_ch1-n1p_black-flatA_touch-test_no-response.png
2026-07-07_s12_attempt-b04_ch1-n1p_black-flatC_touch-test_no-forehead_no-response.png
2026-07-07_s12_attempt-b05_ch1-n1p_white-flatC_touch-test_no-forehead_no-response.png
2026-07-07_s12_attempt-b06_ch1-n1p_white-flatD_touch-test_no-forehead_no-response.png
2026-07-07_s12_attempt-b07_ch1-n1p_white-flatD_touch-test_srb-bias-reseated_no-response.png
2026-07-07_s12_attempt-b08_ch2-n2p_white-flatD_touch-test_channel-switched_global-transient-inconclusive.png
2026-07-07_s12_attempt-b09_ch2-n2p_white-flatD_forehead-baseline_near-railed.png
2026-07-07_s12_attempt-b10_ch2-n2p_white-flatD_forehead-baseline-contact-adjusted_near-railed.png
2026-07-07_s12_attempt-b11_ch2-n2p_white-flatD_left-forehead-contact-position_not-railed.png
2026-07-07_s12_attempt-b12_ch2-n2p_white-flatD_left-forehead-contact-position-repeat_near-railed.png
2026-07-07_s12_attempt-b13_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB-swapped_not-railed.png
2026-07-07_s12_attempt-b14a_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_stream-restart_initial-not-railed.png
2026-07-07_s12_attempt-b14b_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_stream-restart_drift-to-near-railed.png
2026-07-07_s12_attempt-b15a_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_contact-repeat_initial-not-railed.png
2026-07-07_s12_attempt-b15b_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_contact-repeat_drift-to-near-railed.png
2026-07-07_s12_attempt-b15c_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_contact-repeat_drift-to-railed.png
2026-07-07_s12_attempt-b16_ch2-n2p_white-flatD_left-forehead-baseline_srb-assemblyB_bias-assembly-swapped_near-railed-plateau.png
2026-07-07_s12_attempt-b17_ch2-n2p_black-goldcup-ten20_left-forehead-control_srbB-biasB_railed.png
2026-07-07_s12_check-b18a_no-active-electrode_srbB-biasB_ch3-floating-control_initial-near-railed.png
2026-07-07_s12_check-b18b_no-active-electrode_srbB-biasB_ch3-floating-control_drift-to-railed.png
```

## 6. Current interpretation

The continuation did not recover a stable forehead acquisition baseline.

Main observations:

- Ch1 forehead baseline was not recovered.
- Ch2 showed partial responsiveness but did not provide stable baseline acquisition.
- Contact position affected the Ch2 result, but the improvement was not repeatably stable.
- SRB assembly B produced temporary improvement, but the condition drifted over time.
- BIAS assembly swap did not establish a stable Not Railed baseline.
- Active gold cup + Ten20 forehead control did not establish usable Ch2 acquisition.
- No-active-electrode control showed unintended channel activity under the current GUI/session state.

Current interpretation:

```text
The unresolved bottleneck is acquisition/contact/reference stability.
The current evidence is insufficient for returning to posterior acquisition testing.
```

## 7. Current decision

Hardware testing was stopped after B18.

No stable acquisition baseline was established in this continuation block.

Next work should begin with a narrower acquisition-stability test using one controlled active channel, one reference condition, one BIAS condition, and a fixed observation window.

Possible next-session direction:

- Use SRB assembly B as the initial reference candidate.
- Use BIAS assembly B as the initial BIAS candidate.
- Define one active channel and one active electrode/contact method before starting.
- Observe for a fixed stability window before treating the condition as usable.
- Record time-dependent drift explicitly if the Railed / Near Railed status changes during observation.

## 8. Session 12-C controlled acquisition-stability check

### 8.1 Purpose

After the 2026-07-07 continuation block, the next check was limited to one controlled acquisition-stability test.

The purpose was to test whether a stable forehead acquisition baseline could be recovered under one fixed condition, without continuing broad electrode, cable, posterior, or gold cup troubleshooting.

Scope:

```text
one active channel
one active electrode/contact condition
fixed SRB / BIAS condition
fixed observation window
GUI-level observation only
```

Out of scope:

```text
posterior acquisition
BrainFlow recording
EEG feature interpretation
alpha reactivity
focus estimation
robot control
```

### 8.2 C00 full-reset board only check

| Attempt | Setup / action | Observation | Interpretation | Next decision |
|---|---|---|---|---|
| C00     | Full reset. GUI / COM3 live stream. No body electrodes. | Data stream started. Time Series traces and accelerometer values were visible. | GUI / Cyton / COM3 live-stream path was active after full reset. This was a board-only check, not a body-contact acquisition test. | Proceed to one controlled body-contact stability check. |

### 8.3 C01 controlled body-contact stability check

| Attempt | Setup / action | Observation | Interpretation | Next decision |
|---|---|---|---|---|
| C01     | Ch2 / N2P, white snap cable, flat D, left forehead contact position, SRB assembly B, BIAS assembly B. | Ch2 started in a Near Railed state. During the fixed observation window, the condition did not stabilize. The Railed percentage increased over time, and Ch2 eventually drifted to Railed 100% / 0.00 uVrms. | The controlled C01 condition did not recover a stable forehead acquisition baseline. The result is consistent with the time-dependent drift observed in the previous Session 12 continuation attempts. | Stop hardware testing. Do not proceed to posterior acquisition, BrainFlow recording, alpha interpretation, or robot-control testing. Prepare OpenBCI inquiry using Session 10??2 evidence. |


### 8.4 Evidence files

Evidence files are stored in:

```text
figures/session-12/contact-assisted/
```

Relevant 2026-07-08 files:

```text
2026-07-08_s12_attempt-c00_full-reset_gui-com3-live-stream_board-only.png
2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_initial.png
2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_90s.png
2026-07-08_s12_attempt-c01_ch2-n2p_white-flatD_left-forehead_srbB-biasB_railed_100.png
```

### 8.5 Session 12-C decision

Session 12-C did not recover a stable acquisition baseline under the fixed Ch2 / white flat D / left forehead / SRB assembly B / BIAS assembly B condition.

Current decision:
```text
Stop further self-guided hardware troubleshooting for this block.
Prepare an OpenBCI forum/support inquiry with Session 10??2 evidence.
Move the project forward through the public EEG replay-control and Arduino minimum-demo track.
```

Current boundary:
```text
The unresolved issue should be treated as acquisition/contact/reference stability risk.
The current evidence does not support posterior acquisition testing, BrainFlow recording, or EEG feature-level interpretation from self-recorded OpenBCI data.
```
