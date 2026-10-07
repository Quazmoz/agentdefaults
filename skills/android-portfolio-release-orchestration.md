# Android Portfolio Release Orchestration

## Purpose

Coordinate many locally checked-out Android/Wear OS repositories through repository refresh, release qualification, exact-candidate build, Google Play Internal Testing upload, verification, and later promotion without weakening per-app release standards.

This skill orchestrates existing repository-local Gradle logic and MRA. It does not replace either.

## Use When

Use for requests such as:

- build every Android/Wear app currently checked out on a workstation;
- qualify a portfolio locally without spending hosted CI minutes;
- upload all successful exact candidates to Play Internal Testing;
- prepare a production-promotion approval packet;
- promote already-qualified internal artifacts without rebuilding them.

## Required Components

```text
app repository source/configuration     authoritative implementation truth
Quazmoz/android-portfolio              optional routing/inventory truth
local filesystem                       authoritative checkout/worktree state
Gradle wrapper in each app             build/qualification execution
MRA                                    Play read/write and verification surface
```

Never make `android-portfolio` authoritative for current version codes, build results, release state, or defects.

## Safety Defaults

- Default batch target is `internal`, never production.
- A dirty or diverged worktree is not auto-reset, stashed, rebased, or overwritten.
- Never inject signing credentials into prompts, logs, repositories, or agent-visible summaries.
- Never rebuild a different artifact for promotion after qualification.
- Never retry an ambiguous Play mutation before reconciling live remote state.
- Production/open/closed rollout remains approval-gated by MRA.
- One app failing must not cause the agent to falsely report the portfolio as successful.

## Discovery

### Local checkout discovery

Search only operator-approved workspace roots.

A candidate repository should have enough Android evidence to inspect safely, such as:

- `.git`;
- `gradlew`;
- `settings.gradle` or `settings.gradle.kts`;
- Android application modules or repository-local profile metadata.

If `Quazmoz/android-portfolio` is available, use its registry to classify/rout known apps, but do not assume every registry entry is checked out locally and do not assume every local Android repository is registered.

### Per-repository read order

Before building:

1. root `AGENTS.md`;
2. `.quazmoz/app.yaml` when present;
3. repository documentation index;
4. settings/build files and module graph;
5. current Git state;
6. relevant current issues/PR/release evidence when consequential.

## Git Refresh Policy

For each repository:

```text
if worktree dirty:
    BLOCK refresh/build-for-release unless the task explicitly authorizes using that exact dirty state
    report changed/untracked paths without modifying them
else:
    fetch origin
    determine default/current release branch
    fast-forward only when safe
    never force-reset local work
```

Record the exact candidate Git SHA after refresh.

## Internal-candidate versus production qualification

Internal Testing is a QA distribution lane, not evidence that an app is
production-qualified. Do not require every production-only physical-device,
paired-runtime, billing-sandbox, screenshot, store-copy, or rollout gate before
an artifact may reach Internal Testing unless the repository explicitly marks
that gate as required before any internal distribution.

Use these concepts separately:

- `INTERNAL_READY` — the exact current-main candidate is suitable for Internal
  Testing so QA can continue. Artifact-integrity build/lint/test/static gates
  have passed, release signing/package/version identity is valid, and there is
  no known crash, data-loss, security/privacy, or entitlement defect that makes
  tester distribution unsafe.
- `RELEASE-QUALIFIED` — every applicable repository release gate, including
  required device/emulator/paired-runtime/Play-installed/manual gates, has
  actually passed.

A candidate may be `INTERNAL_READY` while production qualification remains
`UNVERIFIED`. Those unfinished gates remain blockers for later production
promotion when the repository requires them.

## Qualification and Build

Do not blindly copy one Gradle command across the portfolio.

Inspect the repository's actual task graph and release documentation. Run the applicable release gates for that app, normally some subset of:

```text
lint/static checks
unit tests
targeted integration/instrumentation tests
assembleRelease
bundleRelease
release-specific R8/native/signing checks
```

Use the project's own wrapper and JDK/toolchain.

A failed gate required for artifact integrity or internal distribution marks
that app `BLOCKED` or `UNVERIFIED`. An unexecuted production-only
manual/device gate keeps `RELEASE-QUALIFIED=false` but does not by itself
prevent `INTERNAL_READY=true`.

## Release signing and final AAB

Use MRA's Keychain-backed signing broker for the final Play artifact whenever the
configured upload key is required.

First check:

```text
android_signing_status(identity="play-upload")
```

or:

```bash
mra-agent signing status --name play-upload
```

If it is not ready, classify the app `BLOCKED_SIGNING`. Do not ask the operator
to paste passwords into chat. The only supported setup handoff is the
operator-interactive local command:

