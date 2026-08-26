# Agent Loop Operator Guide

## Purpose

Explain when AgentDefaults workflows should run as an agent loop, how the repository's formal Bounded Completion loop works, and how to operate it without creating unbounded retries, authority confusion, stale evidence, or false completion claims.

This is the operator-level guide. The canonical behavior remains defined by:

```text
agents/bounded-completion-lead.md
agents/bounded-completion-reviewer.md
skills/bounded-completion-orchestration.md
schemas/bounded-completion-*.schema.json
config/bounded-completion.json
scripts/bounded-completion.py
```

The VS Code/Copilot quickstart is [`../quickstarts/bounded-completion.md`](../quickstarts/bounded-completion.md).

## What Counts as an Agent Loop?

An agent workflow becomes a meaningful loop when it intentionally repeats a cycle based on new evidence until an explicit stop condition is reached.

A safe loop defines:

- objective;
- authoritative state;
- iteration boundary;
- evidence produced each cycle;
- retry/stuck-state policy;
- maximum attempts/time/cost;
- approval boundaries;
- termination conditions;
- escalation behavior.

“Keep working until it looks good” is not a safe loop.

## Three Operating Modes

AgentDefaults currently distinguishes three patterns.

| Pattern | Use when | Durable loop state? | Independent reviewer required? | Deterministic gate? |
|---|---|---:|---:|---:|
| **Normal single-agent task** | Scope is clear, deterministic verification is straightforward, one coherent pass is sufficient | No | No | Target checks only |
| **Iterative domain workflow** | The owning agent naturally cycles through inspect/change/verify/review but conversation/workspace state is enough | Usually no | Optional | Target checks only |
| **Bounded Completion** | Work needs durable state, independent challenge, repeated implementation/review, resumability and objective completion evidence | Yes | Yes | Yes |

Do not use Bounded Completion for every edit. Orchestration overhead is justified only when it materially improves reliability or recoverability.

## Formal Loop Included in This Repository

The only formal persisted control-plane loop currently shipped by AgentDefaults is **Bounded Completion**.

Codebase maintenance, agent design, research and other agents may contain internal iterative procedures, but they do not create `.agent-loop/` state unless Bounded Completion is deliberately overlaid.

This distinction matters because “iterative” does not automatically mean:

- durable state exists;
- a second model reviewed the work;
- stale evidence is invalidated;
- a hard iteration ceiling exists;
- a completion gate was evaluated.

## The Ownership Model

Always select the smallest correct **domain owner first**.

Examples:

```text
AI application defect
  -> Principal AI Engineer

Terraform/Jenkins/Ansible platform work
  -> Principal DevOps Engineer or relevant specialist

K8SHomelab Flux/Kubernetes work
  -> Kubernetes Homelab Engineer

Behavior-preserving cleanup
  -> Codebase Maintenance and De-Slop Engineer
```

Then, when justified, add Bounded Completion:

```text
domain owner supplies domain behavior and authority
                         ↓
Bounded Completion Lead owns integration/evidence lifecycle
                         ↔
Bounded Completion Reviewer independently challenges work
                         ↓
deterministic verification and completion gate
```

The loop **cannot broaden authority**. If the domain owner/task does not authorize production deployment, destructive mutation, credential rotation, release publishing or another side effect, the loop does not create that authority.

## When to Use Bounded Completion

Good candidates include:

- multi-file implementation with several acceptance criteria;
- release qualification where “all required evidence is current” matters;
- difficult bug fixing with repeated-failure risk;
- security/reliability hardening that benefits from independent challenge;
- visual/UI work that needs real artifact inspection;
- work likely to span several chat/model sessions;
- tasks where reviewer findings must be tracked to disposition;
- tasks where a final “done” claim must be machine-gated rather than subjective.

Prefer a normal workflow for:

- one small deterministic edit;
- documentation typo/formatting fixes;
- a read-only answer with no iterative mutation;
- work where no meaningful independent review or persisted state is needed.

## Prerequisites

For the current VS Code/Copilot workflow:

