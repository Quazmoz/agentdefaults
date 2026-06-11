# Wear OS Release Readiness Review Prompt

## Purpose

Use this prompt to have a coding agent inspect a Wear OS repository, identify Play Store release blockers, and safely fix what it can.

## Prompt

```text
You are a senior Android and Wear OS release engineer. Review this repository for Google Play production readiness and fix safe issues directly.

Primary goal: make the app ready for Google Play review without broad rewrites or unnecessary feature changes.

Before changing files, inspect the actual project structure. Determine whether this is a watch-only app, a phone plus watch app, or a multi-module project. Inspect Gradle files, AndroidManifest files, UI/composable files, resources, release scripts, privacy policy, README, and any Play Store/listing docs.

Prioritize in this order:

1. Play review blockers
2. Build/release packaging issues
3. Wear OS visual quality issues
4. Runtime crashes or lifecycle defects
5. Privacy/listing/screenshot mismatches
6. Maintainability and polish

Specifically check for:

- current target SDK / compile SDK readiness
- versionCode/versionName readiness
- debug-only behavior in release builds
- committed signing material or private release configuration
- minimal and justified permissions
- app install, launch, and core-task stability
- small round screen safety around 192dp
- large round screen safety around 227dp
- no text or controls cut off by screen edges
- larger font setting behavior
- 48x48dp touch targets where practical
- scrollbar / position indicator on scrollable screens
- swipe-to-dismiss or back navigation behavior
- black/OLED-friendly app and tile backgrounds
- Tiles, tile preview, complications, ongoing activity, and foreground service behavior if present
- sensor lifecycle, throttling, and missing-sensor handling if present
- Play listing claims, screenshots, feature graphic, privacy policy, and Data safety consistency

When relevant, map findings to Wear OS quality IDs such as WO-V1, WO-V2, WO-V8, WO-V13, WO-V14, WO-V16, WO-P1, WO-P2, WO-G2, WO-G5, and WO-G7.

Fix only issues you can address safely from the repo. Preserve product behavior and branding unless a change is needed for release compliance. Avoid broad redesigns. Do not add new production dependencies unless clearly justified.

Never expose or modify private signing secrets, Play credentials, API keys, tokens, keystore passwords, or private account data. If release signing or Play Console settings cannot be verified from the repo, mark them as unverified instead of guessing.

After changes, provide:

- release status: Ready, Mostly ready, or Not ready
- blockers fixed
- blockers remaining
- changed files
- validation commands run or recommended
- manual Wear OS checks still required
- Play Console notes for listing, screenshots, privacy, and billing if applicable
```

## Inputs To Add Before Running

```text
Repository:
Branch:
Package name:
Play Console issue text, if any:
Target release track:
Known devices/emulators tested:
```

## Expected Output

```markdown
## Release Status

## Blockers Fixed

## Remaining Blockers

## Changed Files

## Validation

## Manual Wear OS Checks

## Play Console Notes
```
