# Milestone 01 Report: Session 01–03

## 1. Overview

This report summarizes the first milestone of the EEG-BCI robot control project.

The first three sessions focused on building the conceptual foundation required before moving into signal processing, public EEG dataset analysis, OpenBCI setup, and Arduino-based robot control.

At this stage, the goal was not to build a working BCI system immediately.  
The goal was to understand what kind of signal EEG actually provides, what can and cannot be inferred from it, and how raw brain signals may eventually be transformed into interpretable features and simple control commands.

## 2. Period Covered

| Item | Description |
|---|---|
| Milestone | Milestone 01 |
| Sessions covered | Session 01–03 |
| Period | 2026.03.28 – 2026.04.26 |
| Current phase | Conceptual foundation and project framing |
| Next phase | Python environment setup and public EEG dataset analysis |

## 3. Sessions Covered

| Session | Date | Main Focus | Main Output |
|---|---|---|---|
| Session 01 | 2026.03.28–29 | Overall project structure, EEG-BCI-robot pipeline, basic brain structure and cognitive function | Conceptual pipeline draft |
| Session 02 | 2026.04.18–19 | EEG generation, neural signaling, postsynaptic potentials, ERP, attention and plasticity | EEG generation and feature bridge notes |
| Session 03 | 2026.04.25–26 | EEG waveform components, frequency bands, alpha/beta/theta/gamma meanings, focus feature candidates | EEG frequency band and focus feature selection notes |

## 4. Project Direction After Milestone 01

The project is currently framed as a simple EEG-based BCI robot control pipeline.

The minimal structure is:

```text
brain state change
→ EEG acquisition
→ preprocessing / noise reduction
→ feature extraction
→ threshold-based decision
→ control command generation
→ robot actuation
```

The key understanding from this milestone is that BCI should not be treated as a direct mind-reading system.

A more realistic interpretation is:

```text
indirect brain signal
→ measurable signal feature
→ decision rule
→ control command
```

Therefore, the project should begin with modest and interpretable goals:

1. Record or obtain EEG data.
2. Understand the raw signal structure.
3. Apply basic preprocessing.
4. Extract simple and interpretable features.
5. Compare features across defined conditions.
6. Design a threshold rule only after observing feature distributions.
7. Connect the decision output to Arduino-based robot control.

## 5. Key Conceptual Outcomes

### 5.1 EEG is an indirect population-level signal

EEG does not measure individual thoughts or the firing of a single neuron.

The scalp EEG signal mainly reflects the summed electrical activity of large populations of cortical neurons, especially synchronized postsynaptic potentials from pyramidal cells.

This means EEG should be understood as:

- indirect
- noisy
- low spatial resolution
- population-level
- sensitive to artifacts
- strongly dependent on experimental conditions

This understanding is important because it prevents overinterpretation.

In this project, EEG should not be described as directly measuring “focus,” “intention,” or “cognition.”  
Instead, it should be treated as a signal from which measurable features may be extracted.

### 5.2 Raw EEG is not a control signal

Raw EEG cannot directly control a robot.

It must first pass through several stages:

```text
raw EEG
→ preprocessing
→ feature extraction
→ condition comparison
→ threshold decision
→ control command
```

This means the main technical problem is not simply acquiring EEG.  
The more important problem is deciding which features are reliable enough to support control.

### 5.3 Frequency bands and rhythms must be distinguished

One important understanding from Session 03 is that a frequency band and a rhythm are not the same thing.

For example, observing activity in the 8–13 Hz range does not automatically mean that a meaningful alpha rhythm is present.

A rhythm should be interpreted by considering:

- frequency
- amplitude
- scalp distribution
- repetition
- duration
- state dependency
- reactivity
- artifacts

This distinction is important for later analysis.  
The project should avoid interpreting EEG bands in a simplistic way, such as:

```text
alpha = relaxation
beta = concentration
gamma = high cognition
```

Instead, each feature should be interpreted only within a defined experimental context.

### 5.4 Alpha reactivity is a suitable first sanity check

Alpha activity is currently the most realistic starting point for early EEG validation.

Before attempting focus-based control, the project should first check whether basic alpha reactivity can be observed.

A simple initial comparison would be:

