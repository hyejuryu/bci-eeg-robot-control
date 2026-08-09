# Research Agent Pilot 001 — Pilot Log

* **Project:** bci-eeg-robot-control
* **Research session:** Session 21
* **Pilot:** Research Agent Pilot 001
* **Status:** Ongoing
* **Current stage:** Operational Implementation Planner run completed; implementation proposal under human review; analysis execution not yet started
* **Governing protocol:** `research-agent/docs/operating_protocol_v0.1.md`
* **Frozen specification:** `pilot_spec.md`

## 1. Purpose

This log records material workflow events, human decisions, and agent-design observations arising during Research Agent Pilot 001.

It retains information directly relevant to:

* research decisions;
* workflow behavior;
* execution boundaries; and
* observations affecting future agent implementation.

---

## 2. Pilot Workflow Record

### E01 — Manual workflow initiated

The initial phase of Session 21 was conducted as a manual simulation of the human-supervised research-agent workflow.

The workflow proceeded as:

```text
project-context review
→ method proposal
→ methodological discussion
→ analysis-plan proposal
→ human review
→ human approval
→ specification freeze
```

#### Interaction environment

The manual phase was conducted in a task-focused chat within the ChatGPT web project workspace.

```text
interface: ChatGPT web
model: GPT-5.6
reasoning setting: High
context environment: project workspace
repository-connected SEARCH / READ tools: none
automated execution runtime: none
```

The initial task requested review of the existing EEG-BCI project state through Session 20, reference to the Research Agent design context, proposal of candidate Session 21 analyses, and requests for additional material where needed.

Project context was available through the project workspace. Additional project records and Session 14/15 result artifacts were supplied during the discussion as needed.

Methodological discussion, revision, approval, and specification freeze remained human-supervised throughout this phase.

### E02 — Analysis plan approved and specification frozen

Following methodological discussion and revision, the Session 21 Phase 1 analysis plan was human-approved and formalized as the frozen executable specification.

The authorized scope is:

```text
Phase 1A
Complete 18-configuration decision-rule parameter grid

Phase 1B
Temporal feature-variability analysis

Phase 2A
Not authorized

Phase 2B
Not authorized
```

Execution must remain within the frozen Phase 1 specification.

A material methodological change requires a new human decision and, where applicable, a new specification version.

### E03 — Planner backend qualified and selected

An OpenAI API backend and a local Ollama backend were evaluated with a repository tool-loop smoke test before selecting the first operational Implementation Planner backend.

`gpt-5.6-sol / medium` satisfied the bounded SEARCH–READ contract.

`gpt-oss:20b / high / 32K` completed the repository tool loop but exceeded the permitted READ boundary in both observed smoke runs.

#### Decision

Use the OpenAI Responses API as the operational Implementation Planner backend for Pilot 001.

Do not advance the tested local configuration to a full Planner evaluation in the current pilot.

Detailed record:

`research-agent/results/pilot-001/backend_qualification.md`

---

## 3. Agent-Design Observations

### O01 — Prior-work reconciliation was insufficient before the initial proposal

During the manual ChatGPT-based planning phase, the model retrieved and discussed relevant prior work from Sessions 14 and 15, including previous smoothing, dwell, feature-variability, and decision-rule analyses.

The initial Session 21 proposal nevertheless treated several smoothing- and dwell-related analyses as new work.

Subsequent review of the existing Session 15 records showed that corresponding configurations had already been evaluated.

Further reconciliation established that Session 21 was intended to:

* complete the decision-rule parameter grid deferred from Session 15; and
* extend the existing feature-variability analysis with a temporal-variability axis.

The analysis plan was revised before specification freeze.

This observation identifies a workflow-level reconciliation gap: relevant prior work may be available and discussed without its relationship to each newly proposed analysis being consistently classified.

The pilot record does not attribute this gap to a specific model, interface, context-retrieval mechanism, or prompt component.

#### Design implication

