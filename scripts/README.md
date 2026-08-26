# Scripts

## Purpose

Document the executable validation and orchestration utilities under `scripts/`, including which commands are canonical and how to interpret their results.

Run commands from the repository root unless a command explicitly says otherwise.

## Canonical Repository Validation

Use:

```bash
python3 scripts/validate-agentdefaults.py
```

This is the normal entrypoint after AgentDefaults changes. It composes the repository's core and specialist validators rather than requiring contributors to remember every component command.

Do not report it as passed unless it actually completed successfully.

## Component Validators

Component validators exist for focused development and regression diagnosis:

```text
validate-agentdefaults-core.py
validate-engineering-contracts.py
validate-cross-tool-routing.py
validate-documentation-stack.py
validate-devsecops-security-stack.py
validate-codebase-maintenance-stack.py
validate-bounded-completion.py
```

Use the relevant component while iterating, then run `validate-agentdefaults.py` before declaring the repository validation complete.

A repository-level validator does not replace build/lint/type/test/e2e/security checks in a target repository being operated by one of the agents.

## Bounded Completion Control Plane

[`bounded-completion.py`](bounded-completion.py) is the stable command entrypoint for the formal bounded completion loop. Its implementation is split across [`bounded_completion/`](bounded_completion/).

Authoritative runtime evidence is stored under ignored `.agent-loop/` in the **target repository root**.

Basic lifecycle:

```bash
python3 scripts/bounded-completion.py init --contract <contract.json>
python3 scripts/bounded-completion.py status
python3 scripts/bounded-completion.py advance --description "implemented coherent slice"
python3 scripts/bounded-completion.py verify
python3 scripts/bounded-completion.py gate
```

Use the full operator guide at [`../docs/loops/README.md`](../docs/loops/README.md).

## Bounded Completion Command Reference

| Command | Purpose |
|---|---|
| `init --contract <path>` | Initialize a new active task. |
| `init --contract <path> --replace-active` | Archive the current task and deliberately start another. |
| `status` | Read current durable state and findings. |
| `advance --description <text>` | Advance the full-loop counter for a genuine new implementation/review cycle. |
| `verify` | Run configured deterministic verification and persist evidence. |
| `criterion --id <id> --status <status> --evidence <text>` | Record acceptance-criterion state/evidence. |
| `record-review --kind plan|diagnosis|final --summary <text> ...` | Persist reviewer evidence and optional verified model identity. |
| `add-finding --from-file <json>` | Add a structured reviewer finding. |
| `dispose-finding --id <id> --disposition <value> [--evidence <text>]` | Record the current disposition of a finding. |
| `resolve-finding --id <id> --evidence <text>` | Resolve an accepted finding with evidence. |
| `record-visual --criterion <id> --artifact <path> --inspected-by <who> --review <text>` | Record actual visual artifact review. |
| `record-diff --summary <text>` | Record final/current diff inspection evidence. |
| `record-integrity --summary <text> <assertion flags>` | Record validation-integrity assertions after inspecting the current diff. |
| `approve --name <name> --source operator-confirmed|runtime-policy --evidence <text>` | Record a required approval with trusted provenance. |
| `gate` | Evaluate the objective completion gate against fresh evidence. |
| `escalate --reason <text>` | Persist a terminal escalation reason. |
| `stop-hook` | VS Code custom-agent Stop-hook entrypoint; normally invoked by the runtime, not by hand. |

Use:

```bash
python3 scripts/bounded-completion.py --help
python3 scripts/bounded-completion.py <command> --help
```

for exact arguments.

## Exit Codes

For the bounded-completion CLI:

```text
0  command succeeded; verify/gate passed when those commands were used
1  verify or gate completed but did not pass
2  control-plane/input/JSON/OS error
```

A nonzero `gate` result is not a reason to weaken a criterion or validator. Continue with materially useful work or escalate when the configured limits require it.

## Do Not Manually Edit Loop State

When an equivalent control-plane command exists, do not hand-edit:

```text
.agent-loop/current/task-contract.json
.agent-loop/current/state.json
.agent-loop/current/findings.json
```

The control plane maintains invariants and workspace fingerprints used to invalidate stale evidence.

## Platform Notes

The canonical examples use `python3` on macOS/Linux and CI. The bounded-completion Stop hook has Windows handling documented in [`../docs/quickstarts/bounded-completion.md`](../docs/quickstarts/bounded-completion.md).

Do not invent or commit runtime/model identifiers that the repository cannot verify.

## Safety

Verification commands are evidence-producing operations and should not intentionally dump secrets or unrelated credential stores.

The control plane does not itself create authorization for deployment, release publication, production mutation, credential rotation, force-push, destructive cloud actions or other privileged operations. Those remain governed by the selected owner and explicit task approval.

## Validation Changes

When modifying validators or control-plane code:

1. inspect the acceptance-test document for the affected stack;
2. add a regression case for any material defect;
3. run the focused validator;
4. run `python3 scripts/validate-agentdefaults.py`;
5. report anything not executable in the current environment as unverified.

Bounded-completion control-plane changes should run:

```bash
python3 scripts/validate-bounded-completion.py
python3 scripts/validate-agentdefaults.py
```
