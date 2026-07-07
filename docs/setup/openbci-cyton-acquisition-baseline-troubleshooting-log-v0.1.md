\# OpenBCI Cyton acquisition baseline troubleshooting log v0.1



\## 1. Document metadata



\- Session: 12 continuation

\- Date: 2026-07-07

\- Related sessions: Session 10–12

\- Version: v0.1

\- Scope: forehead baseline recovery, channel/path checks, SRB/BIAS assembly checks, and GUI-level acquisition stability

\- Out of scope: posterior acquisition validation, BrainFlow recording, EEG feature interpretation, alpha reactivity, focus estimation, robot control



\## 2. Purpose and scope



This document records the Session 12 continuation troubleshooting after the initial posterior contact-assisted acquisition attempts.



The initial Session 12 posterior contact-assisted test did not establish stable posterior acquisition. At the end of that block, the known-good forehead flat-electrode baseline was also not reproduced. Therefore, the continuation shifted from posterior contact testing to acquisition baseline troubleshooting.



This document focuses on whether a stable forehead acquisition baseline could be recovered before returning to posterior testing.



\## 3. Starting point



Before this continuation:



```text

Session 10:

\- GUI / Cyton / COM3 live stream was confirmed.

\- Ch1 and Ch2 produced Not Railed forehead flat-electrode signals under simplified diagnostic conditions.

\- Posterior dry-comb acquisition remained unresolved.



Session 12 initial block:

\- Posterior gold cup + Ten20 attempts were not repeatably stable.

\- Forehead gold cup control remained Near Railed.

\- Known-good Ch1 forehead flat-electrode baseline was not reproduced at the end of the block.

```



Continuation decision:



```text

Restart from full reset.

Recover a stable forehead acquisition baseline before returning to posterior acquisition testing.

```



\## 4. Attempt log



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



\## 5. Evidence files



Evidence files are stored in:



```text

figures/session-12/contact-assisted/

```



Relevant 2026-07-07 files:



```text

2026-07-07\_s12\_check-b00\_full-reset\_gui-com3-live-stream\_board-only-floating-inputs.png

2026-07-07\_s12\_attempt-b01\_ch1-n1p\_black-flatA\_forehead-baseline\_railed.png

2026-07-07\_s12\_attempt-b02\_ch1-n1p\_black-flatA\_forehead-baseline-contact-adjusted\_railed.png

2026-07-07\_s12\_attempt-b03\_ch1-n1p\_black-flatA\_touch-test\_no-response.png

2026-07-07\_s12\_attempt-b04\_ch1-n1p\_black-flatC\_touch-test\_no-forehead\_no-response.png

2026-07-07\_s12\_attempt-b05\_ch1-n1p\_white-flatC\_touch-test\_no-forehead\_no-response.png

2026-07-07\_s12\_attempt-b06\_ch1-n1p\_white-flatD\_touch-test\_no-forehead\_no-response.png

2026-07-07\_s12\_attempt-b07\_ch1-n1p\_white-flatD\_touch-test\_srb-bias-reseated\_no-response.png

2026-07-07\_s12\_attempt-b08\_ch2-n2p\_white-flatD\_touch-test\_channel-switched\_global-transient-inconclusive.png

2026-07-07\_s12\_attempt-b09\_ch2-n2p\_white-flatD\_forehead-baseline\_near-railed.png

2026-07-07\_s12\_attempt-b10\_ch2-n2p\_white-flatD\_forehead-baseline-contact-adjusted\_near-railed.png

2026-07-07\_s12\_attempt-b11\_ch2-n2p\_white-flatD\_left-forehead-contact-position\_not-railed.png

2026-07-07\_s12\_attempt-b12\_ch2-n2p\_white-flatD\_left-forehead-contact-position-repeat\_near-railed.png

2026-07-07\_s12\_attempt-b13\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB-swapped\_not-railed.png

2026-07-07\_s12\_attempt-b14a\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB\_stream-restart\_initial-not-railed.png

2026-07-07\_s12\_attempt-b14b\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB\_stream-restart\_drift-to-near-railed.png

2026-07-07\_s12\_attempt-b15a\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB\_contact-repeat\_initial-not-railed.png

2026-07-07\_s12\_attempt-b15b\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB\_contact-repeat\_drift-to-near-railed.png

2026-07-07\_s12\_attempt-b15c\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB\_contact-repeat\_drift-to-railed.png

2026-07-07\_s12\_attempt-b16\_ch2-n2p\_white-flatD\_left-forehead-baseline\_srb-assemblyB\_bias-assembly-swapped\_near-railed-plateau.png

2026-07-07\_s12\_attempt-b17\_ch2-n2p\_black-goldcup-ten20\_left-forehead-control\_srbB-biasB\_railed.png

2026-07-07\_s12\_check-b18a\_no-active-electrode\_srbB-biasB\_ch3-floating-control\_initial-near-railed.png

2026-07-07\_s12\_check-b18b\_no-active-electrode\_srbB-biasB\_ch3-floating-control\_drift-to-railed.png

```



\## 6. Current interpretation



The continuation did not recover a stable forehead acquisition baseline.



Main observations:



\- Ch1 forehead baseline was not recovered.

\- Ch2 showed partial responsiveness but did not provide stable baseline acquisition.

\- Contact position affected the Ch2 result, but the improvement was not repeatably stable.

\- SRB assembly B produced temporary improvement, but the condition drifted over time.

\- BIAS assembly swap did not establish a stable Not Railed baseline.

\- Active gold cup + Ten20 forehead control did not establish usable Ch2 acquisition.

\- No-active-electrode control showed unintended channel activity under the current GUI/session state.



Current interpretation:



```text

The unresolved bottleneck is acquisition/contact/reference stability.

The current evidence is insufficient for returning to posterior acquisition testing.

```



\## 7. Current decision



Hardware testing was stopped after B18.



No stable acquisition baseline was established in this continuation block.



Next work should begin with a narrower acquisition-stability test using one controlled active channel, one reference condition, one BIAS condition, and a fixed observation window.



Possible next-session direction:



\- Use SRB assembly B as the initial reference candidate.

\- Use BIAS assembly B as the initial BIAS candidate.

\- Define one active channel and one active electrode/contact method before starting.

\- Observe for a fixed stability window before treating the condition as usable.

\- Record time-dependent drift explicitly if the Railed / Near Railed status changes during observation.

