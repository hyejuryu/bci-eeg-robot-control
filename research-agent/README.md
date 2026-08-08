# Research Agent

Human-supervised research-agent development for the `bci-eeg-robot-control` project.

## Purpose

This subproject explores a research workflow in which an AI agent can:

* review the current research context;
* propose relevant methods or analysis directions;
* explain methodological concepts and supporting evidence;
* prepare explicit analysis plans;
* execute approved analyses through defined tools;
* pause and report when human review is required;
* preserve traceable records of execution and decisions;
* propose subsequent research steps.

Research questions, consequential methodological decisions, and interpretation remain under human control.

## Current Status

**Stage:** Initial pilot setup
**Operating protocol:** `docs/operating_protocol_v0.1.md`
**Initial approach:** Human-supervised, single-agent workflow with deterministic analysis tools

The first pilots will evaluate the interaction loop:

```text
proposal
→ discussion
→ approval
→ execution
→ reporting
→ next proposal
```

before introducing additional automation, persistent execution, local language models, or multi-agent coordination.

## Repository Boundary

Actual EEG research outputs remain in the main project session directories, for example:

```text
results/session-21/
```

Records specifically related to agent behavior, pilot execution, and agent evaluation are stored under:

```text
research-agent/results/
```

These records should remain distinguishable but cross-referenceable.

## Current Structure

```text
research-agent/
├── README.md
├── docs/
│   └── operating_protocol_v0.1.md
└── results/
    └── pilot-001/
```
