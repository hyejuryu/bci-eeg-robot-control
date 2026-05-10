# From Raw EEG to Alpha Power: Building My First EEG Analysis Pipeline

*How I moved from synthetic signals to public EEG data before collecting my own OpenBCI recordings.*

When I first started studying EEG-based BCI, most of the project still lived at the conceptual level.

I was thinking about brain states, attention, signal features, thresholds, and robot control. But at that stage, EEG was still something I mainly understood through diagrams and descriptions.

This changed when I started working with actual signal data.

The second milestone of my EEG-BCI robot control project was not about controlling a robot yet. It was not about collecting my own OpenBCI data yet either.

It was about building the first working analysis path:

```text
signal
→ data structure
→ frequency-domain representation
→ band power feature
→ condition comparison
```

Before using an OpenBCI Cyton 8-channel board, I wanted to answer a simpler question:

> Can I take EEG data, inspect its structure, transform it into frequency-domain features, and observe a basic condition-dependent difference?

For this milestone, I used a public EEG dataset and focused on a basic comparison:

```text
eyes open
vs.
eyes closed
```

The goal was not to detect “focus” or read a mental state.

The goal was more modest:

> Build a reliable path from raw EEG to measurable features.

## Why I Did Not Start With OpenBCI Immediately

It is tempting to start a BCI project by connecting hardware immediately.

That would be more exciting. It would also be risky.

If I collect noisy EEG data without understanding the analysis pipeline, I may not know whether a failed result comes from the electrode setup, the code, the feature definition, the preprocessing, or the experimental design.

So I decided to separate the problem into smaller steps.

Before collecting my own data, I first needed to understand:

- how EEG-like time-series signals are represented in Python
- how sampling frequency relates to time and sample index
- how to compute a power spectrum
- how alpha and beta band power can be extracted
- how raw EEG data is stored in a real dataset
- why raw EEG waveform visualization is not enough
- how eyes-open and eyes-closed conditions can be compared using PSD

This was not just preparation.

It was the beginning of the actual research workflow.

## Step 1: Testing the Pipeline With a Synthetic Signal

The first step was to build a simple analysis environment and test whether the basic signal-processing code worked.

I created a synthetic EEG-like signal using three components:

```text
10 Hz alpha-like sine wave
20 Hz beta-like sine wave
random noise
```

This was not real EEG.

That distinction is important.

A synthetic signal does not show alpha rhythm or beta activity in a physiological sense. It is simply a controlled signal where I already know what frequency components are present.

That makes it useful as a smoke test.

If I create a signal with a strong 10 Hz component and a smaller 20 Hz component, then the PSD should show a larger peak around 10 Hz and a smaller peak around 20 Hz. If the code cannot detect that, then it should not be trusted on real EEG data yet.

[Insert Figure 1 here: `figures/session-05/synthetic_signal_psd.png`]

The synthetic signal helped me understand a basic but important point:

> A signal that looks complicated in the time domain may become more interpretable in the frequency domain.

In the time-domain graph, the signal looks noisy and irregular.

In the PSD graph, the frequency structure becomes visible.

This is the first reason frequency-domain analysis matters in EEG.

Raw EEG is not usually clean or visually obvious. If I want to talk about alpha or beta power, I need to transform the time-series signal into a frequency-domain representation.

## Step 2: Opening Real EEG Data

After the synthetic signal test, I moved to a public EEG dataset.

I used the EEGBCI dataset through MNE-Python and loaded baseline eyes-open and eyes-closed runs for Subject 1.

This step was less glamorous than feature extraction, but it was essential.

Before interpreting EEG, I needed to inspect the raw data structure:

- sampling frequency
- channel names
- number of channels
- number of samples
- recording duration
- annotations
- data shape

One of the most important things I learned was that EEG is not stored as a continuous “brain wave picture.”

Inside Python, EEG is numerical time-series data.

In this dataset, the sampling frequency was 160 Hz.

That means:

```text
1 second = 160 samples
```

So when I visualize 10 seconds of EEG, I am actually selecting about 1600 sample points and plotting them over time.

This changed how I thought about EEG.

Instead of imagining EEG as a mysterious waveform, I started to see it as structured numerical data:

```text
channels × samples
```

