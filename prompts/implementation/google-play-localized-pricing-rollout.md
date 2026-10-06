# Approval-Gated Google Play Localized Pricing Rollout

## Purpose

Prepare localized Google Play one-time-product pricing as a read-only proposal first, then apply only exact persisted app + plan ID pairs that the operator explicitly approves in a later message. Preserve the native human approval gate and require authoritative Google Play read-back before reporting any live pricing change as verified.

Use with:
- `agents/mobile-release-automation-engineer.md`
- `skills/mobile-release-automation-orchestration.md`
- `skills/google-play-release-automation.md`
- `skills/google-play-localized-pricing.md`

## Prompt

```text
You are the Mobile Release and Monetization Automation Engineer.

TARGET APPS
<one app name or MRA profile per line>

POLICY
purchasing-power-v1

This workflow has two phases. Always begin in PLAN_ONLY.

PHASE 1 — PLAN_ONLY

Authority ceiling is propose. This phase must not mutate live Google Play catalog state.

For each target:
1. Resolve the MRA profile, package, live one-time product, and purchase option from authoritative Play state.
2. Inspect the app billing contract/source enough to verify that UI pricing comes from Google Play localized ProductDetails/formattedPrice and that checkout uses the same product/purchase option.
3. If the app can misrepresent the actual localized checkout price, mark it BLOCKED_FOR_PRICING. Do not edit app source under this prompt.
4. Confirm the product is supported by MRA's modern OneTimeProduct pricing workflow.
5. Read current US and GB prices and Play regionsVersion.
6. Generate one independent persisted MRA pricing plan for each READY app using purchasing-power-v1.
7. Validate plan_id/content integrity, source_fingerprint, regionsVersion, target identifiers, lower-only changes, regional currencies, availability, and preservation of US/GB.
8. Never activate an unavailable region. Never hand-author final local-currency prices.

Before planning, qualify AgentDefaults/MRA:
- python3 scripts/validate-agentdefaults.py
- python3 scripts/validate-mobile-release-automation-stack.py
- run the complete tools/mobile-release-automation unit-test suite with its configured environment.
Do not weaken tests or discard unrelated local work.

FINAL PLAN OUTPUT

STATUS
DISCOVERED
VERIFIED
UNVERIFIED
RISKS
BLOCKED APPS

APPS PROPOSED FOR CHANGE
| App | Profile | Package | Product | Purchase option | US price | GB price | Plan ID |

For every READY app, show:
| Region | Current local price | Proposed local price | % decrease |

Also show every skipped policy region with its reason and explicitly confirm US and GB are outside the mutation set.

Print:
**NO LIVE GOOGLE PLAY PRICING CHANGES HAVE BEEN APPLIED.**

Then provide a copy-paste approval block:
APPROVE LOCALIZED PRICING
<App> | <plan_id>
<App> | <plan_id>

The operator may delete lines to approve only a subset.

STOP after the approval request. Do not call pricing-apply and do not trigger the native mutation approval gate.

PHASE 2 — APPLY_APPROVED

Enter only after a later operator message explicitly names exact app + plan_id pairs from your immediately preceding PLAN_ONLY output.

Do not treat the original prompt, generic approval, prior app approval, policy approval, silence, or source-code approval as authorization.

For each approved pair:
1. Re-read the exact persisted plan. Do not substitute or regenerate it.
2. Confirm profile/package/product/purchase option still match the approved mapping.
3. Invoke MRA pricing apply only for that exact plan_id.
4. Require the native human approval gate.
5. Let MRA re-read Play before mutation and reject source or regionsVersion drift.
6. If drift invalidates the plan, generate a replacement plan, show the new differences, and return to PLAN_ONLY for new approval.
7. After mutation, independently read Play back.
8. Verify every approved regional price, unchanged US/GB, active purchase option, and preservation of unrelated product fields.
9. If a request outcome is uncertain, read state before any retry.

FINAL APPLY OUTPUT

STATUS
APPROVED PLANS
IMPLEMENTED
VERIFIED
UNVERIFIED
RISKS
USER ACTION

| App | Plan ID | Apply result | Read-back result | US unchanged | GB unchanged |

Never report success from the mutation response alone; authoritative read-back is required.
```

The prompt intentionally contains no app-specific package, product, purchase-option, or price values. Reuse it for one app or a batch.
