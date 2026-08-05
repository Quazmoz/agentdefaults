# Automation Platform Evidence and Confidence

## Purpose

Make automation-platform recommendations traceable, edition-aware, and appropriately uncertain. This skill prevents unsupported feature matrices, stale product claims, and weighted scores that appear precise despite missing evidence.

## When To Use

Use whenever the recommendation compares named products, editions, hosting models, licensing tiers, integrations, limits, support lifecycles, or migration compatibility.

## Inputs Needed

- shortlisted products and exact editions
- hosting models
- evaluation date and evidence cutoff
- mandatory gates
- weighted criteria
- official documentation or other approved sources
- unresolved product, licensing, support, or implementation questions

## Evidence Model

Classify every material claim as one of:

```text
observed
  Directly visible in the inspected environment, repository, export, or product configuration.

official
  Supported by current first-party product documentation, release notes, lifecycle pages, licensing pages, or support statements.

derived
  Calculated from observed or official inputs using a stated method.

inferred
  A reasoned conclusion based on evidence, but not directly stated by a source.

proposed
  A recommended future design, control, pilot, or migration step.

unknown
  Material information that has not been verified.
```

Do not present `inferred`, `proposed`, or `unknown` statements as product facts.

## Evidence Status

Assign one status to each version-sensitive claim:

```text
verified
  Current first-party evidence supports the exact product, edition, and hosting model.

partially_verified
  Some relevant evidence exists, but an edition, limit, integration, or operating assumption remains unresolved.

conflicting
  Reliable sources or observed behavior disagree.

stale
  Evidence predates the allowed cutoff or a material product change.

unverified
  No adequate evidence has been collected.

not_applicable
  The criterion does not apply to the candidate or automation unit.
```

## Source Hierarchy

Prefer sources in this order:

1. Observed deployment, repository, configuration, license, or approved export.
2. Official product documentation for the exact edition and hosting model.
3. Official release notes, lifecycle notices, security advisories, and pricing or licensing pages.
4. Maintainer-owned repositories and specifications.
5. Reputable independent analysis for operational experience or comparison context.
6. Community reports only as supporting evidence, never as the sole source for a critical capability claim.

Record access dates. Do not assume a product name implies the same features across SaaS, self-hosted, community, enterprise, or legacy editions.

## Evidence Ledger

Maintain a compact ledger for material claims:

| Claim ID | Product / Edition | Claim | Type | Status | Source | Access Date | Applies To | Notes |
|---|---|---|---|---|---|---|---|---|

`Applies To` should identify the automation unit, hosting model, version, plan, or environment.

## Confidence-Aware Scoring

### Keep fit and evidence separate

For every scored criterion record:

```text
fit_score: 0 to 5
fit_rationale
evidence_status
evidence_confidence: high | medium | low | unknown
source_ids
```

Do not encode missing evidence as a low fit score. `unknown` is not equivalent to `0`.

### Optional confidence-adjusted score

When a numeric comparison is useful, use:

```text
high confidence    factor 1.00
medium confidence  factor 0.75
low confidence     factor 0.50
unknown confidence no adjusted score

adjusted_points = weight × fit_score × confidence_factor
```

Always show raw fit and confidence separately. The adjusted score is a prioritization aid, not a probability or product-quality rating.

### Coverage threshold

Calculate evidence coverage from the weighted criteria with verified or partially verified support.

```text
evidence_coverage = supported_criterion_weight / applicable_criterion_weight
```

Do not declare a high-confidence winner when:

- evidence coverage is below 80 percent
- a mandatory gate is unresolved
- the leading products are within a materially insignificant margin
- the result depends on an unverified edition, integration, license, or support assumption
- reliable sources conflict

Use `needs_more_evidence` or `pilot_first` instead.

## Tie and Margin Rules

Do not manufacture significance from small weighted-score differences.

- Treat candidates within 5 percent of total applicable points as effectively tied unless a hard requirement, operating-model advantage, or migration difference is decisive.
- Prefer the lower-risk incumbent when candidates are effectively tied and migration has no material strategic benefit.
- Prefer a pilot when the tie depends on scale, failure recovery, usability, or integration behavior that documentation cannot prove.

## Freshness Rules

Version-sensitive claims always require a source date and product context, including:

- product and edition availability
- runner, agent, controller, and target support
- limits and quotas
- approval, environment, policy, identity, and audit features
- licensing and pricing
- support lifecycle and deprecations
- migration or state compatibility
- plugin, provider, action, module, collection, cookbook, and integration maintenance

When evidence is stale, state what must be reverified rather than silently reusing it.

## Required Output

```markdown
## Evidence Quality Summary
- Evaluation date:
- Evidence cutoff:
- Weighted evidence coverage:
- Material unresolved gates:
- Overall confidence:

## Evidence Ledger
| ID | Product / Edition | Claim | Type | Status | Source | Access Date | Notes |
|---|---|---|---|---|---|---|---|

## Confidence-Aware Matrix
| Criterion | Weight | Candidate | Raw Fit | Confidence | Adjusted Points | Source IDs |
|---|---:|---|---:|---|---:|---|

## Conflicting or Stale Evidence

## Verification Actions
| Priority | Unknown | Verification Method | Decision Impact |
|---|---|---|---|
```

## Guardrails

- Do not cite a product homepage as proof of a specific edition feature.
- Do not use search-result snippets as final evidence when the underlying official page is available.
- Do not score `unknown` as zero.
- Do not average non-applicable criteria into a candidate score.
- Do not hide conflicting sources.
- Do not call a recommendation high confidence when a mandatory gate is unverified.
- Do not claim a score is statistically significant or predictive.

## Quality Bar

- Every material product claim is traceable.
- Exact editions and hosting models are visible.
- Fit, evidence quality, and uncertainty remain separate.
- Stale and conflicting evidence are explicit.
- Small score differences do not create false certainty.
- Verification work is prioritized by decision impact.
