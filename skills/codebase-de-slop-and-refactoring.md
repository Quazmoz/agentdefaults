# Codebase De-Slop and Refactoring Skill

## Purpose

Provide a repeatable, language-aware method for reducing code rot in repositories produced or heavily modified through iterative agentic coding. The skill emphasizes behavior preservation, comment accuracy, practical simplification, evidence-backed removal, and verification.

Use this skill with `agents/codebase-maintenance-engineer.md` or another authorized engineering agent when maintainability cleanup is a material part of the task.

## Objective

Reduce future change cost without introducing semantic drift.

The desired result is not merely fewer lines or fewer linter findings. A successful pass leaves the target area:

- easier to understand from current source
- less duplicated or internally contradictory
- less dependent on stale comments or agent history
- explicit about important invariants and failure behavior
- free of proven-dead residue in scope
- aligned with repository-native conventions and tooling
- no slower or less reliable without a justified tradeoff
- covered by sufficient tests or verification for the risk of the refactor

## Preconditions

Before mutating code, establish as much as the repository and runtime allow:

- target repository and branch
- repository-local instructions
- requested scope
- whether behavior changes are allowed
- language/framework/build-system inventory
- public APIs, persistence, wire formats, CLI/config contracts, or externally consumed behavior in scope
- available build/test/lint/type/static-analysis tools
- mutation authority

If the requested scope is broad, split work into coherent verified slices rather than editing the entire repository at once.

## Trust and Evidence Rules

Treat these as evidence rather than unquestionable truth:

- comments and docstrings
- TODO/FIXME/HACK markers
- tests
- README/API docs
- issues and PR descriptions
- generated code
- previous agent summaries
- runtime logs

Executable code and authoritative runtime/contract evidence generally outrank stale prose. However, accepted specifications and public contracts can show that the implementation is wrong. When evidence conflicts, classify the conflict before editing instead of silently choosing whichever source is easier.

## Phase 1: Repository Fingerprint

Identify the actual ecosystem before applying cleanup rules.

Capture relevant:

```text
languages
frameworks
build systems
package/dependency managers
formatters
linters
static analyzers
type checkers
test runners
code generators
migration systems
CI checks
runtime entry points
plugin/reflection/DI mechanisms
serialization formats
configuration sources
```

Prefer configured repository-native tools. Do not introduce new tools merely because they are common in the language.

## Phase 2: Establish Baseline

Run or inspect the strongest feasible pre-change checks.

Suggested order when available:

```text
format check
lint/static analysis
type/compile
unit tests
integration/contract tests
targeted e2e
benchmark/profile/query plan
```

Record pre-existing failures. A cleanup pass must not erase the distinction between an existing defect and a regression caused by the pass.

## Phase 3: Build the Slop Inventory

Classify findings into the following categories.

### A. Comment drift

Look for:

- comments describing behavior no longer present
- comments naming old classes/functions/fields/flags
- docstrings with stale defaults, exceptions, units, return values, threading, side effects, or examples
- TODOs that were already resolved
- historical narration left by agents
- commented-out code
- comments that state the obvious while missing the real invariant
- workaround comments with no removal condition

For material comments, use:

```text
accurate
stale
redundant
missing_rationale
uncertain
```

Do not rewrite every comment just because the file was touched. Reconcile the comments that influence understanding of the changed behavior.

### B. Duplication and parallel concepts

Look for repeated:

- validation
- parsing/formatting
- mapping/translation
- retries/timeouts
- serialization/deserialization
- state transitions
- error handling
- constants/configuration
- test fixtures/builders
- API or database models

Before consolidating, ask:

1. Are these truly the same domain concept?
2. Do they have the same invariants and failure semantics?
3. Will they change for the same reasons?
4. Does abstraction make the common rule clearer rather than merely moving lines?

If not, leave them separate.

### C. Dead and abandoned residue

Candidates include:

- unreachable branches
- unused symbols/imports/resources
- orphaned feature flags/config keys
- abandoned migrations
- unused dependencies/plugins/build features
- compatibility shims whose supported window has expired
- old implementations beside replacements
- debug instrumentation
- disabled tests
- unreferenced generated artifacts

Removal requires evidence appropriate to the runtime. Static reference search is insufficient when dynamic loading, reflection, dependency injection, plugin discovery, manifests, templates, serialization, native entry points, or external callers are plausible.

### D. Abstraction inflation

Question layers that only forward work or obscure domain rules:

