# Implementation Planner v0.0.1 — Scope

* **Project:** bci-eeg-robot-control
* **Research-agent pilot:** Pilot 001
* **Research session:** Session 21
* **Planner version:** v0.0.1
* **Status:** FROZEN
* **Governing protocol:** `operating_protocol_v0.1.md`
* **Research specification:** `../results/pilot-001/pilot_spec.md`

## 1. Objective

Implementation Planner v0.0.1 is a read-only planning component.

It MUST:

1. read the frozen research specification;
2. inspect relevant Git-tracked project records;
3. reconcile relevant prior implementation and outputs;
4. distinguish reuse, extension, and new implementation requirements;
5. prepare an implementation proposal for human review.

The planner operates before implementation execution.

```text
FROZEN RESEARCH SPEC
→ repository inspection
→ prior-work reconciliation
→ implementation assessment
→ implementation proposal
→ human review
→ APPROVE / REVISE / REJECT

APPROVE
→ IMPLEMENTATION PLAN FREEZE
→ implementation
→ implementation validation
→ Runtime v0.0.1
```

The planner MUST stop after submitting its proposal.

The planner MUST NOT implement or execute the proposal.

---

## 2. Governing Input

The planner MUST load:

```text
research-agent/docs/operating_protocol_v0.1.md
research-agent/results/pilot-001/pilot_spec.md
```

The frozen research specification defines the research scope.

The planner MUST NOT:

* modify the frozen research specification;
* reinterpret the specification to expand its scope;
* introduce a methodological requirement not present in the specification.

If implementation requires a methodological decision outside the frozen specification, the planner MUST report it under `OPEN_DECISIONS`.

---

## 3. Repository Read Access

The planner MAY search any Git-tracked project file.

The planner MUST retrieve only files relevant to the current planning task.

The planner MUST NOT load the full repository into the LLM context by default.

Relevant files MAY include:

* project and milestone documentation;
* session and weekly notes;
* scripts and source code;
* configuration and metadata files;
* CSV and JSON outputs;
* validation records;
* frozen decisions and specifications;
* README and related project documentation.

For each material implementation judgment, the planner MUST retain the Git-tracked file path or paths supporting that judgment.

Historical records MAY provide context or evidence.

Historical records MUST NOT override the current governing protocol or frozen research specification.

The planner MUST NOT access:

* files outside the Git-tracked project scope;
* credentials or secrets;
* unrelated personal files;
* repository-internal `.git` data.

---

## 4. Tool Boundary

Implementation Planner v0.0.1 MUST expose read-only repository tools.

Minimum permitted operations are:

```text
SEARCH
READ
```

The planner MUST NOT be given tools that permit:

```text
WRITE
DELETE
EXECUTE
INSTALL
GIT COMMIT
GIT PUSH
```

The planner MUST NOT trigger Runtime v0.0.1.

The planner MUST NOT approve its own proposal.

---

## 5. Planning Responsibilities

### 5.1 Prior-Work Reconciliation

The planner MUST identify existing implementation, outputs, definitions, and validation records directly relevant to the frozen research specification.

It MUST determine whether each material implementation requirement is:

```text
REUSE
EXTENSION
NEW
```

### 5.2 Reuse Assessment

`REUSE` applies when an existing implementation or output can be used without material implementation change.

### 5.3 Extension Assessment

`EXTENSION` applies when an existing implementation provides the basis for the required work but requires modification or expansion within the frozen research specification.

### 5.4 New-Implementation Assessment

`NEW` applies when the planner does not identify a suitable existing implementation for the required function.

### 5.5 Validation Planning

The planner MUST identify:

* existing outputs that can serve as reproduction or consistency references;
* explicit validation requirements in the frozen specification;
* dependencies that must be satisfied before execution.

### 5.6 Execution Planning

The planner MUST propose an implementation and execution sequence.

The proposed sequence MUST remain within the frozen research specification.

### 5.7 Open-Decision Detection

The planner MUST identify unresolved decisions that prevent implementation approval.

The planner MUST NOT resolve such decisions autonomously.

---

## 6. Decision Metadata

Each material implementation judgment MUST include:

```text
PROJECT_RELATION:
REUSE | EXTENSION | NEW

BASIS:
one or more Git-tracked repository paths

RATIONALE:
1–3 sentences
```

### PROJECT_RELATION

Identifies the relationship between the proposed implementation item and existing project work.

### BASIS

Lists the repository record or records directly supporting the judgment.

### RATIONALE

States why the item was classified or proposed in that way.

No additional mandatory decision metadata is defined in v0.0.1.

Additional fields MAY be introduced only if later pilots identify a specific review need.

---

## 7. Planner Status

Every planner run MUST return exactly one top-level status:

```text
PLANNER_STATUS:
COMPLETE | BLOCKED
```

### COMPLETE

Use `COMPLETE` only when the planner has sufficient repository evidence to submit an implementation proposal for human review.

