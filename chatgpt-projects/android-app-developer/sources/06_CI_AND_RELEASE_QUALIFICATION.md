# CI and Release Qualification Standard

## Goal

Maximize useful signal per CI minute without weakening correctness.

## Three-level default model

1. Fast automatic gate
   - debug compilation/assembly
   - unit tests
   - lint/static checks
   - cheap deterministic contract checks

2. Targeted expensive gate
   - emulator/instrumentation
   - migrations
   - integration tests
   - large matrices
   - native/artifact audits

3. Release qualification
   - release lint/R8
   - release APK/AAB
   - signing/package surface
   - exact-candidate runtime checks
   - console/vendor verification

## Trigger discipline

- do not run Android builds for docs-only changes
- use relevant `paths` filters
- avoid duplicate branch-push + PR runs that do the same work
- use `concurrency.cancel-in-progress: true` when safe
- keep manual release qualification available
- inspect actual Gradle tasks before copying workflow commands

## Gradle efficiency

On ephemeral hosted runners:

- avoid `clean` unless validating clean-build behavior
- prefer one coherent Gradle invocation for compatible tasks
- do not run broad tasks followed by duplicate narrower tasks
- avoid dumping full dependency graphs on every run
- cache only when it is safe and reproducible

## CI evidence boundary

A workflow that never obtains a runner or executes zero steps is infrastructure evidence, not proof that source failed.

Do not edit application source to chase a pre-runner capacity/start failure.

When execution resumes, treat the first real failing step as a new observed failure.

## Release candidate

Do not rebuild production from different source after qualification when promotion of the tested artifact is possible.

Track:

- Git SHA
- artifact digest
- versionCode/versionName
- package name
- build toolchain
- test results
- release notes/candidate identity

## Failure policy

Never weaken tests just to make CI green.

Never blindly retry a non-idempotent release/publish action after an ambiguous timeout. Reconcile remote state first.
