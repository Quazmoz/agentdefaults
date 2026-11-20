---
title: Skip Play archive stubs when checking a shipped billing product
author: Quinn
date: 2026-11-20
branch: main
id: l-9e3c604f
scope: repo
status: active
src: agent
touches:
  - skills/google-play-localized-pricing.md
---

## Decided

For the shipping-binary check in skills/google-play-localized-pricing.md, verify the exact catalog SKU in a full generated base APK for the current production version and form factor because the same bundle can generate both archive placeholders and installable builds.

## Tried and ruled out

Taking the first generated base split produced false negatives for known shipped billing IDs. It was a Play app-archive stub with a small DEX and archive resources. A later base split for the same version contained the app's billing identifier.

## Watch out

In the code: call the Android Publisher generatedApks.list endpoint for the production version code. Inspect base splits with an empty split ID and skip any APK with com_android_vending_archive resources. A phone and watch release can have different version codes and billing content. A SKU in classes*.dex shows shipped presence, and absence only covers the APK and modules inspected.
