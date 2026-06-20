# Cyton Board Map v0.1

## 1. Purpose

This document summarizes the basic connection map of the OpenBCI Cyton board before designing the first EEG montage.

The goal is to understand how electrodes, Cyton input pins, reference, BIAS, USB dongle, battery power, and software recording are connected.

## 2. Board components

| Component | Role | Current understanding |
|---|---|---|
| N1P–N8P | Active EEG input channel candidates | Electrodes placed on scalp measurement positions can be connected here. |
| SRB2 | Common reference candidate | Used as the reference point for EEG channel measurements. |
| BIAS | Bias / noise-reduction body connection | Not an active EEG channel. Used as a body connection for noise reduction. |
| USB dongle | Wireless communication | Receives data from Cyton and sends it to the computer. |
| Battery | Isolated power source | Cyton should be powered by battery during body-connected recording. |
| OpenBCI GUI | Real-time signal check and recording | Used for Session 10 connection and waveform test. |
| BrainFlow | Python-based data acquisition | Planned for later Python recording workflow. |

## 3. Candidate Hardware Connections

| Function | Candidate hardware |
|---|---|
| Active EEG input | Comb or flat electrodes connected to N1P–N8P |
| Reference | One earclip connected to SRB2 |
| BIAS |  Opposite earclip connected to Cyton BIAS pin. Exact physical pin position will be verified before connection. |
| Computer connection | USB dongle |
| Power | Lithium polymer battery |

## 4. Simple recording chain

```text
electrode
→ snap cable
→ Cyton N1P–N8P / SRB2 / BIAS
→ Cyton board
→ USB dongle
→ OpenBCI GUI
→ recorded file
→ Python analysis
```

## 5. My current understanding

- N1P–N8P are active EEG input channel candidates.
- SRB2 is a reference candidate for EEG channel measurement.
- BIAS is not an EEG measurement channel; it is used as a noise-reduction body connection.
- EEG channel values are measured relative to a reference electrode.
- The measurement-level reference is different from later feature-level ratios such as beta/alpha ratio.

## 6. Reference note

EEG channels are measured as voltage differences relative to a reference electrode.

For the first OpenBCI headband setup, the practical reference candidate is one earclip connected to SRB2. Other EEG reference strategies exist, such as linked ears, mastoid reference, Cz reference, and average reference, but these are not the initial priority for this project.

Initial plan:

- SRB2: one earclip reference
- BIAS: opposite earclip

## 7. Unclear points

- How does BIAS reduce common-mode noise in practice?
- How does the reference location affect the recorded EEG signal?
- For the first alpha reactivity test, should I use 2 active posterior channels or 3 active posterior channels?
- In the OpenBCI GUI, which hardware settings should be checked before recording, such as channel on/off, SRB2, BIAS, gain, and impedance?

