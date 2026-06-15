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
- scrollable content lacks a scrollbar, `ScrollIndicator`, or `PositionIndicator`
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
UI framework: Compose Material 2 / Compose Material 3 / XML / custom view:
```

If the repo can be inspected, do not block on every input.

## Debugging Workflow

1. Identify the failing screen from screenshot, route, activity, composable, or view.
2. Locate the layout file or composable.
3. Detect the UI stack: `androidx.wear.compose.material`, `androidx.wear.compose.material3`, XML views, or custom drawing.
4. Check whether the screen is scrollable.
5. Check whether scrollable content has the correct visible indicator for the stack.
6. Check whether content uses round-safe padding and avoids the physical edge.
7. Check for fixed heights, fixed widths, absolute offsets, hardcoded spacers, and edge-aligned controls.
8. Check labels for long text, wrapping, and larger font behavior.
9. Check if buttons/chips meet practical 48x48dp touch targets.
10. Replace crowded static columns with scrollable Wear OS patterns.
11. Validate at 192dp round, 227dp round, and larger font size.

## Kotlin / Compose API Rules

Do not blindly paste a generic snippet. First inspect the dependency stack.

### If the repo uses Wear Compose Material 3

Prefer Material 3 primitives where available:

- `androidx.wear.compose.material3.ScreenScaffold`
- `androidx.wear.compose.material3.ScrollIndicator`
- `androidx.wear.compose.foundation.lazy.TransformingLazyColumn`
- `androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState`
- Material 3 `Button`, `TextButton`, `IconButton`, `Card`, `ListHeader`, and related components

Material 3 projects may still contain older Material 2 APIs during migration. Do not mix Material 2 and Material 3 components unless the repo already does so intentionally.

### If the repo uses Wear Compose Material 2

Use the project-standard Material 2 pattern, commonly:

- `androidx.wear.compose.material.Scaffold`
- `androidx.wear.compose.material.PositionIndicator`
- `androidx.wear.compose.material.ScalingLazyColumn`
- `androidx.wear.compose.material.rememberScalingLazyListState`

### If the repo uses XML views

Prefer:

- `NestedScrollView`, `ScrollView`, or `RecyclerView` for content that can overflow
- round-screen resource variants where needed
- `android:ellipsize` only for non-essential text
- dimensions that avoid fixed-height dynamic text
- emulator screenshots at small round and large round sizes

## Code Smells

Treat these as likely causes of Play Store visual quality failures:

- non-scrollable `Column` with many children
- `Modifier.height(...)` wrapping dynamic text
- `Modifier.requiredHeight(...)` or `requiredSize(...)` around content that may scale
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
- mixing Material 2 and Material 3 list/scaffold components accidentally

## Preferred Fix Patterns

### Pattern 1: Material 3 scroll-safe screen

Use this as direction, not as a blind paste. Adapt imports and function signatures to the repo's exact dependency versions.

```kotlin
@Composable
fun EdgeSafeListScreen(
    modifier: Modifier = Modifier,
    content: TransformingLazyColumnScope.() -> Unit,
) {
    val listState = rememberTransformingLazyColumnState()

    ScreenScaffold(
        modifier = modifier.background(Color.Black),
        scrollState = listState,
        scrollIndicator = { ScrollIndicator(state = listState) },
    ) { contentPadding ->
        TransformingLazyColumn(
            state = listState,
            modifier = Modifier.fillMaxSize(),
            contentPadding = contentPadding,
            horizontalAlignment = Alignment.CenterHorizontally,
            content = content,
        )
    }
}
```

If the current Material 3 version uses a different `ScreenScaffold`, `ScrollIndicator`, or list-state signature, inspect the local IDE/API docs and adapt. The important requirement is not the exact snippet; it is a Wear-aware scroll container plus visible scroll indicator plus safe content padding.

### Pattern 2: Material 2 scroll-safe screen

Use this pattern only when the repo uses `androidx.wear.compose.material`.

```kotlin
@Composable
fun EdgeSafeScalingListScreen(
    modifier: Modifier = Modifier,
    content: ScalingLazyListScope.() -> Unit,
) {
    val listState = rememberScalingLazyListState()

    Scaffold(
        modifier = modifier.background(Color.Black),
        positionIndicator = { PositionIndicator(scalingLazyListState = listState) },
    ) {
        ScalingLazyColumn(
            state = listState,
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 10.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            content = content,
        )
    }
}
```

### Pattern 3: Shorten labels and move details down

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

### Pattern 4: Use safe padding without hardcoding everything

For small round screens, keep essential controls away from the circular edge. Prefer project-level dimensions or helper modifiers over repeated magic numbers. Avoid exact pixel-perfect placement.

### Pattern 5: Let text wrap or scroll

For dynamic user content, medication names, habit names, workout names, or settings labels:

- avoid fixed-height parent containers
- allow at least two lines where useful
- truncate only non-essential detail text
- keep the primary action visible and reachable
- use `stringResource` and test long strings where practical

### Pattern 6: Test large font early

After layout changes, test with larger system font sizes before claiming the fix is complete.

## Validation Commands

Use repo-specific commands. Common commands:

```bash
./gradlew projects
./gradlew clean assembleDebug
./gradlew lintDebug
./gradlew testDebugUnitTest
./gradlew assembleRelease
adb devices
adb shell settings get system font_scale
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
scrollable screens while interacting
```

## Output Format

```markdown
## Screen Edge Safety Status

Ready / Mostly ready / Not ready

## Root Cause

- exact layout cause

## Fix

- exact file-level change

## Kotlin / Compose API Notes

- Material 2 / Material 3 / XML stack detected
- scaffold/list/indicator APIs used

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
- the chosen Kotlin/Compose APIs match the repo dependency stack
- fix is reusable where possible
- final answer clearly states what was and was not verified