### BLOCKED

Use `BLOCKED` when the planner cannot produce a reliable implementation proposal.

A blocked result MUST include:

```text
PLANNER_STATUS:
BLOCKED

BLOCK_REASON:
MISSING_CONTEXT | ACCESS_ERROR | SPEC_CONFLICT | OTHER

DETAIL:
1–3 sentences

BASIS:
relevant repository path(s), if available
```

The planner MUST stop after returning `BLOCKED`.

The planner MUST NOT fill missing information by speculation.

---

## 8. Implementation Proposal

When `PLANNER_STATUS = COMPLETE`, the planner MUST return an **Implementation Proposal** containing the following sections.

### PRIOR_WORK

Identify relevant existing implementation, outputs, definitions, and validation records.

### REUSE

Identify items classified as `REUSE`.

### NEW_IMPLEMENTATION

Identify items classified as `EXTENSION` or `NEW`, and state what implementation work is required.

### VALIDATION

State how the proposed implementation will be checked against:

* existing reference outputs; and/or
* explicit requirements in the frozen specification.

### EXECUTION_PLAN

Provide the proposed implementation and execution order.

### OPEN_DECISIONS

Return exactly one of:

```text
OPEN_DECISIONS:
NONE
```

or:

```text
OPEN_DECISIONS:
REQUIRED
```

When `OPEN_DECISIONS = REQUIRED`, each decision MUST include:

```text
DECISION:
question requiring human judgment

BASIS:
relevant repository path(s)

IMPACT:
1–3 sentences describing what cannot be finalized until the decision is made
```

The planner MUST stop after submitting the proposal.

---

## 9. Human Review and Implementation-Plan Freeze

Human review MUST return exactly one status:

```text
HUMAN_REVIEW_STATUS:
APPROVED | REVISION_REQUIRED | STOP
```

### APPROVED

Use `APPROVED` when the current implementation proposal can proceed without modification.

An approved proposal MUST be converted into a frozen implementation plan before implementation begins.

```text
APPROVED
→ IMPLEMENTATION PLAN FREEZE
```

The planner MUST stop after the implementation plan is frozen.

### REVISION_REQUIRED

Use `REVISION_REQUIRED` only when the requested change can be made without modifying the frozen research specification.

The human reviewer MUST provide an explicit revision instruction.

The planner MAY:

* re-read relevant Git-tracked project files;
* revise the implementation proposal;
* update implementation judgments and their supporting `BASIS`.

The planner MUST NOT:

* modify the frozen research specification;
* execute code;
* modify project files.

The revised proposal MUST return to human review.

```text
REVISION_REQUIRED
→ human revision instruction
→ proposal revision
→ HUMAN REVIEW
```

### STOP

Use `STOP` when:

* the current planning cycle will not proceed;
* the current proposal is no longer being pursued; or
* the requested change requires modification of the frozen research specification.

```text
STOP
→ planner termination
```

The planner MUST NOT resume automatically after `STOP`.

A new planning run MAY begin only through explicit human initiation.

If `STOP` results from a required change to the frozen research specification, that specification MUST be reviewed and, if changed, re-approved and re-frozen before a new planner run begins.

The planner MUST NOT assign `HUMAN_REVIEW_STATUS` itself.

---

## 10. Handoff After Freeze

Only a frozen implementation plan may proceed to implementation.

For Pilot 001, implementation may remain human-assisted or manual.

Implementation MUST be validated before Runtime v0.0.1 executes the approved Session 21 workflow.

Runtime v0.0.1 remains responsible for:

* controlled execution;
* validation checkpoints;
* persistent runtime state;
* progress reporting;
* human-review pause;
* resume;
* stopping at the frozen Phase 1 execution boundary.

The planner does not inherit Runtime execution authority.

---

## 11. Explicit Non-Scope

Implementation Planner v0.0.1 MUST NOT perform:

* code execution;
* code modification;
* automatic code generation into the repository;
* scientific interpretation;
* methodological proposal outside the frozen research specification;
* research-scope expansion;
* specification revision;
* web or literature research;
* cross-model audit;
* notifications or messenger actions;
* Git write operations;
* multi-agent coordination.

---

## 12. Success Criteria

Implementation Planner v0.0.1 passes the pilot if it:

1. preserves the frozen research scope;
2. inspects relevant Git-tracked records without human file selection;
3. identifies relevant prior implementation and outputs;
4. correctly separates `REUSE`, `EXTENSION`, and `NEW`;
5. provides repository paths for material judgments;
6. identifies relevant validation references and dependencies;
7. returns `BLOCKED` rather than speculating when required evidence is unavailable;
8. exposes unresolved decisions under `OPEN_DECISIONS`;
9. produces a reviewable implementation proposal when `PLANNER_STATUS = COMPLETE`;
10. performs no project modification or code execution;
11. stops after proposal submission.
