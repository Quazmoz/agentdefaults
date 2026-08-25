# Codebase Maintenance Engineer Quickstart

## Purpose

Show how to use the Principal Codebase Maintenance and De-Slop Engineer for evidence-backed cleanup of repositories affected by rapid or agentic coding.

## Stack

```text
agents/codebase-maintenance-engineer.md
skills/codebase-de-slop-and-refactoring.md
prompts/implementation/codebase-de-slop-task.md
schemas/codebase-maintenance-task.schema.json
examples/codebase-maintenance-task.yaml
docs/codebase-maintenance-engineer-acceptance-tests.md
.github/agents/codebase-maintenance-engineer.agent.md
```

Use the canonical agent and skill as the source of truth. The Copilot adapter is intentionally thin.

## Best Use Cases

Use this stack after periods of rapid feature development, repeated coding-agent sessions, migrations, or large implementation bursts when the code works but maintenance quality may have drifted.

High-value targets include:

- stale comments/docstrings and TODO residue
- duplicate helpers or parallel abstractions created across sessions
- old implementation paths left after replacement
- unused dependencies/configuration/feature flags
- forwarding abstractions and speculative extensibility
- catch-all or silent error handling
- weak, flaky, skipped, or implementation-coupled tests
- N+1 I/O/query patterns and repeated expensive work
- unbounded retries/tasks/queues/caches
- names/tests/docs that still describe a superseded contract

## Minimal Invocation

Use:

```text
Use agents/codebase-maintenance-engineer.md with skills/codebase-de-slop-and-refactoring.md.

Target: <repo/ref/scope>
Mode: de_slop
Preserve behavior and external contracts.
Inspect first, establish a baseline, identify P0-P3 code-rot findings, implement the smallest coherent cleanup slices, reconcile comments in touched files, run repository-native verification, then perform a second-pass de-slop review of the final diff.
```

For a repeatable full task, use [`../../prompts/implementation/codebase-de-slop-task.md`](../../prompts/implementation/codebase-de-slop-task.md).

## Modes

```text
audit
  Read-only findings. Use before deciding whether cleanup is worth the churn.

de_slop
  Default implementation mode for bounded behavior-preserving cleanup.

refactor
  Use when a specific subsystem is known to need structural simplification.

comment_reconcile
  Use when comments/docstrings/API docs/TODOs are the primary concern.

efficiency
  Use when runtime, query, I/O, build, allocation, or algorithmic efficiency is the primary concern.
```

## What Makes This Different From Generic "Clean Code"

The stack does not grade source against an abstract style ideal. It asks whether the code is becoming more expensive or dangerous to change.

It specifically checks for agentic-development failure modes:

- spec and implementation drift across sessions
- helpers recreated because prior helpers were not discovered
- comments preserved from superseded approaches
- temporary compatibility paths that became permanent
- broad fallback/catch-all logic that looks defensive but masks failure
- abstractions generated in anticipation of requirements that never arrived
- dependencies added for one small convenience and never retired
- tests edited to follow the implementation rather than protect behavior
- partial renames/replacements that leave old state behind

## Comment Policy

The agent treats stale comments as defects.

Keep comments that explain **why**, a non-obvious invariant, compatibility requirement, concurrency/lifecycle rule, or exact workaround-removal condition.

Rewrite comments whose intent is still valid but whose names, edge cases, failures, or behavior changed.

Delete comments that:

- narrate syntax
- describe code that no longer exists
- preserve commented-out source
- contain agent/process narration such as "we now" or "this fix"
- duplicate obvious code
- make unverified safety/performance claims

Clearer code is preferred over more comments when the type system, naming, or structure can express the rule directly.

## Cross-Language Behavior

The agent fingerprints the repository before editing and uses the tools already declared by that ecosystem.

Examples include:

```text
Python       ruff/black, mypy/pyright, pytest
JS/TS        eslint/biome/prettier, tsc, vitest/jest/playwright
Java/Kotlin  Gradle/Maven, Android lint, detekt/ktlint/Spotless/Checkstyle, JUnit
Go           gofmt, go vet/staticcheck, go test
Rust         cargo fmt, clippy, cargo test
C/C++        project build, compiler warnings, clang-tidy/sanitizers when configured
C#           dotnet format/analyzers/build/test
Swift        SwiftPM/Xcode tooling, SwiftFormat/SwiftLint when configured, XCTest
Shell        shellcheck, shfmt, bats
Terraform    fmt, validate, plan/policy tooling when configured
SQL          migration tests and EXPLAIN/query plans for performance claims
```

These are examples, not mandatory installations. Repository-native configuration wins.

## Recommended Workflow

1. Resolve current branch/ref and requested scope.
2. Read repository instructions and architecture decisions relevant to scope.
3. Fingerprint languages, build/test/static-analysis tools, generators, and dynamic entry mechanisms.
4. Establish a pre-change baseline.
5. Build a P0-P3 slop inventory with evidence.
6. State the invariant for each proposed refactor slice.
7. Implement one coherent slice at a time.
8. Reconcile comments/docs in the touched surface.
9. Run native verification and targeted regression tests.
10. Review the final diff for new slop introduced by the cleanup itself.
11. Report verified versus unverified claims separately.

## Safe Dead-Code Removal

Do not remove source merely because plain text search found no caller.

Check for language/runtime mechanisms such as:

```text
reflection
dependency injection
plugin discovery
manifest registration
serialization/deserialization
templates/resources
JNI/native entry points
framework conventions
code generation
external API/CLI consumers
migrations
```

Use stronger evidence for higher-blast-radius removals.

## Efficiency Work

In `efficiency` mode require:

```text
hot path/workload
baseline metric or complexity
bottleneck mechanism
correctness invariant
change
post-change metric or analytical expectation
measurement limitations
```

Prefer deleting unnecessary work over clever micro-optimization. Do not claim measured gains without measurement.

## Structured Brief

Use [`../../schemas/codebase-maintenance-task.schema.json`](../../schemas/codebase-maintenance-task.schema.json) when a task will be generated or consumed programmatically.

The example at [`../../examples/codebase-maintenance-task.yaml`](../../examples/codebase-maintenance-task.yaml) shows a behavior-preserving `de_slop` pass.

## Completion Standard

Do not accept "looks cleaner" as completion.

A successful implementation pass requires:

- evidence-backed findings
- explicit behavior/contract invariants for risky refactors
- coherent scoped edits
- comment reconciliation in touched code
- appropriate regression coverage
- repository-native verification actually executed where available
- truthful labeling of unverified behavior/performance/dead-code assumptions
- a final second-pass review for fresh agent-generated slop

See [`../codebase-maintenance-engineer-acceptance-tests.md`](../codebase-maintenance-engineer-acceptance-tests.md) for adversarial cases.
