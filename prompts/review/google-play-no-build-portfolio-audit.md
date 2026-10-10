# Google Play No-Build Portfolio Growth Audit (Codex + MRA)

## Purpose

Provide a reusable Codex/MRA assessment for no-build Google Play growth opportunities across an Android/Wear OS portfolio. The audit is strictly read-only and produces approval packets rather than live vendor mutations.

## Mission

Find the **smallest, defensible Google Play Console actions** that could improve qualified installs, conversion, net revenue, or customer trust across a live Android/Wear OS portfolio **without changing, rebuilding, or releasing app binaries**.

Route growth decisions through `agents/google-play-growth-optimizer-agent.md`; route live Play, RevenueCat, and AdMob observations through `agents/mobile-release-automation-engineer.md` and MRA. Follow their skill and approval contracts. Use `skills/google-play-listing-localization-review.md`, `skills/google-play-localized-pricing.md`, and `skills/app-growth-experimentation-and-measurement.md` as relevant.

## Authority and scope

**PLAN_ONLY / OBSERVE.** Read live vendor state and current GitHub source; draft proposed metadata, price plans, image/review changes, and approval packets. Do not publish, change prices/products/countries, reply to reviews, start experiments, upload assets, promote releases, or commit Play edits.

No Android/Gradle/Kotlin changes; no AAB build or upload; no repo commits as part of an audit. Never infer production state from current `main`, proposed screenshots, draft copy, or historical Play observations. If API access is unavailable, report `UNKNOWN` and continue with only supported evidence. Do not ask the user to paste secrets or copy account tokens into prompts or repositories.

## Inputs and source precedence

1. Resolve app names and repositories from the private `Quazmoz/android-portfolio/registry/apps.yaml`, not a hardcoded app list. It deliberately does **not** contain live prices, versions, production status, or performance.
2. From each app repo, inspect the current `AGENTS.md`, canonical store-listing files, package/billing contracts, and known quality defects. Record source commit and distinguish unreleased code from currently marketed features.
3. Use **live MRA API reads** for Play track/version, localized listings, product/purchase-option/region availability, review metadata, and images. Match package and track explicitly. Do not treat a candidate version's copy as shipped.
4. Use MRA reporting freshness checks and **actual accessible Play bulk CSV/ZIP reports** for traffic, conversion, sales, refunds, and country/language breakdowns; use Developer Reporting API for vitals. `mra play freshness` alone reports data availability/latency, not business-performance rankings. If report-row parsing is not implemented, show that gap and do not fabricate conversion metrics.
5. Validate changing API behavior and localization/policy constraints using current official Google documentation. The listings API supports `edits.listings.update` (create or update), but do not bypass MRA's approval-bound create/update contracts.

## Audit workflow

1. Preflight local MRA authorization/capabilities in read-only mode. Identify configured profiles, track IDs, developer-account reporting bucket, source freshness, and missing grants. No credential disclosure.
2. Inventory **published** apps separately from registered but non-production apps; exclude draft-only apps from live growth actions.
3. For each published app, compare live source listing, each live locale, and actual production-shipped claims. Flag absent high-value locales, source-language leakage, stale translations, misleading prices, unsupported form-factor claims, and unqualified candidate-only copy.
4. Identify listing visibility/conversion opportunities from measured visitors/clicks and channel/locale/country segmentation. Keep store listing clicks separate from completed acquisitions; document Play metric-definition changes. Avoid claiming uplift from low samples.
5. Identify product/region pricing opportunities from actual Play product type, active purchase option, local prices, revenue and purchase counts, refunds, and supported MRA `OneTimeProduct` capability. Protected US/GB markets stay untouched under `purchasing-power-v1`. Do not guess elasticity, pricing IDs, or tax-adjusted outcomes. Report legacy-only and paid-download prices as unsupported by this MRA workflow.
6. Audit unanswered critical reviews for actionable, source-verified responses; never promise a fix unless it shipped. Rank known crashes, billing failures and deceptive copy before acquisition expansion.
7. Review listing screenshots, current UI, Wear vs phone identity, and optional video. Never generate or upload invented screenshots. Prefer an accurate first screenshot and conservative localized copy to broad speculative expansion.
8. For missing locales, prepare native-review-ready **complete listing JSON**, preserving actual shipped product truth and explicitly acknowledging untranslated in-app UI where relevant. Mark human linguistic review `REQUIRED` when unavailable. Do not claim that translated store text makes the app's runtime localized.
9. Rank actions with expected incremental value as a **hypothesis**, confidence, source freshness, conversion denominator, implementation effort, and blast radius; include a measurement/rollback plan. Prefer high-traffic/high-confidence issues and low-effort factual corrections.
10. Produce an immutable per-app/locale/product approval packet: package, production version/track, original state or explicit absence, exact proposed payload/hash, price plan ID (when supported), affected regions, known unknowns, API capability, approval status. No live mutation.

## What Codex can execute in a later, separately approved task

- **Existing locale:** `mra --yes play listing-update --profile <profile> --language <locale> --expected-current <before.json> --body <after.json>`. Preserve existing optional promotional-video metadata.
- **Absent locale:** validate the full approved file and compute `shasum -a 256 <locale.json>`. First dry-run `mra play listing-create --profile <profile> --language <locale> --body <locale.json> --sha256 <hash> --dry-run`. After **exact separate authorization** for the app, locale, and hash, use `mra --yes play listing-create ...`. Its same-edit absence check refuses overwriting a locale created since audit. A concurrent Play commit conflict or an uncertain response must be reconciled by reading Play state, **not** blindly retried.
- **Regional price:** use `mra play pricing-plan` for a supported modern one-time product; apply only an exact separately approved app/plan_id, never a guessed price mapping.
- **Reviews/images:** use existing MRA approval-gated mutations only after verifying authenticity and scope.

A verified API commit is **not proof of user-visible publication**. Inspect Play Console Publishing overview/managed publishing and public listing propagation separately. Treat rollback as a separately approved action; for a newly added locale do not auto-delete it.

## Final output contract

```markdown
# Portfolio No-Build Growth Audit
Date, GitHub source refs, live Play observation times, report coverage/permissions
## Coverage: published / draft / unknown apps
## Top 15 ranked actions: app | locale/market | issue | evidence | impact hypothesis | effort | confidence | approval
## Top 5 missing/stale listing locale opportunities
## Top 5 pricing candidates (modern one-time products only)
## Critical review queue
## Screenshot/copy factual mismatches
## MRA capability/permission gaps, including missing report-row analytics
## 30-day rollout: pilots first, baseline and holdouts when feasible
## Exact immutable approval packets and rollback/read-back criteria
## DISCOVERED / VERIFIED / UNVERIFIED / RISKS / USER ACTION
```

Stop at `PLAN_ONLY`. Do not silently interpret this prompt as publishing authorization.