```text
interfaces with no boundary reason
single-purpose generic frameworks
factory/provider/manager/service chains
adapters with no translation/policy/isolation role
wrapper-on-wrapper APIs
premature extension/plugin systems
premature provider portability
queues/event buses/caches without demonstrated need
```

Do not flatten a boundary that exists for security, test isolation, dependency inversion, process separation, protocol translation, lifecycle ownership, generated-code isolation, or public API stability.

### E. Failure-handling slop

Inspect:

- catch-all exceptions
- ignored errors
- default-on-failure behavior
- `null`/zero/empty fallback that hides impossible state
- retries without classification/bounds/idempotency
- timeouts without cancellation
- fire-and-forget tasks
- missing awaits/joins
- partial failure with no reconciliation
- resource cleanup omitted on error paths

Simplification must preserve or improve diagnosability and correctness.

### F. Test slop

Look for:

- tests coupled to private call ordering or internals instead of behavior
- weak assertions
- duplicate fixture defaults
- unexplained skipped tests
- sleep-based synchronization
- snapshots/goldens updated without semantic review
- tests that only prove mocks were invoked
- missing regression coverage around a discovered defect

Do not delete tests simply because refactoring makes them inconvenient.

### G. Efficiency slop

Inspect for practical cost, not micro-optimization theater.

Common high-value issues:

- N+1 database or API calls
- nested scans on growing collections
- repeated parse/compile/deserialize work
- repeated filesystem/network calls inside loops
- blocking calls on UI/event/reactor/main threads
- unnecessary full-materialization instead of streaming/pagination
- large copies/allocations in hot paths
- unbounded queues/caches/tasks/threads/goroutines/retries
- repeated model/embedding/tool calls in AI code
- redundant build steps or generated work

Prefer measurement. When a profiler or benchmark is unavailable, state the algorithmic or I/O argument and do not claim a measured gain.

### H. Dependency/configuration slop

Check for:

- packages no longer imported or loaded
- build plugins with no remaining task
- two libraries for the same concern
- environment variables read nowhere
- duplicate config keys or defaults
- stale workaround pins
- inconsistent version declarations
- permissions retained after feature removal
- copied constants that should have one source of truth

Dependency removal must account for code generation, runtime loading, build scripts, plugins, tests, and operational tooling.

## Phase 4: Prioritize

Rank findings by expected risk/cost reduction versus churn.

Use:

```text
P0  catastrophic correctness/security/data-loss issue discovered during maintenance
P1  major latent correctness/reliability/security/runaway-resource issue
P2  significant maintainability/performance/operational debt likely to increase future defect rate or agent cost
P3  localized clarity, consistency, minor efficiency, or hygiene improvement
```

A pile of P3 formatting observations must not displace a P1 failure-semantics defect.

## Phase 5: Define the Refactor Invariant

Before each slice, state the invariant that must hold afterward.

Examples:

```text
All callers validate account IDs through the same domain rule and receive the same error semantics.

Public JSON field names and persisted schema remain byte-compatible while internal model naming is simplified.

Cancellation still propagates from request scope to all child work after the helper consolidation.

The hot path performs at most one database round trip per batch instead of one per item.
```

If the invariant cannot be stated clearly, the slice is not ready to implement.

## Phase 6: Implement the Smallest Coherent Slice

Preferred operations:

```text
remove proven-dead residue
simplify control flow
consolidate truly identical domain logic
replace magic values with an existing canonical constant/config source
clarify naming without changing external identifiers
make failure semantics explicit
reduce forwarding layers
reduce repeated expensive work
reconcile tests with observable behavior
reconcile comments/docs with current truth
```

Avoid:

- unrelated file churn
- repository-wide formatting
- new frameworks
- speculative extensibility
- generic "utility" dumping grounds
- one giant refactor commit spanning unrelated domains
- semantic changes disguised as cleanup

## Comment Handling Procedure

For every materially touched source file:

1. Read the code before the comments.
2. Identify comments/docstrings that make behavioral claims.
3. Compare those claims to current control flow, types, errors, state, and tests.
4. Update stale claims in the same slice.
5. Delete comments that narrate syntax or development history.
6. Add concise rationale for non-obvious invariants that future agents are likely to accidentally remove.
7. Preserve legal/license/generated markers and ecosystem-required documentation.
8. If a comment is uncertain because behavior depends on an external contract, verify the contract or mark the point unverified rather than guessing.

### Good comment characteristics

A good comment answers one or more of:

