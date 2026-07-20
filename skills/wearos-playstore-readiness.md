# Wear OS Play Store Readiness Skill

## Purpose

Use this skill to review a Wear OS app before Google Play submission or resubmission.

The skill focuses on release blockers, Wear OS visual quality, build packaging, screenshots, listing accuracy, and privacy-policy alignment.

## When To Use

Use this skill when:

- A Wear OS app is close to release.
- Google Play Console reports a Wear OS quality issue.
- UI is clipped on round watches.
- A scrollable screen is missing a visible scroll indicator.
- Text does not fit with larger system font sizes.
- The app needs final release, listing, screenshot, or privacy review.

## Inputs Needed

Inspect or request:

- repository and target branch
- package name
- module layout
- Play Console issue text, if available
- whether the app includes Tiles, complications, foreground services, sensors, billing, account flows, or networking
- existing listing copy, screenshots, and privacy policy

Do not block on every input when the repository can be inspected.

## Procedure

### 1. Identify the app shape

Determine:

- module layout: `app`, `wear`, `mobile`, or multi-module
- UI framework: Compose for Wear OS, XML views, custom canvas, Watch Face Format, or hybrid
- release artifact type: APK or AAB
- standalone app vs companion app
- user surfaces: app, tile, complication, watch face, ongoing activity, foreground service

### 2. Review release blockers

Check:

- debug and release builds succeed
- target SDK matches current Play requirements
- package/applicationId is correct
- versionCode is ready for next upload
- no debug-only labels, endpoints, or behavior are present in release
- no private signing material is committed
- permissions are minimal and justified
- privacy policy and Data safety answers match actual behavior
- screenshots can be generated from the current app version
- app installs, launches, and completes its core task

### 3. Review Wear OS visual quality

Check:

- no text or controls are cut off on small round screens
- essential UI fits inside the physical display area
- larger system font sizes do not break layout
- touch targets are at least 48x48dp where practical
- scrollable views show a scrollbar or position indicator when interacted with
- swipe-to-dismiss or back navigation works where expected
- black background is used for apps and tiles unless intentionally designed otherwise
- splash screen uses the app icon on a black background

### 4. Review Wear-specific surfaces

If the app includes Tiles:

- tile service declaration is correct
- tile preview exists and matches the real tile
- unavailable states are handled
- rendering is lightweight

If the app includes complications:

- complication service metadata is correct
- supported types are appropriate
- empty and error states are useful

If the app ships a watch face:

- as of 2026-01-14, only Watch Face Format (WFF) watch faces can be published or updated on Google Play; treat a legacy AndroidX / Wearable Support Library watch face as a release blocker (migrate to WFF, e.g. via Watch Face Studio 1.8.7+)
- always-on display draws no more than ~15% of pixels
- memory stays within limits (roughly ≤10 MB ambient, ≤100 MB interactive)
- no more than 8 complication slots
- listing icon, category tag, shape count, source-file size, and tooling version meet current watch-face requirements
- re-verify thresholds against the current Wear OS app quality page

If the app uses sensors:

- listeners are lifecycle-scoped
- polling is throttled
- missing sensors are handled gracefully
- ambient/always-on behavior is battery-safe

If the app uses foreground services or ongoing activities:

- service type and permissions are correct
- notification/channel behavior is correct
- user can stop or exit the active session clearly

### 5. Review Play listing assets

Check:

- title, short description, and long description are accurate
- claims are realistic and not overstated
- Tile or complication support is mentioned only if implemented
- screenshots are 1:1 Wear OS screenshots of the current UI
- screenshots do not include frames, overlays, transparent backgrounds, or fake UI
- feature graphic is not misleading
- privacy policy is app-specific enough

## Output Format

```markdown
## Status

Ready / Not ready / Mostly ready

## Blockers

- **Issue** — Impact. Fix: exact action.

## High Priority

- **Issue** — Impact. Fix: exact action.

## Files Changed or To Change

- `path` — summary

## Validate

```bash
./gradlew clean assembleDebug lintDebug
./gradlew assembleRelease
```

## Manual Wear OS Checks

- 192dp small round emulator/device
- 227dp large round emulator/device
- large font size
- scrollable screens
- tile/complication if present

## Play Console Notes

- Listing
- Screenshots
- Privacy/Data safety
- Billing, if applicable
```

## Validation Commands

Use the repo's actual module names. Common examples:

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

## Common Fix Patterns

### Missing scrollbar

Use a Wear OS scrollable component with a visible position indicator. In Compose, wire the list state to `PositionIndicator` or use the project-standard Wear list scaffold.

### Cut off on round screens

Use round-screen-aware padding, shorten labels, keep critical controls away from edges, move secondary content into scrollable areas, and test at 192dp.

### Font scaling failure

Avoid fixed-height text containers. Ensure text wraps, scrolls, or scales without clipping.

### Grey background

Prefer black backgrounds for app screens, tiles, and splash screens unless the product intentionally uses another color and still passes visual review.

### Screenshot rejection risk

Use actual 1:1 Wear OS screenshots from the current build with no device frames, transparent backgrounds, extra text, marketing overlays, or fake values.

## Quality Bar

The skill is successful when it produces:

- a clear release status
- blocker-first findings
- exact files and fixes
- practical Gradle/ADB validation
- manual small-round and large-round checks
- listing, screenshot, privacy, and billing notes
- no unsupported compliance claims
