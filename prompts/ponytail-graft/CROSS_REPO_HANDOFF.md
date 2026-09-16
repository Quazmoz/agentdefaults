# Cross-Repository Ponytail + Graft Handoff

## Purpose

Use this transport layer when the coding-agent session is running in a target repository that does not already contain the AgentDefaults Ponytail + Graft prompt files or managed sidecar.

The **AgentDefaults source repository** and the **target repository** are intentionally different things:

- source contract: `https://github.com/Quazmoz/agentdefaults`
- target to install or repair: `TARGET_DIR`

A first-install target is allowed to contain none of these files yet:

```text
prompts/ponytail-graft/ponytail-graft.md
prompts/ponytail-graft/multi-repo-ponytail-graft.md
prompts/ponytail-graft/HARDENING.md
.agent-tools/ponytail-graft/
```

Their absence in `TARGET_DIR` is **expected before installation and is not a blocker**. Those first three files are source-contract artifacts from AgentDefaults; the sidecar is an output created in the target by the tested installer contract.

This handoff changes only how an agent obtains the tested contract. It does not replace, summarize, or weaken the setup behavior in the three canonical prompt files.

## Inputs

Require:

```text
TARGET_DIR=<path visible to the coding agent>
```

Accept the same optional installer inputs:

```text
TARGET_MODE=auto
UPDATE_TOOLS=false
HOSTS=claude,codex,cursor,kiro,copilot
```

Optional source selection:

```text
AGENTDEFAULTS_REF=main
```

Use one coherent AgentDefaults source snapshot for the whole run. Never mix the router, baseline, hardening contract, bootstrap code, or documentation from different commits.

## Copy/paste task

```text
Install or repair Ponytail + Graft in TARGET_DIR using the tested AgentDefaults contract.

AgentDefaults is the SOURCE of the installer contract; TARGET_DIR is only the installation TARGET. A fresh target is not expected to already contain AgentDefaults prompt files or .agent-tools/ponytail-graft.

Resolve one coherent AgentDefaults source snapshot from https://github.com/Quazmoz/agentdefaults. If an AgentDefaults checkout is already available to this session, use it. Otherwise obtain a fresh temporary checkout outside TARGET_DIR. Record the exact source commit with `git rev-parse HEAD` before making target changes.

From that source snapshot, read and execute these files in order:
1. prompts/ponytail-graft/ponytail-graft.md
2. prompts/ponytail-graft/multi-repo-ponytail-graft.md
3. prompts/ponytail-graft/HARDENING.md

Do not search TARGET_DIR or the target repository's origin for those three AgentDefaults source files as a prerequisite. Their absence from the target is normal on first install. Do not require .agent-tools/ponytail-graft to exist before the installer creates it.

Do not copy AgentDefaults wholesale into TARGET_DIR. Mutate the target only where the tested setup contract authorizes it. Preserve all target-repository safety, ownership, no-global-write, exact-pin, runtime-health, and verification requirements from the canonical prompt files.

If the AgentDefaults source snapshot cannot be obtained or verified, stop before mutating TARGET_DIR and report the source/ref failure. Do not misdiagnose the situation as the target repository missing required setup artifacts.
```

Then append the desired inputs, for example:

```text
TARGET_DIR=/path/to/repository
TARGET_MODE=auto
UPDATE_TOOLS=false
HOSTS=claude,codex,cursor,kiro,copilot
AGENTDEFAULTS_REF=main
```

## Source-resolution rules

Use the following order:

1. **Existing AgentDefaults checkout visible to the session.** Confirm its repository identity and record `git rev-parse HEAD`.
2. **Fresh temporary checkout of the canonical repository.** Place it outside `TARGET_DIR`; do not turn the target into a clone of AgentDefaults. Use `AGENTDEFAULTS_REF` when one was supplied, otherwise use the requested/current AgentDefaults branch and record the resolved commit SHA.
3. **Block before target mutation** if neither source path can be verified.

A temporary source checkout is read-only input to the installation procedure. It must not become a target dependency, Git submodule, copied source tree, or user-global installation.

When a specific commit/ref is requested, resolve all three canonical prompt files and any AgentDefaults bootstrap material from that same source snapshot. A mutable branch name such as `main` is a convenience selector, not the reproducibility identity; the recorded commit SHA is.

## What not to do

Do not:

- search the target repository for `multi-repo-ponytail-graft.md` or `HARDENING.md` and stop merely because they are absent;
- search the target repository's GitHub origin for AgentDefaults source files;
- require a pre-existing `.agent-tools/ponytail-graft/` directory on a first install;
- fabricate package versions, bootstrap files, or host behavior when AgentDefaults source cannot be read;
- copy the AgentDefaults repository wholesale into the target;
- install Graft or Ponytail globally as a fallback;
- use a floating `npx` invocation as a fallback; or
- continue with target mutation after source-contract resolution fails.

## Expected first-install state

A repository containing only its application/specification files and Git metadata is a valid target. The correct sequence is:

```text
resolve AgentDefaults source snapshot
        ↓
read router + portable baseline + hardening contract from AgentDefaults
        ↓
classify TARGET_DIR using the canonical installer rules
        ↓
create the target's tracked .agent-tools/ponytail-graft sidecar and host adapters
        ↓
run the tracked bootstrap and repo-local Graft health probes
        ↓
report written / verified / unverified separately
```

The sequence must never be inverted into “the target has no AgentDefaults files, therefore setup is blocked.”

## Existing installed target

If `TARGET_DIR` already contains a managed `.agent-tools/ponytail-graft/`, the canonical installer decides whether it is current/stale/foreign and whether bootstrap/repair is required. This handoff does not authorize overwriting it merely because a newer AgentDefaults source snapshot exists.

`UPDATE_TOOLS=false` still preserves existing exact managed pins. Source-contract freshness and target package-version upgrades are separate decisions.

## Acceptance criteria

This handoff is working when all of the following are true:

- an otherwise empty/new target repository can reach the canonical AgentDefaults installer without containing the three source prompt files beforehand;
- the agent records one exact AgentDefaults source commit for the run;
- all canonical setup files are read from that same source snapshot;
- target-repository absence of AgentDefaults source files is treated as normal first-install state;
- the installer still creates and validates target-local artifacts according to the existing tested contract; and
- an unavailable/unverifiable AgentDefaults source blocks safely **before** target mutation with a source-resolution error, not a false target-prerequisite error.

## Maintainer boundary

This file is a transport/discovery wrapper only. The behavioral source of truth remains, in order:

1. `prompts/ponytail-graft/ponytail-graft.md`
2. `prompts/ponytail-graft/multi-repo-ponytail-graft.md`
3. `prompts/ponytail-graft/HARDENING.md`

Do not duplicate their implementation details here. If setup semantics change, change and regression-test the canonical source rather than letting this handoff become a second installer implementation.
