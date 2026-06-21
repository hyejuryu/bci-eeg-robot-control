# OpenBCI Cyton initial signal troubleshooting log v0.1

## Document metadata

* Session: 10
* Scope: Signal-level and scalp-contact troubleshooting after Cyton-to-GUI live stream confirmation
* Status: in progress

## 1. Purpose

This document records signal-level and scalp-contact troubleshooting during Session 10.

The OpenBCI GUI installation and Cyton connection-level setup are documented separately in:

* `docs/setup/openbci-gui-install-and-connection-log-v0.1.md`

This document focuses on the first signal-level issue observed after the Cyton-to-GUI live stream was confirmed:

```text
The intended posterior headband montage did not yet produce stable, non-flat, non-railed scalp-contact waveforms from Ch1 or Ch2.
```

Feature-level EEG interpretation is out of scope in this document.

## 2. Starting point before troubleshooting

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

## 3. Initial body-connected montage tested

The initial montage followed the Session 09 approximate posterior montage.

* Ch1 / N1P: black snap cable, posterior-left headband position, comb electrode
* Ch2 / N2P: white snap cable, posterior-right headband position, comb electrode
* SRB / SRB2 reference function: left earclip
* BIAS: right earclip
* Ch3–Ch8: unused in the initial test

The active electrode positions were recorded as approximate posterior-left and posterior-right headband positions, not exact 10–20 O1/O2 positions.

## 4. Initial problem statement

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

## 5. Troubleshooting attempts

| Attempt | Action                                            | Observation                                                                                                                        | Interpretation                                                                    | Status       |
| ------- | ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------ |
| 01      | Board-only stream test                            | Moving traces and accelerometer values were visible                                                                                | Cyton-to-GUI stream path worked; traces were not EEG                              | Confirmed    |
| 02      | Initial posterior headband placement with Ch1/Ch2 | Ch1 and Ch2 remained railed / flat                                                                                                 | Usable scalp-contact acquisition was not achieved                                 | Not resolved |
| 03      | Unused channels handled as off / ignored          | Ch3–Ch8 were no longer treated as relevant; Ch1/Ch2 still remained railed                                                          | Unused channels were not the main issue                                           | Confirmed    |
| 04      | Hardware Settings checked                         | Gain, input type, Bias Include, SRB2, and SRB1 states were observed                                                                | Initial settings did not show an obvious connection-level failure                 | Confirmed    |
| 05      | Cyton pin / channel mapping checked               | Ch1/N1P, Ch2/N2P, SRB, and BIAS mapping were reviewed                                                                              | No obvious mapping mismatch was identified                                        | Confirmed    |
| 06      | Ch1 comb electrode touch test                     | Ch1 responded when the Ch1/black comb electrode was touched directly                                                               | Ch1 channel path was likely functional                                            | Confirmed    |
| 07      | Ch2 comb electrode touch test                     | Ch2 responded when the Ch2/white comb electrode was touched directly                                                               | Ch2 channel path was likely functional                                            | Confirmed    |
| 08      | Comb electrode contact pressure changed           | A waveform appeared once when the comb electrode was held with more stable contact, but the effect was not consistently reproduced | Electrode contact was likely involved, but this did not confirm a stable solution | Inconclusive |

## 6. Current interpretation

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
* accelerometer stream
* Ch1 / N1P channel path
* Ch2 / N2P channel path
* snap cables
* comb electrodes

The following was not yet achieved:

* stable non-flat, non-railed waveform from posterior-left headband placement
* stable non-flat, non-railed waveform from posterior-right headband placement
* usable scalp-contact acquisition from the intended posterior montage

The current interpretation remains provisional because Ch1-only forehead contact testing and posterior retry have not yet been completed.

`Railed 100%` was treated as a non-usable acquisition state, not as strong EEG. Feature-level analysis remains out of scope until a stable, non-flat, non-railed scalp-contact waveform is achieved.

Further body-connected testing was paused because the LiPo battery connector was difficult to remove from the USB charger after charging.

## 7. Next troubleshooting plan

The next troubleshooting should isolate contact and channel issues with the smallest possible setup.

Planned sequence:

1. Test Ch1 only at a forehead skin-contact position.
2. If Ch1 shows a stable, non-flat, non-railed waveform, save a screenshot.
3. Optionally test Ch2 at a forehead skin-contact position to confirm the second channel path.
4. Retry Ch1 only at the posterior comb electrode position.
5. If Ch1 becomes stable posteriorly, add Ch2 at the posterior comb electrode position.
6. If posterior dry-comb contact remains unstable, consider a contact-improvement method such as hair-parting, improved headband pressure, conductive gel/paste if appropriate, or another electrode/contact strategy.
7. Do not run eyes-open / eyes-closed alpha reactivity testing until stable acquisition is confirmed.

Success criterion for the next step:

```text
At least one active channel shows a stable, non-flat, non-railed waveform in a controlled contact test.
```

## 8. Evidence files

To be added when screenshots or recordings are produced.

No valid EEG feature dataset has been produced at this stage.

## 9. Final troubleshooting status

To be completed after the next troubleshooting attempt.

Current status:

```text
Connection-level setup: confirmed
Ch1/Ch2 channel response: confirmed by touch tests
Stable posterior dry-comb acquisition: not yet achieved
Main suspected bottleneck: dry comb electrode scalp-contact instability
EEG feature interpretation: not performed
```