[Insert Figure 2 here: `figures/session-06/subject-001_run-01_baseline_eyes_open_first_10s.png`]

The raw waveform was noisy.

It did not look like a clean sine wave. It had fluctuations, channel differences, and irregular amplitude changes.

But it also did not look completely random.

This was an important moment. EEG is noisy biological data, but it is still structured data.

The question is how to extract useful structure without overinterpreting the waveform.

## Why Raw EEG Waveform Is Not Enough

Looking at raw EEG is useful, but it is not enough.

When I compared eyes-open and eyes-closed raw waveforms visually, I could see that the signals looked somewhat different. But I could not responsibly say:

```text
alpha increased
beta decreased
```

from the raw waveform alone.

That kind of statement requires frequency-domain analysis.

This is one of the most important lessons from this milestone:

> Raw EEG visualization is not the same as EEG rhythm analysis.

A waveform may look different across conditions, but alpha and beta are frequency-domain features. To analyze them, I need to compute the power spectrum and then summarize power within defined frequency bands.

So the analysis path became:

```text
raw EEG
→ band-pass filtering
→ posterior channel selection
→ Welch PSD
→ posterior mean PSD
→ alpha/beta band power
→ eyes-open vs eyes-closed comparison
```

This is the first real version of my EEG analysis pipeline.

## Step 3: Moving Into the Frequency Domain

For the actual EEG analysis, I applied a 1–40 Hz band-pass filter and selected posterior channels.

The reason for using posterior channels is that alpha reactivity is often most visible in posterior regions during eyes-closed and eyes-open comparisons.

Then I computed the Power Spectral Density using Welch’s method.

Welch PSD estimates how signal power is distributed across frequency. Instead of looking at amplitude over time, I can now ask:

> Which frequency ranges contain more power?

For this analysis, I defined:

```text
alpha band: 8 Hz ≤ f < 13 Hz
beta band: 13 Hz ≤ f ≤ 30 Hz
```

The PSD data had the following structure:

```text
6 posterior channels × 500 frequency points
```

This detail matters.

PSD is not just a graph. It is an array.

The frequency axis tells me where I am in the spectrum. The PSD values tell me how much power each channel has at each frequency point.

By averaging across posterior channels, I obtained a posterior mean PSD for each condition.

This made it possible to compare eyes-open and eyes-closed conditions more directly.

## Alpha Reactivity as a First Sanity Check

The main result was clear:

```text
eyes closed → stronger posterior alpha peak around 10 Hz
eyes open   → much lower posterior alpha power
```

[Insert Figure 3 here: `figures/session-07/subject-001_eyes_open_vs_eyes_closed_posterior_mean_psd.png`]

In this Subject 1 analysis, posterior alpha power was much higher in the eyes-closed condition than in the eyes-open condition.

The alpha power in the eyes-closed condition was approximately 11.5 times higher than in the eyes-open condition.

Beta power also increased in the eyes-closed condition, but the increase was smaller. Because alpha power increased much more strongly, the beta/alpha ratio became lower in the eyes-closed condition.

[Optional Figure 4 here: `figures/session-07/subject-001_alpha_beta_power_comparison.png`]

This was encouraging because it showed that the pipeline could detect a basic and expected condition-dependent spectral difference.

But the interpretation has to stay limited.

This result does not mean that the system read a mental state.

It does not mean:

```text
eyes closed = relaxation
eyes open = focus
```

A more careful interpretation is:

> In this public EEG dataset, posterior alpha-band power differed between defined eyes-closed and eyes-open baseline conditions.

That is less dramatic.

It is also more scientifically useful.

## Why This Matters Before OpenBCI

This alpha reactivity result is not the final goal of the project.

The final project aims to collect EEG using OpenBCI, extract features in Python, and eventually connect a decision rule to Arduino-based robot control.

But before that, I need a sanity check.

If I cannot observe a basic eyes-open versus eyes-closed alpha difference in a clean public dataset, it would be premature to expect stable real-time control from my own OpenBCI recordings.

Alpha reactivity gives me a first checkpoint:

```text
Can the pipeline detect a known physiological condition difference?
```

If the answer is yes, then I can move toward more difficult questions:

