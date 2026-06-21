# OpenBCI Cyton initial signal troubleshooting log v0.1

## Document metadata

- Session: 10
- Date range: 2026-06-20–2026-06-
- Scope: Signal-level and scalp-contact troubleshooting after Cyton-to-GUI live stream confirmation
- Status: in progress
- Version: v0.1
- Coverage: Attempts 01–09
- Update rule: append new troubleshooting attempts and update current/final status without deleting earlier observations
- Related connection log: `docs/setup/openbci-gui-install-and-connection-log-v0.1.md`

## 1. Purpose

This document records signal-level and scalp-contact troubleshooting during Session 10.

The OpenBCI GUI installation and Cyton connection-level setup are documented separately in:

* `docs/setup/openbci-gui-install-and-connection-log-v0.1.md`

This document focuses on the first issue observed after the Cyton-to-GUI live stream was confirmed:

```text
The intended posterior headband montage did not yet produce stable, non-flat, non-railed scalp-contact waveforms from Ch1 or Ch2.
```

This document is not an EEG feature analysis record.

No alpha, beta, attention, focus, or robot-control interpretation is made here.

## 2. Related setup documents

* `docs/setup/openbci-equipment-inventory.md`
* `docs/setup/cyton-board-map-v0.1.md`
* `docs/setup/alpha-reactivity-montage-v0.1.md`
* `docs/setup/eeg-recording-safety-environment-checklist.md`
* `docs/setup/openbci-gui-install-and-connection-log-v0.1.md`

## 3. Starting point before troubleshooting

Before signal troubleshooting, the following connection-level items were already confirmed:

* OpenBCI GUI launched successfully on Windows 11.
* CYTON live data source was available.
* Manual serial connection through COM3 succeeded.
* Start Session succeeded.
* Start Data Stream succeeded.
* Time Series widget showed live traces.
* Accelerometer values were visible.
* Board-only stream confirmed the Cyton-to-GUI live streaming path.

Confirmed connection path:

```text
Cyton board
→ USB dongle
→ COM3 serial connection
→ OpenBCI GUI
→ live data stream
```

The board-only traces were treated as floating-input activity and environmental/electrical noise, not physiological EEG, because no body-connected electrode/reference montage was present during that check.

## 4. Initial body-connected montage tested

The initial montage followed the Session 09 approximate posterior montage.

* Ch1 / N1P: black snap cable, posterior-left headband position, comb electrode
* Ch2 / N2P: white snap cable, posterior-right headband position, comb electrode
* SRB / SRB2 reference function: left earclip
* BIAS: right earclip
* Ch3–Ch8: unused in the initial test

The active electrode positions were recorded as approximate posterior-left and posterior-right headband positions, not exact 10–20 O1/O2 positions.

## 5. Initial problem statement

During the initial body-connected posterior headband test:

* Accelerometer values remained visible.
* Ch1 and Ch2 did not show stable scalp-contact waveforms during normal posterior headband placement.
* Ch1 and Ch2 appeared railed / flat, with values similar to:

  * `Railed 100%`
  * flat waveform
  * `0.00 uVrms`
* Ch3–Ch8 also showed railed behavior initially, but they were not part of the intended initial montage.

After unused channels were turned off or ignored, Ch1 and Ch2 still remained railed during normal posterior headband placement.

This suggested that the main issue was unlikely to be the GUI launch, COM port connection, or live streaming path.

## 6. Troubleshooting attempts

