# Market Opportunity Clustering

## Purpose

Convert autocomplete, competitor, listing, and community research artifacts into evidence-linked market opportunity clusters with transparent scoring and feasibility caveats.

## When To Use

Use this skill after at least one upstream research artifact exists. Use multiple source types when making a material recommendation.

## Inputs Needed

- Artifacts from other app-market skills.
- Target platform.
- Developer constraints.
- Monetization preference.
- Technical capabilities.
- Optional scoring weights.
- Output directory.

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Validate input schemas and locales.
- Preserve source identifiers and evidence links.
- Separate missing data from zero values.
- Define scoring weights before ranking.

## Workflow

1. Normalize concepts without discarding original phrases.
2. Cluster semantically similar requests and search terms.
3. Separate broad categories from specific product opportunities.
4. Link every conclusion to underlying evidence.
5. Identify direct competitors and substitutes before calling a need unmet.
6. Flag strong free substitutes.
7. Assess platform-native fit such as Tiles, complications, notifications, sensors, haptics, rotary input, and phone companion behavior.
8. Flag inaccessible APIs, restricted permissions, unreliable background execution, policy risk, and high maintenance burden.
9. Score with transparent dimensions.
10. Separate measured facts, derived metrics, inferred conclusions, and speculation.
11. Generate manual validation tasks for remaining unknowns.

Suggested dimensions:

```text
evidence_strength
pain_frequency
recency
direct_competition
substitute_competition
watch_native_usefulness
technical_feasibility
policy_risk
monetization_potential
maintenance_burden
differentiation_potential
```

A sample normalized score:

```text
score = weighted_positive_dimensions - weighted_risk_dimensions
```

Document the exact weights and transformations. Do not imply statistical precision that the data does not support.

## Human Handoff Points

Request human review when:

- Two clusters overlap materially.
- A platform restriction is uncertain.
- Monetization assumptions depend on private business data.
- The evidence is sparse but the inferred opportunity appears attractive.
- The final shortlist will drive substantial development effort.

## Authentication Behavior

This skill should normally operate on generated artifacts and does not need authentication. Keep Play Console-derived evidence private and use only the approved aggregate scope.

## Output Contract

Create:

- `opportunity_clusters.csv`
- `opportunity_report.md`
- `evidence_map.json`
- `manual_validation_tasks.md`

Every recommended opportunity must include:

```text
Problem statement
Target user
Evidence
Existing competitors
Existing substitutes
Unresolved gap
Proposed MVP
Differentiation
Technical feasibility
Key platform restrictions
Monetization hypothesis
Confidence level
Manual validation required
```

## Checkpoint Format

```json
{
  "skill": "market-opportunity-clustering",
  "stage": "normalized|clustered|scored|reported",
  "input_artifact_hashes": {},
  "clusters_completed": 12,
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Missing source type: continue with an explicit evidence limitation.
- Conflicting data: preserve both observations and lower confidence.
- Unsupported platform claim: mark unknown and add validation.
- Dominant free substitute: flag it instead of hiding it.
- Unstable score: provide sensitivity notes.
- Corrupt artifact: stop that input and record the validation failure.

## Privacy and Safety Requirements

- Do not expose private Play Console data in public reports.
- Do not convert discussion frequency into market-size claims.
- Do not use model prior knowledge as sole evidence.
- Keep speculation explicitly labeled.

## Example Invocation

```text
Cluster the Wear OS market artifacts for a solo developer who prefers low-cost one-time paid utilities. Weight watch-native usefulness and technical feasibility above total discussion frequency.
```

## Example Successful Result

```text
Produced nine evidence-linked opportunity clusters and a three-item shortlist with competitor, feasibility, policy, and monetization caveats.
```

## Example Partial Result

```text
Clustering is complete, but monetization scores are provisional because Play Console search-term data was unavailable.
```

## Example Failure Result

```text
Stopped because the input artifacts did not retain source identifiers, making evidence linkage unreliable.
```

## Quality Bar

- Every recommendation traces to evidence.
- Competitors and substitutes are considered.
- Feasibility and policy risks are explicit.
- Scoring is transparent and sensitivity-aware.
