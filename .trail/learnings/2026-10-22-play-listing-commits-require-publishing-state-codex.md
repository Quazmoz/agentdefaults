---
title: Play listing commits require publishing-state evidence
author: Codex
date: 2026-10-22
branch: main
touches:
  - "tools/mobile-release-automation/mra/play.py#PlayClient.edit"
---

## Decided

Treat Publishing overview as a separate safety gate for listing-only batches. API listing reads, completed edit-track status and PUBLISHED production release lifecycle summaries do not establish whether unrelated listing, policy or store-setting changes are waiting for submission, review or managed publishing.

## Tried and ruled out

The documented applications.tracks.releases.list GET can distinguish binary lifecycle states without opening an edit, but its scope is releases, not the complete Publishing overview. A successful disposable-edit listing dry-run proves validation only; it does not prove safe publication or public visibility.

## Watch out

Google documents edits.commit changesInReviewBehavior as defaulting to CANCEL_IN_REVIEW_AND_SUBMIT, potentially canceling an existing review and submitting all changes. The current PlayClient.edit helper does not send ERROR_IF_IN_REVIEW. changesNotSentForReview is not a substitute for reviewing pending state. See https://developers.google.com/android-publisher/api-ref/rest/v3/edits/commit . A user prompt can authorize isolated localization while still requiring a clean publishing-state precondition; do not waive that precondition to hit a batch-size target.
