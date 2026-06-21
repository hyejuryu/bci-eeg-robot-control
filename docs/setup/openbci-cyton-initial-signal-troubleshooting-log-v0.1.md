# OpenBCI Cyton initial signal troubleshooting log v0.1

## Document metadata

* Session: 10
* Scope: Signal-level and scalp-contact troubleshooting after Cyton-to-GUI live stream confirmation
* Status: in progress

## 1. Purpose

This document records signal-level and scalp-contact troubleshooting during Session 10.

The OpenBCI GUI installation and Cyton connection-level setup are documented separately in:

* [`docs/setup/openbci-gui-install-and-connection-log-v0.1.md`](../docs/setup/openbci-gui-install-and-connection-log-v0.1.md)

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

### Temporary electrode labels

For the swap tests, the two flat electrodes are temporarily labeled as follows:

* Flat electrode A: the flat electrode that produced a Not Railed Ch1 forehead signal with the black snap cable
* Flat electrode B: the flat electrode that repeatedly produced Near Railed results

These labels are only for troubleshooting and do not indicate official electrode names.

## 5. Troubleshooting attempts

| Attempt | Action                                                        | Observation                                                                                                                        | Interpretation                                                                    | Status             |
| ------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------ |
| 01      | Board-only stream test                                        | Moving traces and accelerometer values were visible                                                                                | Cyton-to-GUI stream path worked; traces were not EEG                              | Confirmed          |
| 02      | Initial posterior headband placement with Ch1/Ch2             | Ch1 and Ch2 remained railed / flat                                                                                                 | Usable scalp-contact acquisition was not achieved                                 | Not resolved       |
| 03      | Unused channels handled as off / ignored                      | Ch3–Ch8 were no longer treated as relevant; Ch1/Ch2 still remained railed                                                          | Unused channels were not the main issue                                           | Confirmed          |
| 04      | Hardware Settings checked                                     | Gain, input type, Bias Include, SRB2, and SRB1 states were observed                                                                | Initial settings did not show an obvious connection-level failure                 | Confirmed          |
| 05      | Cyton pin / channel mapping checked                           | Ch1/N1P, Ch2/N2P, SRB, and BIAS mapping were reviewed                                                                              | No obvious mapping mismatch was identified                                        | Confirmed          |
| 06      | Ch1 comb electrode touch test                                 | Ch1 responded when the Ch1/black comb electrode was touched directly                                                               | Ch1 channel path was likely functional                                            | Confirmed          |
| 07      | Ch2 comb electrode touch test                                 | Ch2 responded when the Ch2/white comb electrode was touched directly                                                               | Ch2 channel path was likely functional                                            | Confirmed          |
| 08      | Comb electrode contact pressure changed                       | A waveform appeared once when the comb electrode was held with more stable contact, but the effect was not consistently reproduced | Electrode contact was likely involved, but this did not confirm a stable solution | Inconclusive       |
| 09      | Ch1-only forehead test using comb electrode                   | Ch1 showed a visible non-flat waveform but remained Near Railed                                                                    | Comb electrode forehead contact did not confirm stable acquisition                | Not resolved       |
| 10      | Ch1-only forehead test using flat electrode A and black cable | Ch1 changed to Not Railed and remained stable for about 30 seconds                                                                 | Ch1/N1P can produce a stable non-railed signal under flat forehead contact        | Confirmed          |
| 11      | Ch2-only forehead test using flat electrode B and white cable | Ch2 remained Near Railed despite increased contact pressure                                                                        | Stable Ch2 acquisition was not confirmed under this electrode/cable combination   | Not resolved       |
| 12      | Flat electrode B with white cable moved to Ch1/N1P            | Ch1 still remained Near Railed, around 80%                                                                                         | The issue was not explained by Ch2/N2P input alone                                | Not resolved       |
| 13      | Ch1 baseline repeated with flat electrode A and black cable   | Ch1 again showed Not Railed behavior                                                                                               | The Ch1 + black cable + flat electrode A condition was reproducible               | Confirmed          |
| 14      | Flat electrode A tested with white cable on Ch1/N1P           | Ch1 changed to Not Railed, with the GUI showing approximately 67%                                                                  | White cable was likely functional when paired with the working flat electrode     | Confirmed          |
| 15      | Flat electrode B tested with black cable on Ch1/N1P           | Ch1 remained Near Railed                                                                                                           | Flat electrode B or its snap/contact condition became the main suspect            | Suspect identified |
| 16      |  Ch2/N2P tested with white cable and flat electrode A | Ch2 changed to Not Railed under forehead contact | Ch2/N2P input and white cable were likely functional when paired with the working flat electrode | Confirmed |
| 17 | Ch1/N1P posterior retry using black cable and original comb electrode | Ch1 remained Near Railed around 85%, with high amplitude around 197 uVrms | Posterior comb placement did not produce usable acquisition; high amplitude was treated as contact/artifact-dominated rather than EEG | Not resolved |

## 6. Current interpretation

Session 10 troubleshooting has now separated several possible causes.

The following parts are likely functional:

* OpenBCI GUI launch
* Cyton-to-GUI live streaming path
* USB dongle / COM3 connection
* accelerometer stream
* Ch1 / N1P input path
* Ch2 / N2P input path
* black snap cable
* white snap cable
* SRB / BIAS setup, at least under forehead flat-electrode contact conditions
* flat electrode A

The following issue is currently suspected:

```text
flat electrode B
or
flat electrode B snap/contact condition
```

This is because flat electrode B remained Near Railed with both the white and black snap cables on Ch1/N1P, while flat electrode A produced Not Railed results with both cables on Ch1/N1P.

Flat electrode A also produced a Not Railed result when used with Ch2/N2P and the white snap cable. This reduced the likelihood that Ch2/N2P or the white snap cable was the main cause of the earlier Ch2 Near Railed result.

The following remains unresolved:

* stable posterior dry-comb acquisition
* stable non-flat, non-railed waveform from posterior-left headband placement
* stable non-flat, non-railed waveform from posterior-right headband placement
* usable scalp-contact acquisition from the intended posterior Ch1/Ch2 montage

`Railed` or `Near Railed` states were treated as non-usable acquisition states, not as strong EEG. Feature-level analysis remains out of scope until a stable, non-flat, non-railed scalp-contact waveform is achieved.

Further posterior troubleshooting should avoid using flat electrode B unless it is re-checked or replaced.


## 7. Next troubleshooting plan

The next step is to test Ch2/N2P using the known-working flat electrode A.

Planned sequence:

1. Test Ch2 / N2P with white cable and flat electrode A at a forehead skin-contact position.
2. If Ch2 becomes Not Railed, record that Ch2/N2P is likely functional and flat electrode B is the main suspect.
3. If Ch2 remains Near Railed, test Ch2 / N2P with black cable and flat electrode A.
4. If Ch2 remains Near Railed with both cables using flat electrode A, inspect Ch2/N2P setting, board connection, or channel-specific configuration.
5. Do not return to two-channel posterior testing until Ch2 is checked with the known-working flat electrode.
6. Do not run eyes-open / eyes-closed alpha reactivity testing until stable acquisition is confirmed.

Success criterion for the next step:

```text
Ch2 / N2P shows a stable, non-flat, non-railed waveform using the known-working flat electrode A under forehead contact.
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