- open the target repository root;
- ensure Python 3 is available;
- choose the intended lead/reviewer models through the runtime when exact model IDs are not repository-discoverable;
- enable the custom-agent Stop hook only if your VS Code runtime supports it;
- prepare a task contract conforming to [`../../schemas/bounded-completion-task.schema.json`](../../schemas/bounded-completion-task.schema.json);
- define real acceptance criteria and verification commands rather than invented checks.

The repository currently records preferred model labels in [`../../config/bounded-completion.json`](../../config/bounded-completion.json). Those labels are not permission to guess provider-qualified model identifiers.

## Runtime State

The control plane creates ignored state under the **target repository**:

```text
.agent-loop/current/task-contract.json
.agent-loop/current/state.json
.agent-loop/current/findings.json
.agent-loop/logs/
.agent-loop/archive/
```

Responsibilities:

```text
task-contract.json
  stable task objective, acceptance criteria, verification, approvals and limits

state.json
  lifecycle, criteria state, iteration/review evidence and current completion status

findings.json
  reviewer findings, dispositions and resolution evidence

logs/
  verification output/evidence

archive/
  prior task state preserved during deliberate replacement/reset
```

Conversation memory is not authoritative loop state.

Do not manually edit these files when an equivalent `bounded-completion.py` command exists.

## Fastest Safe Start

1. Copy [`../../examples/bounded-completion-task.json`](../../examples/bounded-completion-task.json).
2. Replace the target, acceptance criteria, verification and approvals with the real task.
3. Select the appropriate domain owner conceptually.
4. In the supported VS Code flow select `Bounded Completion Lead` and the intended lead model.
5. Start through the runtime prompt or initialize directly.

CLI initialization:

```bash
python3 scripts/bounded-completion.py init --contract <contract.json>
```

Check state:

```bash
python3 scripts/bounded-completion.py status
```

Do not use `--replace-active` merely because the current task is inconvenient. It is for deliberately starting another task while archiving the active one.

## Lifecycle

A typical loop has these phases.

### 1. Contract and evidence map

The lead reads repository instructions and the task contract, then maps every acceptance criterion to concrete evidence.

A criterion should not become `SATISFIED` because the model says it is complete. Evidence must support that specific criterion.

### 2. Independent plan challenge

Before major implementation, obtain an independent reviewer challenge and record it:

```bash
python3 scripts/bounded-completion.py record-review \
  --kind plan \
  --summary "<review summary>"
```

If distinct-model evidence is required, only record that fact when the operator/runtime actually confirms the reviewer used a different model.

### 3. Coherent implementation increment

The domain behavior is applied in one understandable slice.

Advance the loop counter only for a genuine new implementation/review cycle:

```bash
python3 scripts/bounded-completion.py advance \
  --description "implemented <coherent slice>"
```

Do not increment it for trivial status reads or repeated identical attempts.

### 4. Verification

Run configured deterministic verification:

```bash
python3 scripts/bounded-completion.py verify
```

Verification may return:

```text
PASS
FAIL
TIMEOUT
UNAVAILABLE
```

Do not hide or reinterpret a failure as success.

### 5. Criterion evidence

Record supported criteria:

```bash
python3 scripts/bounded-completion.py criterion \
  --id AC-1 \
  --status SATISFIED \
  --evidence "<specific current evidence>"
```

A passing build does not automatically satisfy UI, security, migration, documentation or behavior-specific criteria.

### 6. Findings and dispositions

Every reviewer finding must be tracked and dispositioned.

Allowed dispositions are:

```text
accepted-blocking
accepted-non-blocking
rejected-with-evidence
duplicate-resolved
requires-user-input
deferred-out-of-scope
```

Add a structured finding:

```bash
python3 scripts/bounded-completion.py add-finding --from-file <finding.json>
```

Disposition it:

```bash
python3 scripts/bounded-completion.py dispose-finding \
  --id <finding-id> \
  --disposition accepted-blocking \
  --evidence "<why>"
```

Resolve accepted work with evidence:

```bash
python3 scripts/bounded-completion.py resolve-finding \
  --id <finding-id> \
  --evidence "<resolution evidence>"
```

Do not relabel a real accepted blocker as a duplicate merely to pass the gate.

### 7. Repeat only with material progress

If verification changes or a new finding gives a discriminating hypothesis, perform another coherent cycle.

