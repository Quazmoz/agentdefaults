# Live-First Google Play Portfolio Growth Audit (MRA + Any Execution-Capable Agent)

## Purpose

Audit the **actual, current Google Play Console state** of an Android/Wear OS portfolio using the **already-configured Mobile Release Automation (MRA) Play authentication**, then return **one evidence-backed, prioritized no-build growth plan** and, where ready, **one immutable approval batch**.

This prompt works with Codex, Claude Code, or another agent that can execute commands on the machine with the existing MRA setup (or invoke its connected **read-only** MCP tools). **Do the live inspection before presenting recommendations.** GitHub files, user memories, previous audits, public indexed listings, and product ideas are not proof of what Google Play currently serves.

**Default execution mode: AUDIT_AND_PLAN_ONLY.** No live Play changes until the operator separately approves the exact complete batch SHA-256 in a later message.

## Mandatory acceptance gate: LIVE PLAY FIRST

**Do not return a proposed publish/pricing plan before completing a real Play read for each app proposed for mutation.** For every action-ready target, you must verify the app's package and observed production-track state, and retrieve the relevant **live** listing or product state using the pre-existing MRA Play credentials. A success from `mra doctor` or a GitHub listing file **alone does not count** as a live read.

1. Determine whether your execution environment can run the **installed, authenticated** `mra` CLI or connected MRA read-only MCP tools. First attempt the current local setup; inspect `tools/mobile-release-automation/README.md` and `docs/quickstarts/mobile-release-automation.md` only when needed for locating an installed entry point.
2. **Reuse** the current MRA credential references and `MRA_HOME` settings. MRA resolves its Play session internally. **Do not** ask the operator for a key, reset OAuth, create a new service account, edit permission grants, display tokens, upload credentials into GitHub/cloud agents, or copy secret files into the workspace.
3. Run `mra profile list` and `mra doctor`; inspect the **Play service-account** check separately from unrelated RevenueCat/AdMob doctor failures. If a command is unavailable, locate the repo's documented installation/launcher and retry safely; do not replace the established credential setup.
4. Prove *working Google Play access* using at least one live `mra play tracks --profile <slug>` and `mra play listings --profile <slug>` call against a verified package. A local profile existing is **not** proof of API authorization.
5. Resolve **every** registered portfolio app and attempt relevant live reads on all mapped app profiles/packages, not only the easy or previously profitable ones. Continue past individual permission errors; classify them per app. A missing profile is a routing/configuration gap, **not** evidence that the app is unpublished.
6. If this agent is in a remote environment without access to the already-authorized MRA installation, **do not pretend to have completed the audit** and do not present speculative live prices/locales as an actionable plan. Use an available authorized local execution channel if one exists; otherwise return a concise **LIVE_AUDIT_BLOCKED** report with the tested commands and required access arrangement. Never request secrets in chat.

**No live API evidence = no READY mutation for that app.** You may report `UNVERIFIED` hypotheses, but do not put them into the execution manifest. Partial live coverage is acceptable only when precisely reported, with unverified apps excluded from ready actions.

## Canonical read-only command inventory

Use actual MRA interfaces before resorting to ad hoc vendor HTTP calls. The examples below are **read-only** unless explicitly noted; the agent supplies the real profile values found locally:

```bash
mra profile list
mra doctor
mra play tracks --profile "<profile>"
mra play listings --profile "<profile>"
mra play listing --profile "<profile>" --language en-US
mra play products --profile "<profile>"
mra play freshness --profile "<profile>"
```

Read each **existing** locale returned by `play listings` using `play listing --language ...` as needed to validate exact before-snapshots and accuracy. Do **not** infer a missing locale from a single `en-US` lookup; use the full inventory.

When the MRA MCP server is already available, use its **read-only** tools for supplementary evidence: `play_list_tracks`, `play_list_listings`, `play_get_listing`, `play_list_images`, `play_list_reviews`, `play_country_availability`, `play_list_products`, and `play_reporting_freshness` where actually registered. Confirm tool availability rather than fabricating a call. Do not call update, reply, upload, publish, activate, or other mutating tools during audit.

