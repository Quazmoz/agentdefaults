# Community App Validation Quickstart

## Purpose

Show how to use AgentDefaults to research whether an app idea has prior history in a subreddit or public community, identify existing solutions and unmet needs, and decide whether a new validation post would add useful evidence.

## Stack

```text
Agent:
  agents/community-app-idea-validation-agent.md

Core research:
  skills/browser-research-foundations.md
  skills/forum-demand-mining.md
  skills/subreddit-app-idea-validation.md

One-shot prompt:
  prompts/research/validate-app-idea-in-community.md

GitHub Copilot wrapper:
  .github/agents/community-app-idea-validator.agent.md
```

For broader competitor and store research, add:

```text
agents/app-market-research-agent.md
skills/play-store-competitor-discovery.md
skills/play-store-listing-teardown.md
skills/market-opportunity-clustering.md
```

## Use This Instead of Broad Market Research When

- The question centers on one subreddit or community.
- You need historical precedent rather than a full market-size study.
- You want to know whether a validation post would be repetitive.
- You need evidence from comments, workarounds, objections, and previous product launches.
- You need to separate community demand from the validity of health, financial, legal, or scientific claims.

Use the broader [`app-market-research.md`](app-market-research.md) workflow when the decision also requires store keywords, competitor listings, Play Console data, or cross-market opportunity scoring.

## Setup

1. Load the canonical agent and three core skills.
2. Provide the app concept, underlying problem, target community, platform, and desired date range.
3. Mark sensitive domains explicitly.
4. Run public research only unless the user explicitly authorizes authenticated browsing.
5. Save source URLs, exact dates, thread classifications, solution states, and evidence limitations.
6. Review the post recommendation before publishing anything.

## Copy-Paste Invocation

```text
Load agents/community-app-idea-validation-agent.md and skills/subreddit-app-idea-validation.md.

Research all available history in <COMMUNITY> for <APP IDEA OR USER PROBLEM>. Search exact concept terms, problem-first language, app-search intent, workarounds, dissatisfaction, named competitors, builder posts, and launches. Emphasize the past 24 months and identify evidence from the past 6 months separately.

Read enough comments to determine what people currently use, whether existing solutions actually solve the problem, why users reject them, and what remains unresolved. Collapse cross-posts and repeated promotion campaigns. Verify current product availability before calling something an active competitor.

Check the community's current rules. Decide whether I should post now, narrow the question, comment on an existing thread, research elsewhere first, or not post. Explain what unresolved decision a new post would test.

If this is a sensitive domain, separate market demand from medical, scientific, financial, legal, or regulatory validity. Do not infer safety or efficacy from community anecdotes.

Return a chronological evidence map, solution map, unmet needs, objections, trust barriers, recommendation, confidence, limitations, and sources. Draft a non-promotional validation post only if it would add new evidence.
```

## Example: Supplement Interaction App

```text
Concept: An Android and web app that tracks supplement-supplement and supplement-medication interactions, timing conflicts, duplicated ingredients, and evidence strength.
Problem: People with large supplement stacks cannot easily distinguish serious risks from weak, theoretical, or low-priority warnings.
Community: r/Biohackers
Date range: All history, emphasizing the past 24 months
Sensitive domain: Supplements and medication
Desired output: Research, post recommendation, and draft only if useful
```

The agent should search beyond “supplement interaction app,” including stack management, timing, contraindications, duplicated ingredients, spreadsheets, databases, Drugs.com, Examine, Cronometer, Medisafe, LLM workflows, privacy, affiliate concerns, false warnings, and evidence citations.

## Output Layout

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

## Decision Standard

A validation post is worthwhile only when it can answer a decision not already resolved by prior history.

Strong examples:

```text
Which warnings must be separated by severity?
Would source citations and evidence grades change trust?
Do users need supplement-medication coverage, or would that increase distrust?
What makes people abandon current trackers after setup?
Is local-only storage important enough to affect switching?
```

Weak examples:

```text
Would you use this app?
Is this a good idea?
Would anyone pay for this?
Do you like these features?
```

## Known Limitations

- Reddit and external search indexes are incomplete.
- Deleted, removed, or inaccessible threads may leave gaps.
- Upvotes and comment counts are not market-size estimates.
- Launch-post engagement can overstate independent demand.
- Old recommendations may refer to abandoned products.
- Community anecdotes do not establish safety, efficacy, causality, or professional consensus.
- A useful validation post does not prove willingness to pay or retention.

## Quality Bar

- Search vocabulary covers the problem and substitutes, not only the proposed product.
- Exact precedent is separated from adjacent discussion.
- Comments and objections are analyzed.
- Existing products are verified where possible.
- The recommendation names the unresolved decision.
- Any drafted post is transparent, non-leading, non-promotional, and rule-aware.
