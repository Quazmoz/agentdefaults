# Google Play Localized Pricing

## Purpose

Use MRA to lower Google Play prices in selected lower-purchasing-power markets while preserving reference-market pricing and requiring explicit operator approval for the exact live change.

## Scope

Initial implementation supports modern Google Play `OneTimeProduct` purchase options. Do not silently fall back to the legacy `inappproducts` API and do not change subscription prices through this workflow until subscription-specific migration/price-change semantics are implemented and tested.

## Canonical Policy

`purchasing-power-v1` derives target-market prices from the current US price and asks Google's `monetization.convertRegionPrices` endpoint to produce locally valid currencies and price patterns.

| Region | Factor |
|---|---:|
| India (IN) | 0.35 |
| Indonesia (ID) | 0.40 |
| Philippines (PH) | 0.45 |
| Turkey (TR) | 0.45 |
| Vietnam (VN) | 0.45 |
| Thailand (TH) | 0.50 |
| Brazil (BR) | 0.55 |
| Malaysia (MY) | 0.55 |
| Mexico (MX) | 0.60 |
| South Africa (ZA) | 0.60 |

US and GB are reference/protected markets and are not changed by this policy.

The factors are product policy, not foreign-exchange calculations. Google still determines the actual local currency amount and country-specific pricing pattern.

## Workflow

1. Resolve the exact MRA profile, package, product ID, and purchase-option ID from live Play state.
2. Confirm the product is a modern `OneTimeProduct`. If it is legacy-only, stop and report the migration requirement.
3. Create a plan:
   ```bash
   mra play pricing-plan \
     --profile medtick \
     --product-id <product-id> \
     --purchase-option-id <purchase-option-id>
   ```
4. Review the persisted plan. It contains:
   - app/profile and package
   - exact product and purchase option
   - current and proposed price per changed region
   - skipped regions and reasons
   - Play `regionVersion`
   - source-state fingerprint
   - SHA-256 `plan_id`
5. Present the operator a final approval table. List every app affected and every exact regional price change. Do not call apply yet.
6. Stop and wait for explicit approval naming the plan/app.
7. After approval, apply only the approved `plan_id`:
   ```bash
   mra --yes play pricing-apply \
     --profile medtick \
     --plan-id <approved-plan-id>
   ```
   The CLI still requires a native macOS approval dialog. The secure MCP tool has the same native gate.
8. MRA re-reads Play before mutation. It refuses stale source state or a changed Play `regionVersion`.
9. MRA patches only the selected purchase option pricing field and then re-reads Play. Success is reportable only if all approved regional prices match the read-back.

## Safety Invariants

- Planning is read-only with respect to product state. `convertRegionPrices` is a calculation call, not a catalog mutation.
- The agent never supplies arbitrary live prices to the apply path.
- Apply accepts a persisted `plan_id`, not an agent-authored price map.
- Plan content is integrity-checked before use.
- Any purchase-option drift after planning invalidates the plan.
- Any Play `regionVersion` change invalidates the plan.
- The approved plan must lower each target-region price; equal/higher proposals are skipped.
- Regions that are missing or not currently `AVAILABLE` are skipped rather than activated.
- US/GB must not be modified by `purchasing-power-v1`.
- A successful PATCH is insufficient; read-back verification is mandatory.
- Never convert a user approval for one app into approval for another app or a portfolio batch.

## Multi-App Rollout

After the single-app pilot is verified, generate independent plans per app/product. Before asking for portfolio approval, show:

```text
APP
PACKAGE
PRODUCT
PURCHASE OPTION
PLAN ID
REGIONS CHANGED
CURRENT -> PROPOSED PRICES
SKIPPED/UNSUPPORTED
```

Approval must name every app being changed. If the operator approves only a subset, apply only those plan IDs.

## Pilot History and Reusable Rollout Rule

MedTick was the first production pilot for this workflow. That pilot established the plan -> exact approval -> apply -> read-back pattern; it is historical evidence, not a permanent scope restriction.

Do not mutate Play until the operator has explicitly approved the exact app + `plan_id` pair being applied.

For every future app or batch:

- do not assume package name, product ID, purchase-option ID, or current price from documentation or memory when live Play state can establish them;
- generate an independent persisted plan per app/product;
- inspect enough app billing source/documentation to determine whether the UI presents Google Play's localized price for the same product/purchase option used at checkout;
- treat hardcoded/stale/mismatched app-side price display as a `PRICING_UI_WARNING` to remediate separately; it does not by itself block a store-side pricing plan when the live Play package/product/purchase option are safely and uniquely resolved;
- block pricing only when live Play target identity or supported catalog state cannot be established safely enough to guarantee the intended product would be changed;
- end the planning session at the approval boundary;
- apply only exact app + plan_id pairs explicitly approved by the operator.

The reusable invocation is `prompts/implementation/google-play-localized-pricing-rollout.md`.
