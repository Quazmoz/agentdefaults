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

A failed or unavailable required gate marks that app `BLOCKED` or `UNVERIFIED`; it does not become release-qualified because another app passed.

## Exact Candidate Manifest

For every successfully built release candidate, record at minimum:

```json
{
  "repository": "owner/name",
  "path": "/local/checkout",
  "git_sha": "...",
  "branch": "main",
  "application_id": "...",
  "version_code": 123,
  "version_name": "1.2.3",
  "aab_path": "...",
  "aab_sha256": "...",
  "gradle_tasks": ["..."],
  "qualification": {
    "built": true,
    "tested": true,
    "release_qualified": false
  }
}
```

Never call an app `RELEASE-QUALIFIED` unless its repository's required gates actually passed.

## Internal Testing Upload

For a candidate that passed the required gates:

1. run MRA diagnostics/approval-policy checks;
2. read the current Play tracks;
3. confirm package/application ID and versionCode do not conflict with live state;
4. upload the exact recorded AAB to `internal`;
5. read the internal track back;
6. verify the uploaded versionCode is present;
7. retain the same candidate digest in the report.

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
QUALIFIED
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
