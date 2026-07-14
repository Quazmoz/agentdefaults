# App Market Research Orchestrator

## Purpose

Coordinate public and authenticated app-market research into a resumable, evidence-linked workflow for Google Play, Wear OS, Android, community demand, competitor analysis, and Play Console search-term analysis.

## When To Use

Use this skill for multi-source research briefs that combine two or more of:

- Google Play autocomplete.
- Competitor discovery.
- Listing teardown.
- Reddit, XDA, forum, or public GitHub issue mining.
- Play Console analysis.
- Opportunity clustering.

## Inputs Needed

A validated brief containing:

- Platform.
- Markets and languages.
- Seed keywords.
- Sources.
- Competitor limit.
- Date range.
- Authenticated sources.
- Output formats.
- Developer constraints.
- Monetization preference.
- Optional scoring weights.

Use [`../schemas/app-market-research-brief.schema.json`](../schemas/app-market-research-brief.schema.json) as the machine-readable contract.

## Preconditions

- Load [`browser-research-foundations.md`](browser-research-foundations.md).
- Validate the brief.
- Create a run ID and isolated output directory.
- Load prior manifest and checkpoints when resuming.
- Confirm which authenticated sources are approved.

## Workflow

1. Validate the research brief.
2. Create a unique run ID.
3. Create an isolated output layout.
4. Run public unauthenticated research first.
5. Execute autocomplete collection.
6. Execute competitor discovery.
7. Execute listing teardowns for selected apps.
8. Execute public forum demand mining.
9. Normalize and deduplicate findings.
10. Pause only when an authenticated source is reached.
11. Use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md).
12. Run approved Play Console export analysis.
13. Run opportunity clustering.
14. Generate the final manifest.
15. Report incomplete tasks, evidence gaps, and confidence limitations.

Suggested layout:

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

## Skill Routing

- Shared reliability: [`browser-research-foundations.md`](browser-research-foundations.md)
- Autocomplete: [`play-store-autocomplete-research.md`](play-store-autocomplete-research.md)
- Competitors: [`play-store-competitor-discovery.md`](play-store-competitor-discovery.md)
- Listing analysis: [`play-store-listing-teardown.md`](play-store-listing-teardown.md)
- Community demand: [`forum-demand-mining.md`](forum-demand-mining.md)
- Authentication: [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md)
- Console data: [`play-console-search-term-analysis.md`](play-console-search-term-analysis.md)
- Opportunity synthesis: [`market-opportunity-clustering.md`](market-opportunity-clustering.md)

## Human Handoff Points

Pause only after saving state when:

- Authentication or CAPTCHA is required.
- The correct account, app, region, or export scope is ambiguous.
- A private report download needs confirmation.
- A consequential action appears.
- The user needs to validate an ambiguous source or cluster.

## Authentication Behavior

Authenticated work must be deferred until public research is complete. Follow [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) and never request credentials or session material.

## Output Contract

At minimum produce:

```text
brief.yaml
manifest.json
reports/final_research_report.md
reports/manual_validation_tasks.md
logs/failures.jsonl
```

The manifest must list:

- Run metadata.
- Brief hash.
- Skills executed.
- Completed and pending units.
- Artifacts.
- Source counts.
- Failure counts.
- Authenticated-source status.
- Evidence limitations.
- Final status.

## Checkpoint Format

```json
{
  "skill": "app-market-research-orchestrator",
  "run_id": "string",
  "stage": "validate|public_research|auth_handoff|console|clustering|report",
  "completed_skills": [],
  "pending_skills": [],
  "blocked_reason": "string|null",
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Invalid brief: stop before navigation and report exact validation errors.
- Partial source failure: continue independent sources and mark the run partial.
- Authentication unavailable: finish public research and checkpoint the authenticated stage.
- Corrupt artifact: exclude it from clustering and report the reason.
- Rate limit: defer the source rather than increasing automation pressure.
- Consequential action: stop and require explicit immediate confirmation.
- Platform adapter missing: document the required adapter interface and manual fallback.

## Privacy and Safety Requirements

- Public research first.
- Authenticated artifacts private.
- No credentials, cookies, session data, or private exports in source control.
- No bypass of access controls.
- No unsupported claims about browser-agent APIs.
- Platform-specific controls must be implemented as adapters when undocumented.

## Example Invocation

```text
Use the app-market research orchestrator with examples/app-market-research-brief.yaml. Run public sources first, pause for Play Console login only when needed, and resume from checkpoints.
```

## Example Successful Result

```text
Run complete. Public and approved Console sources were processed, nine opportunity clusters were generated, and all material conclusions link to evidence.
```

## Example Partial Result

```text
Public research and clustering are complete. Console analysis is checkpointed at authentication and the final report marks Console evidence unavailable.
```

## Example Failure Result

```text
The brief failed schema validation because markets and seed_keywords were empty. No browser navigation occurred.
```

## Quality Bar

- Brief validated before execution.
- Public sources complete before authentication.
- Per-skill checkpoints support resume.
- Final recommendations trace to evidence.
- Incomplete work and limitations are explicit.
