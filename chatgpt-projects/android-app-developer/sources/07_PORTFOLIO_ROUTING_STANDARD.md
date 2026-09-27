# Portfolio Routing and Governance Standard

## Control-plane role

`Quazmoz/android-portfolio` is a coordination and governance layer. It is not the implementation source of truth for an individual app.

Use it for:

- repository routing
- app classification
- stable architecture/capability metadata
- portfolio standards
- cross-app evidence-backed failure patterns
- health/triage tooling

Do not use it as canonical storage for:

- versionCode/versionName
- current SDK/dependency versions
- current build/test result
- current defects
- Play release state
- pricing
- secrets

## App repository read order

For substantial app work:

1. repository root `AGENTS.md`
2. `.quazmoz/app.yaml` when present
3. documentation index
4. source/build configuration
5. relevant current GitHub state

A `.quazmoz/app.yaml` profile is routing context, not a replacement for code inspection.

## Profile concepts

The portfolio profile schema can describe:

- phone / Wear platforms
- module paths
- Room
- DataStore
- WorkManager
- Data Layer
- Tiles
- complications
- Play Billing
- RevenueCat
- AdMob
- UMP
- analytics
- crash reporting
- account support/deletion
- documentation paths

Only trust fields supported by current repository evidence.

## Portfolio triage

Triage output is prioritization evidence, not proof that a defect still exists.

Before acting:

- re-fetch current `main`
- inspect current source/config
- reproduce or verify the issue when practical

Use severity roughly as:

- P0 — severe crash/ANR/data loss/security/permanent-entitlement correctness
- P1 — release/core-flow/build/signing/version/purchase lifecycle/Wear UI blockers
- P2 — reliability/battery/background/sync/permissions/accessibility/Tile/complication correctness
- P3 — docs/listing/screenshots/lower-risk polish

Do not fabricate user counts, revenue impact, or certainty.

## Generic capability routing

Reusable generic Android/Wear/release automation belongs in `Quazmoz/agentdefaults`.

Portfolio-specific private routing and observations belong in `Quazmoz/android-portfolio`.

Current app implementation always wins over both.
