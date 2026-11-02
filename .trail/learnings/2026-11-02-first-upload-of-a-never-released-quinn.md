---
title: First upload of a never-released Play app must be a draft release
author: Quinn
date: 2026-11-02
branch: main
cost: { minutes: 8, tokens: 75334 }
id: l-b4a70430
scope: repo
status: active
src: agent
---

## Decided
For a Play app that has never had a release (a draft app), upload to Internal Testing with status draft. Validate with a draft dry run first. The tester rollout then happens in Play Console once app setup is complete.

## Tried and ruled out
A completed-status dry run on a draft app failed at edits.validate with a bare HTTP 500 INTERNAL and no message. It does not mean Play is down, so retrying it is wasted effort. The same AAB validated straight away with status draft.

## Watch out
A committed draft release reaches no testers. Read the track back and report it as draft, not as available to testers. Hit with WearRelay versionCode 4 on 2026-11-02.

In the code: mra play publish --status draft (CLI) or play_publish_bundle status="draft" (MCP).
