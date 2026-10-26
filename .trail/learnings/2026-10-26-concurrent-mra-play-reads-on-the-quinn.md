---
title: "Concurrent mra play reads on the same app invalidate each other's edits"
author: Quinn
date: 2026-10-26
branch: main
cost: { minutes: 25, tokens: 343108 }
id: l-96af980a
scope: repo
status: active
src: agent
touches:
  - tools/mobile-release-automation/mra/play.py
---

## Decided
Run `mra play tracks` and `mra play listings` for one app strictly one after the other. Different apps can run in parallel.

## Tried and ruled out
Running both reads in parallel for every profile: about half the calls failed with HTTP 400 FAILED_PRECONDITION "This Edit has been deleted." MRA's read commands each open a Play edit (PlayClient.edit in tools/mobile-release-automation/mra/play.py) and delete it in cleanup. A second edit for the same package invalidates the first. The failure is not an auth or permission problem, even though MRA classifies it as malformed_request.

## Watch out
growth-batch-check can also hit a transient Play 503 on list listings. It is read-only, so one retry is safe. Do not blindly retry the apply path.
