# OpenBCI Posterior Contact-Assisted Acquisition Log v0.1



## 1. Document metadata



* Created in: Session 12
* Related sessions: Session 10–12
* Version: v0.1
* Status: prepared before Session 12 test
* Scope: posterior contact-assisted acquisition testing using Ten20 conductive paste / gel and OpenBCI gold cup electrodes
* Update rule: add entries for documented posterior contact-assisted setup attempts only



## 2. Purpose and scope



This document records Session 12 posterior contact-assisted acquisition testing.



Session 10 confirmed the Cyton-to-GUI live streaming path, but the posterior dry-comb setup did not produce stable posterior scalp-contact acquisition under the current hair/contact conditions.



Session 12 tests a revised contact strategy using Ten20 conductive paste / gel and OpenBCI gold cup electrodes.



This document covers setup attempts, channel mapping, SRB / BIAS placement, GUI contact observations, and the decision on whether to proceed to short BrainFlow recording.



Feature-level EEG interpretation, alpha reactivity analysis, focus estimation, and robot-control testing are out of scope.



## 3. Starting point



Current starting point before Session 12:



```text

Session 10:

Cyton-to-GUI acquisition path confirmed

Ch1 / Ch2 functional under easier forehead flat-electrode contact

posterior dry-comb scalp contact through hair unresolved



Session 11:

BrainFlow acquisition, raw saving, metadata logging, and readback verification confirmed

actual posterior acquisition quality not tested



Session 12:

test contact-assisted posterior setup before feature-level interpretation

```



## 4. Planned setup



### 4.1 Equipment



Planned equipment:



| Item                         | Planned use                                |

| ---------------------------- | ------------------------------------------ |

| OpenBCI Cyton                | EEG acquisition board                      |

| USB dongle                   | Cyton-to-computer communication            |

| LiPo battery                 | Cyton power source                         |

| Ten20 conductive paste / gel | contact-assisted posterior electrode setup |

| OpenBCI gold cup electrodes  | posterior active electrode candidates      |

| Earclip electrode            | SRB2 reference candidate                   |

| Earclip electrode            | BIAS candidate                             |

| Windows 11 laptop            | OpenBCI GUI and/or BrainFlow acquisition   |



Required isolation condition:



```text

Cyton battery-powered EEG recording only

No Arduino / robot hardware connected during EEG recording

```



### 4.2 Reference and BIAS condition



Initial Session 12 reference / BIAS plan:



| Function             | Planned connection                           |

| -------------------- | -------------------------------------------- |

| SRB / SRB2 reference | left earclip, unless changed and documented  |

| BIAS                 | right earclip, unless changed and documented |



If SRB / BIAS placement is changed, record the change in the attempt table.



### 4.3 Channel strategy



Start with a small number of channels.



Planned initial channel mapping:



| Channel   | Planned position                         | Electrode / contact method              | Status                              |

| --------- | ---------------------------------------- | --------------------------------------- | ----------------------------------- |

| Ch1 / N1P | approximate posterior candidate          | gold cup + Ten20 conductive paste / gel | first test channel                  |

| Ch2 / N2P | optional approximate posterior candidate | gold cup + Ten20 conductive paste / gel | add only if Ch1 condition is usable |

| Ch3–Ch8   | unused                                   | -                                       | off or ignored                      |



Electrode positions should be recorded as approximate posterior positions unless actual 10–20 locations are measured.



### 4.4 Pre-run conditions



Before contact-assisted posterior testing:



* Cyton is battery powered.
* Arduino / robot hardware is disconnected.
* OpenBCI GUI is used first for contact sanity check.
* BrainFlow is used only after the GUI is closed and the COM port is free.
* Ten20 conductive paste / gel and gold cup electrodes are available.
* SRB / BIAS placement is recorded.
* Approximate posterior electrode position is recorded.



## 5. Decision criteria



Proceed to short BrainFlow recording only if:



- at least one intended posterior channel is not persistently Railed or Near Railed

- the waveform is not flat

- contact appears stable enough for a short recording

- SRB / BIAS placement and electrode contact method are documented



Do not proceed if posterior contact remains unstable or the setup cannot be documented clearly.



## 6. Attempt log

