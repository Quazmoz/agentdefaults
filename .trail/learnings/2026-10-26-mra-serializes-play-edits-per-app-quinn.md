---
title: MRA serializes Play edits per app; concurrent same-app calls are safe
author: Quinn
date: 2026-10-26
branch: main
cost: { minutes: 16, tokens: 106324 }
id: l-1f0a152e
scope: repo
status: active
replaces: l-96af980a
src: agent
touches:
  - tools/mobile-release-automation/mra/play.py
  - tools/mobile-release-automation/mra/play_management.py
  - tools/mobile-release-automation/tests/__init__.py
  - tools/mobile-release-automation/tests/test_play_edit_concurrency.py
  - tools/mobile-release-automation/README.md
  - docs/quickstarts/google-play-one-approval-batch.md
---

## Decided
PlayClient.edit (tools/mobile-release-automation/mra/play.py) holds a per-package flock at $MRA_HOME/locks/play-edit-<package>.lock for the whole edit lifetime. Reads use edits too. Different apps stay parallel. Listing create/update commits send changesInReviewBehavior=ERROR_IF_IN_REVIEW (play_management.LISTING_REVIEW_BEHAVIOR). Failures are classified as edit_invalidated, changes_in_review and review_submission_blocked instead of malformed_request.

## Tried and ruled out
Before the fix, running `mra play tracks` and `listings` in parallel for one app failed about half the time with 400 "This Edit has been deleted". Google documents one open edit per user per app; a new edit deletes the old one. Running reads one at a time only worked around it. Setting changesNotSentForReview automatically on listing writes was also ruled out, because it silently queues changes unsent.

## Watch out
The lock is machine-local. Another machine, another tool on the same service account, or a Console edit can still delete an MRA edit. Retry reads; re-read state before retrying writes. Growth-batch still commits each locale in its own edit, not grouped by app. A transient Play 503 on read-only checks is safe to retry once.
