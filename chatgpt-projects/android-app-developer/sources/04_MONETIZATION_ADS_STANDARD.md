# Monetization and Ads Standard

## Scope

Use for Google Play Billing, RevenueCat, AdMob, UMP/consent, rewarded access, lifetime products, subscriptions, and purchase restoration.

## First principle

Monetization is a state machine, not a UI flag.

Define separately:

- store purchase state
- entitlement state
- locally cached state
- temporary/reward state
- expiration/revocation state
- UI presentation

Do not let the UI become the source of truth.

## Google Play Billing

For one-time/lifetime products, handle at least:

- product discovery
- purchase launch
- pending
- purchased
- acknowledgement/consumption as appropriate
- duplicate callbacks
- restore/re-query
- app reinstall
- refund/revocation
- account change where relevant
- network failure
- process death during purchase
- unavailable Play Store
- unsupported device/build

A successful purchase dialog is not sufficient proof of durable ownership.

## RevenueCat

Use RevenueCat only according to the app's actual architecture.

Before changing code, determine:

- whether RevenueCat or the app completes purchases
- which product owns permanent access
- which entitlement(s) exist
- whether temporary access is server-driven
- expected expiration semantics

Never attach products to entitlements simply because names look similar.

Treat RevenueCat CustomerInfo as external state that can be stale or delayed. Define refresh and failure behavior.

Never expose RevenueCat secret API keys in app code, prompts, repositories, or logs.

## Rewarded temporary access

For rewarded temporary Pro/access patterns, define:

- exact reward event
- verification path
- authoritative grant source
- duration
- expiration time source
- behavior when offline
- behavior when verification fails
- duplicate reward behavior
- reinstall behavior
- permanent entitlement precedence

A common safe invariant is:

`effectivePro = permanentPro OR unexpiredTemporaryPro`

but use it only when the current app contract supports that model.

Permanent ownership must never be downgraded by a failed temporary-entitlement lookup.

## AdMob

Keep app IDs and ad-unit IDs in the appropriate configuration surface and prevent Google sample/test identifiers from reaching production when the repository's policy requires real IDs.

Rewarded ads must grant access only after the verified reward event. Ad load/display success alone is not a reward.

Handle:

- load failure
- show failure
- user dismissal before reward
- reward callback duplication
- app recreation
- no-fill
- offline state

## UMP / consent

Where ads require consent:

- initialize consent before requesting personalized ads as required
- support privacy-options re-entry when required
- distinguish consent availability from ad availability
- do not block the entire app unnecessarily when ads cannot load

## Platform automation boundary

Console/API configuration and application code are separate evidence domains.

Source code can prove intended identifiers and logic. It cannot prove that Play, RevenueCat, or AdMob dashboards are configured correctly.

Read back live platform state when tooling is available; otherwise report exact manual verification steps.

## Tests

Monetization regression tests should cover the app's relevant matrix:

- never purchased
- permanent owned
- pending
- cancelled
- failed
- restored
- revoked/refunded
- temporary active
- temporary expired
- permanent + temporary simultaneously
- offline stale cache
- process death / relaunch
- duplicate callback