If the same failure signature repeats without material progress, stop applying essentially the same fix. Obtain an independent diagnosis and create a test/observation capable of distinguishing competing explanations.

### 8. Final current-workspace evidence

After the last implementation change, record a current diff inspection:

```bash
python3 scripts/bounded-completion.py record-diff \
  --summary "<final diff inspection>"
```

Record validation integrity only after inspecting the current diff:

```bash
python3 scripts/bounded-completion.py record-integrity \
  --summary "<integrity review>" \
  --no-unrelated-destructive-change \
  --no-validation-weakening \
  --no-unjustified-test-disabling \
  --no-placeholder-implementation
```

Then run canonical verification **again** so the evidence is newer than the last implementation change.

### 9. Final independent review

Record final review against the same current workspace:

```bash
python3 scripts/bounded-completion.py record-review \
  --kind final \
  --summary "<final independent review>"
```

Where runtime/operator evidence actually confirms a distinct reviewer model, add the supported model identity arguments. Do not fabricate them.

### 10. Gate

Evaluate completion:

```bash
python3 scripts/bounded-completion.py gate
```

Only a passing deterministic gate may transition the durable task to `COMPLETE`.

If it does not pass, the returned reasons are the next evidence/blocker list.

## Evidence Freshness

Bounded Completion fingerprints the workspace using Git `HEAD` plus changed/untracked workspace content while excluding `.agent-loop/`.

This prevents stale evidence from satisfying completion after later code/config/artifact changes.

A material workspace change can invalidate previous:

- verification;
- final review;
- final diff inspection;
- integrity assertions;
- visual review.

This is intentional.

The safe final ordering is:

```text
last implementation change
        ↓
current diff/integrity inspection
        ↓
canonical verification
        ↓
final independent review
        ↓
gate
```

If you change the workspace after those steps, regenerate the affected evidence.

## Visual Criteria

Rendered/UI criteria require a real artifact.

Example:

```bash
python3 scripts/bounded-completion.py record-visual \
  --criterion AC-UI-1 \
  --artifact artifacts/screenshot.png \
  --inspected-by "<reviewer identity>" \
  --review "No clipping at the required viewport"
```

Source inspection is not visual approval.

If the workspace changes in a way that can affect the rendered result, regenerate/reinspect the artifact before expecting the gate to accept it.

Do not invent screenshots, report an unavailable emulator/browser as visually verified, or use a stale artifact from a previous build.

## Approval-Gated Work

Some task contracts may require explicit approval evidence.

Record only trusted approval:

```bash
python3 scripts/bounded-completion.py approve \
  --name production-change \
  --source operator-confirmed \
  --evidence "User explicitly approved this named operation"
```

Supported provenance is controlled by the CLI/schema. An agent saying “approved” is not operator approval.

Tool availability is not authorization.

## Reviewer Model Independence

Independent review is useful because it can reduce correlated reasoning failures, but only if independence is real.

The repository intentionally does not commit guessed provider/model IDs for local registrations.

Therefore:

- a VS Code native subagent may inherit the lead model;
- same-model review may still provide useful challenge;
- `--distinct-model-confirmed` is valid only when operator/runtime evidence confirms the reviewer actually ran on a distinct model;
- when the gate requires distinct-model evidence and automatic delegation cannot prove it, use a manual reviewer handoff or escalate.

Do not solve model-identity uncertainty by inventing an identifier.

## Stop Hook

The Copilot lead adapter can use a scoped `Stop` hook when supported.

Its role is narrow:

1. evaluate the deterministic gate when the agent attempts to stop;
2. allow stop if the gate passes;
3. block once for another continuation when allowed;
4. avoid recursive continuation by checking `stop_hook_active`;
5. escalate after the configured continuation ceiling.

The default config currently bounds Stop-hook continuation. The hook is a convenience, not the source of completion truth.

If hooks are disabled or unavailable, run the gate manually.

## Bounded Limits

Defaults live in [`../../config/bounded-completion.json`](../../config/bounded-completion.json), including limits for:

- full loop iterations;
- repeated unchanged failure attempts;
- plan/final review rounds;
- verification/subagent timeouts;
- retained verification logs;
- unchanged state iterations;
- Stop-hook continuations.

Task-specific overrides may tighten limits where supported. They must not silently widen safety bounds.

