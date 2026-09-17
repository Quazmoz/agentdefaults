# Capability-aware mobile release automation

Mobile Release Automation (MRA) treats Google Play, RevenueCat, and AdMob as one
reconcilable system while respecting the very different write capabilities and
risk boundaries of each vendor.

The primary agent workflow is:

```text
mra_plan -> inspect proposed drift/actions -> mra_apply -> mra_verify
```

For fleet health use:

```text
mra_audit_profile
mra_audit_portfolio
```

## Design rules

1. **Public documented APIs only.** MRA does not scrape vendor consoles or call
   private browser endpoints.
2. **Capabilities, not assumptions.** AdMob exposes useful reporting/inventory
   even when Google has not enabled limited-access monetization writes for the
   account.
3. **Secrets stay behind MCP.** Desired state contains identifiers and optional
   `*_secret_id` references only. Literal authorization headers, API keys,
   private keys, passwords, and OAuth tokens are rejected.
4. **High-risk writes fail closed.** Public Play listing/tester changes,
   irreversible AdMob linking, RevenueCat current-offering changes, webhooks,
   and purchase-access wiring require the native local approval gate.
5. **Read back after writing.** Apply re-plans after each mutation, and verify
   re-reads authoritative vendor state rather than trusting mutation responses.
6. **Account-gated AdMob writes degrade gracefully.** If Google returns the
   documented limited-access denial, MRA returns `manual_required` with one
   precise console action and expects `mra_verify` afterward.
7. **Relationship convergence is additive by default.** Desired RevenueCat
   product links are attached when missing; unspecified existing links are not
   silently detached. Destructive convergence requires a separate explicit
   policy rather than treating omission as deletion.

## Desired-state shape

Desired state is a JSON-shaped object passed directly to `mra_plan`,
`mra_apply`, or `mra_verify`. The reconciler covers the highest-value setup and
wiring state across all three vendors:

```json
{
  "play": {
    "listing": {
      "language": "en-US",
      "title": "MotionGuard: Motion Alarm",
      "short_description": "Movement alarm for your Android device.",
      "full_description": "Long Play Store description here."
    },
    "testers": [
      {
        "track": "internal",
        "google_groups": ["android-testers@example.com"]
      }
    ]
  },
  "revenuecat": {
    "project": {"name": "MotionGuard"},
    "app": {"name": "MotionGuard Android"},
    "products": [
      {
        "store_identifier": "motionguard_lifetime",
        "type": "non_consumable",
        "display_name": "Lifetime"
      }
    ],
    "entitlements": [
      {
        "lookup_key": "pro",
        "display_name": "Pro",
        "products": ["motionguard_lifetime"]
      }
    ],
    "offerings": [
      {
        "lookup_key": "default",
        "display_name": "Default",
        "is_current": true,
        "packages": [
          {
            "lookup_key": "$rc_lifetime",
            "display_name": "Lifetime",
            "position": 1,
            "products": [
              {
                "store_identifier": "motionguard_lifetime",
                "eligibility_criteria": "all"
              }
            ]
          }
        ]
      }
    ],
    "webhooks": [
      {
        "name": "Production events",
        "url": "https://example.com/revenuecat",
        "environment": "production",
        "authorization_header_secret_id": "00000000-0000-0000-0000-000000000000"
      }
    ]
  },
  "admob": {
    "app": {
      "display_name": "MotionGuard",
      "platform": "ANDROID",
      "linked_package": "com.quazmoz.motionguard"
    },
    "ad_units": [
      {
        "display_name": "rewarded_unlock",
        "format": "REWARDED",
        "ad_types": ["RICH_MEDIA", "VIDEO"]
      }
    ]
  }
}
```

The UUID above is only an example reference. Do not place a secret value in the
object. Store webhook authorization material in Bitwarden Secrets Manager and
pass its immutable secret UUID.

For RevenueCat package product relationships, a string is shorthand for
`{"store_identifier": "...", "eligibility_criteria": "all"}`. The explicit
object form is useful when Google Play billing eligibility needs a narrower
criterion. Entitlement `products` are store-identifier strings.

For AdMob, omitting `linked_package` defaults to the profile's Android package.
Setting `linked_package` explicitly to `null` requests a manual/unlinked AdMob
app instead and avoids the irreversible store-link operation.

## Planning semantics

Each action reports:

- `platform`: `play`, `revenuecat`, or `admob`
- `operation`: the concrete reconciliation operation
- `status`: `satisfied`, `needed`, or `blocked`
- `risk`: `observe`, `contained`, or `high`
- `params`: non-secret execution parameters
- `detail`: why the action is or is not required

