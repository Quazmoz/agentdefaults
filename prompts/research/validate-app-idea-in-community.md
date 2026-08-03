# Validate an App Idea in a Community

## Purpose

Provide a one-shot prompt for researching whether an app idea has meaningful prior history in a subreddit or public community and whether a new validation post would add useful evidence.

## Prompt

```text
Act as the Community App Idea Validation Agent.

Load:
- agents/community-app-idea-validation-agent.md
- skills/browser-research-foundations.md
- skills/forum-demand-mining.md
- skills/subreddit-app-idea-validation.md

Research this concept:

Concept: <APP OR FEATURE IDEA>
Problem it solves: <USER PROBLEM>
Target community: <SUBREDDIT OR PUBLIC FORUM>
Platform or audience: <ANDROID / WEAR OS / IOS / WEB / DESKTOP / OTHER>
Date range: <ALL OR SPECIFIC RANGE>
Locale: <OPTIONAL>
Known competitors or substitutes: <OPTIONAL>
Safety-sensitive domain: <NONE / HEALTH / SUPPLEMENTS / MEDICATION / FINANCE / LEGAL / OTHER>
Desired output: <RESEARCH ONLY / POST RECOMMENDATION / POST RECOMMENDATION AND DRAFT>

Required work:

1. Check the community's current rules and whether research, surveys, app discussion, self-promotion, or medical-advice requests are restricted.
2. Expand the search vocabulary beyond the proposed app name. Include exact-concept, problem-first, app-search, workaround, dissatisfaction, competitor, builder, and launch language.
3. Search all available history, while emphasizing the past 24 months and clearly identifying evidence from the past 6 months.
4. Use both native community search and external domain-restricted search when available.
5. Review thread bodies and enough comments to identify actual user behavior, existing recommendations, objections, and unresolved needs.
6. Classify each relevant thread as an explicit app request, recommendation request, problem report, workaround discussion, feature request, competitor launch, developer validation, trust/safety concern, or background-only discussion.
7. Mark each item as an exact match, close substitute, adjacent problem, or background evidence.
8. Mark the outcome as solved, partly solved, unresolved, abandoned, or unknown.
9. Collapse cross-posts and repeated promotion from the same product campaign.
10. Build a chronological history of the idea.
11. Build a solution map covering apps, websites, spreadsheets, databases, LLM workflows, manual methods, and professional services.
12. Verify whether named products still exist before describing them as current alternatives.
13. Separate market-demand evidence from technical, scientific, clinical, legal, or regulatory validity.
14. For a sensitive domain, flag authoritative-data requirements, false-positive and false-negative risks, privacy issues, maintenance burden, liability, and professional-review needs.
15. Decide whether to post now, narrow the question, comment on an existing thread, research elsewhere first, or not post.
16. Explain exactly what unresolved decision a new post would test.
17. When a post is requested, draft a transparent, non-promotional post that asks about current behavior, failed solutions, trust requirements, switching criteria, and abandonment reasons. Do not rely on “Would you use this?”

Return:

Status:
Community and scope:
Search window:
Coverage and limitations:
Prior-history verdict:
Chronological evidence:
Existing products and substitutes:
Repeated user problems:
Unresolved gaps:
Objections and trust barriers:
Sensitive-domain constraints:
Post recommendation:
Unresolved decision worth testing:
Questions worth asking:
Suggested post angle:
Draft post, if requested:
Confidence:
Sources:

Do not claim market size, willingness to pay, safety, efficacy, or novelty unless the collected evidence directly supports that claim. Cite every material factual conclusion and label inference explicitly.
```

## Example

```text
Concept: An app that tracks supplement-supplement and supplement-medication interactions, timing conflicts, and evidence strength.
Problem it solves: People managing large supplement stacks cannot easily distinguish serious interaction risks from weak or theoretical warnings.
Target community: r/Biohackers
Platform or audience: Android and web
Date range: All available history, emphasizing the past 24 months
Safety-sensitive domain: Supplements and medication
Desired output: Post recommendation and draft
```

## Expected Output

A source-backed history and product-opportunity report that explains whether community validation is still needed and, when useful, provides a focused post designed to collect decision-quality evidence.

## Quality Bar

- Searches the user problem as well as the proposed solution.
- Distinguishes exact precedent from adjacent discussion.
- Reads comments and maps existing solutions.
- Separates market demand from sensitive-domain validity.
- Recommends a post only when it can answer an unresolved question.