```text
eyes closed
vs.
eyes open
```

Expected pattern:

```text
eyes closed  → posterior alpha activity increases
eyes open    → posterior alpha activity decreases or becomes suppressed
```

This does not prove that the participant is relaxed or focused.  
Rather, it helps confirm that the EEG setup is capturing a meaningful physiological state change.

Therefore, alpha reactivity should be used as an early data quality and state reactivity check.

### 5.5 Focus should be operationally defined

“Focus” is not directly measurable.

For this project, focus should be treated as a task condition rather than a directly observed mental state.

Possible task conditions include:

```text
rest
eyes open
eyes closed
mental arithmetic
focused visual task
```

A better research question is not:

```text
Can I detect focus?
```

A better question is:

```text
Can I find a feature that changes reliably between a defined baseline condition and a defined task condition?
```

This framing is important because it keeps the experiment measurable and avoids vague psychological interpretation.

### 5.6 Candidate features after Milestone 01

Based on the first three sessions, the initial feature candidates are:

| Feature | Current status | Reason |
|---|---|---|
| Posterior alpha power | Strong candidate | Useful for eyes-closed / eyes-open comparison |
| Alpha suppression | Strong candidate | Useful for state reactivity and task engagement |
| Low beta power | Candidate | May be related to task engagement or problem solving |
| Beta/alpha ratio | Candidate | May be useful after baseline comparison |
| Gamma / 40 Hz activity | Deferred | Too vulnerable to muscle artifacts and noise at this stage |
| ERP / P300 | Later candidate | Requires more structured stimulus-based experimental design |

The current priority should be:

```text
alpha reactivity
→ alpha suppression
→ low beta power
→ beta/alpha ratio
```

Gamma should not be used as an initial control feature.

### 5.7 Thresholds should come after feature distribution analysis

A simple BCI control rule may eventually look like this:

```python
if beta_power > threshold:
    send_command_to_robot()
```

However, the threshold should not be chosen only from theory.

Before setting a threshold, the project needs to inspect:

- baseline feature distribution
- task feature distribution
- overlap between conditions
- trial-to-trial variability
- false trigger rate
- latency caused by window length
- stability across sessions

Therefore, threshold design should be treated as the result of signal analysis, not the starting point of the system.

## 6. Decisions Made After Milestone 01

After reviewing Sessions 01–03, the following decisions were made.

### 6.1 Initial experiment direction

The project will begin with simple condition comparison rather than direct robot control.

Initial priority:

```text
public EEG data analysis
→ eyes open / eyes closed comparison
→ alpha reactivity check
→ alpha and beta power visualization
→ baseline-normalized feature comparison
```

### 6.2 Focus-state BCI direction

Focus-state BCI will not be defined as direct measurement of concentration.

Instead, it will be defined as a comparison between baseline and task conditions.

Possible future task conditions:

- rest
- focus task
- mental arithmetic
- visual attention task

Possible behavioral measures:

- task accuracy
- reaction time
- task difficulty
- trial duration
- self-reported task engagement, if needed

### 6.3 Robot control direction

Robot control will be postponed until basic signal analysis is stable.

The expected sequence is:

```text
offline EEG analysis
→ feature distribution check
→ threshold rule design
→ simulated control decision
→ Arduino serial command
→ servo / gripper actuation
```

This order reduces the risk of building an impressive but scientifically meaningless demo.

## 7. Outputs Produced

### Session Notes

- Session 01 study note
- Session 02 study note
- Session 03 study note

### Concept Documents

- `session-01-core-brain-function-structure.md`
- `session-02-core-eeg-generation-and-neural-signaling.md`
- `session-02-eeg-components-erp-and-feature-bridge.md`
- `session-03-eeg-core-structure.md`
- `session-03-eeg-frequency-bands-and-rhythms.md`
- `session-03-focus-state-feature-list-and-selection-criteria.md`

### Figures

- EEG-BCI-robot conceptual pipeline figure

### Blog Output

The first public-facing English blog post was published on Medium:

- `EEG Does Not Read the Brain: Why Features Matter in BCI`

The Korean companion note is archived in GitHub.

## 8. Open Questions

The following questions remain open after Milestone 01.

### 8.1 EEG interpretation

