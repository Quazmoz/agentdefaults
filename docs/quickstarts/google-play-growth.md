# Google Play Growth Quickstart

## Purpose

Show how to use AgentDefaults for end-to-end Google Play ASO, listing conversion, app quality, web SEO, and AI-agent recommendation readiness.

## Stack

```text
Agent:
  agents/google-play-growth-optimizer-agent.md

Orchestrator:
  skills/google-play-growth-orchestrator.md

Core skills:
  skills/google-play-aso-foundations.md
  skills/google-play-keyword-and-metadata-optimization.md
  skills/google-play-creative-conversion-optimization.md
  skills/google-play-quality-and-retention-signals.md
  skills/app-web-seo-and-entity-optimization.md
  skills/ai-agent-recommendation-readiness.md
  skills/app-growth-experimentation-and-measurement.md

Optional research:
  agents/app-market-research-agent.md
  skills/browser-research-foundations.md
  skills/authenticated-browser-handoff.md
  skills/play-store-autocomplete-research.md
  skills/play-store-competitor-discovery.md
  skills/play-store-listing-teardown.md
  skills/forum-demand-mining.md
  skills/play-console-search-term-analysis.md
  skills/market-opportunity-clustering.md

Brief:
  schemas/google-play-growth-brief.schema.json
  examples/google-play-growth-brief.yaml

Acceptance tests:
  docs/google-play-growth-acceptance-tests.md
```

## Setup

1. Copy the agent, orchestrator, and only the needed skills into the target agent context.
2. Fill in [`../../examples/google-play-growth-brief.yaml`](../../examples/google-play-growth-brief.yaml).
3. Validate the brief against [`../../schemas/google-play-growth-brief.schema.json`](../../schemas/google-play-growth-brief.schema.json).
4. Run public listing, web, query, competitor, and policy research first.
5. Use human takeover for Play Console authentication.
6. Export only approved reports.
7. Draft changes before publishing.
8. Review the measurement and rollback plan.
9. Obtain explicit approval for each consequential action.

## Copy-Paste Invocation

```text
Load agents/google-play-growth-optimizer-agent.md and skills/google-play-growth-orchestrator.md.

Validate examples/google-play-growth-brief.yaml and create an isolated growth run. Audit the public Play listing, current product claims, screenshots, app quality, reviews, website, canonical entity facts, crawler controls, and AI recommendation prompts. Use approved Play Console exports only after human-controlled authentication.

Produce:
- a diagnostic scorecard
- query and intent map
- compliant title, short-description, and full-description variants with character counts
- a form-factor-specific screenshot storyboard
- quality, retention, ratings, and review actions
- localization and custom-listing opportunities
- app landing-page SEO and structured-data changes
- AI crawler and recommendation-readiness fixes
- a prioritized experiment backlog
- a measured 30-day plan

Do not publish Play Console, pricing, release, review, or production website changes without explicit approval.
```

## Minimal Invocation

```text
Audit this Google Play listing for one primary market. Give me the top five evidence-backed actions, one recommended title, one short description with character count, the first four screenshot concepts, the biggest product-quality blocker, and the highest-value web or AI-discovery fix.
```

## Wear OS Invocation

```text
Run the Google Play growth stack for this Wear OS app. Treat watch screenshots, small-round UI, Tiles, complications, background color, large text, rotary input, sensor support, and companion-phone behavior as separate validation areas. Do not place watch screenshots in device frames or add overlays when current Play requirements prohibit them.
```

## Output Layout

```text
growth-runs/<run-id>/
  brief.yaml
  manifest.json
  checkpoints/
  sources/
  play/
  web/
  ai-discovery/
  experiments/
  implementation/
  reports/
  logs/
```

## Safe Authentication Script

```text
The legitimate Play Console login page is open. Please take control and complete account selection, login, passkey, CAPTCHA, or multifactor authentication directly. Do not send credentials or security codes through chat. Navigate to the target app and report, then tell me when it is loaded. I will resume from the saved checkpoint in read-only mode.
```

## Approval Boundaries

A growth audit may inspect and draft. It does not automatically authorize:

- Publishing a store listing.
- Changing title, descriptions, category, tags, or graphics.
- Starting or stopping an experiment.
- Changing price, products, subscriptions, countries, or availability.
- Releasing an app bundle.
- Responding to reviews.
- Editing a production website.
- Changing robots or crawler access.
- Buying ads, links, mentions, ratings, reviews, or installs.

## Validation

Use [`../google-play-growth-acceptance-tests.md`](../google-play-growth-acceptance-tests.md).

Repository validation:

```bash
python3 scripts/validate-agentdefaults.py
```

## Known Limitations

- Google Play does not expose a complete public ranking formula.
- Search terms, conversion, and recommendations vary by locale, device, account, and time.
- Third-party keyword metrics are estimates.
- Store experiments can be underpowered for low-traffic apps.
- Before/after comparisons contain confounds.
- AI recommendation results vary between products, sessions, locales, and dates.
- No workflow can guarantee ranking, featuring, installs, reviews, or AI inclusion.
