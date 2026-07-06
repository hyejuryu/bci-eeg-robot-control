\# OpenBCI Posterior Contact-Assisted Acquisition Log v0.1



\## 1. Document metadata



\* Created in: Session 12

\* Related sessions: Session 10–12

\* Version: v0.1

\* Status: prepared before Session 12 test

\* Scope: posterior contact-assisted acquisition testing using Ten20 conductive paste / gel and OpenBCI gold cup electrodes

\* Update rule: add entries for documented posterior contact-assisted setup attempts only



\## 2. Purpose and scope



This document records Session 12 posterior contact-assisted acquisition testing.



Session 10 confirmed the Cyton-to-GUI live streaming path, but the posterior dry-comb setup did not produce stable posterior scalp-contact acquisition under the current hair/contact conditions.



Session 12 tests a revised contact strategy using Ten20 conductive paste / gel and OpenBCI gold cup electrodes.



This document covers setup attempts, channel mapping, SRB / BIAS placement, GUI contact observations, and the decision on whether to proceed to short BrainFlow recording.



Feature-level EEG interpretation, alpha reactivity analysis, focus estimation, and robot-control testing are out of scope.



\## 3. Starting point



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



\## 4. Planned setup



\### 4.1 Equipment



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



\### 4.2 Reference and BIAS condition



Initial Session 12 reference / BIAS plan:



| Function             | Planned connection                           |

| -------------------- | -------------------------------------------- |

| SRB / SRB2 reference | left earclip, unless changed and documented  |

| BIAS                 | right earclip, unless changed and documented |



If SRB / BIAS placement is changed, record the change in the attempt table.



\### 4.3 Channel strategy



Start with a small number of channels.



Planned initial channel mapping:



| Channel   | Planned position                         | Electrode / contact method              | Status                              |

| --------- | ---------------------------------------- | --------------------------------------- | ----------------------------------- |

| Ch1 / N1P | approximate posterior candidate          | gold cup + Ten20 conductive paste / gel | first test channel                  |

| Ch2 / N2P | optional approximate posterior candidate | gold cup + Ten20 conductive paste / gel | add only if Ch1 condition is usable |

| Ch3–Ch8   | unused                                   | -                                       | off or ignored                      |



Electrode positions should be recorded as approximate posterior positions unless actual 10–20 locations are measured.



\### 4.4 Pre-run conditions



Before contact-assisted posterior testing:



\* Cyton is battery powered.

\* Arduino / robot hardware is disconnected.

\* OpenBCI GUI is used first for contact sanity check.

\* BrainFlow is used only after the GUI is closed and the COM port is free.

\* Ten20 conductive paste / gel and gold cup electrodes are available.

\* SRB / BIAS placement is recorded.

\* Approximate posterior electrode position is recorded.



\## 5. Decision criteria



Proceed to short BrainFlow recording only if:



\- at least one intended posterior channel is not persistently Railed or Near Railed

\- the waveform is not flat

\- contact appears stable enough for a short recording

\- SRB / BIAS placement and electrode contact method are documented



Do not proceed if posterior contact remains unstable or the setup cannot be documented clearly.



\## 6. Attempt log



| Attempt | Date/time | Action / setup | Observation | Interpretation | Status | Next decision |

| ------- | --------- | -------------- | ----------- | -------------- | ------ | ------------- |

| S12-A01 | TBD       | TBD            | TBD         | TBD            | TBD    | TBD           |

| S12-A02 | TBD       | TBD            | TBD         | TBD            | TBD    | TBD           |

| S12-A03 | TBD       | TBD            | TBD         | TBD            | TBD    | TBD           |



\## 7. BrainFlow recording decision



BrainFlow recording performed:



```text

TBD

```



Reason:



```text

TBD

```



If BrainFlow recording is performed, record:



\* script name

\* serial port

\* recording duration

\* raw file path

\* metadata file path

\* readback summary path

\* original shape

\* restored shape

\* sample-count plausibility result



If BrainFlow recording is not performed, record the reason.



\## 8. Final decision and boundary



Session 12 final decision:



```text

TBD

```



Use one of the following decision categories:



```text

stable enough for short posterior BrainFlow acquisition

not stable enough for posterior BrainFlow acquisition

needs further contact adjustment before acquisition

test interrupted or incomplete

```



Interpretation boundary:



This log supports decisions about posterior contact-assisted acquisition readiness only.



It does not validate alpha reactivity, EEG feature interpretation, focus estimation, or robot-control readiness.



