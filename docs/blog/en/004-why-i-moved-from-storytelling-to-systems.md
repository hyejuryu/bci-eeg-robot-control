# Why I Moved from Storytelling to Systems

*How writing, business strategy, and engineering led me toward computational neuroscience.*

I did not start from neuroscience.

For a long time, my questions belonged much more naturally to literature, theater, philosophy, and social thought.

I was interested in why people misunderstand each other, why the same situation can produce completely different reactions, why language sometimes connects people and sometimes fails completely, and why the world seems to contain both repetition and difference at the same time.

At first, writing felt like the right tool for that kind of question.

A novel is not just a sequence of sentences. A play is not just dialogue. Both require a world. They require internal rules, tension, causality, timing, and characters who respond differently depending on their histories and conditions.

In that sense, storytelling taught me to care about patterns.

But eventually, I became dissatisfied with interpretation alone.

I did not only want to describe what something meant. I wanted to understand how something worked.

## From Meaning to Mechanism

The humanities and the arts gave me powerful ways to think about meaning.

They helped me understand ambiguity, conflict, identity, desire, and interpretation. They gave me a language for human experience.

But I started to feel that many explanations stopped too early.

They could describe human difference, but they often could not show the mechanism that generated it. They could describe conflict, but they did not always explain how different internal states, histories, environments, and interactions produced different outcomes.

I began to feel that I was looking for something underneath interpretation.

Not a single answer.

Not a simple formula.

But a way to ask:

> What kind of system produces this kind of pattern?

That question gradually moved me toward engineering.

## What Engineering Changed

My first serious contact with engineering did not happen in a university lab.

It happened through work.

I entered the world of AI infrastructure and high-performance computing from a business and strategy role. My work was not to design GPU servers directly, but I was surrounded by systems that made abstract computation physically real: hardware architecture, liquid cooling, monitoring, serial communication, data center infrastructure, and large-scale operational constraints.

That environment changed the way I thought.

Before that, I was used to thinking in terms of meaning, narrative, and structure.

Engineering forced me to think in terms of operation.

A system either runs or it does not.  
A signal is either measured or it is not.  
A device either responds or it does not.  
A design either survives constraints or it fails.

This was refreshing.

It showed me that an idea has to pass through implementation before it becomes real.

At the same time, engineering also revealed its own limit for me. Engineering is powerful because it builds things that work. But my deepest question was not only how to build a system. It was why different systems produce different patterns, how small changes propagate, and how stable structures emerge from interactions.

So I did not want to abandon meaning.

I wanted to connect meaning to mechanism.

![Career path from storytelling to systems](../docs/blog/assests/004-career-path-from-storytelling-to-systems.png.png)


## Why Computational Neuroscience Became the Next Step

This is why computational neuroscience became important to me.

Not because I think neuroscience is the final answer to every question.

And not because I want to reduce human life to brain activity.

Rather, the brain is one of the most interesting systems where physical signals, biological structure, information processing, behavior, and experience meet.

It is a system that can be measured.

It is also a system that changes over time.

It contains noise, variability, feedback, adaptation, and state transitions. It is not a static object. It is a dynamical system.

That is what interests me.

I am drawn to neuroscience not only as the study of the brain, but as a training ground for studying how complex patterns emerge from interacting components.

This framing matters because it changes the kind of question I want to ask.

A shallow version of the question would be:

> Can we detect focus from EEG?

A more useful version is:

> Under a defined experimental condition, does a measurable EEG feature change in a reliable way?

An even deeper version, for future work, might be:

> How do neural features evolve over time as a system moves between states?

At my current stage, I am not ready to answer the deepest version of that question.

But I can begin with the smaller one.

## Why I Am Starting With EEG and BCI

My current project is an EEG-based BCI robot control study.

At first glance, that may sound like a project about controlling a machine with the mind.

That is not how I frame it.

For me, this project is a way to learn how to move from an abstract question to a measurable system.

The pipeline looks like this:

```text
brain state change
→ EEG acquisition
→ preprocessing
→ feature extraction
→ decision rule
→ robot command
```

Each arrow in this pipeline is a problem.

