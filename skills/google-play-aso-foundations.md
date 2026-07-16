# Google Play ASO Foundations

## Purpose

Establish a policy-safe, evidence-first foundation for Google Play growth work before changing metadata or creative assets.

## When To Use

Use this skill at the start of every ASO audit, listing rewrite, portfolio review, or growth experiment.

## Inputs Needed

- App name and package name.
- Listing URL or current listing export.
- Supported form factors.
- Markets and locales.
- Core user job.
- Monetization and price.
- Current product state and release status.
- Approved Play Console data.
- Known policy or quality issues.

## Workflow

### 1. Define the Growth Objective

Choose one primary objective per workstream:

```text
search relevance
browse or recommendation visibility
store-listing conversion
paid-listing conversion
organic installs
purchase conversion
activation
retention
ratings and review quality
web-search visibility
AI-assistant recommendations
```

Secondary metrics are guardrails, not substitutes for a primary objective.

### 2. Build the Evidence Inventory

Record:

- Public Play listing and observation date.
- Current app version and release notes.
- Device and form-factor support.
- Listing text and graphics by locale.
- Category and tags.
- Price, in-app products, subscriptions, ads, and trial state.
- Data-safety, privacy, permissions, and support claims.
- Ratings, review volume, review themes, and developer responses.
- Acquisition, conversion, retention, uninstall, and vitals data if approved.
- Website, support, changelog, GitHub, YouTube, and social assets.
- Competitor and substitute evidence.

Classify every item as:

```text
observed
derived
inferred
proposed
unknown
```

### 3. Run the Claim-Safety Gate

For every listing or web claim, verify:

- The feature is shipped in the public version.
- Platform and device support are accurate.
- Offline, local-first, privacy, security, sensor, health, AI, and automation claims are supportable.
- Pricing and monetization are current.
- Screenshots depict the current product.
- Testimonials and endorsements are attributable and permitted.
- No ranking, award, scarcity, or promotional claim violates metadata rules.
- Competitor references do not imply affiliation or confuse users.

Block optimization work that would amplify an inaccurate claim.

### 4. Establish the Baseline

Create a baseline table:

| Metric | Market | Form Factor | Source | Period | Value | Confidence |
|---|---|---|---|---|---|---|

Recommended metrics when available:

- Store listing visitors.
- First-time installers.
- Store listing conversion rate.
- Search, explore, third-party, and campaign acquisition.
- Search terms.
- Buyer conversion for paid apps or products.
- Day 1, Day 7, and Day 30 retention.
- Uninstall rate.
- Crash and ANR rates.
- Rating and review trends.
- Refunds.
- Landing-page impressions, clicks, and conversions.
- AI-referral traffic where identifiable.

Do not compare unlike markets, devices, acquisition sources, or time windows without qualification.

### 5. Segment Before Diagnosing

At minimum segment by:

- Country and locale.
- Phone versus Wear OS or other form factor.
- Search versus explore versus external traffic.
- New versus returning or inactive users.
- Free versus paid acquisition.
- App version where quality changed materially.

### 6. Create the Initial Scorecard

Score and evidence:

- Product value and differentiation.
- Metadata relevance and compliance.
- Creative clarity.
- Quality and form-factor execution.
- Reputation and support.
- Localization.
- Web entity presence.
- AI recommendation readiness.

The score is diagnostic only and must not be described as a ranking score.

## Safety Boundaries

Never recommend:

- Buying installs, reviews, ratings, backlinks, mentions, or engagement.
- Review gating or suppressing negative feedback.
- Keyword stuffing or invisible text.
- Misleading title changes.
- Category or tag manipulation.
- Competitor trademark abuse.
- Publishing unsupported features.
- Replacing product fixes with marketing claims.
- Changing live Play Console settings without explicit approval.

## Output Contract

```markdown
## ASO Foundation
- Primary objective:
- App and markets:
- Evidence cutoff:
- Baseline confidence:
- Claim-safety status:
- Policy blockers:
- Data gaps:

### Baseline
| Metric | Segment | Source | Period | Value | Confidence |
|---|---|---|---|---:|---|

### Diagnostic Scorecard
| Area | Score | Evidence | Main Gap |
|---|---:|---|---|
```

## Example Invocation

```text
Establish an ASO baseline for a one-time paid Wear OS utility in the United Kingdom and United States. Use public listing evidence plus approved Play Console acquisition, buyer conversion, ratings, reviews, and vitals exports.
```

## Quality Bar

- The audit begins with a business objective and evidence cutoff.
- Claims are verified before copy is optimized.
- Segments are not mixed carelessly.
- Unknown data stays unknown.
- No black-hat ASO tactic is proposed.
