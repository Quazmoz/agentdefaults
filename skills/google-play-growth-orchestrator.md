# Google Play Growth Orchestrator

## Purpose

Coordinate ASO, creative conversion, product quality, web SEO, AI recommendation readiness, and measurement into a safe, resumable Google Play growth workflow.

## When To Use

Use for a full app audit, portfolio-wide optimization, release growth pass, or implementation plan spanning Play Console and public web assets.

## Required Inputs

Prefer `schemas/google-play-growth-brief.schema.json`.

At minimum:

- App identity.
- Markets and form factors.
- Primary objective.
- Approved data sources.
- Constraints.
- Requested outputs.
- Whether implementation is audit-only, draft-only, or approved for specified code changes.

## Canonical Sequence

```text
1. validate brief
2. create run ID and output directory
3. inventory sources and freshness
4. establish policy-safe baseline
5. run public query and competitor research if needed
6. request human authentication only for approved private data
7. analyze Play Console exports
8. create query-to-asset map
9. draft metadata
10. create creative storyboard
11. analyze quality, activation, ratings, and reviews
12. plan localization and custom listings
13. audit web SEO and canonical entity facts
14. audit AI crawler and recommendation readiness
15. create experiment backlog and measurement plan
16. prioritize 30-day actions
17. implement only explicitly authorized changes
18. validate artifacts and report limitations
```

## Skill Routing

Use:

- [`google-play-aso-foundations.md`](google-play-aso-foundations.md) for objectives, evidence, policy, and baseline.
- [`google-play-keyword-and-metadata-optimization.md`](google-play-keyword-and-metadata-optimization.md) for query mapping and listing copy.
- [`google-play-creative-conversion-optimization.md`](google-play-creative-conversion-optimization.md) for icon, screenshots, feature graphic, video, and creative tests.
- [`google-play-quality-and-retention-signals.md`](google-play-quality-and-retention-signals.md) for product promise, activation, vitals, ratings, reviews, and retention.
- [`app-web-seo-and-entity-optimization.md`](app-web-seo-and-entity-optimization.md) for crawlability, landing pages, schema, and entity consistency.
- [`ai-agent-recommendation-readiness.md`](ai-agent-recommendation-readiness.md) for crawler policy, recommendation facts, comparison utility, and prompt tests.
- [`app-growth-experimentation-and-measurement.md`](app-growth-experimentation-and-measurement.md) for experiments and decision rules.

Optional research:

- [`browser-research-foundations.md`](browser-research-foundations.md)
- [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md)
- [`play-store-autocomplete-research.md`](play-store-autocomplete-research.md)
- [`play-store-competitor-discovery.md`](play-store-competitor-discovery.md)
- [`play-store-listing-teardown.md`](play-store-listing-teardown.md)
- [`forum-demand-mining.md`](forum-demand-mining.md)
- [`play-console-search-term-analysis.md`](play-console-search-term-analysis.md)
- [`market-opportunity-clustering.md`](market-opportunity-clustering.md)

## Run Layout

```text
growth-runs/<run-id>/
  brief.yaml
  manifest.json
  checkpoints/
  sources/
  play/
    current-listing/
    metadata/
    creative/
    console/
    reviews/
    quality/
  web/
    technical/
    entity/
    content/
    structured-data/
  ai-discovery/
    crawler-policy/
    prompt-tests/
    evidence/
  experiments/
  implementation/
  reports/
  logs/
```

Keep authenticated exports private and outside public source control.

## Checkpoints

Create a checkpoint after each major stage:

```json
{
  "run_id": "growth-YYYYMMDD-app-locale",
  "stage": "metadata",
  "status": "complete",
  "inputs": ["..."],
  "outputs": ["..."],
  "source_cutoff": "RFC3339 timestamp",
  "approvals": [],
  "limitations": [],
  "updated_at": "RFC3339 timestamp"
}
```

Statuses:

```text
pending
in_progress
blocked_auth
blocked_approval
partial
complete
failed
```

## Authentication and Consequential Actions

- Run public work first.
- Use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) for Play Console or other approved private sources.
- Never request or capture credentials, cookies, tokens, passkeys, or security codes.
- Research authorization does not authorize mutations.
- Pause before publishing listings, changing price, modifying products, changing countries, starting experiments, editing releases, responding to reviews, or changing production web infrastructure unless the calling environment already has explicit authorization for that exact action.
- Record every approved mutation in the manifest.

## Portfolio Mode

For multiple apps:

1. Build a lightweight baseline for each app.
2. Rank opportunities by impact, confidence, effort, and strategic fit.
3. Select a small wave.
4. Avoid changing every listing simultaneously.
5. Preserve a portfolio experiment calendar to reduce confounds.
6. Reuse entity and landing-page templates without duplicating thin content.

Portfolio priority:

```text
priority = (impact × confidence × strategic_fit) / effort
```

Show component scores and assumptions.

## Final Report

```markdown
# Google Play Growth Plan

## Executive Summary
## Baseline and Evidence
## Diagnostic Scorecard
## Query and Intent Map
## Metadata Copy
## Creative Storyboard
## Quality and Retention Actions
## Localization and Custom Listings
## Web SEO and Entity Plan
## AI Recommendation Readiness
## Experiment Backlog
## 30-Day Execution Plan
## Measurement and Rollback
## Approvals Required
## Sources, Freshness, and Limitations
```

## Completion Contract

```text
Status:
Run ID:
Apps and markets:
Skills completed:
Public sources:
Authenticated sources:
Artifacts:
Implemented changes:
Draft-only changes:
Experiments:
Validation:
Limitations:
Approval required:
```

## Example Invocation

```text
Load agents/google-play-growth-optimizer-agent.md and skills/google-play-growth-orchestrator.md. Use examples/google-play-growth-brief.yaml. Audit the current app, draft compliant listing copy, create a Wear OS screenshot plan, identify quality and review blockers, improve the app landing-page entity record, test AI recommendation prompts, and produce a measured 30-day plan. Do not publish any Play Console changes.
```

## Quality Bar

- The workflow is resumable.
- Private data is protected.
- Public evidence precedes private access.
- Listing, product, web, and AI-discovery recommendations are connected.
- Every material action has a metric and approval state.
