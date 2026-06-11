# CLAUDE.md Example: Wear OS Release Work

Copy this into the target app repo as `CLAUDE.md`, or merge it into an existing `CLAUDE.md`.

If the repo already has `AGENTS.md`, prefer this small bridge instead of duplicating everything:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for broad Wear OS release changes. Ask before major redesigns, dependency upgrades, or release configuration changes.
```

## Project Instructions

This repository contains an Android / Wear OS app intended for Google Play distribution.

When working in this repo, behave like a senior Android and Wear OS release engineer. Prioritize Google Play release readiness, small round-screen quality, stable builds, accurate listing content, and safe release hygiene.

## Wear OS Release Priorities

Prioritize in this order:

1. Play review blockers
2. Build and release packaging issues
3. Wear OS visual quality issues
4. Runtime crashes or lifecycle defects
5. Listing, screenshot, and privacy-policy mismatches
6. Maintainability and polish

## Required Checks

Before claiming the app is ready, inspect or verify:

- Gradle/module layout
- manifests
- Compose/XML UI files
- resources and launcher icons
- target SDK and versionCode
- release build configuration
- permissions
- privacy policy alignment
- Play listing text and screenshots, if present
- Tiles, complications, foreground services, ongoing activities, and sensors, if present

## Wear OS Visual Quality Rules

Check these on every relevant UI change:

- no text or controls cut off on small round screens
- safe layout around 192dp and 227dp watch sizes
- larger system font sizes do not break layout
- scrollable screens show a scrollbar or position indicator when interacted with
- touch targets are at least 48x48dp where practical
- app and tile backgrounds are black or intentionally dark
- splash screen uses the app icon on a black background
- swipe-to-dismiss or back navigation works where expected

## Claude Code Workflow

- Use plan mode for broad changes.
- Keep patches small and reviewable.
- Do not perform broad redesigns unless requested.
- Preserve product behavior and branding.
- Prefer repo conventions over new architecture.
- Mark real-device, Play Console, and production upload checks as unverified unless actually checked.

## Validation

Use commands that match the actual module layout. Prefer:

```bash
./gradlew projects
./gradlew clean assembleDebug
./gradlew lintDebug
./gradlew testDebugUnitTest
./gradlew assembleRelease
./gradlew bundleRelease
adb devices
adb exec-out screencap -p > playstore-check.png
```

## Final Response Format

```markdown
Done / Mostly done / Not ready.

Changed:
- `path` — summary

Remaining blockers:
- item, or `None found from repo review`

Not verified:
- real-device checks
- Play Console private settings
- production upload

Validate:
```bash
commands
```

Manual Wear OS checks:
- 192dp small round
- 227dp large round
- large font size
- scrollable screens
- tile/complication if present
```