```bash
mra-agent signing configure \
  --name play-upload \
  --keystore /Users/quinnfavo/my-release-key.jks \
  --alias my-key-alias
```

Once ready, build the final signed AAB through:

```text
android_build_signed_bundles(
  repo_path="/absolute/repo/path",
  modules=["app"],
  identity="play-upload"
)
```

Use the actual application modules discovered from repository evidence; pass
multiple modules for separate phone/Wear artifacts.

The helper deliberately refuses dirty Git worktrees before it resolves signing
secrets, uses Android Studio-compatible injected signing properties, disables
the Gradle daemon for the signing invocation, redacts captured output, verifies
the AAB signature, and requires the signer certificate to match the configured
upload key.

Do not run ad-hoc `bundleRelease` commands with passwords on the command line,
do not create repository-local signing property files, and do not substitute a
debug-signed bundle. The helper-produced AAB is the candidate that must be
hashed, qualified, and uploaded.

## Exact Candidate Manifest

For every successfully built release candidate, record at minimum:

```json
{
  "repository": "owner/name",
  "path": "/local/checkout",
  "git_sha": "...",
  "branch": "main",
  "application_id": "...",
  "version_codes": [123, 124],
  "version_name": "1.2.3",
  "artifacts": [
    {"module": "app", "aab_path": "...", "aab_sha256": "..."},
    {"module": "wear", "aab_path": "...", "aab_sha256": "..."}
  ],
  "gradle_tasks": ["..."],
  "qualification": {
    "built": true,
    "tested": true,
    "internal_ready": true,
    "release_qualified": false
  }
}
```

Never call an app `RELEASE-QUALIFIED` unless its repository's required gates actually passed.

## Internal Testing Upload

For a candidate that is `INTERNAL_READY`:

1. run MRA diagnostics/approval-policy checks;
2. read the current Play tracks;
3. confirm package/application ID and versionCode do not conflict with live state;
4. determine the complete Play artifact set and the live target track ID for
   each form factor;
5. for a single-artifact app, upload the exact AAB to its internal track;
6. if multiple artifacts belong to the **same** track, use
   `play_publish_bundles` or repeated CLI `--aab` arguments;
7. if Play uses dedicated form-factor tracks (for example phone `internal`
   plus Wear `wear:internal`), use `play_publish_track_set` or CLI
   `play publish-set` so all uploads and all track PUTs occur inside one
   package edit and one validate/commit boundary;
8. use the exact track identifiers returned by live Play state; do not invent a
   form-factor track alias from documentation alone;
9. read every affected internal/form-factor track back;
10. verify each intended versionCode is present on its intended track;
11. retain every candidate digest in the report.

Never force a Wear bundle onto the mobile track when Play has dedicated Wear
tracks enabled. Never perform separate package edits when one atomic edit can
validate/commit the coordinated form-factor release set.

The internal upload may be automated as a contained mutation under MRA's policy, but the operator's local MRA configuration remains authoritative.

## Production Promotion

Production promotion is a distinct later phase.

Eligibility requires:

- exact candidate already present on an approved lower track;
- required qualification evidence is still valid;
- no newer source rebuild substituted for the candidate;
- live Play state reconciled immediately before promotion;
- explicit local human approval through MRA.

Promotion should move existing version codes. Do not rebuild production merely to change tracks.

## Batch Behavior

Default to sequential or bounded low concurrency for Gradle builds to avoid memory, thermal, emulator, signing, and disk contention on a developer workstation.

A portfolio run must continue past isolated app failures when safe, while preserving an explicit result per app:

```text
INTERNAL_READY
RELEASE_QUALIFIED
BUILT_NOT_QUALIFIED
BLOCKED_DIRTY_WORKTREE
BLOCKED_GIT_DIVERGENCE
BLOCKED_SIGNING
BLOCKED_VERSION_COLLISION
BUILD_FAILED
TEST_FAILED
UPLOAD_FAILED
INTERNAL_VERIFIED
UNVERIFIED
```

Never collapse `UNVERIFIED` into success.

## Output Contract

```markdown
# Portfolio Release Run

## Summary
- discovered:
- refreshed:
- built:
- tested:
- release-qualified:
- uploaded to internal:
- blocked:
- failed:

## Per-App Results
| App | Git SHA | Version | Qualification | AAB SHA-256 | Play Internal | Blocker |

## Production-Eligible Candidates
| App | VersionCode | Internal Verification | Candidate Digest | Approval Needed |

## Failures / Manual Work
- ...

## Evidence
- commands actually run:
- MRA reads/writes performed:
- unverified gates:
```

## Completion Criteria

A portfolio run is complete when every discovered in-scope repository has an explicit outcome, exact candidates are traceable, Internal Testing uploads were read back, failures remain visible, and no production action occurred without the separate MRA approval boundary.
