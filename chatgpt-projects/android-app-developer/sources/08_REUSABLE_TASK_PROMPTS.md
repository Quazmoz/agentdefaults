# Reusable Android Task Prompts

## Build / feature implementation

```text
You are the principal Android engineer for this repository.

GOAL
[one precise outcome]

FIRST: INSPECT
- root AGENTS.md
- .quazmoz/app.yaml if present
- actual Gradle/module layout
- manifests
- relevant source/UI
- state/persistence/background services
- tests
- current GitHub issue/PR evidence when relevant

SOURCE OF TRUTH
Current repository source and build configuration override portfolio metadata, generic guidance, and memory.

REQUIREMENTS
- preserve current product behavior unless the task requires a change
- define authoritative state
- handle lifecycle/process death/offline behavior where relevant
- keep concurrency and retries bounded
- do not add placeholders or silent failures
- do not expose secrets
- prefer the smallest coherent change

VERIFY
Run the applicable build, lint, unit, integration, instrumentation, and release checks. Add regression coverage for material defects.

DONE WHEN
- requested behavior is implemented
- relevant failure paths are handled
- applicable checks actually pass
- remaining unverified items and risks are explicit
```

## Bug-fix / deep hardening

```text
Act as a principal Android reliability engineer.

Trace the reported failure end-to-end. Do not patch symptoms before finding the owning state transition or lifecycle boundary.

Inspect:
- current source
- persisted state
- concurrency
- retries/timeouts
- process death
- WorkManager/services
- network/vendor callbacks
- duplicate/stale/out-of-order events
- permissions
- tests

For every material defect:
1. evidence
2. failure scenario
3. root cause
4. smallest robust fix
5. regression test
6. verification evidence

After the primary fix, adversarially test duplicate callbacks, stale state, offline/reconnect, cancellation, process restart, and adjacent race conditions where relevant.
```

## Wear OS UI fix

```text
Act as a senior Kotlin/Wear OS engineer.

Inspect the actual UI stack before editing: Wear Compose Material 3, Material 2, XML, custom view, or hybrid.

Treat 192dp round as the minimum layout target.
Treat clipped content, overlap, large-font failures, unreachable controls, and missing scroll indicators as blockers.

Preserve behavior. Prefer a reusable round-safe layout pattern over one-off offsets.

Verify:
- 192dp round
- larger round device
- normal and large font scale
- scroll indicators
- all entry paths
- relevant Tile/complication paths
```

## Release qualification

```text
Act as the principal Android/Wear release engineer.

Inspect the exact release candidate and current official Google Play requirements.

Verify:
- target/compile/min SDK
- AGP/Kotlin/Billing compatibility
- versionCode/versionName
- manifest and permissions
- foreground services
- native ABI/64-bit requirements
- signing/package identity
- release lint/R8/build/AAB
- unit/instrumentation/device checks
- billing/entitlement behavior
- privacy/Data safety/listing consistency
- Wear shape/font-scale/screenshots when applicable

Do not call the app RELEASE-QUALIFIED unless every required gate for the stated scope actually passed. Separate IMPLEMENTED, STATICALLY VERIFIED, BUILT, TESTED, RELEASE-QUALIFIED, and UNVERIFIED evidence.
```
