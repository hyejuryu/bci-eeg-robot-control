# Research Agent Pilot 001 — Pilot Log

* **Project:** bci-eeg-robot-control
* **Research session:** Session 21
* **Pilot:** Research Agent Pilot 001
* **Status:** Ongoing
* **Current stage:** Analysis specification frozen; execution not yet started
* **Governing protocol:** `research-agent/docs/operating_protocol_v0.1.md`
* **Frozen specification:** `pilot_spec.md`

## 1. Purpose

This log records material workflow events, human decisions, and agent-design observations arising during Research Agent Pilot 001.

It is not a transcript of the full research discussion.

Only information relevant to research decisions, workflow behavior, execution boundaries, or future agent implementation is retained.

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

No automated agent runtime or direct tool access was used during this phase.

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

Any material methodological change requires a new human decision and, where appropriate, a new specification version.

---

## 3. Agent-Design Observations

### O01 — Prior-work reconciliation was insufficient before the initial proposal

During early method proposal and planning, the agent treated some smoothing- and dwell-related analyses as if they were new Session 21 work.

Review of the existing Session 15 records showed that several corresponding configurations had already been evaluated.

Further reconciliation established that Session 21 was intended to:

* complete the decision-rule parameter grid deferred from Session 15; and
* extend the existing feature-variability analysis with a temporal-variability axis.

The analysis plan was revised before specification freeze.

#### Design implication

A future agent should explicitly reconcile prior project state before proposing new work.

The minimum project-relation labels identified during this pilot are:

```text
NEW
DEFERRED
EXTENSION
COMPLETED
```

These labels are intended to make the relationship between a proposal and prior work visible to human review.

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

Evaluate after Pilot 001 whether a future protocol should explicitly represent:

```text
analysis plan
→ human approval
→ specification freeze
→ execution authorization
→ execution
```

A future agent runtime should treat freeze as an explicit state rather than relying only on conversational agreement.

---

### O03 — Method proposals need visible evidence positioning

During discussion of successive feature-change measures, human review required clarification of:

* the methodological basis of the proposed measure;
* whether the method was established, emerging, or project-defined;
* whether the cited literature directly supported the proposed use;
* how the proposal related to analyses already present in the project.

This showed that attaching citations alone is insufficient for efficient human review.

#### Design implication

Method proposals should expose a minimal set of non-overlapping decision metadata:

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

The purpose of these labels is not to restrict methodological exploration, but to make the basis of agent judgment visible and reviewable.

Relevant primary or methodological sources should be identified where applicable, and project-defined extensions should be labeled explicitly.

---

### O04 — Canonical bibliographic metadata should be maintained through Zotero

Bibliographic details may vary slightly across publisher pages, repositories, and manually entered citations.

#### Decision

For research records and final reference lists, use:

```text
DOI / original source
→ Zotero record
→ canonical project citation metadata
```

Zotero will serve as the canonical bibliographic record for references retained in the project.

Relevant papers should also be linked to their methodological role in the corresponding session records or Zotero collection.

---

### O05 — Human-review language and canonical artifact language can be separated

The human researcher identified a practical need to review plans and approval requests quickly while away from the development environment.

English remains appropriate for canonical repository artifacts, while Korean review versions improve rapid human review.

#### Decision

Treat review language as a human-interface preference rather than a research-governance rule.

A future agent configuration may support:

```text
canonical_artifact_language: en
human_review_language: ko
```

No change to `operating_protocol_v0.1.md` is required on this basis alone.

---

### O06 — Independent model audit should be optional and human-triggered

An independent second-model audit of the frozen Session 21 Phase 1 specification was considered but not performed.

The useful design distinction was not a fixed list of mandatory audit cases, but whether additional independent review would materially improve confidence before freeze.

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

Independent model review should remain an optional review layer rather than a mandatory checkpoint.

When used, the independent model functions as an error-detection reviewer.

Final adjudication remains human-controlled.

---

### O07 — Hard constraints and judgment metadata should serve different roles

Pilot discussion showed that not every desirable behavior should be converted into a prohibition or mandatory rule.

Some requirements concern execution safety or reproducibility and should be structurally enforced.

Other decisions require contextual judgment and are better exposed to human review through compact decision metadata.

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

is an execution boundary and should be enforced structurally.

By contrast, judgments such as:

```text
Is this method established?
How direct is the evidence?
Is this new work or an extension?
Is an independent audit useful?
```

should remain reviewable judgments rather than being converted prematurely into rigid rules.

The appropriate metadata set should remain minimal and may be revised after additional pilots.

---

## 4. Current Pre-Execution Findings

The manual portion of Pilot 001 has identified the following provisional requirements for future agent implementation:

1. prior-work reconciliation before method proposal;
2. explicit specification-freeze state;
3. minimal decision metadata for methodological proposals;
4. canonical bibliographic records through Zotero;
5. separation of canonical artifact language and human-review language;
6. optional human-triggered independent model audit;
7. separation of hard execution constraints from reviewable agent judgments.

These findings remain provisional until the execution, validation, reporting, and retrospective phases of Pilot 001 are completed.

---

## 5. Pending Evaluation

The following stages have not yet been evaluated:

```text
frozen specification
→ tool-enabled execution
→ intermediate reporting
→ validation
→ final reporting
→ follow-up proposal
→ pilot retrospective
```

Additional observations should be appended during or after those stages rather than retrospectively rewriting earlier entries.
