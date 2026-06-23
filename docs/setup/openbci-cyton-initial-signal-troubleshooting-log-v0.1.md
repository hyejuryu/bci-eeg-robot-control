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

| Attempt | Action                                                                | Observation                                                                                                                        | Interpretation                                                                                                                        | Status             |
| ------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| 01      | Board-only stream test                                                | Moving traces and accelerometer values were visible                                                                                | Cyton-to-GUI stream path worked; traces were not EEG                                                                                  | Confirmed          |
| 02      | Initial posterior headband placement with Ch1/Ch2                     | Ch1 and Ch2 remained railed / flat                                                                                                 | Usable scalp-contact acquisition was not achieved                                                                                     | Not resolved       |
| 03      | Unused channels handled as off / ignored                              | Ch3–Ch8 were no longer treated as relevant; Ch1/Ch2 still remained railed                                                          | Unused channels were not the main issue                                                                                               | Confirmed          |
| 04      | Hardware Settings checked                                             | Gain, input type, Bias Include, SRB2, and SRB1 states were observed                                                                | Initial settings did not show an obvious connection-level failure                                                                     | Confirmed          |
| 05      | Cyton pin / channel mapping checked                                   | Ch1/N1P, Ch2/N2P, SRB, and BIAS mapping were reviewed                                                                              | No obvious mapping mismatch was identified                                                                                            | Confirmed          |
| 06      | Ch1 comb electrode touch test                                         | Ch1 responded when the Ch1/black comb electrode was touched directly                                                               | Ch1 channel path was likely functional                                                                                                | Confirmed          |
| 07      | Ch2 comb electrode touch test                                         | Ch2 responded when the Ch2/white comb electrode was touched directly                                                               | Ch2 channel path was likely functional                                                                                                | Confirmed          |
| 08      | Comb electrode contact pressure changed                               | A waveform appeared once when the comb electrode was held with more stable contact, but the effect was not consistently reproduced | Electrode contact was likely involved, but this did not confirm a stable solution                                                     | Inconclusive       |
| 09      | Ch1-only forehead test using comb electrode                           | Ch1 showed a visible non-flat waveform but remained Near Railed                                                                    | Comb electrode forehead contact did not confirm stable acquisition                                                                    | Not resolved       |
| 10      | Ch1-only forehead test using flat electrode A and black cable         | Ch1 changed to Not Railed and remained stable for about 30 seconds                                                                 | Ch1/N1P can produce a stable non-railed signal under flat forehead contact                                                            | Confirmed          |
| 11      | Ch2-only forehead test using flat electrode B and white cable         | Ch2 remained Near Railed despite increased contact pressure                                                                        | Stable Ch2 acquisition was not confirmed under this electrode/cable combination                                                       | Not resolved       |
| 12      | Flat electrode B with white cable moved to Ch1/N1P                    | Ch1 still remained Near Railed, around 80%                                                                                         | The issue was not explained by Ch2/N2P input alone                                                                                    | Not resolved       |
| 13      | Ch1 baseline repeated with flat electrode A and black cable           | Ch1 again showed Not Railed behavior                                                                                               | The Ch1 + black cable + flat electrode A condition was reproducible                                                                   | Confirmed          |
| 14      | Flat electrode A tested with white cable on Ch1/N1P                   | Ch1 changed to Not Railed, with the GUI showing approximately 67%                                                                  | White cable was likely functional when paired with the working flat electrode                                                         | Confirmed          |
| 15      | Flat electrode B tested with black cable on Ch1/N1P                   | Ch1 remained Near Railed                                                                                                           | Flat electrode B or its snap/contact condition became the main suspect                                                                | Suspect identified |
| 16      | Ch2/N2P tested with white cable and flat electrode A                  | Ch2 changed to Not Railed under forehead contact                                                                                   | Ch2/N2P input and white cable were likely functional when paired with the working flat electrode                                      | Confirmed          |
| 17      | Ch1/N1P posterior retry using black cable and original comb electrode | Ch1 remained Near Railed around 85%, with high amplitude around 197 uVrms                                                          | Posterior comb placement did not produce usable acquisition; high amplitude was treated as contact/artifact-dominated rather than EEG | Not resolved       |
| 18      | Ch1/N1P posterior retry using black cable and a second comb electrode | Ch1 again remained Near Railed around 87%                                                                                          | The issue was not resolved by changing the comb electrode; posterior dry-comb scalp contact remained unresolved                       | Not resolved       |
| 19      | Ch1/N1P posterior retry with hair parted for direct comb contact      | Ch1 still did not become Not Railed                                                                                                | Hair-parting alone did not resolve posterior dry-comb contact instability                                                             | Not resolved       |
| 20     |  Ch1 forehead baseline repeated using flat electrode A and black cable | Ch1 showed visible Not Railed waveform | Known-good acquisition baseline was reproduced | Confirmed
## 6. Current interpretation

Session 10 troubleshooting separated the initial signal problem into three layers:

```text
connection / channel path
→ forehead flat-electrode contact
→ posterior dry-comb scalp contact
```

### 1. Connection-level failure became unlikely

The Cyton-to-GUI live streaming path was already confirmed before signal troubleshooting.

The following parts are likely functional:

* OpenBCI GUI launch
* Cyton-to-GUI live streaming path
* USB dongle / COM3 connection
* accelerometer stream

