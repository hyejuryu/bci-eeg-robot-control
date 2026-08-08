# Agent Runtime v0.0.1 — Implementation Scope

* **Project:** bci-eeg-robot-control
* **Research-agent pilot:** Pilot 001
* **Research session:** Session 21
* **Runtime version:** v0.0.1
* **Status:** FROZEN
* **Governing protocol:** `operating_protocol_v0.1.md`
* **Execution specification:** `../results/pilot-001/pilot_spec.md`

## 1. Objective

Implement the minimum deterministic orchestration layer required to execute the frozen Session 21 Phase 1 specification while preserving explicit execution boundaries, validation checkpoints, persistent runtime state, and human-review pauses.

Runtime v0.0.1 does not perform methodological proposal or scientific interpretation.

Its role begins after specification freeze.

```text
FROZEN SPEC
→ controlled execution
→ validation
→ progress report or pause
→ resume when authorized
→ completion
```

## 2. Inputs

The runtime may read Git-tracked project files for context, validation, and execution support.

Read access does not authorize execution, modification, or methodological change.

Project records are treated according to their role.

### Governing Records

These define the current executable authority:

* `research-agent/docs/operating_protocol_v0.1.md`
* `research-agent/results/pilot-001/pilot_spec.md`
* persisted runtime state and recorded human decisions

### Project Context and Evidence

Other Git-tracked project files may be searched and read when relevant, including:

* project and milestone documentation;
* session and weekly notes;
* scripts and source code;
* existing result CSV, JSON, and metadata files;
* previous analysis records and frozen decisions;
* README and related project documentation.

These files provide context or evidence only.

Historical plans, prior instructions, comments, or documentation do not override the current governing records.

The runtime should retrieve only files relevant to the current task rather than loading the entire repository into active context by default.

## 3. Runtime State

The minimum persistent states are:

```text
READY
RUNNING_PHASE_1A
VALIDATING_PHASE_1A
RUNNING_PHASE_1B
VALIDATING_PHASE_1B
PAUSED_FOR_REVIEW
PHASE_1_COMPLETED
STOPPED
```

Current runtime state must be persisted outside process memory so that a paused run can be inspected and resumed after program termination.

The initial persistence target is:

```text
research-agent/results/pilot-001/runtime_state.json
```

## 4. Allowed Tools

### READ

The runtime may search and read Git-tracked files within the project repository for context, validation, and execution support.

Read access is broader than execution or write authority.

Files outside the Git-tracked project scope, including credentials, secrets, unrelated personal files, and repository-internal `.git` data, are outside the intended read scope.

### EXECUTE

The runtime may execute only Session 21 Phase 1 analysis and validation code explicitly associated with the frozen specification.

### WRITE

The runtime may write only:

* approved Session 21 research outputs;
* runtime state;
* execution and validation records;
* progress reports;
* human-review pause reports.

### NOT ALLOWED

Runtime v0.0.1 may not:

* treat contextual or historical project documents as execution authority;
* modify the frozen specification;
* execute Phase 2;
* expand the approved parameter space;
* introduce a new metric or methodological decision;
* modify prior-session research outputs;
* delete project files;
* perform Git commit or push;
* install packages;
* access unrelated files outside the project scope;
* perform web research;
* generate or modify analysis methodology autonomously.

## 5. Execution Boundary

The runtime may begin execution only when:

```text
SPEC_STATUS = FROZEN
AND
AUTHORIZED_SCOPE = PHASE_1
```

The approved order is:

```text
Phase 1A execution
→ Phase 1A validation
→ Phase 1A progress or pause report
→ Phase 1B execution
→ Phase 1B validation
→ Phase 1 completion report
→ STOP
```

Phase 2 is outside the executable boundary.

Completion of Phase 1 must not automatically trigger a follow-up analysis.

## 6. Reporting Behavior

Runtime reports are classified into three types.

### PROGRESS

Generated when an approved stage completes and validation passes.

```text
report
→ continue automatically
```

No human decision is required.

### REVIEW_REQUIRED

Generated when continuation would require human review.

```text
persist state
→ generate review report
→ stop execution
```

No downstream stage may run until a human decision is recorded.

### FAILURE

Generated when execution cannot safely continue because of a technical or validation failure.

```text
persist state
→ record failure
→ stop execution
```

The runtime must not silently recover from a failure if doing so could alter the approved research execution.

## 7. Stop Conditions

The runtime must enter `PAUSED_FOR_REVIEW` or `STOPPED` when:

* a Session 15 reproduction check fails;
* required input is missing or inconsistent;
* the expected number or identity of Phase 1A configurations is incorrect;
* required Run 1 or Run 2 output is missing;
* Phase 1B input ordering or finite-value validation fails;
* expected saved outputs fail reload validation;
* continuation would require a methodological choice not present in the frozen specification;
* execution attempts to exceed the Phase 1 authorization boundary.

Purely technical errors may be reported for human review before retry.

## 8. Resume Behavior

A paused run must not resume solely because the program is restarted.

Resume requires an explicit human decision associated with the pending review condition.

The runtime should then:

```text
load persisted state
→ verify the recorded human decision
→ identify the last valid checkpoint
→ resume only from an authorized stage
```

The exact command-line interface for recording and applying the human decision will be defined during implementation.

## 9. Runtime Outputs

Minimum agent-runtime records:

```text
research-agent/results/pilot-001/

runtime_state.json
runtime_execution_log.jsonl
runtime_report.md
```

Actual research outputs remain in the project locations defined by the frozen specification:

```text
results/session-21/
figures/session-21/
```

`runtime_report.md` records execution and validation status. It is not the final scientific Session 21 interpretation.

## 10. Explicit Non-Scope

Runtime v0.0.1 does not include:

* an LLM;
* conversational interaction;
* methodological proposal;
* automatic literature search;
* scientific interpretation;
* automatic code generation;
* cross-model audit;
* notifications or messenger integration;
* database or vector database infrastructure;
* multi-agent coordination;
* Phase 2 execution.

These capabilities may be considered only after the deterministic execution and pause/resume workflow has been evaluated.

## 11. Success Criteria

Runtime v0.0.1 is successful if it can:

1. load and respect the frozen Phase 1 execution boundary;
2. invoke only approved Session 21 analysis code;
3. execute Phase 1A before Phase 1B;
4. perform the required validation checkpoints;
5. continue automatically after a valid progress checkpoint;
6. persist state and stop when human review is required;
7. resume only after an explicit human decision;
8. preserve research outputs separately from agent-runtime records;
9. stop after Phase 1 completion without executing Phase 2.

The purpose of v0.0.1 is to validate controlled execution, not agent autonomy.
