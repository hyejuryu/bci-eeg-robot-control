# Not Every 8–13 Hz Signal Is an Alpha Rhythm

*Why EEG interpretation requires more than frequency bands.*

- Status: Draft
- Medium link: [Not Every 8–13 Hz Signal Is an Alpha Rhythm](MEDIUM_LINK)
- Date drafted: 2026-04-29
- Related sessions:
  - [Session 03](../../../weekly-notes/session-03-260425.md)
- Type: Technical reflection
- Previous post:
  - [EEG Does Not Read the Brain: Why Features Matter in BCI](./001-eeg-does-not-read-the-brain.md)

---

When I first started studying EEG, frequency bands looked deceptively simple.

Delta is associated with slow activity.  
Theta is often linked to drowsiness or internal processing.  
Alpha is commonly described as relaxation.  
Beta is often connected to attention or task engagement.  
Gamma is sometimes associated with higher cognition.

This kind of summary is useful as a first map.

But it can also be misleading.

If I treat EEG interpretation as a simple dictionary —

```text
alpha = relaxation
beta = concentration
gamma = higher cognition
```

— then I am already in trouble.

EEG analysis is not just about finding a frequency range and attaching a psychological label to it. A signal around 8–13 Hz does not automatically become a meaningful alpha rhythm. A decrease in alpha power does not automatically mean that someone is focused. A rise in beta power does not automatically prove attention.

This distinction matters for my EEG-BCI project because I eventually want to use EEG features for simple robot control.

Before asking whether a feature can control a robot, I need to ask a more basic question:

> What exactly am I measuring?

## Frequency Bands Are Not the Same as Rhythms

A frequency band is a range.

For example, the alpha band is usually described as activity around 8–13 Hz.

But a rhythm is more than a range of frequencies.

A rhythm has structure. It has context. It has a typical distribution, state dependency, duration, reactivity, and relationship to other signals.

This means that observing power in a frequency band is not enough. I also need to consider where it appears, under what condition it appears, whether it repeats, whether it reacts to a change in state, and whether it might be contaminated by artifacts.

In other words:

```text
frequency band = where in the spectrum the activity appears
rhythm = a structured physiological pattern interpreted in context
```

This distinction may look small, but it changes how I read EEG data.

If I only look at frequency bands, I may be tempted to interpret every 10 Hz component as alpha.

If I think in terms of rhythm, I have to ask whether that 10 Hz activity behaves like alpha rhythm.

## What Makes Alpha Rhythm More Than 8–13 Hz?

Alpha rhythm is not simply any activity between 8 and 13 Hz.

In a basic EEG context, alpha rhythm is often discussed as a posterior dominant rhythm that appears more clearly when a person is awake, relaxed, and has their eyes closed. It tends to decrease when the eyes open or when visual processing and task engagement increase.

This decrease is often called alpha blocking or alpha suppression.

So the important question is not only:

> Is there activity around 8–13 Hz?

The better question is:

> Does this activity appear in the expected region, under the expected condition, and react to state changes in a meaningful way?

For example, in an early EEG experiment, I would not immediately try to detect “focus.”

A better first step is to compare:

```text
eyes closed
vs.
eyes open
```

If posterior alpha activity increases during eyes-closed periods and decreases when the eyes open, that gives me a basic sign that the recording is capturing a meaningful physiological change.

This does not prove that the participant is relaxed in a deep psychological sense.

It simply tells me that the EEG setup may be detecting a basic state-dependent response.

That is already useful.

## Why Alpha Reactivity Matters Before BCI Control

For a beginner EEG-BCI project, alpha reactivity is not just a neuroscience concept. It is a practical checkpoint.

Before I use EEG to control anything, I need to know whether my setup can capture a simple, expected change.

If I cannot observe a clear eyes-closed versus eyes-open difference, then I should not rush into focus-based robot control.

Instead, I should first check more basic problems:

- electrode contact
- reference setup
- channel location
- eye movement artifacts
- muscle artifacts
- environmental noise
- filtering choices
- preprocessing errors

In this sense, alpha reactivity is a sanity check.

It helps answer:

> Is the EEG signal responding to a basic physiological condition change?

Only after that question becomes reasonably stable should I move toward more complex conditions such as mental arithmetic, visual attention, or focus tasks.

## Alpha Suppression Is Not the Same as “Concentration”

One of the easiest mistakes is to say:

> Alpha decreased, so the participant was focused.

That may be possible in some experimental contexts, but it is too simple as a general statement.

Alpha power can decrease for many reasons.

The participant may have opened their eyes.  
They may be processing visual input.  
They may have moved slightly.  
The electrode contact may have changed.  
The signal may contain artifacts.  
The analysis window may be too short or unstable.