```text
Why is this surprising implementation necessary?
What invariant would a future refactor otherwise violate?
What external compatibility constraint is not visible from the type signature?
What ordering/concurrency/lifecycle rule matters here?
What exact condition allows this workaround to be removed?
```

### Bad comment characteristics

Delete or rewrite comments that:

```text
repeat the code
say "we" or "I" changed something
refer to a previous patch rather than current behavior
promise safety/performance without evidence
preserve old code in comments
use TODO as a substitute for a defined issue/removal condition
```

## Language-Aware Verification

Select checks from the repository's actual toolchain. Examples when configured:

```text
Python       ruff/black, mypy/pyright, pytest
TypeScript   eslint/biome/prettier, tsc, vitest/jest/playwright
Java/Kotlin  Gradle/Maven compile/test, lint, detekt/ktlint/Spotless/Checkstyle
Go           gofmt, go vet/staticcheck, go test
Rust         cargo fmt, clippy, cargo test
C/C++        compiler warnings, clang-tidy, sanitizer tests, project test runner
C#           dotnet format/analyzers/build/test
Swift        SwiftFormat/SwiftLint, build, XCTest
Shell        shellcheck, shfmt, bats
Terraform    fmt, validate, plan/policy/security checks when available
SQL          migration validation, tests, EXPLAIN/query plan for performance claims
```

Do not invent a command. Read repository scripts and CI first.

## Performance Improvement Rules

A performance cleanup should identify:

```text
workload/hot path
baseline metric or complexity
bottleneck mechanism
change
correctness invariant
post-change metric or analytical expectation
measurement limitations
```

Do not optimize low-frequency code at the cost of readability unless the user has a concrete reason.

Prefer eliminating unnecessary work over clever micro-optimization.

## Dependency Removal Checklist

Before removing a dependency or plugin, check:

- direct source imports/references
- tests and fixtures
- build scripts/plugins
- code generation
- runtime/service loading
- reflection/plugin discovery
- manifests/resources/templates
- CLI/dev tooling
- deployment packaging
- transitive dependency relied upon accidentally

After removal, regenerate lockfiles/manifests only through the repository's package manager or documented workflow when available.

## Dead-Code Removal Checklist

Before removing suspected dead code, establish at least one strong form of evidence such as:

- compiler/static analyzer proves unreachable/unused
- exhaustive reference/call graph plus no dynamic entry mechanism
- owning manifest/config/registration no longer references it
- feature flag has no enabled path and current supported releases no longer need compatibility
- tests plus runtime/telemetry or product contract establish non-use

The stronger the blast radius, the stronger the evidence required.

## Refactor Review Checklist

After implementation ask:

- Did external behavior change unintentionally?
- Did error classification or retry behavior change?
- Did state ownership become less explicit?
- Did concurrency/cancellation semantics change?
- Did ordering change?
- Did serialization/persistence/API identifiers change?
- Did resource cleanup regress?
- Did security validation/logging/authorization weaken?
- Did a new abstraction appear that is more complex than what it replaced?
- Did comments and tests still describe the actual behavior?
- Did the diff include unrelated formatting or generated noise?

## Second-Pass Agentic Slop Check

Coding agents can introduce fresh slop while removing old slop. Inspect the final diff specifically for:

- new duplicate helpers
- overly broad utility modules
- comments explaining the patch rather than the code
- placeholder TODOs
- defensive fallback that hides errors
- excessive try/catch
- new dependency for trivial logic
- over-generalized interfaces
- tests weakened to fit the refactor
- debug logging or temporary flags
- stale names left after partial rename
- unbounded loops/retries/tasks
- claims of performance improvement without evidence

Remove these before completion.

## Output Contract

Return:

```text
BASELINE
FINDINGS (P0-P3 with evidence)
INVARIANTS
CHANGES
COMMENT RECONCILIATION
VERIFICATION
UNVERIFIED
MAINTENANCE DELTA
RISKS
```

For audit-only work, `CHANGES` must say `none`.

## Completion Criteria

This skill is complete for a task only when:

- the target area and toolchain were inspected
- material findings are evidence-backed
- refactor invariants were explicit before risky edits
- changes are scoped and coherent
- touched comments/docs are reconciled
- behavior-sensitive changes have appropriate regression coverage when practical
- native verification ran to the extent available
- remaining uncertainty is labeled
- the final diff received a second-pass slop review

Do not expand indefinitely. Stop at the requested scope and report unrelated debt separately.
