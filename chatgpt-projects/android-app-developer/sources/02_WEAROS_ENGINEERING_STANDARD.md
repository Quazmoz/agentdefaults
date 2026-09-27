# Wear OS Engineering Standard

## Scope

Use for Wear OS development, phone+watch apps, Tiles, complications, Data Layer synchronization, ongoing activities, foreground services, sensors, and Play quality review.

## Design floor

Design for a small 192dp circular screen first, then validate larger supported round/rectangular shapes.

Treat as blockers:

- content cut off by the physical edge
- overlapping text/controls
- essential content unreachable without scrolling
- large-font clipping
- scrollable content with no appropriate scroll indicator
- touch targets that are impractically small
- phone-style dense screens on the watch

## Wear Compose stack detection

Detect before editing:

- Wear Compose Material 3
- Wear Compose Material 2
- XML views
- custom drawing/canvas
- Watch Face Format
- hybrid

Do not mix Material 2 and Material 3 APIs accidentally.

When the repository uses Wear Compose Material 3, prefer the local-version-compatible equivalents of:

- `ScreenScaffold`
- `ScrollIndicator`
- `TransformingLazyColumn`
- `rememberTransformingLazyColumnState`

When the repository uses Wear Compose Material 2, match its existing pattern, commonly:

- `Scaffold`
- `PositionIndicator`
- `ScalingLazyColumn`
- `rememberScalingLazyListState`

Do not force a Compose migration for a narrow XML/custom-view bug.

## Stable Wear quality anchors

Use current official Wear OS quality guidance before final compliance claims.

Important areas to verify include:

- font scaling
- 48x48dp touch-target expectations
- swipe/back behavior
- scroll indicators
- black/OLED-friendly backgrounds
- minimum readable text
- splash-screen behavior
- watch-shape safety
- target API requirement
- basic install/launch/task stability
- listing and screenshots

## Current platform anchors (verify live before release)

As of 2026-09-27:

- New/updated Wear OS apps submitted to Google Play must target API 35 or higher.
- Google states Wear OS apps must support 64-bit devices as of 2026-09-15.
- Watch faces must use Watch Face Format under current Play/Wear requirements.

These are not permanent constants. Re-check official Android Developers / Play Console documentation before release.

## Screen implementation rules

Prefer scrollable layouts for screens containing more than a few vertically stacked elements.

Avoid:

- fixed height around dynamic text
- absolute offsets
- large hardcoded spacers
- edge-aligned primary controls
- long button/chip labels
- non-scrollable settings screens
- hidden overflow for essential information

Validate at minimum:

- 192dp round
- a larger round device around 227dp
- normal font scale
- large font scale
- all navigation entry points
- any Tile/complication entry path

## Tiles

For Tiles:

- keep rendering fast and glanceable
- avoid heavy network/sensor work in rendering
- provide useful unavailable/error state
- verify service declarations and previews when required
- preserve battery
- use current platform APIs and quality guidance

## Complications

For complications:

- declare supported types correctly
- provide useful empty/error behavior
- avoid leaking sensitive information
- verify update cadence and battery implications

## Data Layer and phone/watch sync

Assume:

- messages can duplicate
- messages can arrive out of order
- nodes disconnect/reconnect
- one side may be on an older version
- process death can occur between send and persistence

For important state:

- define authoritative side
- persist before acknowledging where needed
- version payloads
- validate payload schema
- deduplicate/idempotently apply
- reconcile after reconnect
- do not rely on UI timing for correctness

## Sensors and battery

Register only while necessary. Unregister deterministically.

Use:

- throttling/debouncing/batching where appropriate
- conservative wake locks
- graceful missing-sensor behavior
- explicit foreground-service types/permissions when required

Battery regressions are release defects for watch apps.

## Release evidence

Compilation alone is not proof of Wear UI quality. For screen-edge or font-scale issues, require emulator/device visual evidence.