**Important monetization nuance:** current `mra play products`/`play_list_products` returns legacy in-app-product and subscription catalog summaries. It is **not sufficient** to establish a modern `OneTimeProduct` purchase option's live regional price. For an exact, app-source-confirmed modern product ID and purchase-option ID, use the existing `mra play pricing-plan --profile ... --product-id ... --purchase-option-id ...` read/plan path (or registered `play_plan_localized_one_time_pricing` MCP tool). It reads Play and persists a **local** hashed proposal; it does **not** change Google Play. Do not guess IDs or create unsupported plans for paid-app download prices, legacy-only products, or subscriptions. Verify the relevant billing source/catalog identity first.

`mra play freshness` checks **actual report availability and date coverage**. It is not a complete business-performance report. Review available bulk-report data and dimensional definitions where authorized; if traffic/financial reporting is missing, explicitly lower opportunity confidence instead of inventing revenue, conversion, price elasticity, or rankings.

## Source and execution order

### Phase 0 — locate the real environment without disrupting it

- Read `AGENTS.md` and the relevant MRA docs. Detect your current working directory, the installed CLI/tool path, current profile inventory, Play auth check, and one successful live Play call. Treat all credentials and private storage as out of scope for output.
- If on GitHub-only/cloud infrastructure lacking access to the established local MRA auth: use a connected authorized tool if available; otherwise report the execution boundary. Do not automatically install substitute credentials or proceed with old store metadata.
- Run observability checks **without** `--yes`. A command that creates/commits a Play edit, changes local auth, alters profiles, or mutates vendor state is not a read.

### Phase 1 — discover the complete app population

- Read `Quazmoz/android-portfolio/registry/apps.yaml` and, when necessary, each app's `.quazmoz/app.yaml`, Gradle package ID, release instructions, listing contract, and `AGENTS.md`. Resolve slug, repo, platform (Wear/phone/both), package, and MRA profile. Never assume the registry's list proves Play publication.
- Join registered apps to `mra profile list` using **package identity**, not just similar app names. Detect missing, duplicate or mismatched package bindings. Use verified package reads if the CLI accepts `--package`; do not silently create/change profiles during AUDIT_AND_PLAN_ONLY.
- Capture the Git commit SHA of any repository claims used to draft copy or establish product capabilities.

### Phase 2 — read CURRENT Play state for every accessible app

For each successfully resolved package, collect **timestamped, independently obtained** observations:

| Source | Required question | Evidence |
|---|---|---|
| `mra play tracks` | What production / Wear track and release status/version is **actually** available? | Track identifiers, release status, version codes; exact read timestamp |
| `mra play listings` | Which localized listings exist **right now**? | Locale inventory, default-language presence, count |
| `mra play listing` | What title, short/full description and video are currently configured? | Exact original text (stored locally), locale, read time |
| `mra play products` | What legacy products and subscriptions are visible? | Source IDs and types; explicitly not proof of modern pricing |
| MRA pricing plan read | Which identified modern one-time purchase option and local prices exist? | Persisted plan ID, live original regional prices, currency, availability, skip reasons, US/GB preservation |
| MCP image/review/availability reads (when exposed) | What actual store assets, reviews and geographical targeting are visible? | Source locale, data limits, latest review dates; no invented metrics |
| `mra play freshness` and authorized bulk exports | What data is fresh enough to rank opportunity by traffic or revenue? | Metric, unit/denominator, date interval, dimensions, completeness, timezone, missing permissions |

Distinguish `PRODUCTION_CONFIRMED`, `TESTING_ONLY`, `DRAFT_OR_UNPUBLISHED`, `INACCESSIBLE`, and `UNKNOWN`; do not turn an absent track or HTTP error into a false business status. Wear-only, phone-only and paired apps may use different release arrangements. Capture the relevant live track/release evidence, not only repo versionName.

