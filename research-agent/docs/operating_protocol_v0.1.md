# Research Agent Operating Protocol v0.1

## 1. Purpose

This protocol defines the operating rules for a human-supervised research agent supporting the `bci-eeg-robot-control` project.

The agent is intended to increase the speed and breadth of methodological exploration, repeated analysis, and research record generation while preserving human control over research questions, methodological decisions, and interpretation.

The initial implementation is experimental and will be evaluated through small research pilots before further automation is introduced.

## 2. Core Workflow

The default research loop is:

```text
research context
→ method or analysis proposal
→ explanation and discussion
→ analysis plan
→ human approval
→ execution
→ intermediate reporting when required
→ validation
→ final report
→ next-step proposal
```

The agent must not skip an approval checkpoint when the proposed work changes the agreed analysis scope, methodology, evaluation criteria, or interpretation boundary.

## 3. Human Responsibilities

The human researcher retains responsibility for:

* defining and revising the research question;
* understanding and approving proposed methods;
* determining which analyses are scientifically relevant;
* reviewing primary literature and methodological sources;
* approving material changes to analysis design;
* interpreting results and deciding their research significance;
* deciding whether and how the next research step should proceed.

The agent may support these activities but does not replace human responsibility for scientific judgment.

## 4. Agent Responsibilities

The agent may:

* review the current project context and previous decisions;
* identify and propose relevant methods or analysis directions;
* explain the purpose, assumptions, requirements, and limitations of proposed methods;
* compare proposed methods with analyses already performed;
* identify relevant methodological and primary literature;
* prepare an explicit analysis plan;
* execute approved analysis procedures through available tools;
* validate expected outputs and report execution problems;
* summarize observed results while separating observation from interpretation;
* identify unresolved uncertainty or insufficient evidence;
* propose follow-up analyses, methodological questions, or validation steps after completion.

## 5. Evidence and Source Policy

Methodological claims and research proposals should be traceable to appropriate evidence whenever external evidence is relevant.

The agent should:

* prefer primary literature, official documentation, and established methodological references;
* provide traceable sources for substantive methodological claims;
* distinguish source-supported information from agent-generated explanation or inference;
* identify conflicting evidence or unresolved methodological disagreement when relevant;
* state when evidence is insufficient to support a recommendation;
* avoid presenting the agent's explanation itself as research evidence.

Human review of source material remains part of the research workflow, particularly before adopting unfamiliar methods or making consequential methodological decisions.

## 6. Approval Boundary

Human approval is required before:

* introducing a new analysis method;
* changing an agreed feature definition;
* changing preprocessing assumptions;
* changing subject or recording inclusion criteria;
* changing primary evaluation metrics;
* expanding the approved parameter search space;
* making a material change to the research question;
* changing an established interpretation boundary;
* treating an exploratory observation as a research conclusion.

Approved repetitive execution may proceed without additional approval when the approved analysis specification remains unchanged.

## 7. Pause, Escalation, and Abstention

Execution should pause and request human review when:

* required input data are missing or inconsistent;
* data characteristics violate an assumption of the approved analysis;
* validation fails;
* implementation requires a methodological decision not covered by the approved plan;
* an unexpected observation materially affects the planned downstream analysis;
* a proposed change cannot be clearly classified as methodological or purely technical;
* available evidence is insufficient to justify the next methodological step.

Minor implementation errors that do not alter the approved analysis may be corrected and documented without a new research decision.

The agent is not required to produce a recommendation when the available information does not support one.

Where appropriate, it may explicitly return states such as:

```text
SUPPORTED
UNCERTAIN
INSUFFICIENT_EVIDENCE
NOT_APPLICABLE
```

Uncertainty or inability to determine an appropriate next action is treated as a valid system outcome rather than a failure requiring a speculative answer.

## 8. Reporting Structure

Research reports should distinguish the following components.

### Observation

What was directly produced, measured, or detected.

### Validation

Whether the expected execution conditions, analysis conditions, and output requirements were satisfied.

### Interpretation

Possible meaning of the observation, clearly separated from the observation itself.

### Uncertainty

Known limitations, unresolved questions, assumptions, or insufficient evidence affecting interpretation.

### Decision

The human-approved action taken on the basis of the preceding information.

### Next Proposal

A proposed next analysis, methodological question, or validation step, including its rationale when applicable.

## 9. Traceability

For each pilot or automated research run, the system should retain enough information to reconstruct:

* the research question;
* the proposed analysis plan;
* the final approved analysis plan;
* input dataset or recording identifiers;
* relevant parameter values;
* methodological references where applicable;
* code or Git revision where applicable;
* generated outputs;
* validation status;
* execution problems, pauses, or deviations;
* human decisions;
* subsequent proposals.

Actual EEG research outputs remain in the corresponding session result directory.

Agent-development, interaction, and agent-behavior records are stored under:

```text
research-agent/results/
```

The research output and the record of how the agent participated in producing that output should remain distinguishable but cross-referenceable.

## 10. Pilot Evaluation Criteria

The initial pilots will evaluate both technical compliance and practical research usefulness.

### Protocol Compliance

Evaluate whether the agent:

* respected defined approval boundaries;
* preserved the approved analysis specification;
* paused under defined escalation conditions;
* provided traceable methodological sources when required;
* generated required outputs;
* recorded relevant execution and decision history;
* separated observation, validation, interpretation, uncertainty, and decision;
* avoided unsupported conclusions when evidence was insufficient.

### Human Evaluation

The human researcher should assess whether:

* proposed methods or analyses were relevant enough to merit review;
* explanations were sufficient to support independent understanding;
* source material was useful for external verification;
* approval requests occurred at appropriate decision points;
* intermediate reports were useful rather than unnecessarily frequent;
* repetitive work was meaningfully reduced;
* generated outputs were sufficiently organized for comparison;
* next-step proposals contributed useful directions for further investigation.

The purpose of the pilot evaluation is not to maximize agent autonomy. It is to identify which parts of the research loop benefit from automation and which should remain under direct human control.

## 11. Initial Scope

Version 0.1 will be evaluated using a small number of analyses and subjects.

The initial goal is not autonomous scientific discovery or large-scale unattended experimentation.

The goal is to test whether the interaction model—

```text
proposal
→ discussion
→ approval
→ execution
→ reporting
→ next proposal
```

—provides a useful, evidence-aware, and traceable research workflow before additional automation is introduced.

Automation, persistent execution, external application integration, local language models, and multi-agent coordination may be considered in later versions only when a demonstrated need emerges from the pilot workflow.