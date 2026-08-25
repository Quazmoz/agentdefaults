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
- multiple nominal sources of truth for one domain rule
- old implementation paths left after replacement
- unused dependencies/configuration/feature flags
- forwarding abstractions and speculative extensibility
- catch-all or silent error handling
- weak, flaky, skipped, or implementation-coupled tests
- characterization tests that may have frozen accidental behavior
- generated output that diverges from its schema/template/generator
- manual lockfile or vendored/minified source edits with no sustainable ownership path
- N+1 I/O/query patterns and repeated expensive work
- unbounded retries/tasks/queues/caches
- names/tests/docs that still describe a superseded contract
- code structure that forces future agents to traverse many valueless forwarding layers before finding ownership

## Minimal Invocation

Use:

```text
Use agents/codebase-maintenance-engineer.md with skills/codebase-de-slop-and-refactoring.md.

Target: <repo/ref/scope>
Mode: de_slop
Preserve behavior and external contracts.
Inspect first, map compatibility surfaces, establish a baseline, classify evidence/confidence, identify P0-P3 code-rot findings, implement the smallest coherent cleanup slices, reconcile comments and generated artifacts, run repository-native verification, then perform a second-pass de-slop/churn review of the final diff.
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
- later agents removing deliberate safety/compatibility logic because its intent was not rediscovered
- broad fallback/catch-all logic that looks defensive but masks failure
- abstractions generated in anticipation of requirements that never arrived
- dependencies added for one small convenience and never retired
- tests edited to follow implementation rather than protect contracts
- characterization tests that silently canonize suspicious incidental behavior
- partial renames/replacements that leave old state behind
- generated/lock/vendor artifacts edited outside their source-of-truth workflow

## Compatibility Surface Map

Before risky refactoring, identify the surfaces that must remain compatible:

```text
public APIs / exported symbols
wire/protocol fields and errors/statuses
persisted schemas, keys, migrations, on-disk formats
CLI/config/environment contracts
routes/resources/manifest/plugin registrations
UI/UX behavior relied upon by callers/users
security/trust-boundary checks
retry/timeout/cancellation/ordering/idempotency semantics
operational telemetry contracts
code-generation inputs and generated outputs
build/package outputs and reproducibility
```

Classify each relevant surface as `preserve`, `explicitly_authorized_change`, `not_touched`, or `unverified`.

## Evidence and Confidence

Use the evidence ladder:

```text
E0 intuition/style smell
E1 text/local reference evidence
E2 static graph/config/dependency/history evidence
E3 compiler/analyzer/contracts/tests/reproducible generation
E4 authoritative runtime/external-consumer/production evidence
```

Use confidence labels `low`, `medium`, `high`, `very_high`.

Text search can find candidates but is not enough for risky dead-code removal. Local removal normally requires high confidence. Public/persistence/migration/security/plugin/external-consumer removal normally requires very-high confidence or explicit migration/behavior-change authority. Prefer independent evidence for high-blast-radius removals.

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

## Generated, Vendored, and Lockfile Policy

Default to source-and-regenerate:

1. Identify the authoritative schema/template/generator/source.
2. Update that source first.
3. Regenerate with repository-native tooling.
4. Inspect semantic generated changes.
5. Re-run generation when practical to detect non-determinism.
6. Update lock/resolution files only through the native package/dependency manager.
7. Treat snapshots/goldens as semantic evidence, not files to bulk-accept.
8. Do not refactor vendored/minified third-party source like first-party code; update upstream or use the repository's patch mechanism.

Direct generated edits require explicit justification when the authoritative source/generator cannot be used.

## Characterization Tests

A characterization test can preserve a contract or accidentally immortalize a bug.

Before adding one, classify current behavior as:

```text
contractual
intentional_compatibility
incidental_but_authorized_to_preserve
suspected_defect
unknown
```

Do not silently lock `suspected_defect` or `unknown` behavior into snapshots/goldens. Check accepted specs, consumers, history, and domain ownership first.

## Cross-Language Behavior

The agent fingerprints the repository before editing and uses tools already declared by that ecosystem.

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

1. Resolve current branch/ref, scope, and exclusions.
2. Read repository instructions and architecture decisions relevant to scope.
3. Fingerprint language/build/test/static-analysis/generation tooling and dynamic entry mechanisms.
4. Map compatibility surfaces.
5. Establish a pre-change baseline.
6. Build a P0-P3 slop inventory with evidence level, confidence, and blast radius.
7. Inspect recent history when intent of compatibility/safety/migration/concurrency logic is ambiguous.
8. Distinguish contractual behavior from incidental/suspicious behavior before characterization.
9. State the invariant for each proposed refactor slice.
10. Implement one coherent, low-churn slice at a time.
11. Reconcile comments/docs and regenerate derived artifacts from authoritative sources.
12. Run native verification, compatibility checks, reproducibility checks, and targeted regressions.
13. Review the final diff for fresh slop, compatibility drift, generated-artifact mistakes, and unjustified churn.
14. Report verified versus unverified claims separately.

## Safe Dead-Code Removal

Do not remove source merely because plain text search found no caller.

Check for runtime mechanisms such as:

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

## Maintenance Economics

Prefer changes with clear net maintenance value:

```text
+ defect/risk reduction
+ lower future human/agent reasoning cost
+ fewer sources of truth
+ lower runtime/build/I/O cost
+ better diagnostics/tests
- implementation churn
- reviewer cognitive load
- compatibility/migration risk
- new abstractions/dependencies/configuration
```

Do not manufacture a numeric score. Line-count reduction is not a success metric.

## Future-Agent Context Efficiency

Good de-slopping usually makes ownership easier to find: stable domain vocabulary, canonical rule locations, colocated invariants, fewer valueless forwarding hops, and obvious generated/config sources of truth.

Do not optimize for token count alone. Excessive file splitting or flattening legitimate security/lifecycle/protocol/process boundaries can make future reasoning worse.

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

The example at [`../../examples/codebase-maintenance-task.yaml`](../../examples/codebase-maintenance-task.yaml) shows a behavior-preserving `de_slop` pass with explicit evidence, churn, compatibility, history, and generated-artifact policy.

## Completion Standard

Do not accept "looks cleaner" as completion.

A successful implementation pass requires:

- evidence-backed findings with confidence proportional to blast radius
- explicit compatibility surfaces and behavior/contract invariants for risky refactors
- coherent scoped edits with justified churn
- comment reconciliation in touched code
- generated/derived changes following source-of-truth and reproducibility policy
- characterization that does not silently freeze suspicious behavior
- appropriate regression coverage
- repository-native verification actually executed where available
- truthful labeling of unverified behavior/performance/dead-code/reproducibility assumptions
- a final second-pass review for fresh agent-generated slop

See [`../codebase-maintenance-engineer-acceptance-tests.md`](../codebase-maintenance-engineer-acceptance-tests.md) for adversarial cases.
