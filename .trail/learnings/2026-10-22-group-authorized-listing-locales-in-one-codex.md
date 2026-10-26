---
title: Group authorized listing locales in one guarded edit per app
author: Codex
date: 2026-10-22
branch: main
touches:
  - "tools/mobile-release-automation/mra/play.py#PlayClient.edit"
  - "tools/mobile-release-automation/mra/growth_batch.py#_apply_action"
---

## Decided

For an authorized app with several absent listing locales, put all of that app's approved locale payloads into one Play edit and commit once with changesInReviewBehavior=ERROR_IF_IN_REVIEW. Reuse MRA authentication and edit cleanup. Bind execution to the unchanged manifest SHA-256, check complete listing/track/app-details state before writing, and reject any change to existing fields or unrelated resources.

## Tried and ruled out

The existing growth-batch implementation commits each locale separately and does not set the review-protection flag. A first locale can start a review before a later locale commit, so grouping by app avoids follow-up commits for the same authorized metadata batch. No global MRA or repository behavior had to change: a private adapter restricted writes to exact approved locale paths and bodies. Scope-check self-tests and real guarded commits succeeded; a separate read-only process matched every saved field and checked preservation.

## Watch out

A precise operator confirmation can resolve a previously unknown pending-state precondition; preserve its provenance as operator evidence rather than claiming an independent Console observation. The commit guard protects against existing reviews, not every possible unrelated pending change. API persistence and public publication remain separate: successful guarded commits and exact read-back did not establish public propagation or managed-publishing state. Keep per-app journals before commit, and reconcile an uncertain outcome instead of replaying a commit.
