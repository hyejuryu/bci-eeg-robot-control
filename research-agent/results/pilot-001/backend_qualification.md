# Pilot 001 — Implementation Planner Backend Qualification

* **Date:** 2026-08-09
* **Component:** Implementation Planner v0.0.1
* **Purpose:** Backend selection for the first LLM-dependent stage of the research-agent workflow
* **Evaluated configurations:**

  * OpenAI Responses API — `gpt-5.6-sol`, reasoning effort `medium`
  * Ollama native chat — `gpt-oss:20b`, thinking `high`, context length `32768`
* **Subsequently frozen implementation commit:** `b52011a820d8347fc5d31713f812a45904a4a9d1`

## 1. Purpose

The research agent was designed around the following human-supervised workflow:

```text
current research context
→ method / implementation proposal
→ human review and approval
→ specification freeze
→ implementation
→ deterministic execution and validation
→ intermediate / final reporting
```

The Implementation Planner is the first stage in this workflow where an LLM materially participates. Its role is to read the frozen research specification and existing repository records and prepare an implementation proposal.

Before proceeding with the full Planner workflow, an API-based backend and a local backend were evaluated for suitability under the Planner's repository-access and execution constraints.

The qualification focused on whether each backend could execute the minimum required repository tool loop within explicitly defined procedural boundaries.

## 2. Candidate Selection and Test Configuration

### 2.1 OpenAI Backend

The OpenAI Responses API was selected as the API-based reference backend.

OpenAI models were already used in the existing research workflow, and the API environment was available. `gpt-5.6-sol` with `medium` reasoning effort was therefore used as the reference configuration for the initial Planner tool-loop qualification.

### 2.2 Local Backend

The local backend was implemented through Ollama.

The test environment was a Windows laptop with approximately 16 GB of RAM. The initial local candidate was selected to maximize practical reasoning capability within the available hardware.

`gpt-oss:20b` was tested first. Context length was increased incrementally to verify local feasibility:

```text
4K
→ 8K
→ 16K
→ 32K
```

The model remained executable at `32K`, but physical memory usage approached the available limit and substantial pagefile use was observed. A context length of `32768` tokens was therefore adopted as the practical ceiling for the current hardware.

Because local inference did not incur an additional per-call API charge, the reasoning setting was kept at `thinking=high`.

The final qualification configurations were:

```text
OpenAI
model: gpt-5.6-sol
reasoning_effort: medium

Local
runtime: Ollama
model: gpt-oss:20b
thinking: high
context_length: 32768
```

If the 20B configuration proved impractical on the current hardware, a smaller model in the Qwen 9B range was planned as a subsequent candidate.

## 3. Qualification Procedure and Observations

### 3.1 Smoke-Test Contract

A repository tool-loop smoke test was used before full Implementation Planner execution.

Both backends received the same repository tools and were required to execute the following sequence:

```text
1. SEARCH "decision_rule" exactly once
2. Select one Python file representing the offline decision-rule implementation
3. READ the selected file exactly once
4. Perform no additional repository operation
5. Return exactly:
   TOOL_LOOP_OK: <repository path>
```

The smoke test defined the bounded repository tool-use contract used for backend qualification.

### 3.2 OpenAI Result

`gpt-5.6-sol / medium` completed the required sequence as specified.

```text
Validator status: PASS
Model turns: 3
Tool calls: 2
SEARCH calls: 1
READ calls: 1

Final selected path:
scripts/10_eegbci_offline_decision_rule.py

Cumulative input tokens: 3,753
Cumulative output tokens: 83
Backend wall time: 7.65 s
```

The observed sequence was:

```text
Turn 1 → SEARCH
Turn 2 → READ
Turn 3 → TOOL_LOOP_OK
```

### 3.3 First Local Smoke Run

`gpt-oss:20b / high / 32K` successfully invoked the repository SEARCH and READ tools and ultimately selected an appropriate implementation file.

However, the model performed an additional READ after the required READ:

```text
SEARCH calls: 1
READ calls: 2
```

At that point, the smoke validator checked minimum tool counts rather than exact contract compliance and reported the run as `PASS`.

This run identified a gap between the written smoke-test contract and its deterministic validation.

### 3.4 Validator Revision and Local Retest

The smoke validator was revised to enforce the following conditions directly:

```text
model_turns = 3
search_calls = 1
read_calls = 1
tool_calls = 2
read_history entries = 1
final reported path = actual READ path
```

The same local configuration was then tested again.

```text
Validator status: FAIL
Model turns: 8
Tool calls: 7
SEARCH calls: 1
READ calls: 6
Unique inspected paths: 2

Final selected path:
scripts/10_eegbci_offline_decision_rule.py

Cumulative input tokens: 31,812
Cumulative output tokens: 1,634
Backend wall time: 1,328.60 s
```

The local backend completed tool invocation, result routing, multi-turn interaction, and final response generation.

During the run, it repeatedly READ portions of:

```text
src/bci_robot/decision_rule.py
scripts/10_eegbci_offline_decision_rule.py
```

and exceeded the repository-operation limit defined by the smoke-test contract.

Additional READ operations occurred in both observed local smoke runs.

## 4. Result and Backend Decision

Both backends successfully used the repository tools and ultimately selected the same decision-rule implementation file.

The qualification outcome differed at the procedural level:

```text
GPT-5.6 Sol / Medium
→ smoke contract PASS

gpt-oss:20b / High / 32K
→ repository tool loop operational
→ smoke contract FAIL
```

Implementation Planner v0.0.1 uses `MUST` and `MUST NOT` requirements to define repository-access and execution boundaries. Compliance with these boundaries was treated as a prerequisite for full Planner evaluation.

The local configuration did not satisfy this prerequisite in the observed smoke runs and was therefore not advanced to a full Implementation Planner run.

The OpenAI Responses API was selected as the operational backend for the current pilot.

The 20B result was not used to infer the performance of smaller local models. Evaluation of a Qwen 9B-class model was deferred because an operational backend had already been identified and further local-model benchmarking was not required for the current backend decision.

## 5. Follow-up

The current pilot will continue with the OpenAI backend for the Implementation Planner workflow based on the frozen S21 research specification.

The same smoke-test harness can be reused if local inference is evaluated again under different model or hardware conditions.

Potential follow-up conditions include:

* a smaller local model such as Qwen 9B;
* alternative local inference settings;
* hardware with greater available memory;
* revised deterministic enforcement of repository tool boundaries.

The `gpt-oss:20b / high / 32K` smoke results are retained as the current local-backend baseline.