A future agent should explicitly reconcile each proposed item against prior project state before presenting it for human review.

The minimum project-relation labels identified during this pilot are:

```text
NEW
DEFERRED
EXTENSION
COMPLETED
```

These labels make the relationship between a proposal and prior work directly reviewable by the human researcher.

---

### O02 — Human approval and specification freeze are distinct workflow states

The governing protocol defines human approval before execution but does not explicitly identify specification freeze as a separate state.

During Pilot 001, a practical distinction emerged between:

```text
human approval
```

and:

```text
frozen executable specification
```

The approved Session 21 Phase 1 plan was therefore formalized as `pilot_spec.md` before execution.

#### Decision

Do not modify `operating_protocol_v0.1.md` during the active pilot.

After Pilot 001, evaluate whether a future protocol should explicitly represent:

```text
analysis plan
→ human approval
→ specification freeze
→ execution authorization
→ execution
```

A future agent runtime should represent freeze as an explicit workflow state.

---

### O03 — Method proposals need visible evidence positioning

During review of successive feature-change measures, human review required the following information:

* the methodological basis of the proposed measure;
* the current methodological status of the measure;
* how directly the cited literature supports the proposed use; and
* how the proposal relates to analyses already present in the project.

This indicated a need for compact decision metadata alongside methodological references.

#### Design implication

Method proposals should expose:

```text
METHOD_STATUS
EVIDENCE_BASIS
PROJECT_RELATION
RATIONALE
```

Initial label sets:

```text
METHOD_STATUS:
ESTABLISHED
EMERGING
PROJECT_DEFINED
```

```text
EVIDENCE_BASIS:
DIRECT
ADJACENT
INSUFFICIENT
```

```text
PROJECT_RELATION:
NEW
DEFERRED
EXTENSION
COMPLETED
```

`RATIONALE` should remain a short free-text explanation of why the method is being proposed for the current research question.

Relevant primary or methodological sources should be linked where applicable, and project-defined extensions should be labeled explicitly.

---

### O04 — Canonical bibliographic metadata should be maintained through Zotero

Bibliographic details may differ across publisher pages, repositories, and manually entered citations.

#### Decision

Use the following path for project reference metadata:

```text
DOI / original source
→ Zotero record
→ canonical project citation metadata
```

Zotero serves as the canonical bibliographic record for references retained in the project.

Retained papers should also be linked to the methodology or decision they support in the corresponding session record or Zotero collection.

---

### O05 — Human-review language and canonical artifact language can be separated

The human researcher identified a need to review plans and approval requests efficiently outside the development environment.

Canonical repository artifacts remain in English, while Korean versions may be used for human review.

#### Decision

Treat review language as a human-interface configuration rather than a research-governance rule.

A future agent configuration may support:

```text
canonical_artifact_language: en
human_review_language: ko
```

No change to `operating_protocol_v0.1.md` is required on this basis alone.

---

### O06 — Independent model audit should be optional and human-triggered

An independent second-model audit of the frozen Session 21 Phase 1 specification was considered but not performed.

The relevant decision was whether additional independent review would materially improve confidence before freeze.

#### Proposed decision flow

```text
Agent draft
→ human review
→ [AUDIT_DECISION]
      ├─ NOT_REQUIRED → freeze
      └─ REQUIRED
            ↓
     independent model audit
            ↓
       human adjudication
            ↓
           freeze
```

Minimal decision metadata:

```text
AUDIT_DECISION:
REQUIRED | NOT_REQUIRED

RATIONALE:
short human-reviewable explanation
```

#### Decision

Independent model review should remain an optional review layer.

When used, the independent model functions as an error-detection reviewer.

Final adjudication remains human-controlled.

---

### O07 — Hard constraints and judgment metadata should serve different roles

Pilot discussion showed that execution constraints and contextual judgments require different forms of control.

Conditions directly related to execution safety or reproducibility should be structurally enforced.

