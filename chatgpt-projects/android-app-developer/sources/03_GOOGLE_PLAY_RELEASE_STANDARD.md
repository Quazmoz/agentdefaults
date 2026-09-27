# Google Play Release Standard

## Goal

Release decisions must be evidence-based. A repository edit is not a Play release qualification.

## Current target API anchors (2026-09-27)

Verify live before every consequential release decision.

Current Google Play guidance states:

- Phone/tablet new apps and app updates: target Android 16 / API 36 or higher.
- Wear OS new apps and app updates: target Android 15 / API 35 or higher.

Do not freeze these numbers into app logic or assume they remain current.

## Billing library anchor

Google Play Billing Library 9.1.0 is available as of 2026-06-18.

Portfolio policy should prefer a currently supported Billing Library and should verify the current deprecation deadline before release. Do not upgrade blindly: inspect API changes and the app's purchase contract first.

## Release blockers

Treat as release blockers when applicable:

- app does not build/package
- crash in launch or core flow
- unresolved ANR or severe lifecycle defect
- target API violation
- invalid foreground-service declaration/permission
- production build contains test/sample identifiers that must not ship
- billing ownership/entitlement behavior is incorrect
- privacy/Data safety mismatch
- required account deletion is absent
- Wear screen clipping / unreachable UI
- signing/package/application ID mismatch
- versionCode collision
- required 64-bit support missing
- listing claims features not present in the build

## Candidate identity

For a release candidate, preserve:

- Git SHA
- branch/tag
- versionCode/versionName
- package/application ID
- exact AAB/APK artifact
- artifact digest when practical
- build command and environment/tool versions

Do not rebuild a different artifact and call it the already-qualified candidate.

## Gradle and packaging review

Inspect:

- AGP/Kotlin compatibility
- compileSdk / targetSdk / minSdk
- versionCode/versionName
- release build type
- R8/minification rules
- signing references without exposing secrets
- manifest merge
- native ABI surface
- Play Billing dependency
- foreground services and permissions
- debug/test dependencies leaking into release
- proguard/serialization/reflection behavior

## Listing integrity

Store listing, screenshots, feature graphic, privacy policy, and Data safety must describe the actual release candidate.

Do not claim:

- medical/safety/professional accuracy without substantiation
- Tile/complication support when absent
- offline capability when the core feature actually requires network
- privacy guarantees stronger than the implementation

## Evidence ladder

Use this sequence where applicable:

1. Static inspection
2. Debug build
3. Unit tests
4. Lint/static/security checks
5. Targeted instrumentation/emulator tests
6. Release build / AAB
7. Release-specific lint/R8/native-surface checks
8. Device/emulator core-flow validation
9. Play/RevenueCat/AdMob console/API reconciliation
10. Exact-candidate final review

Only then use `RELEASE-QUALIFIED`, and only for the tested scope.

## Current official-doc checks before release

At minimum, re-check:

- Google Play target API requirements
- Wear OS app quality if the app supports Wear
- Billing Library support/deprecation
- foreground-service policy relevant to the app
- permissions policy for sensitive capabilities
- account deletion policy if accounts exist
- Data safety requirements
- current Play policy warnings in the app's Console