A brain state is not directly visible.  
EEG is noisy and indirect.  
Raw signals are not immediately interpretable.  
Features need to be defined carefully.  
Thresholds should not be chosen only from theory.  
A robot should not move because I guessed what the signal means.

This is why I am documenting the project step by step.

I am not trying to build a dramatic demo first.

I am trying to build a careful path from signal to feature to decision.

## From Raw Signal to Measurable Feature

In the first stage of the project, I studied what EEG actually measures and why it should not be treated as mind reading.

Then I moved into signal analysis.

I set up a Python environment, generated a synthetic signal, tested a basic PSD pipeline, loaded a public EEG dataset, inspected raw EEG structure, and compared eyes-open and eyes-closed conditions using alpha power.

This may sound like a small technical step.

But for me, it was important.

It changed EEG from a concept into data.

I began to see EEG not as a mysterious waveform, but as structured numerical time-series data:

```text
channels × samples
```

From there, I could transform the signal into the frequency domain, calculate band power, and compare defined conditions.

In a public EEG dataset, I observed a clear posterior alpha power difference between eyes-closed and eyes-open baseline conditions.

The careful interpretation is not:

```text
eyes closed = relaxation
eyes open = focus
```

The careful interpretation is:

> A measurable spectral feature changed between two defined experimental conditions.

That may sound less exciting.

But it is exactly the kind of statement I want to learn how to make.

## Why Documentation Matters

I am also learning that research is not only about producing results.

It is about leaving a trail that can be inspected.

That is why I am keeping weekly notes, milestone reports, scripts, figures, and blog posts in a public GitHub repository.

The format is intentionally structured:

```text
objectives
what I studied
key takeaways
my understanding
questions / unclear points
next actions
outputs
references
```

This format helps me avoid turning the project into a diary.

It also helps me avoid turning it into a performance.

I want the record to show what I understood, what I did not understand, what I tested, what I produced, and what should be done next.

That habit matters because my background is not linear.

I did not move from an undergraduate neuroscience degree into a neuroscience lab.

I moved from writing and theater to business strategy, from business strategy to engineering, and from engineering toward computational neuroscience.

Because of that, documentation is not just a habit.

It is part of how I build credibility.

## The Bigger Question, Kept Small

There is a much larger question behind this path.

I am interested in how stable patterns emerge from interactions.

I am interested in how small differences in state, history, or condition can produce different trajectories.

I am interested in why the world contains both common structure and radical difference.

But those questions are too large to study directly.

So I need to keep them small.

Right now, the question is not:

> What is the fundamental structure of reality?

The current question is:

> Can I measure a simple EEG feature reliably under a defined condition?

That is a smaller question.

But it is also a real one.

And if I cannot handle the smaller question carefully, I have no right to make claims about the larger one.

## What I Am Trying to Become

I do not think of this transition as leaving my previous background behind.

Writing taught me to see structure in experience.

Business strategy taught me to translate complexity into decisions.

Engineering taught me to respect mechanisms and constraints.

Computational neuroscience is where I am trying to bring those habits into a more rigorous research practice.

My goal is not to become someone who uses technical language to make vague ideas sound scientific.

My goal is the opposite.

I want to take large, intuitive questions and reduce them into smaller, testable, measurable forms.

That is the discipline I am trying to build.

## Closing

I still care about stories.

But I no longer want to stop at storytelling.

I still care about meaning.

But I want to understand the systems that make meaning possible.

I still care about human difference.

But I am increasingly interested in the dynamics that produce difference, stability, transition, and pattern across systems.

That is why I moved from storytelling to systems.

And that is why, for now, I am starting with EEG.

Not because EEG can answer everything.

But because it gives me a place to begin:

```text
a signal
a system
a measurable feature
a condition change
a next question
```

For me, that is enough for the next step.

---

## Note

This post is a personal reflection on my transition from writing, business strategy, and engineering toward computational neuroscience.

My current project is an EEG-BCI robot control study documented through GitHub, milestone reports, and technical blog posts. At this stage, the goal is not to make strong claims about cognition or consciousness, but to build a careful research practice around measurable signals, defined conditions, and reproducible analysis.

## Project Repository

The project notes and session logs are archived on GitHub:

[EEG-BCI Robot Control Project](GITHUB_REPOSITORY_LINK)