Context-dependent judgments should remain visible to human review through compact decision metadata.

#### Design implication

Use:

```text
few hard execution constraints
+
minimal, non-overlapping decision metadata
```

For example:

```text
SPEC_STATUS != FROZEN
→ execution unavailable
```

is an execution boundary and can be enforced structurally.

By contrast, questions such as:

```text
Is this method established?
How direct is the evidence?
Is this new work or an extension?
Is an independent audit useful?
```

remain contextual judgments and should be exposed for review rather than converted prematurely into rigid rules.

The metadata set should remain minimal and may be revised after additional pilots.

---

### O08 — Repository-wide context access suggested a separate planning responsibility

After Runtime v0.0.1 was frozen, the role of planned repository-wide read access was reconsidered.

Broad Git-tracked repository access was primarily required for:

* inspecting prior implementations;
* reconciling completed and deferred work;
* identifying reusable code and existing outputs; and
* preparing an implementation proposal before execution.

These responsibilities are distinct from deterministic execution of an approved specification.

#### Design implication

Evaluate a separate read-only **Implementation Planner** responsible for:

```text
Git-tracked repository inspection
→ prior-work reconciliation
→ reuse / new-implementation assessment
→ implementation proposal
→ human review
```

The execution runtime remains responsible for controlled execution, validation, state persistence, pause, and resume.

Runtime v0.0.1 remains unchanged as the frozen Pilot 001 baseline. Any future change to its read authority should be introduced through an explicit version revision.

---

### O09 — Deterministic validation is required for bounded tool use

In the first local repository smoke run, `gpt-oss:20b / high / 32K` performed an additional READ after the required single READ.

The initial smoke validator checked minimum call counts and reported the run as `PASS`.

The validator was revised to inspect exact tool counts and read history.

The same local configuration was then tested again. Additional repository READ operations occurred again, and the strengthened validator returned `FAIL`.

#### Design implication

Separate LLM instruction from deterministic execution enforcement.

Tool-use boundaries defined by material `MUST` and `MUST NOT` requirements should be checked by deterministic validation or runtime control when their violation affects the permitted execution path.

Detailed backend qualification record:

`research-agent/results/pilot-001/backend_qualification.md`

---

### O10 — Exploratory full-run retrieval behavior

The exploratory `gpt-5.6-sol / medium` full Planner run completed with:

```text
PLANNER_STATUS: COMPLETE

tool_calls: 30 / 30
search_calls: 15
read_calls: 15
```

The trace showed that some governing records already supplied through the governing-document loader were subsequently READ again through the LLM repository tool.

Observed duplicate governing-record retrieval included:

```text
operating_protocol_v0.1.md
pilot_spec.md
```

The run also surfaced implementation definitions requiring human review rather than resolving them internally.

#### Decision

Retain governing-context duplicate retrieval and tool-budget headroom as Implementation Planner retrospective candidates.

Retrieval policy was not modified before the operational Planner run.

---

## 4. Current Agent-Design Findings

Pilot 001 has identified the following provisional requirements for future agent implementation:

1. explicit prior-work reconciliation before method proposal;
2. explicit specification-freeze state;
3. minimal decision metadata for methodological proposals;
4. canonical bibliographic records through Zotero;
5. separation of canonical artifact language and human-review language;
6. optional human-triggered independent model audit;
7. separation of hard execution constraints from reviewable agent judgments;
8. separation of read-only implementation planning from deterministic execution runtime; and
9. deterministic validation of bounded tool use.

These findings will be reassessed after the execution, validation, reporting, and retrospective stages of Pilot 001.

---

## 5. Pending Evaluation

The operational Implementation Planner run has been completed, and its implementation proposal is under human review.

The remaining workflow stages are:

```text
approved implementation plan
→ deterministic analysis execution
→ intermediate reporting
→ validation
→ final reporting
→ follow-up proposal
→ pilot retrospective
```

Additional observations should be appended from the results of those stages.