- How far can scalp EEG features be connected to underlying neural mechanisms?
- How should the project avoid overinterpreting EEG frequency bands?
- What level of explanation is appropriate for a beginner-level BCI project?

### 8.2 Feature selection

- Is alpha suppression more stable than low beta power for early task comparison?
- Should beta/alpha ratio be used only after inspecting individual feature behavior?
- How should feature values be normalized across sessions and individuals?

### 8.3 Experimental design

- Which public EEG dataset is most suitable for initial analysis?
- Should the first experiment prioritize eyes-open / eyes-closed conditions?
- When should mental arithmetic or focused visual tasks be introduced?
- What trial length is appropriate for stable power estimation?

### 8.4 Control design

- How should window length affect latency and stability?
- How much false triggering is acceptable for a simple demo?
- Should threshold rules be fixed, adaptive, or baseline-normalized?

## 9. Risks Identified

| Risk | Description | Current response |
|---|---|---|
| Overinterpretation | Treating EEG as direct measurement of thought or focus | Use operational definitions and condition comparisons |
| Noisy data | Eye movement, muscle activity, electrode issues, environmental noise | Study artifacts and preprocessing before control |
| Premature robot demo | Building control before feature stability is confirmed | Postpone hardware control until feature analysis is stable |
| Unstable threshold | Choosing thresholds from theory rather than data | Inspect feature distributions first |
| Gamma misinterpretation | Treating high-frequency activity as cognition without artifact control | Defer gamma analysis |

## 10. Next Actions

The next block should focus on moving from conceptual understanding to actual EEG signal analysis.

### Session 05–08 Direction

1. Set up Python analysis environment.
2. Install and test required libraries.
3. Find and download a public EEG dataset.
4. Inspect raw EEG structure:
   - channels
   - sampling rate
   - amplitude scale
   - file format
   - event markers
5. Practice basic preprocessing:
   - band-pass filtering
   - artifact awareness
   - segmentation, if applicable
6. Compute frequency-domain features:
   - power spectrum
   - alpha power
   - beta power
   - alpha/beta or beta/alpha ratio
7. Visualize feature differences across conditions.
8. Document the full analysis pipeline.

## 11. Milestone Reflection

The most important outcome of Milestone 01 is a change in framing.

At the beginning, BCI could easily be imagined as a system where the brain directly controls a machine.

After Sessions 01–03, the project is now framed more carefully:

```text
brain activity
→ indirect scalp signal
→ noisy time series
→ extracted feature
→ decision rule
→ physical action
```

This framing is less dramatic, but more useful.

The project should continue with this principle:

```text
Do not claim to read mental states directly.
Instead, define experimental conditions carefully and test whether measurable EEG features change reliably.
```

This principle will guide the next phase of the project.

## 12. Related Links

- [Session 01](../weekly-notes/session-01-260328.md)
- [Session 02](../weekly-notes/session-02-260418.md)
- [Session 03](../weekly-notes/session-03-260425.md)
- [English Medium Post 01: EEG Does Not Read the Brain: Why Features Matter in BCI](https://medium.com/@hyejuryuwork/eeg-does-not-read-the-brain-why-features-matter-in-bci-da6fc647426b)
- [English Medium Post 02: Not Every 8–13 Hz Signal Is an Alpha Rhythm](https://medium.com/@hyejuryuwork/not-every-8-13-hz-signal-is-an-alpha-rhythm-9a909f7383cb)
- [Korean Blog Archive 01 : 001-eeg는-뇌를-읽는-기술이-아니다.md](../docs/blog/ko/001-eeg는-뇌를-읽는-기술이-아니다.md)
- [Korean Blog Archive 02 : 002-8-13-hz가-보인다고-모두-alpha-rhythm은-아니다.md](../docs/blog/ko/002-8-13-hz가-보인다고-모두-alpha-rhythm은-아니다.md)

## 13. References

- 정천기 외. *사람 뇌의 구조와 기능*. 범문에듀케이션, 2015.
- 전경희, 원희욱, 정문주, 전병현, 강형원. *뇌파와 뉴로피드백의 이해*. 아카데미아, 2023.
- 대한뇌파연구회. *뇌파분석의 기법과 응용*. 대한의학, 2023.