So I should not interpret alpha suppression by itself as direct evidence of concentration.

A more careful statement would be:

> Compared to the baseline condition, alpha power decreased during the task condition.

Even better:

> Compared to the eyes-closed baseline, posterior alpha power decreased during the eyes-open or task condition, suggesting state-dependent alpha reactivity.

This is less dramatic, but more accurate.

For BCI, accuracy matters more than dramatic interpretation.

## What This Means for Focus-Based BCI

My project eventually aims to connect EEG features to simple robot control.

A possible future control logic might look like this:

```python
if feature_value > threshold:
    send_command_to_robot()
```

But this logic is only meaningful if the feature is well-defined.

If I define focus too vaguely, the control system becomes unstable before it even begins.

So instead of saying:

```text
focus → beta increase → robot moves
```

I need a more careful experimental structure:

```text
defined baseline condition
→ defined task condition
→ feature extraction
→ distribution comparison
→ threshold decision
→ robot command
```

This is why alpha reactivity matters early in the project.

It gives me a first example of how a condition change can be connected to a measurable EEG feature.

The same logic can later be applied to more difficult features such as low beta power or beta/alpha ratio.

But I should not skip the first step.

## The Problem With Simple EEG Labels

The same caution applies to other frequency bands.

Low beta activity may be related to attention, task engagement, or problem solving, but I should not treat a single beta value as a universal concentration marker.

Gamma activity, especially around 40 Hz, is often discussed in relation to higher cognition, binding, or peak performance. But in scalp EEG, high-frequency activity can easily mix with muscle activity, jaw tension, facial movement, and other artifacts.

This means that frequency labels are useful, but dangerous when used too quickly.

A better approach is to treat frequency bands as feature candidates, not conclusions.

```text
alpha band activity → candidate feature
low beta power → candidate feature
gamma activity → later candidate, only after artifact control
```

The goal is not to assign a mental state to every frequency band.

The goal is to test whether a feature behaves reliably under a defined experimental condition.

## A Practical Checklist for Early EEG Analysis

For my current project, I want to avoid interpreting EEG too quickly.

Before calling something a meaningful feature, I should ask:

1. Which frequency band is being measured?
2. Which channel or scalp region does it come from?
3. What condition was the participant in?
4. Was the participant’s eye state controlled?
5. Is the pattern repeatable across trials?
6. Could the signal be explained by artifacts?
7. Was the feature compared against baseline?
8. Is the distribution separable enough for threshold-based control?

This checklist is simple, but it prevents a common mistake:

> treating EEG bands as direct labels for mental states.

That mistake may produce a more exciting story.

But it produces a weaker experiment.

## The Current Role of Alpha in My Project

At this stage, alpha is not my final BCI feature.

It is my first test of whether the pipeline is working.

The immediate goal is not to prove that I can detect focus.

The immediate goal is to see whether I can observe a basic EEG response such as:

```text
eyes closed → posterior alpha increase
eyes open   → alpha suppression
```

If this basic response is visible, then I can move toward more complex analyses:

- alpha suppression during task conditions
- low beta power during problem-solving tasks
- beta/alpha ratio
- baseline-normalized feature changes
- threshold design based on feature distributions

This order matters.

A BCI system should not begin with a dramatic claim.

It should begin with a measurable difference.

## Conclusion

Not every 8–13 Hz signal is an alpha rhythm.

Not every alpha decrease means focus.

Not every beta increase means attention.

And not every frequency band should be turned into a psychological label.

For EEG-based BCI, the important question is not simply:

> Which frequency band changed?

The better question is:

> Under what condition did it change, where did it appear, how stable was it, and can it support a reliable decision rule?

This is the kind of question I need before moving from EEG analysis to robot control.

The goal is not to make EEG sound mysterious.

The goal is to make it usable.

---

## Note

This post is based on my early study notes from an EEG-BCI robot control project. At this stage, the goal is not to make strong claims about attention or cognition, but to distinguish simple frequency-band descriptions from more careful rhythm-based interpretation.

## Project Repository

The project notes and session logs are archived on GitHub:

[EEG-BCI Robot Control Project](GITHUB_REPOSITORY_LINK)

## References / Study Notes

This post is based on my Session 03 study notes from an EEG-BCI robot control project.

Additional references:

- 전경희, 원희욱, 정문주, 전병현, 강형원. *뇌파와 뉴로피드백의 이해* [Understanding EEG and Neurofeedback]. 아카데미아, 2023.
- 대한뇌파연구회. *뇌파분석의 기법과 응용* [Techniques and Applications of EEG Analysis]. 대한의학, 2023.