| Attempt | Date/time | Action / setup | Observation | Interpretation | Status | Next decision |
|---|---|---|---|---|---|---|
| S12-A01 | 2026-07-06 | Ch1 / N1P, black gold cup electrode, Ten20 conductive paste / gel, approximate posterior candidate, SRB left earclip, BIAS right earclip. | Ch1 showed a visible non-flat waveform but remained Near Railed. The displayed state was Near Railed 83.08% with approximately 7.79 uVrms. Ch2–Ch8 were off or ignored. | The first posterior contact-assisted attempt did not establish usable contact. This does not rule out gold cup + Ten20, but the initial placement/contact condition was not sufficient for recording. | Not resolved. | Reapply Ten20, improve hair separation, reduce cable strain, and repeat Ch1 posterior contact-assisted attempt. |
| S12-A02 | 2026-07-06 | Ch1 / N1P, black gold cup electrode, Ten20 reapplied after wiping excess paste, approximate posterior candidate, improved hair separation, SRB left earclip, BIAS right earclip. | Ch1 changed to Not Railed during the GUI check. The displayed state was Not Railed 66.88% with approximately 56.6 uVrms. A visible non-flat waveform was present. The electrode was not manually held during the screenshot. Ch2–Ch8 were off or ignored. | Improved hair separation and Ten20 reapplication supported better posterior contact than S12-A01. This supports continuing posterior contact-assisted testing. This does not establish EEG feature quality or alpha-readiness. | Improved contact condition; not final recording evidence. | Check whether Ch1 remains Not Railed without manual support. If stable, proceed toward additional contact checks. |
| S12-A03 | 2026-07-06 | Ch1 / N1P, black gold cup electrode, Ten20 conductive paste / gel, approximate posterior candidate, hair separated, tape-assisted stabilization if used, SRB left earclip, BIAS right earclip. | Ch1 returned to Near Railed during the GUI check. The displayed state was Near Railed 78.64% with approximately 31.5 uVrms. A visible non-flat waveform was present. No BrainFlow recording was performed. | Compared with S12-A02, the contact-assisted posterior setup was not repeatably stable under the current posterior placement and fixation condition. This does not rule out gold cup + Ten20, but it does not support proceeding to BrainFlow recording from this attempt. | Not resolved; repeatability issue remains. | Run a controlled forehead gold cup + Ten20 check to separate posterior hair/contact issues from gold cup/Ten20 handling issues. |
| S12-A04 | 2026-07-06 | Ch1 / N1P, black gold cup electrode, Ten20 conductive paste / gel, forehead control position, tape-assisted stabilization if used, SRB left earclip, BIAS right earclip. | Ch1 remained Near Railed during the GUI forehead control check. The displayed state was Near Railed 86.19% with approximately 29.8 uVrms. A visible non-flat waveform was present. No BrainFlow recording was performed. | The Near Railed result under forehead control suggests that the current issue is not limited to posterior hair contact. Gold cup + Ten20 handling, active electrode contact, fixation, cable/lead condition, or SRB/BIAS contact remains unresolved. | Not resolved. | Run a known-good Ch1 forehead flat electrode A control if continuing; otherwise stop hardware testing and clean up. |
| S12-A05 | 2026-07-06 | Ch1 / N1P, black snap cable, flat electrode A, forehead contact, SRB left earclip, BIAS right earclip. | The known-good Ch1 forehead flat electrode A baseline was attempted, but Ch1 displayed Railed 100% with 0.00 uVrms. Ch2–Ch8 were off or ignored. COM3 was visible, Cyton blue LED was on, and accelerometer values were visible. No BrainFlow recording was performed. | This did not reproduce the Session 10 known-good forehead baseline. Because this occurred after multiple paste/contact attempts, the result should be interpreted as a current-session control failure rather than evidence that the Session 10 baseline was invalid. Possible remaining issues include SRB/BIAS contact, GUI/channel state, cable/contact condition, or board/session state. | Control not reproduced; session state needs reset. | Stop hardware testing, clean up, and restart board/dongle/GUI in a later session before further electrode troubleshooting. |

### Evidence files

- [`2026-07-06_s12_attempt-01_ch1-n1p_black-goldcup-ten20_posterior_near-railed.png`](../../figures/session-12/contact-assisted/2026-07-06_s12_attempt-01_ch1-n1p_black-goldcup-ten20_posterior_near-railed.png)
- [`2026-07-06_s12_attempt-02_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_not-railed.png`](../../figures/session-12/contact-assisted/2026-07-06_s12_attempt-02_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_not-railed.png)
- [`2026-07-06_s12_attempt-03_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_near-railed.png`](../../figures/session-12/contact-assisted/2026-07-06_s12_attempt-03_ch1-n1p_black-goldcup-ten20_posterior-hair-parted_near-railed.png)
- [`2026-07-06_s12_attempt-04_ch1-n1p_black-goldcup-ten20_forehead-control_near-railed.png`](../../figures/session-12/contact-assisted/2026-07-06_s12_attempt-04_ch1-n1p_black-goldcup-ten20_forehead-control_near-railed.png)
- [`2026-07-06_s12_attempt-05_ch1-n1p_black-flatA_forehead-baseline_railed.png`](../../figures/session-12/contact-assisted/2026-07-06_s12_attempt-05_ch1-n1p_black-flatA_forehead-baseline_railed.png)

## 7. BrainFlow recording decision

BrainFlow recording performed:

```text
No
````

Reason:

```text
No Session 12 GUI attempt established a stable and repeatable posterior contact-assisted condition. S12-A02 showed temporary improvement to Not Railed, but S12-A03 returned to Near Railed. The forehead gold cup control in S12-A04 also remained Near Railed, and the known-good flat electrode A forehead control in S12-A05 was not reproduced. The current session state therefore did not meet the decision criteria for short BrainFlow recording.
```

## 8. Final decision and boundary

Session 12 final decision:

```text
test interrupted or incomplete
```

Session 12 interim conclusion:

```text
Posterior contact-assisted acquisition was tested using Ten20 conductive paste / gel and a gold cup electrode. The setup showed possible improvement in S12-A02 after better hair separation and Ten20 reapplication, but stable and repeatable posterior contact was not established. The forehead gold cup control also remained Near Railed, and the known-good flat electrode A forehead baseline was not reproduced at the end of the session. The session should be treated as incomplete hardware troubleshooting rather than acquisition-ready validation.
```

Next decision:

```text
Stop hardware testing for the current session. In the next session, restart the board/dongle/GUI state and first attempt to reproduce the known-good Ch1 forehead flat electrode A baseline before continuing gold cup + Ten20 posterior testing.
```

Interpretation boundary:

This log supports decisions about posterior contact-assisted acquisition readiness only.

It does not validate alpha reactivity, EEG feature interpretation, focus estimation, or robot-control readiness.


## 9. Related continuation log

Further Session 12 continuation troubleshooting after S12-A05 is documented separately in:

- [`openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md`](openbci-cyton-acquisition-baseline-troubleshooting-log-v0.1.md)

Reason:

After the posterior contact-assisted attempts, the known-good forehead baseline was not reproduced. The continuation therefore shifted from posterior contact-assisted acquisition testing to acquisition baseline / reference troubleshooting.