**Audit completeness gate:** count total registry rows, distinct packages, mapped MRA profiles, packages with successful live Play reads, production-confirmed apps, unverified/blocked apps, and eligible pricing targets. Never silently omit a package because it returned 403/404 or had no product.

For failures, record the attempted command/tool, sanitized error/classification (401/403/404/429/5xx, no credentials), and whether the cause is known or unresolved. Use bounded retries (maximum two attempts after the first, only for transient 429/5xx/timeouts; backoff/jitter), modest concurrency (up to three independent app reads), and no blind retries of uncertain mutations.

### Phase 3 — reconcile production truth before proposing any text

For **production-confirmed** apps, compare live listing copy to actual shipped features (GitHub release/commit history, documented production artifact, Play versionCode). Do not equate current `main` or candidate `1.2.0` with released Play production. If the exact shipped capability cannot be established, propose only **claims conservatively supported by existing live copy/source history** or mark the change blocked for truth review.

Classify findings independently:
- `MISSING_LOCALE`: genuinely absent from live Play inventory, with meaningful market/traffic rationale;
- `STALE_OR_MISLEADING_COPY`: disproven claims, incorrect device/feature wording or stale version-dependent copy;
- `LOW_QUALITY_LOCALIZATION`: unnatural translation, untranslated UI disclosure missing, unsupported keywords;
- `CREATIVE_OR_REVIEW_GAP`: real screenshot/icon/video mismatch or actionable review/reputation issue;
- `PRICING_OPPORTUNITY`: existing modern one-time purchase option, fully identified and region-eligible, with actual price plan;
- `NOT_ACTIONABLE_NOW`: insufficient evidence, materially broken app experience, unsupported API, low confidence, testing-only app.

Prioritize accurate live listings, trustworthy product claims, and payment/reliability defects over amplifying traffic to broken or low-rated builds. Do not fabricate demand, predicted ROI, or store-ranking uplift.

### Phase 4 — rank the opportunity based on evidence

For every candidate, give a justified confidence level, expected mechanism (search relevance, conversion clarity, price accessibility, review trust), measured traffic/revenue if actually accessible, impacted locale/region, effort, policy/compatibility risk, expected direction (not fake precision), and a follow-up measurement period. Keep Play's 2026 install/open **click** model separate from completed installs and old visitor/acquisition metrics.

If samples are too small or reporting is unavailable, mark `LOW_DATA`; prioritize high-certainty factual fixes before experimental discounts. Do not automatically apply the `purchasing-power-v1` coefficients everywhere: they are policy proposals, not validated revenue-optimal prices.

### Phase 5 — construct ONE reviewable manifest, only from live-verified READY actions

- Prepare exact, human-reviewable before/after data for existing Play locales, complete new-locale JSON for absent ones, and **persisted** MRA `pricing-plan` IDs for applicable modern one-time products.
- Flag any translation lacking confident native-language validation `NATIVE_REVIEW_REQUIRED`, and exclude it from READY execution if the claim would be unreliable.
- Put supported `listing-create`, `listing-update`, and `pricing-apply` actions in **one** manifest conforming to `docs/quickstarts/google-play-one-approval-batch.md`. Exact profile/package, locales, expected-current snapshots including live video state when necessary, timestamps/expiry, and price plan IDs must match the actual verified data. Maximum 50 actions and validity window at most seven days. Do not include unsupported image changes, review replies, subscriptions, paid-app upfront prices, country availability or AAB changes in this batch.
- Store snapshots/manifests locally in a **private, operator-accessible location outside the repository**; never commit personal account reports or financial details. Include readable, succinct diffs in the approval report.
- Compute the raw-file SHA-256, then run:
  ```bash
  shasum -a 256 /path/to/play-growth-plan.json
  mra play growth-batch-check --manifest /path/to/play-growth-plan.json --sha256 <exact-hash>
  ```
  This final check is **read-only** and must return every action `ready` or `already_applied`. If it fails, reconcile live Play state and regenerate the manifest **before** showing the approval text. Never suppress failures or mislabel a failed check as ready.
