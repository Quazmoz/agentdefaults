---
title: Check billing eligibility and Rest of the World before enabling all purchase markets
author: Quinn
date: 2026-11-20
branch: main
id: l-216c9834
scope: repo
status: active
src: agent
touches:
  - tools/mobile-release-automation/mra/play.py
  - skills/google-play-localized-pricing.md
---

## Decided

For an all-current-market one-time product availability review, compare the production distribution against Play's quoted prices and current buyer restrictions because the conversion response and the explicit track country list each describe only part of eligibility.

## Tried and ruled out

Using the exact intersection of the conversion map and the explicit track countries would have omitted the Central African Republic even though this track had Rest of the World enabled. Google documents the Central African Republic in that group and returned a current price for it. Blindly accepting every returned quote would have included Russia even though Google had paused in-app purchase processing there.

## Watch out

In the code: tools/mobile-release-automation/mra/play.py uses convert_region_prices and skills/google-play-localized-pricing.md distinguishes price reductions from enabling availability. Read the track's restOfWorld flag and the current countries in Google's Rest of the World list (https://support.google.com/googleplay/android-developer/answer/12201481). Google's Russia and Belarus notice (https://support.google.com/googleplay/android-developer/answer/11950272) explicitly distinguishes purchases inside free apps in Belarus. Recheck eligibility and conversions against current Google sources before applying another availability expansion.
