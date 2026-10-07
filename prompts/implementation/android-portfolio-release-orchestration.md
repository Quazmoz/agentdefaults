# Android Portfolio Release Orchestration Task

## Purpose

Provide a reusable, safety-bounded task contract for a local agent that discovers, qualifies, builds, and uploads many Android/Wear repositories while preserving exact release-candidate identity and MRA approval boundaries.

## Invocation

Act as the principal Android/Wear release engineer and mobile release automation engineer for a portfolio of local repositories.

Load:

- `skills/android-portfolio-release-orchestration.md`
- `skills/mobile-release-automation-orchestration.md`
- `skills/google-play-release-automation.md`

## Goal

Process every in-scope Android/Wear repository under the operator-approved local workspace roots and produce explicit per-app release evidence.

Default target is Google Play Internal Testing only.

Do not promote to production in this run unless the operator separately authorizes production after reviewing the qualification report.

## Workflow

1. Discover local Android/Wear Git repositories.
2. Use `Quazmoz/android-portfolio` only as routing/context when available.
3. For every repository, read its own `AGENTS.md`, `.quazmoz/app.yaml`, docs, Gradle configuration, and current Git state.
4. Never destroy, stash, reset, rebase, or overwrite uncommitted work automatically.
5. Refresh clean repositories from their intended release branch using safe fast-forward semantics.
6. Discover the actual applicable Gradle qualification/release tasks instead of assuming one command fits all apps.
7. Run required lint/test/assembly/release gates, but use MRA's Keychain-backed signing broker for the final Play AAB rather than inventing signing properties.
8. Check `android_signing_status(identity="play-upload")`. If it is not ready, mark `BLOCKED_SIGNING` and tell the operator to run the documented interactive `mra-agent signing configure` command locally; never request a password in chat.
9. For a clean qualified repository, call `android_build_signed_bundles(repo_path, modules, identity="play-upload")` using the real application module(s). Treat the returned signed AAB path, SHA-256 and signer certificate as the exact candidate. Do not rebuild it afterward.
10. Record an exact-candidate manifest including Git SHA, applicationId, versionCode/versionName, AAB path, AAB SHA-256, signer certificate SHA-256, tasks run, and evidence labels.
11. For each qualified candidate, reconcile current Play track state through MRA.
12. Upload the exact recorded AAB to `internal`.
13. Read the internal track back and verify the intended versionCode.
14. Continue past isolated failures when safe and preserve one explicit status per app.

## Hard stops per app

Block that app rather than guessing when any of these occur:

- dirty worktree not explicitly authorized;
- unsafe Git divergence;
- unknown/missing signing;
- versionCode collision;
- failed required build/test/lint gate;
- application/package identity mismatch;
- ambiguous Play mutation outcome that has not been reconciled;
- candidate artifact changed after qualification.

## Production

Do not rebuild for production.

When the operator later requests promotion, use the already-qualified version codes on the lower track and MRA's approval-gated promotion path.

## Output

Return:

- discovered repositories;
- per-app Git SHA/version;
- gates actually run and pass/fail;
- exact AAB SHA-256 and signing-certificate SHA-256;
- Internal Testing upload/read-back status;
- blockers and unverified evidence;
- production-eligible candidates;
- commands/tool actions actually executed.

Use the evidence labels accurately:

`IMPLEMENTED | STATICALLY VERIFIED | BUILT | TESTED | RELEASE-QUALIFIED | UNVERIFIED`
