---

EEG Does Not Read the Brain: Why Features Matter in BCI
A beginner's reflection on why EEG-based brain-computer interfaces are less about reading thoughts than extracting reliable signal features.
When people first encounter brain-computer interfaces, it is tempting to describe them in a dramatic way:
A person thinks, and a machine moves.
This image is powerful. It is also misleading.
A brain-computer interface does not simply "read thoughts" and convert them into commands. At least in the kind of non-invasive EEG-based BCI I am currently studying, the process is much more indirect, limited, and technically fragile.
A more accurate description would be:
A change in brain state produces measurable electrical activity.
 That activity is recorded from the scalp.
 The raw signal is cleaned, transformed, and reduced into features.
 Those features are compared against decision rules.
 Only then can they become control commands.
This distinction matters because it changes how we understand the entire project.
The goal is not to decode the full content of the mind.
 The goal is to identify a measurable pattern that can be used reliably enough for control.
The Minimal Pipeline
The basic pipeline of my current EEG-BCI robot control project can be summarized as follows:
brain state change
→ EEG acquisition
→ preprocessing / noise reduction
→ feature extraction
→ threshold-based decision
→ control command generation
→ robot actuation
At first glance, this looks straightforward. But every arrow in this pipeline hides a problem.
A brain state is not directly visible.
EEG does not capture the brain's activity in a complete or high-resolution way.
Raw EEG is noisy.
A feature may or may not reflect the mental state we care about.
A threshold may work in one session and fail in another.
A robot command may be triggered too late, too often, or for the wrong reason.

This is why BCI is not just a neuroscience problem. It is also a signal processing problem, a control problem, and an experimental design problem.
What EEG Actually Measures
EEG does not measure individual thoughts.
It does not measure the firing of a single neuron.
It does not tell us, in any direct way, whether a person is "focused," "creative," or "intending to move."
What EEG records from the scalp is the summed electrical activity of large populations of neurons, especially synchronized postsynaptic potentials from cortical pyramidal cells. By the time this activity reaches the scalp, it has already passed through biological tissue, mixed with other sources, and lost much of its spatial detail.
This means that EEG is not a transparent window into the brain.
It is a low-resolution, indirect, population-level signal.
That does not make it useless. It makes it interesting.
Because the question becomes:
Can we find a stable, repeatable change in this indirect signal that corresponds to a controlled experimental condition?
For a simple BCI system, this is often more important than asking whether we can fully explain the underlying mental state.
Raw EEG Is Not a Control Signal
A robot cannot move directly from raw EEG.
Raw EEG is a time series. It contains brain activity, artifacts, environmental noise, muscle activity, eye movement, electrode issues, and many other sources of variation.
To use EEG for control, we need to transform the raw signal into something more interpretable.
This is where features come in.
A feature is a measurable property extracted from the signal. In an EEG-based BCI project, examples might include:
alpha power
alpha suppression
low beta power
beta/alpha ratio
event-related potentials
coherence between channels
baseline-normalized power changes

The feature is not the brain state itself.
It is a measurable proxy.
For example, in an attention-related experiment, I should not say:
The EEG shows concentration.
A more careful statement would be:
During the task condition, alpha power decreased relative to baseline, and low beta power increased within a specific frequency range.
That is less dramatic, but it is much more useful.
Why "Focus" Has to Be Redefined
One of the first problems in designing a focus-based BCI experiment is that "focus" is not directly measurable.
In everyday language, focus feels like a psychological state. But in an experiment, it has to be operationally defined.
Instead of asking, "Is the participant focused?" we need to ask more specific questions:
What task are they performing?
What is the baseline condition?
How long is each trial?
Which EEG channels are being analyzed?
Which frequency bands are being compared?
Is the change consistent across trials?
Is the feature separable enough to support a decision rule?

