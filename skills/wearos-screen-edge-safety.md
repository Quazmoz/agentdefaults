# Wear OS Screen Edge Safety Skill

## Purpose

Use this skill to prevent or fix Wear OS screens where text, buttons, chips, icons, or controls are cut off by round screens or physical display edges.

This skill is designed for Play Console issues such as watch-shape failures, clipped content, missing scroll indicators, overlapping elements, and large-font layout failures.

## When To Use

Use this skill when:

- Google Play reports content cut off by screen edges
- Google Play reports watch-shape visual quality issues
- text or controls overlap on Wear OS
- screens look fine on a large emulator but fail on small round watches
- large font size causes clipping
- scrollable content lacks a scrollbar or position indicator
- a Wear OS app is being built and needs safe layout defaults from the beginning

## Requirement Anchors

Before final compliance claims, check the current Android Developers Wear OS app quality page.

Important anchors:

- `WO-V1`: larger system font settings must not cause overlap or edge clipping.
- `WO-V2`: touch targets should be at least 48x48dp.
- `WO-V8`: scrollable views must display a scrollbar when the user interacts with them.
- `WO-V13`: apps and tiles should use black backgrounds.
- `WO-V14`: essential text should be at least 12sp and non-essential text at least 10sp.
- `WO-V16`: app content must fit inside the physical display area, elements must not overlap, text/controls must not be cut off by screen edges, and the app must support a 192dp circle or larger.

## Inputs Needed

Useful inputs:

```text
Repo:
Branch:
Screen name:
Play Console issue text:
Screenshot/evidence:
Device shape and size, if known:
UI framework: Compose / XML / custom view:
```

If the repo can be inspected, do not block on every input.

## Debugging Workflow

1. Identify the failing screen from screenshot, route, activity, composable, or view.
2. Locate the layout file or composable.
3. Check whether the screen is scrollable.
4. Check whether scrollable content has a visible position indicator or scrollbar.
5. Check whether content uses round-safe padding.
6. Check for fixed heights, fixed widths, absolute offsets, hardcoded spacers, and edge-aligned controls.
7. Check labels for long text, wrapping, and larger font behavior.
8. Check if buttons/chips meet practical 48x48dp touch targets.
9. Replace crowded static columns with scrollable Wear OS patterns.
10. Validate at 192dp round, 227dp round, and larger font size.

## Code Smells

Treat these as likely causes of Play Store visual quality failures:

- non-scrollable `Column` with many children
- `Modifier.height(...)` wrapping dynamic text
- `maxLines = 1` on essential labels
- `overflow = TextOverflow.Clip` on essential text
- bottom buttons touching screen edge
- edge-aligned icons or text with no safe padding
- large fixed `Spacer` values
- absolute `offset` values
- `fillMaxSize()` plus dense content and no padding
- long button labels
- small icon-only actions with no accessible target
- duplicated top/bottom bars on a 192dp round screen

## Preferred Fix Patterns

### Pattern 1: Make crowded screens scrollable

Use a Wear-aware scrolling container and add a position indicator.

For Compose Wear apps, adapt to the project dependency versions:

```kotlin
val listState = rememberScalingLazyListState()
Box(Modifier.fillMaxSize().background(Color.Black)) {
    ScalingLazyColumn(
        state = listState,
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        // items
    }
    PositionIndicator(
        scalingLazyListState = listState,
        modifier = Modifier.align(Alignment.CenterEnd)
    )
}
```

### Pattern 2: Shorten labels and move details down

On watch, prefer:

```text
Start
Save
Done
Log
Pause
Settings
```

Instead of:

```text
Start workout session
Save medication schedule
Complete setup process
```

Move explanations into a detail screen, help screen, or secondary text that can scroll.

### Pattern 3: Use safe padding

For small round screens, keep essential controls away from the circular edge. Use compact but nonzero horizontal and vertical padding. Avoid relying on exact pixel-perfect placement.

### Pattern 4: Let text wrap or scroll

For dynamic user content, medication names, habit names, workout names, or settings labels:

- avoid fixed-height parent containers
- allow at least two lines where useful
- truncate only non-essential detail text
- keep the primary action visible and reachable

### Pattern 5: Test large font early

After layout changes, test with larger system font sizes before claiming the fix is complete.

## Validation Commands

Use repo-specific commands. Common commands:

```bash
./gradlew clean assembleDebug
./gradlew lintDebug
./gradlew assembleRelease
adb devices
adb exec-out screencap -p > wearos-edge-check.png
```

Manual validation matrix:

```text
192dp small round emulator/device
227dp large round emulator/device
large system font setting
all launcher screens
all setup/onboarding screens
all settings/help screens
all tile/complication entry screens
```

## Output Format

```markdown
## Screen Edge Safety Status

Ready / Mostly ready / Not ready

## Root Cause

- exact layout cause

## Fix

- exact file-level change

## Files Changed

- `path` — summary

## Why This Prevents Cutoff

- 192dp round protection
- larger font handling
- scroll indicator handling
- touch target handling

## Validate

```bash
commands
```

## Manual Checks Still Needed

- 192dp round screenshot
- 227dp round screenshot
- large font screenshot
```

## Quality Bar

This skill succeeds when:

- no essential text or controls are cut off at 192dp round
- content does not overlap at larger font sizes
- scrollable screens show a scroll indicator
- primary actions remain reachable
- touch targets are practical for Wear OS
- fix is reusable where possible
- final answer clearly states what was and was not verified
