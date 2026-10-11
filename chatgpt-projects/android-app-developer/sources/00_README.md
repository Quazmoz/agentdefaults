# Android App Developer Project Source Pack

## Purpose

This pack supplies stable Android and Wear OS engineering standards for a ChatGPT Project used to design, build, debug, harden, test, and release apps in the Quazmoz portfolio.

It is intentionally not a database of current app state.

## Operating model

Use this precedence whenever evidence conflicts:

1. Current app repository source
2. Current Gradle/build configuration
3. App repository documentation and repository-local `AGENTS.md`
4. Current GitHub issues, pull requests, Actions, releases, and exact-candidate evidence
5. `Quazmoz/android-portfolio` routing/governance metadata
6. This Project Source Pack
7. `Quazmoz/agentdefaults` reusable guidance
8. Memory or prior conversation

Never let a Project Source override current repository evidence.

## Required first-pass inspection

For any non-trivial app task, inspect the smallest relevant set of:

- root `AGENTS.md`
- `.quazmoz/app.yaml` when present
- `settings.gradle*`
- root/module `build.gradle*`
- `gradle/libs.versions.toml`
- `gradle.properties`
- manifests
- relevant Kotlin/Java source
- relevant Compose/XML/resources
- tests
- release/build scripts
- current GitHub issues/PRs/Actions when relevant

Detect the actual module layout before assuming `app`, `mobile`, or `wear`.

## Evidence labels

Use these terms precisely:

- `IMPLEMENTED` — source/configuration changed.
- `STATICALLY VERIFIED` — relevant source/configuration was inspected and appears internally consistent.
- `BUILT` — the stated build command actually completed successfully.
- `TESTED` — the stated tests actually ran successfully.
- `RELEASE-QUALIFIED` — all required release gates for the stated scope completed and no known blocker remains.

Do not convert static inspection into build/test/release claims.

## Mutable platform rules

Google Play, Billing, Wear OS quality rules, SDK deadlines, policy requirements, and vendor APIs change. Before consequential release or monetization decisions, verify current official documentation.

This pack includes current anchors as of 2026-09-27, but those anchors are verification triggers rather than permanent truth.

## Writing standard

Run human-facing text through `09_HUMANIZER_WRITING_STANDARD.md` before handing it over: Play listings, release notes and "What's new", READMEs and marketing docs, social posts and captions, YouTube titles and descriptions, and emails. Skip it for code, commit messages, and terse technical docs.

Plain ChatGPT Projects read only the uploaded sources, so upload file 09 with the rest of this pack. Codex reads the app repository's `AGENTS.md` instead, which should carry the pointer block from `docs/snippets/downstream-agents-pointer.md` in `Quazmoz/agentdefaults`.

## Files

- `01_ANDROID_ENGINEERING_STANDARD.md`
- `02_WEAROS_ENGINEERING_STANDARD.md`
- `03_GOOGLE_PLAY_RELEASE_STANDARD.md`
- `04_MONETIZATION_ADS_STANDARD.md`
- `05_TESTING_RELIABILITY_STANDARD.md`
- `06_CI_AND_RELEASE_QUALIFICATION.md`
- `07_PORTFOLIO_ROUTING_STANDARD.md`
- `08_REUSABLE_TASK_PROMPTS.md`
- `09_HUMANIZER_WRITING_STANDARD.md` (condensed from [Humanizer](https://github.com/blader/humanizer) v3.1.0 by Siqi Chen, MIT)
