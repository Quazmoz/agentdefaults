---
title: "Play screenshot sets: hash-verified atomic replace, gated on the production version"
author: Quinn
date: 2026-10-29
branch: main
cost: { minutes: 1, tokens: 1863 }
id: l-67f98fb3
scope: repo
status: active
src: agent
touches:
  - tools/mobile-release-automation/mra/play_management.py
---

## Decided
Replace a locale's screenshot carousel with `play_replace_image_set` (tools/mobile-release-automation/mra/play_management.py `replace_image_set`, MCP wrapper in mcp_play_management.py): one edit, deleteall for that language+type, uploads in filename order, in-edit sha256 check, explicit `:validate`, one commit with ERROR_IF_IN_REVIEW, then read-back. A live dry run confirmed that the `sha256` Play returns for an uploaded image equals the local file's SHA-256, so hash read-back is a real verification.

## Tried and ruled out
Calling `upload_image` once per image to swap a carousel: every call commits its own edit, so the public listing would go through half-replaced states, and a failure midway leaves a mixed set.

## Watch out
Localized UI captures are only truthful once the version that contains those translations and features is live in production. Before uploading, compare the production track versionCode with the git history of `res/values-*` and the features shown. Apps here have had localized captures from main while production still served an English-only build. A locale without its own screenshots falls back to the default-language set, so leaving one empty is not a defect. Never pipe a file list through `xargs` into ImageMagick `montage`: the last input becomes the output and gets overwritten.
