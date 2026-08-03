# App Market Research Quickstart

## Purpose

Show how to compose AgentDefaults into a resumable browser-research workflow for Google Play, Wear OS, public communities, and approved Play Console data.

## Stack

```text
Agent:
  agents/app-market-research-agent.md

Orchestrator:
  skills/app-market-research-orchestrator.md

Shared:
  skills/browser-research-foundations.md
  skills/authenticated-browser-handoff.md

Research:
  skills/play-store-autocomplete-research.md
  skills/play-store-competitor-discovery.md
  skills/play-store-listing-teardown.md
  skills/forum-demand-mining.md
  skills/play-console-search-term-analysis.md
  skills/market-opportunity-clustering.md

Brief schema:
  schemas/app-market-research-brief.schema.json

Example:
  examples/app-market-research-brief.yaml
```

For focused subreddit or public-community history research, use the smaller specialized stack:

```text
Quickstart:
  docs/quickstarts/community-app-validation.md

Agent:
  agents/community-app-idea-validation-agent.md

Skill:
  skills/subreddit-app-idea-validation.md

Prompt:
  prompts/research/validate-app-idea-in-community.md

GitHub Copilot wrapper:
  .github/agents/community-app-idea-validator.agent.md
```

Use that specialization for questions such as whether a subreddit has discussed an app concept before, what solutions commenters recommended, what remains unresolved, and whether a new validation post would add useful evidence.

## Setup

1. Copy the agent and relevant skill files into the browser-capable agent's context.
2. Configure a writable output root outside source control.
3. Provide the research brief.
4. Map the logical browser adapter contract to the selected platform.
5. Run public research first.
6. Take control of the browser only when authentication, CAPTCHA, consent, or account selection is required.
7. Review the final evidence map and manual-validation queue before making product decisions.
8. For one-community app-idea history questions, load the specialized community-validation stack instead of the full workflow.

## Antigravity-Style Adapter Notes

The repo does not claim a specific undocumented Antigravity skill API. Use the native platform format when documented.

Otherwise, treat these Markdown files as canonical instruction modules and map the browser adapter contract from [`../../agents/app-market-research-agent.md`](../../agents/app-market-research-agent.md) to the platform's browser actions.

Minimum capabilities:

```text
navigate
inspect current URL and title
locate semantic elements
click and type
wait for page state
read visible text
capture screenshot with redaction
download an approved export
pause for human takeover
resume from checkpoint
```

## Copy-Paste Invocation

```text
Load agents/app-market-research-agent.md and skills/app-market-research-orchestrator.md.

Use examples/app-market-research-brief.yaml as the brief.

Run public sources first. Save a checkpoint after each seed, keyword, listing, and thread. When Play Console authentication is required, open the legitimate login page and let me complete login, account selection, CAPTCHA, passkey, or multifactor authentication directly in the browser. Never request or capture credentials, security codes, cookies, tokens, or session data. Resume from the saved checkpoint after I confirm the target app page is loaded.

Produce CSV, JSON, Markdown, screenshots only where useful, failure logs, an evidence map, opportunity clusters, and a final manifest. Keep authenticated artifacts private.
```

For a focused community-history question:

```text
Load agents/community-app-idea-validation-agent.md and skills/subreddit-app-idea-validation.md.

Research all available history in <COMMUNITY> for <APP IDEA OR USER PROBLEM>. Search exact concept terms, problem-first language, app-search intent, workarounds, dissatisfaction, competitor names, builder posts, and launches. Emphasize recent evidence, read comments, verify current alternatives, and collapse duplicate promotion campaigns.

Check current community rules. Decide whether to post now, narrow the question, comment on an existing thread, research elsewhere first, or not post. Explain what unresolved decision a new post would test. Separate market demand from medical, scientific, legal, financial, or regulatory validity when the topic is sensitive.
```

## Output Layout

```text
research-runs/<run-id>/
  brief.yaml
  manifest.json
  checkpoints/
  autocomplete/
  competitors/
  listings/
  communities/
  console/
  evidence/
  screenshots/
  reports/
  logs/
```

Focused community-validation runs may instead use:

```text
research-runs/<run-id>/
  brief.md
  checkpoints/
  community_history.csv
  community_history.json
  solution_map.md
  unmet_needs.md
  post_recommendation.md
  source_index.md
  manual_review_queue.md
```

## Authentication and Human Takeover

The agent must pause before any credential or security step. Complete authentication directly in the browser.

The agent must also pause before:

- Downloading a potentially sensitive private export.
- Selecting an ambiguous account or app.
- Accepting consent or privilege elevation.
- Performing any account-changing action.

Research authorization does not authorize publishing, pricing, release, user, tax, banking, legal, security, credential, or production configuration changes.

## Resume Behavior

A resumed run should:

1. Load `manifest.json`.
2. Load per-skill checkpoints.
3. Skip completed units.
4. Revalidate the current page and locale.
5. Continue from the first pending unit.
6. Preserve prior failures and evidence.

## Acceptance Tests

Use [`../app-market-research-acceptance-tests.md`](../app-market-research-acceptance-tests.md) before relying on a browser adapter for production research.

## Known Limitations

- Search results and listing fields vary by locale, account, device, and time.
- Dynamic page structure may change.
- Autocomplete is a discovery signal, not a volume metric.
- Forum frequency is not market size.
- Native community and external search indexes are incomplete.
- Launch-post engagement may overstate independent demand.
- Community anecdotes do not establish safety, efficacy, causality, or professional consensus.
- Some Play Console metrics may be sampled, thresholded, or unavailable.
- Browser agents may lose tab, port, or control state.
- Authenticated exports must remain private.