The point of the limits is to convert “keep trying” into a controlled engineering process.

## Status and Troubleshooting

Read current state:

```bash
python3 scripts/bounded-completion.py status
```

Use CLI help for the authoritative command surface:

```bash
python3 scripts/bounded-completion.py --help
python3 scripts/bounded-completion.py record-review --help
```

Exit semantics for `verify` and `gate`:

```text
0  passed
1  ran but did not pass
2  control-plane/input/JSON/OS error
```

### Common mistakes

**Reinitializing instead of resuming**

Use `status` and the resume prompt. Do not destroy continuity because the chat changed.

**Treating conversation memory as state**

Read `.agent-loop/` through the control plane and inspect the actual Git workspace.

**Marking criteria satisfied from generic test success**

Attach evidence specific to each criterion.

**Repeating the same fix**

After repeated identical failure evidence, obtain independent diagnosis and a discriminating test.

**Reviewer churn**

A finding needs materially new evidence before reopening after resolution.

**Stale final review**

Any material post-review workspace change can invalidate final evidence.

**Claiming distinct-model review without proof**

Use operator/runtime confirmation only.

**Using the loop to broaden authority**

The domain owner/task remains the authority boundary.

**Weakening validation to pass the gate**

Never disable, dilute or bypass required checks merely to obtain `COMPLETE`.

**Manually editing state**

Use the control-plane command that owns the invariant.

## Resume

Resume rather than reinitialize.

In the supported VS Code flow use the canonical resume prompt. The operator intent is:

```text
read active task/state/findings/logs
+ inspect current Git diff/workspace
+ reconcile recorded evidence with reality
+ continue from the recorded next action
```

Do not discard unresolved findings.

## Safe Reset / New Task

To deliberately start another task while preserving history:

```bash
python3 scripts/bounded-completion.py init \
  --contract <new-contract.json> \
  --replace-active
```

The current state is archived rather than silently deleted.

## Escalation

Escalation is a valid terminal outcome when further autonomous work is unsafe, impossible, or no longer productive.

Persist it:

```bash
python3 scripts/bounded-completion.py escalate \
  --reason "<specific blocker>"
```

A useful escalation states:

1. current task status;
2. exact incomplete criteria;
3. current blockers;
4. verification failures/logs;
5. actions already attempted;
6. why another similar attempt is not justified;
7. smallest required user decision/input;
8. safe options;
9. whether the state is resumable.

Escalation is preferable to endless retrying or pretending the gate passed.

## Using an Iterative Domain Workflow Without Bounded Completion

Example: codebase maintenance.

The maintenance agent intentionally follows a cycle similar to:

```text
inspect real repository/toolchain
        ↓
map compatibility surfaces
        ↓
baseline
        ↓
find evidence-backed maintenance issues
        ↓
implement one coherent slice
        ↓
verify
        ↓
second-pass diff/de-slop review
```

That workflow is often sufficient by itself.

Add Bounded Completion when you additionally need:

- persistent resume state;
- independently tracked findings;
- a reviewer separate from the implementation role;
- formal visual/approval evidence;
- an objective gate before declaring the overall task complete.

Do not create a second ad-hoc state machine inside the maintenance agent.

## Designing New Loops

Use [`../../agents/agent-architect-builder.md`](../../agents/agent-architect-builder.md) and [`../quickstarts/agent-builder.md`](../quickstarts/agent-builder.md).

Before adding another formal loop, justify why normal deterministic orchestration or an existing agent workflow is insufficient.

A production-quality loop should define:

```text
goal
authoritative state
iteration transition
allowed tools/permissions
retryable vs terminal failures
timeout/cancellation
idempotency/duplicate behavior
budget/iteration limits
checkpoint/recovery
review/approval boundaries
telemetry/audit evidence
completion gate
escalation
```

Never rely on the model voluntarily deciding to stop.

## Validation

For Bounded Completion implementation/control-plane changes, run:

```bash
python3 scripts/validate-bounded-completion.py
python3 scripts/validate-agentdefaults.py
```

For documentation-only loop changes, canonical repository validation is still required when an execution environment is available:

```bash
python3 scripts/validate-agentdefaults.py
```

Do not claim these checks passed unless they actually ran.