- Can I observe similar alpha reactivity in my own OpenBCI data?
- How stable is the feature across time windows?
- How much does the feature vary within a condition?
- Can alpha suppression or low beta power distinguish rest and task conditions?
- Can a threshold be chosen from actual feature distributions?
- How much false triggering would occur in real-time control?

These questions are more important than simply asking whether a single feature value is high or low.

## From Classification to Signal Dynamics

At this stage, I am not trying to build a classifier that labels mental states.

That would be too early.

Instead, I am trying to understand how EEG features change under defined conditions.

This distinction matters for the longer direction of the project.

A basic BCI demo might eventually use a rule like:

```python
if beta_power > threshold:
    send_command_to_robot()
```

But that rule is only meaningful if the feature is stable enough, separable enough, and interpretable within the experimental context.

In future stages, I will need to move from single-value comparisons to window-based analysis.

Instead of computing one alpha or beta value from an entire recording, I will need to compute features over short sliding windows:

```text
0–2 s
1–3 s
2–4 s
3–5 s
...
```

Then I can examine how the feature evolves over time.

This matters because a real-time BCI system is not based on a final average after the experiment ends. It has to make decisions while the signal is changing.

Eventually, I want to study not only whether a feature is high or low, but how EEG features evolve during transitions between conditions.

For now, the first step is simpler:

> Build a reliable path from raw signal to measurable feature.

## What I Learned From This Milestone

The most important change in this milestone was that EEG became less abstract.

In the first milestone, I studied what EEG is and why it should not be interpreted as direct mind reading.

In this milestone, I started to handle EEG as data.

The main lesson was:

```text
EEG is not just a waveform.
It is structured numerical time-series data.
```

And EEG analysis is not just plotting.

It requires a sequence of choices:

```text
sampling frequency
channel selection
time window
filtering range
PSD method
frequency bands
feature calculation
condition comparison
interpretation boundary
```

Each choice affects what can be concluded.

This is why I do not want to jump directly from EEG to robot control.

The signal has to pass through measurement, transformation, feature extraction, and decision-making before it can become a command.

## Current Status

At the end of this milestone, I now have a basic offline EEG analysis pipeline:

```text
environment setup
→ synthetic signal test
→ public EEG loading
→ raw EEG inspection
→ band-pass filtering
→ Welch PSD
→ alpha/beta band power
→ eyes-open vs eyes-closed comparison
→ figure and CSV export
```

This is still a small step.

But it is an important one.

It means I can now move toward OpenBCI data collection with a clearer baseline:

```text
eyes open
vs.
eyes closed
→ posterior alpha power difference
```

Before attempting focus-based robot control, I should first check whether my own hardware setup can reproduce this basic response.

If that works, then I can move toward task conditions, sliding-window features, threshold design, and eventually real-time control.

## Conclusion

This milestone was not about proving that EEG can control a robot.

It was about making EEG analyzable.

I started with a synthetic signal where the frequency components were known. Then I opened real EEG data and inspected its structure. Finally, I transformed public EEG recordings into frequency-domain features and observed a clear posterior alpha difference between eyes-closed and eyes-open conditions.

The important result is not that I “detected relaxation” or “read focus.”

The important result is that I built the first working bridge:

```text
raw EEG
→ structured data
→ frequency-domain feature
→ condition comparison
```

For a beginner EEG-BCI project, that bridge matters more than a dramatic demo.

A robot should not move because I guessed what the EEG means.

It should move only after the signal has been measured, transformed, tested, and reduced to a feature that behaves reliably enough to support a decision rule.

That is the next challenge.

---

## Note

This post is based on my Session 05–07 study notes from an EEG-BCI robot control project.

At this stage, the goal is not to make strong claims about attention, relaxation, or cognition. The goal is to build a careful signal analysis pipeline before collecting OpenBCI data and attempting real-time robot control.

## Project Repository

The project notes and session logs are archived on GitHub:

[EEG-BCI Robot Control Project](GITHUB_REPOSITORY_LINK)

## References / Study Notes

This post is based on my Session 05–07 study notes from an EEG-BCI robot control project.

Additional references:

- MNE-Python documentation
- MNE EEGBCI dataset documentation
- SciPy documentation: `scipy.signal.welch`
- PhysioNet EEG Motor Movement/Imagery Dataset
- NumPy documentation
- Matplotlib documentation