This reduced the likelihood that the main issue was GUI launch, COM port connection, dongle communication, or board-level streaming.

### 2. Ch1 and Ch2 channel paths were confirmed under forehead flat-electrode contact

Because the posterior comb setup remained railed, the test was simplified to forehead flat-electrode contact.

Under this easier skin-contact condition:

* Ch1 / N1P produced a Not Railed signal with flat electrode A.
* Ch2 / N2P also produced a Not Railed signal with flat electrode A.
* The black snap cable worked with flat electrode A.
* The white snap cable worked with flat electrode A.
* SRB / BIAS setup was functional at least under forehead flat-electrode contact conditions.

This reduced the likelihood that Ch1/N1P, Ch2/N2P, the black cable, the white cable, or the basic SRB/BIAS setup was the main cause of the earlier Near Railed results.

### 3. Flat electrode B was identified as a local suspect

The forehead flat-electrode swap tests suggested a local electrode/contact issue.

Flat electrode A produced Not Railed results with both black and white snap cables.

Flat electrode B remained Near Railed with both black and white snap cables on Ch1/N1P.

Therefore, the current suspect is:

```text
flat electrode B
or
flat electrode B snap/contact condition
```

This does not prove that flat electrode B is physically defective, but it was unreliable in the current troubleshooting session and should not be used as a known-good electrode without re-checking.

### 4. Posterior dry-comb acquisition remains unresolved

After the forehead flat-electrode tests confirmed that Ch1 and Ch2 can produce Not Railed signals under easier contact conditions, the setup returned to posterior comb testing.

The posterior retry remained Near Railed when:

* the original comb electrode was used
* a second comb electrode was used
* hair was parted to improve direct comb contact

Changing the comb electrode and parting the hair did not resolve the posterior Near Railed state.

This reduced the likelihood that the issue was caused by a single defective comb electrode and strengthened the interpretation that the main unresolved bottleneck is:

```text
posterior dry-comb scalp contact through hair
```

### 5. Current boundary

The following has been confirmed:

* connection-level setup works
* Ch1 / N1P works under forehead flat-electrode contact
* Ch2 / N2P works under forehead flat-electrode contact
* black and white snap cables work with flat electrode A
* flat electrode A is the current known-good flat electrode

The following remains unresolved:

* stable posterior dry-comb acquisition
* stable non-flat, non-railed waveform from posterior-left headband placement
* stable non-flat, non-railed waveform from posterior-right headband placement
* usable scalp-contact acquisition from the intended posterior Ch1/Ch2 montage

`Railed` or `Near Railed` states were treated as non-usable acquisition states, not as strong EEG.

Feature-level analysis remains out of scope until a stable, non-flat, non-railed scalp-contact waveform is achieved.

## 7. Next troubleshooting plan

The next troubleshooting should focus on improving or changing the posterior contact method.

Possible next steps:

1. Re-check SRB earclip and BIAS earclip contact before posterior testing.
2. Retry Ch1/N1P posterior comb contact only if cable strain can be minimized and the comb teeth can remain stable against the scalp without discomfort.
3. If posterior dry-comb contact remains Near Railed, consider contact-improvement methods:

   * more controlled hair separation
   * better cable strain relief
   * slightly adjusted posterior headband position
   * conductive gel/paste if appropriate for the electrode/contact setup
   * replacement or additional electrodes if a hardware/contact issue is suspected
4. Keep flat electrode B out of the main setup unless it is re-checked or replaced.
5. Do not run eyes-open / eyes-closed alpha reactivity testing until stable posterior acquisition is confirmed.

Next success criterion:

```text
At least one posterior comb channel shows a stable, non-flat, non-railed waveform under normal headband placement.
```

## 8. Evidence files

- [`posterior-contact-nonflat-still-railed.png`](../../figures/session-10/troubleshooting/posterior-contact-nonflat-still-railed.png)
  - Initial posterior headband placement showed visible but highly railed Ch1/Ch2 activity.

- [`ch1-forehead-comb-near-railed.png`](../../figures/session-10/troubleshooting/ch1-forehead-comb-near-railed.png)
  - Ch1 forehead contact using a comb electrode showed a visible waveform but remained Near Railed.

- [`ch1-forehead-flat-not-railed.png`](../../figures/session-10/troubleshooting/ch1-forehead-flat-not-railed.png)
  - Ch1 forehead contact using flat electrode A changed to Not Railed and was stable for about 30 seconds.

- [`ch2-forehead-flat-near-railed.png`](../../figures/session-10/troubleshooting/ch2-forehead-flat-near-railed.png)
  - Ch2 forehead contact using flat electrode B remained Near Railed, which later supported the electrode B suspect interpretation.

No valid EEG feature dataset was produced in this troubleshooting stage.

## 9. Current troubleshooting status

Current status:

```text
Connection-level setup: confirmed
Ch1 forehead flat-electrode acquisition: confirmed with flat electrode A
Ch2 forehead flat-electrode acquisition: confirmed with flat electrode A
Black snap cable: likely functional
White snap cable: likely functional
Flat electrode A: working
Flat electrode B: suspect / unreliable
Original comb electrode: did not resolve posterior Near Railed state
Second comb electrode: did not resolve posterior Near Railed state
Hair-parted posterior comb retry: not resolved
Stable posterior dry-comb acquisition: not yet achieved
Main unresolved bottleneck: posterior dry-comb scalp contact through hair
EEG feature interpretation: not performed
