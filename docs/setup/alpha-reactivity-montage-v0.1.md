# Alpha Reactivity Montage v0.1

## Document metadata

- Created in: Session 09
- Related sessions: Session 09–13
- Status: candidate montage; not yet validated for alpha reactivity recording

## 1. Purpose

This document defines the first candidate electrode montage for a future OpenBCI eyes-open / eyes-closed alpha reactivity test.

The goal is not full-brain EEG recording.  
The goal is to prepare a simple headband-based setup for checking whether posterior alpha power changes between defined baseline conditions.

## 2. Target experiment

Planned conditions:

- Eyes open baseline
- Eyes closed baseline

Main analysis target:

```text
eyes open
vs.
eyes closed
→ posterior alpha power comparison
```

## 3. Montage type

This is a headband-based approximate posterior montage.

Because this setup uses the OpenBCI EEG Headband Kit, electrode locations are treated as approximate headband positions rather than precisely measured scalp coordinates.

## 4. Candidate channel mapping

| Cyton channel | Candidate position | Electrode type | Purpose |
|---|---|---|---|
| Ch1 / N1P | Posterior-left headband position | Comb Ag/AgCl electrode | Posterior alpha candidate |
| Ch2 / N2P | Posterior-right headband position | Comb Ag/AgCl electrode | Posterior alpha candidate |
| Ch3 / N3P | Posterior-midline candidate, if stable | Comb Ag/AgCl electrode | Optional posterior alpha candidate |
| Ch4–Ch8 | Unused in first test | - | Reserved for later use |

## 5. Reference and BIAS plan

| Function | Candidate connection |
|---|---|
| Reference | One earclip connected to SRB2 |
| BIAS | Opposite earclip connected to bottom BIAS |

Initial plan:

- SRB2: one earclip reference
- BIAS: opposite earclip
- Active channels: posterior headband electrodes connected to N1P–N3P candidates

## 6. Electrode choice rationale

- Comb Ag/AgCl electrodes are selected for posterior headband positions because these sites are hair-covered.
- Flat Ag/AgCl electrodes are not part of the initial posterior montage, but may be used later for forehead or other hairless positions.
- Earclip electrodes are selected for the initial SRB2 reference and BIAS candidates.
  
## 7. Interpretation boundary

This setup should be interpreted as an approximate posterior headband setup.

The result should be described as coming from posterior-left, posterior-right, or posterior-midline headband positions, not from precisely measured scalp coordinates.

## 8. Main risks

- Unstable electrode contact through hair
- Headband movement
- Unclear exact electrode localization
- Neck, jaw, or facial muscle artifact
- Cable movement artifact
- Poor earclip contact affecting reference or BIAS stability

## 9. Current status after Session 10

The initial posterior dry-comb headband montage was tested during Session 10 as part of the first Cyton-to-GUI acquisition sanity check.

The Cyton-to-GUI acquisition path was confirmed, but the posterior dry-comb setup did not produce stable, non-flat, non-railed acquisition under the current hair/contact conditions.

Current interpretation:

```text
initial posterior dry-comb montage
→ not validated for alpha reactivity testing
→ posterior contact-assisted follow-up pending
```

This montage should remain a candidate plan only. It should not be used for eyes-open / eyes-closed alpha reactivity testing until stable posterior acquisition is confirmed.

The document should be revised more substantially only after a posterior contact-assisted setup, such as Ten20 paste and/or OpenBCI gold cup electrodes, is actually tested or adopted.