For my current project, this means that "focus" will initially be treated as a task condition, not as a directly observed mental substance.
A more realistic starting point is to compare conditions such as:
rest
eyes open
eyes closed
mental arithmetic
focused visual task
Then I can examine whether certain EEG features change in a repeatable way.
For example, alpha activity is often useful as an early sanity check. In a basic experiment, posterior alpha rhythm may increase when the eyes are closed and decrease when the eyes are open or when visual processing begins. This kind of alpha reactivity can help confirm whether the EEG setup is capturing meaningful physiological state changes.
Low beta activity may also be relevant for attention or task engagement, but it has to be handled carefully. A single frequency value should not be treated as a universal marker of concentration. Individual variation, preprocessing choices, muscle artifacts, and session conditions can all affect the signal.
So the initial question is not:
Can I detect focus?
The better question is:
Can I find a feature that changes reliably between a defined baseline and a defined task condition?
Why Thresholds Come Later
In a simple BCI demo, the control logic may look like this:
if beta_power > threshold:
send command to robot
This is easy to understand. It is also easy to misuse.
A threshold should not be chosen just because a theory says a frequency band is related to attention. The threshold should be chosen after looking at the actual feature distribution.
Before setting a threshold, I need to know:
What does the feature look like during baseline?
What does it look like during the task?
How much do the two distributions overlap?
How stable is the feature across time?
How many false triggers occur?
How much latency is introduced by the analysis window?

If the baseline and task distributions are not sufficiently separable, a threshold-based BCI will be unstable. It may trigger when the user is not focused. Or it may fail to trigger when the user is performing the task.
In that sense, the threshold is not the beginning of the system.
It is the result of signal analysis.
The Current Goal of My Project
The first goal of this project is not to build an impressive mind-controlled robot.
The first goal is to build a modest, interpretable pipeline.
At the current stage, I am focusing on the following questions:
Can I record EEG data with sufficient quality?
Can I observe basic physiological reactivity, such as eyes-closed versus eyes-open alpha changes?
Can I extract simple frequency-domain features such as alpha power and low beta power?
Can I compare those features across baseline and task conditions?
Can I use the resulting feature distribution to design a simple threshold rule?
Can that rule produce a stable enough command for Arduino-based robot control?

This may sound less exciting than "controlling a robot with the mind."
But it is a better scientific starting point.
A weak but interpretable system is better than a dramatic but meaningless demo.
From Brain Signals to Control
What interests me most about this project is the translation problem.
A brain state is biological.
An EEG signal is electrical.
A feature is mathematical.
A threshold is computational.
A robot command is mechanical.
BCI sits between all of these layers.
This is also why I find the field intellectually attractive. It forces me to move between neuroscience, signal processing, engineering, and experimental design. It does not allow a single explanation to dominate.
The brain does not become a command directly.
It has to pass through measurement, abstraction, decision, and actuation.
That is where the real problem begins.
A More Careful Definition of BCI
After the first few weeks of study, I would no longer describe EEG-based BCI as a technology that "reads the brain."
A better definition, at least for my current project, would be:
EEG-based BCI is a system that extracts measurable features from indirect brain signals and converts selected patterns into control commands under carefully defined experimental conditions.
This definition is less futuristic.
But it is more honest.
And for now, that is exactly what I need.
Next Step
The next step is to move from conceptual understanding to signal analysis.
Before attempting real-time control, I need to work with EEG data, inspect the raw signal structure, understand sampling rates and channels, apply filtering, compute power spectra, and visualize how alpha and beta features behave under different conditions.
Only after that should the project move toward threshold-based robot control.
The question is not whether the brain can control a machine.
The question is what kind of measurable difference can survive the full pipeline:
brain state
→ scalp signal
→ noisy data
→ extracted feature
→ decision rule
→ physical action
That is the real beginning of the project.

---

Note
This post is based on my early study notes from an EEG-BCI robot control project. At this stage, the goal is not to make strong claims about attention or cognition, but to build a careful pipeline from EEG signals to interpretable features and simple control decisions.
Project Repository
The project notes and session logs are archived on GitHub:
EEG-BCI Robot Control Project
References / Study Notes
This post is based on my Session 01–03 study notes from an EEG-BCI robot control project.
Additional references:
정천기 외. 사람 뇌의 구조와 기능 [Structure and Function of the Human Brain]. 범문에듀케이션, 2015.
전경희, 원희욱, 정문주, 전병현, 강형원. 뇌파와 뉴로피드백의 이해 [Understanding EEG and Neurofeedback]. 아카데미아, 2023.
대한뇌파연구회. 뇌파분석의 기법과 응용 [Techniques and Applications of EEG Analysis]. 대한의학, 2023.