- If no safe action survives verification, give a prioritized findings/blockers report **without** a fictitious approval hash.

## Return to the operator ONCE, after completing the live audit

Do not ask the operator to select candidate apps, manually restate live Play listing text, provide credentials, choose countries, or approve each target while auditing. Work through the complete registered inventory first. Only interrupt if the necessary live authenticated environment is unavailable; report the specific blocker honestly, not a speculative proposed plan.

Your final response must have:

1. **LIVE PLAY EVIDENCE**: current observation date/time (timezone), local MRA access mode, total inventory count, attempted/succeeded/blocked package counts, production/testing/unknown breakdown, live data/report freshness and limits. Explicitly state `LIVE_VERIFIED`, `PARTIALLY_VERIFIED`, or `LIVE_AUDIT_BLOCKED`.
2. **CURRENT APP STATUS TABLE**, one row per registered app (or compact indexed attached evidence file plus a complete in-answer breakdown): repo, verified package/profile, live track/version status, live listing locales, monetization support, report readiness, audit status; distinguish `UNKNOWN` from `NONE`.
3. **TOP PRIORITIZED OPPORTUNITIES**: rank 10–15 defensible actions with market, actual observed deficit, underlying live evidence, why they help, confidence/effort/risk, baseline metrics where available, and verification criteria. Do not claim precise earnings gains without data.
4. **EXACT PROPOSED CHANGES**: each proposed listing title/short/full text and its existing counterpart, or each affected regional currency/price and actual plan ID. Distinguish `READY`, `NEEDS_NATIVE_REVIEW`, `NEEDS_PRODUCT_FIX`, `BLOCKED_AUTH`, `UNSUPPORTED_MRA`, `LOW_DATA`.
5. **ONE APPROVAL PACKET**: manifest file location on the authorized machine, exact SHA-256, action count, list of all affected apps, result of `growth-batch-check`, and a short blast-radius/partial-failure note.
6. **RISKS / UNVERIFIED / USER ACTION**: incomplete live coverage, restricted reporting permissions, app-side release mismatches, monetization caveats, and a 30-day observation/measurement plan.

After presenting the entire verified READY batch, **stop and ask exactly once**:

```text
APPROVE PLAY GROWTH BATCH <exact-64-character-manifest-sha256>
```

**Never** use `--yes` or invoke a mutating MCP tool in the audit phase. Once that exact approval arrives later in the same agent conversation, use `mra --yes play growth-batch-apply --manifest ... --sha256 ...` **once**, without repeated native confirmation dialogs, and follow the existing batch drift/read-back/partial-failure contract. New scope, stale plans, unexpected changes or expired manifests require a newly reviewed batch; chat approval is not cryptographically authenticated by the CLI.

## Definition of done (audit phase)

- [ ] Reused the **existing MRA Play authorization** rather than inventing credentials or substituting stale GitHub copy.
- [ ] Demonstrated at least one successful live Play track **and** listing API read, and attempted live app-level coverage for the full registry.
- [ ] Captured per-app profile/package, production status, locale inventory, and errors with timestamps.
- [ ] Verified every READY listing against live original state and shipped app capabilities.
- [ ] Verified every READY pricing plan against an exact modern product and purchase option, not the legacy product list alone.
- [ ] Separated actual business metrics from report freshness and unsupported assumptions.
- [ ] Ran a successful read-only batch preflight for the complete proposed READY manifest, if nonempty.
- [ ] Returned one coherent, evidence-based audit and one **single-approval** request—without changing Google Play.

**Fail closed:** if live authenticated Play access is unavailable, return `LIVE_AUDIT_BLOCKED` with the actual failure evidence; don't manufacture a plan and ask the operator to approve it.
