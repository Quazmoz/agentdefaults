# Bounded Completion Quick Reference

## Purpose

Provide the shortest safe operator path for the repository's persisted Bounded Completion loop. Use this during day-to-day operation; use [`README.md`](README.md) for the complete model, rationale, troubleshooting, security, and loop-design guidance.

Bounded Completion is an orchestration overlay. Choose the correct domain owner first; the loop does not widen authority or approvals.

## Start or Resume?

```text
new task, no active loop
  -> init

same task after chat/session interruption
  -> status + resume

new task while another loop is active
  -> init --replace-active (archives prior state)
```

Never reinitialize merely because the conversation changed.

## New Task

1. Copy `examples/bounded-completion-task.json`.
2. Replace the example acceptance criteria, verification argv, approvals, and target with real task data.
3. Initialize:

```bash
python3 scripts/bounded-completion.py init --contract <contract.json>
```

4. Confirm state:

```bash
python3 scripts/bounded-completion.py status
```

5. Obtain and record the plan challenge before major implementation.

## Normal Iteration

For each genuine implementation/review cycle:

```bash
python3 scripts/bounded-completion.py advance \
  --description "implemented <coherent slice>"

python3 scripts/bounded-completion.py verify
```

Record criterion evidence only when it proves that criterion:

```bash
python3 scripts/bounded-completion.py criterion \
  --id AC-1 \
  --status SATISFIED \
  --evidence "<specific evidence>"
```

Do not advance the counter for status checks or repeat the same failed strategy indefinitely.

## Reviews

Plan challenge:

```bash
python3 scripts/bounded-completion.py record-review \
  --kind plan \
  --summary "<review summary>"
```

Final review:

```bash
python3 scripts/bounded-completion.py record-review \
  --kind final \
  --summary "<final review summary>"
```

Only add distinct-model confirmation when the operator/runtime actually proves a different reviewer model ran.

## Findings

Add:

```bash
python3 scripts/bounded-completion.py add-finding --from-file <finding.json>
```

Disposition:

```bash
python3 scripts/bounded-completion.py dispose-finding \
  --id <finding-id> \
  --disposition <allowed-disposition> \
  --evidence "<why>"
```

Resolve accepted work:

```bash
python3 scripts/bounded-completion.py resolve-finding \
  --id <finding-id> \
  --evidence "<resolution evidence>"
```

Allowed dispositions:

```text
accepted-blocking
accepted-non-blocking
rejected-with-evidence
duplicate-resolved
requires-user-input
deferred-out-of-scope
```

## Visual Criterion

A visual criterion needs a real inspected artifact:

```bash
python3 scripts/bounded-completion.py record-visual \
  --criterion AC-UI-1 \
  --artifact artifacts/screenshot.png \
  --inspected-by "<reviewer identity>" \
  --review "<actual visual inspection>"
```

Source inspection is not visual approval.

## Required Approval

Record only trusted approval provenance:

```bash
python3 scripts/bounded-completion.py approve \
  --name <approval-name> \
  --source operator-confirmed \
  --evidence "<explicit approval evidence>"
```

An agent statement is not operator approval.

## Safe Final Ordering

After the **last implementation change**:

```bash
python3 scripts/bounded-completion.py record-diff \
  --summary "<current final diff inspection>"

python3 scripts/bounded-completion.py record-integrity \
  --summary "<integrity review>" \
  --no-unrelated-destructive-change \
  --no-validation-weakening \
  --no-unjustified-test-disabling \
  --no-placeholder-implementation

python3 scripts/bounded-completion.py verify

python3 scripts/bounded-completion.py record-review \
  --kind final \
  --summary "<final independent review>"

python3 scripts/bounded-completion.py gate
```

The order matters because workspace changes can invalidate stale verification, review, diff/integrity, and visual evidence.

## If the Gate Fails

Use the returned reasons as the next blocker/evidence list.

```bash
python3 scripts/bounded-completion.py status
```

Do not weaken tests, relabel blockers, fabricate visual/model evidence, or bypass approvals to obtain `COMPLETE`.

## If the Same Failure Repeats

Stop repeating essentially the same change.

Required response:

```text
independent diagnosis
  -> discriminating test/observation
  -> materially different correction
  -> verify again
```

Escalate when configured limits or unavailable required capabilities make further autonomous work unsafe or unproductive.

## Resume

Read durable state and the actual Git workspace, then continue from the recorded next action. Do not discard unresolved findings.

## New Task / Safe Reset

```bash
python3 scripts/bounded-completion.py init \
  --contract <new-contract.json> \
  --replace-active
```

This archives the active loop instead of silently deleting it.

## Escalate

```bash
python3 scripts/bounded-completion.py escalate \
  --reason "<specific blocker>"
```

A useful escalation identifies incomplete criteria, exact blockers, failed verification, attempts already made, why another similar attempt is unjustified, and the smallest required user action.

## Exit Codes

For `verify` and `gate`:

```text
0  pass
1  ran but did not pass
2  control-plane/input/JSON/OS error
```

## Authoritative Help

```bash
python3 scripts/bounded-completion.py --help
python3 scripts/bounded-completion.py <command> --help
```

Full guide: [`README.md`](README.md)

VS Code/Copilot quickstart: [`../quickstarts/bounded-completion.md`](../quickstarts/bounded-completion.md)

Configuration guide: [`../../config/README.md`](../../config/README.md)