| Attempt | Action                                            | Observation                                                                         | Interpretation                                                                 | Status       |
| ------- | ------------------------------------------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ------------ |
| 01      | Board-only stream test                            | Moving traces and accelerometer values were visible                                 | Cyton-to-GUI stream path worked; traces were not EEG                           | Confirmed    |
| 02      | Initial posterior headband placement with Ch1/Ch2 | Ch1 and Ch2 remained railed / flat                                                  | Usable scalp-contact acquisition not achieved                                  | Not resolved |
| 03      | Unused channels handled as off / ignored          | Ch3–Ch8 no longer treated as relevant; Ch1/Ch2 still railed                         | Unused channels were not the main issue                                        | Confirmed    |
| 04      | Hardware Settings checked                         | Gain, input type, Bias Include, SRB2, and SRB1 states were observed                 | Initial settings did not show an obvious connection-level failure              | Confirmed    |
| 05      | Cyton pin / channel mapping checked               | Ch1/N1P, Ch2/N2P, SRB, and BIAS mapping were reviewed                               | No obvious mapping mismatch was identified                                     | Confirmed    |
| 06      | Ch1 comb electrode touch test                     | Ch1 responded when the Ch1/black comb electrode was touched directly                | Ch1 channel path was likely functional                                         | Confirmed    |
| 07      | Ch2 comb electrode touch test                     | Ch2 responded when the Ch2/white comb electrode was touched directly                | Ch2 channel path was likely functional                                         | Confirmed    |
| 08      | Comb electrode pressed more stably                | Channel waveform appeared when the comb electrode was held with more stable contact | Dry comb electrode contact stability was likely involved                       | Confirmed    |
| 09      | Battery connector issue after charging            | LiPo battery connector was difficult to remove from the USB charger                 | Further body-connected testing was stopped for safety and equipment protection | Paused       |

## 7. Current interpretation

Session 10 initial troubleshooting narrowed the issue to the following likely bottleneck:

```text
dry comb electrode
→ unstable scalp contact through hair
→ railed / flat Ch1 and Ch2 during normal posterior headband placement
```

The following parts were likely functional:

* OpenBCI GUI launch
* Cyton-to-GUI live streaming path
* USB dongle / COM3 connection
* Accelerometer stream
* Ch1 / N1P channel path
* Ch2 / N2P channel path
* snap cables
* comb electrodes

The following was not yet achieved:

* stable non-flat, non-railed waveform from posterior-left headband placement
* stable non-flat, non-railed waveform from posterior-right headband placement
* usable scalp-contact acquisition from the intended posterior montage

The current interpretation remains provisional because Ch1-only forehead contact testing and posterior retry have not yet been completed.

## 8. Interpretation boundary

`Railed 100%` was not interpreted as strong EEG.

It was treated as a non-usable acquisition state.

Feature-level analysis remains out of scope until at least one intended active channel shows a stable, non-flat, non-railed scalp-contact waveform.

No EEG feature interpretation was performed in this troubleshooting stage.

## 9. Next troubleshooting steps

The next troubleshooting step should simplify the setup to one active channel.

Planned sequence:

1. Safely disconnect the LiPo battery from the USB charger.
2. Use Cyton with LiPo battery power only.
3. Keep Arduino, servo, and robot hardware disconnected.
4. Use Ch1 / N1P only.
5. Keep SRB earclip reference and BIAS earclip unchanged.
6. Keep Ch2–Ch8 off or ignored.
7. First test Ch1 at a forehead skin-contact position.
8. Prefer a flat snap electrode for forehead contact if available.
9. If Ch1 shows a stable, non-flat, non-railed waveform at the forehead, save a screenshot.
10. Then retry Ch1 at the posterior comb electrode position.
11. Add Ch2 only after Ch1 becomes stable.
12. Do not run eyes-open / eyes-closed alpha reactivity testing yet.

Success criterion for the next step:

```text
At least one active channel shows a stable, non-flat, non-railed waveform in a controlled contact test.
```

## 10. Planned screenshots / records

Screenshots should be added only if they are actually produced.

Planned:

* `figures/session-10/openbci-gui-board-only-live-stream.png`
* `figures/session-10/openbci-gui-hardware-settings-cyton.png`
* `figures/session-10/ch1-forehead-contact-diagnostic.png`
* `figures/session-10/ch1-posterior-contact-retry.png`
* `figures/session-10/ch1-ch2-stable-posterior-waveform.png`

No valid EEG feature dataset has been produced at this stage.

## 11. Final troubleshooting status

To be completed after the next troubleshooting attempt.

Current status:

```text
Connection-level setup: confirmed
Ch1/Ch2 channel response: confirmed by touch tests
Stable posterior dry-comb acquisition: not yet achieved
Main suspected bottleneck: dry comb electrode scalp-contact instability
EEG feature interpretation: not performed
```