`mra_apply` executes only `needed` actions. It re-plans after every attempted
mutation so a newly created RevenueCat project/app/offering/package or AdMob app
can unblock later resources in the same invocation. It will not repeatedly
retry an action that was declined, denied, or failed in that invocation.

`mra_verify` performs a fresh read and returns only remaining drift. A run is
converged only when all requested desired-state actions are satisfied and the
relevant platform reads succeeded. An unrelated platform credential failure does
not make a partial desired-state plan non-converged.

## RevenueCat dependency order

A typical full monetization graph converges in this dependency order:

```text
project
  -> Play app
  -> products
  -> entitlements
      -> entitlement/product attachments
  -> offerings
      -> packages
          -> package/product attachments
      -> current offering
  -> webhooks
```

MRA derives RevenueCat object IDs from authoritative read-back; the desired state
continues to use stable lookup keys and Play store identifiers. Product wiring is
high-risk because it changes live purchase-access behavior, so entitlement and
package attachments require native local approval.

Making an offering current is also high-risk. RevenueCat models this as offering
update state, so MRA creates a missing offering first and then performs the
current-offering update rather than putting `is_current` into the creation
payload.

## AdMob capabilities and reporting

The AdMob MCP surface separates ordinary auth/permission failures from Google's
documented per-account limited-access gate.

Read/diagnostic tools include:

- `admob_capabilities`
- `admob_list_apps`
- `admob_app_approval_summary`
- `admob_list_ad_units`
- `admob_list_ad_sources`
- `admob_list_adapters`
- `admob_list_mediation_groups` where account access permits it
- `admob_list_ad_unit_mappings` where account access permits it
- `admob_network_report`
- `admob_mediation_report`
- `admob_campaign_report`
- `admob_monetization_health`

`admob_monetization_health` is the portfolio-oriented preset. It requests the
request/match/show funnel, clicks, earnings, RPM, app version, Google Mobile Ads
SDK version, ad format, and serving-restriction dimensions so agents can detect
monetization regressions without opening the AdMob UI.

Conditional write tools are implemented for app/ad-unit creation, mediation
groups, mappings, mapping batches, and mediation experiments. They report the
account gate honestly instead of recommending scope/IAM changes that cannot
unlock a Google-side entitlement.

## Google Play management

In addition to bundles, tracks, promotions, subscriptions, and one-time
products, MCP can manage/read:

- localized Store listings
- Store images/screenshots
- Google Group tester configuration
- country availability
- reviews and developer replies
- ProGuard/R8 or native deobfuscation artifacts

Committed public listing/image/tester changes and review replies are approval
gated. Dry-run listing/image/tester operations use a Play edit that is validated
and then discarded.

## RevenueCat management

MRA adds project provisioning, complete entitlement/offering/package product
wiring, current-offering management, and webhook integration management to the
existing app/product workflow.

Webhook authorization headers are never accepted as literal desired-state
values. Supply `authorization_header_secret_id`; MRA resolves the value from
Bitwarden only inside the MCP process. RevenueCat's returned webhook
`signing_secret` is redacted before agent-visible output.

Changing the current offering, attaching products, and creating/updating/deleting
live webhooks are high-risk operations and require native local approval.

## Portfolio audit

`mra_audit_portfolio` isolates failures per profile so one broken vendor binding
does not abort the entire portfolio scan. Current findings include:

- missing package/profile identity
- Play/RevenueCat/AdMob read failures
- unanswered one- or two-star Play reviews
- RevenueCat Play app missing for the configured package
- RevenueCat products present without a current offering
- AdMob apps in `ACTION_REQUIRED` or `IN_REVIEW`
- configured AdMob app IDs not found in inventory
- matched AdMob apps with no ad units

The audit includes raw, redacted snapshots so an agent can investigate without
requiring a second set of broad discovery calls.

## AdMob manual handoff contract

A `manual_required` result is not an automation failure. It means MRA reached a
Google-enforced account gate on a documented limited-access operation.

The expected sequence is:

1. MRA performs every preceding API-supported step.
2. MRA returns the exact app/ad-unit action that remains.
3. The operator performs that action in AdMob.
4. Run `mra_verify` again.
5. MRA discovers the new object and continues normal reconciliation.

Do not add private Console endpoints, cookie/session replay, browser scraping, or
other mechanisms intended to evade Google's account-level API restriction.
