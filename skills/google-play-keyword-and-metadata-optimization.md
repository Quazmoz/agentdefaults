# Google Play Keyword and Metadata Optimization

## Purpose

Create relevant, readable, policy-compliant Google Play metadata that matches real user intent and shipped app capabilities.

## When To Use

Use after the ASO foundation and query research are complete.

## Inputs Needed

- Brand and app name.
- Core user job and differentiators.
- Current title, short description, and full description.
- Target markets and locales.
- Search terms, autocomplete observations, competitor language, review language, and forum language.
- Current Google Play metadata limits and policy guidance.
- Features that are definitely shipped.

## Workflow

### 1. Build a Query Taxonomy

Cluster candidate queries by:

```text
category
problem
job to be done
feature
platform or device
audience
context
comparison
brand
support or troubleshooting
```

For each cluster, record:

| Query Cluster | Intent | Market | Evidence | App Fit | Competition | Priority |
|---|---|---|---|---:|---:|---:|

Reject a candidate when:

- The app cannot satisfy the intent.
- The term depends on an unsupported device or feature.
- It creates trademark or impersonation risk.
- It is only attractive because of estimated volume.
- It would make the listing misleading.

### 2. Create a Query-to-Asset Map

Map each approved cluster to the best surface:

```text
title
short description
full description
screenshot caption
feature graphic
custom store listing
localized listing
app landing page
comparison or use-case page
support page
video title or description
```

Do not force every query into Play metadata.

### 3. Optimize the Title

Requirements:

- Verify the current official character limit.
- Keep the brand recognizable.
- Describe the app accurately.
- Use at most one strong category or job phrase when it reads naturally.
- Avoid generic clutter, promotional claims, ranking language, pricing language, excessive punctuation, and unrelated competitor names.
- Count Unicode characters programmatically when possible.

Generate up to three materially different variants:

1. Brand-led.
2. Job-led.
3. Category-led.

Recommend one default and explain the tradeoff.

### 4. Optimize the Short Description

Requirements:

- Verify the current official character limit.
- State the primary job and differentiator.
- Use plain language.
- Avoid calls to action, rankings, price promotions, repetitive keywords, and unsupported superlatives.
- Do not merely repeat the title.
- Count characters.

Structure:

```text
<primary outcome> + <credible differentiator or platform>
```

### 5. Optimize the Full Description

Recommended information order:

1. Direct opening that explains the job and target user.
2. Core value and differentiator.
3. Scannable shipped features.
4. Platform, device, or sensor requirements.
5. Privacy, offline, account, or data behavior when material.
6. Monetization and limitations when useful for trust.
7. Support or documentation route.

Rules:

- Write for users first.
- Use natural variants and related concepts, not mechanical repetition.
- Place the highest-value information early.
- Keep claims testable.
- Avoid exhaustive keyword lists.
- Do not copy competitor descriptions.
- Do not include content that will quickly become stale unless there is an update process.

### 6. Select Category and Tags

- Choose the category that best represents the primary purpose.
- Use tags that describe actual content and functionality.
- Verify available choices in the current Play Console.
- Do not choose a category or tag solely because it appears less competitive.
- Record ambiguous alternatives and why they were rejected.

### 7. Plan Localization

For each locale:

- Use native or expert-reviewed language where practical.
- Research local search phrasing rather than translating keywords literally.
- Preserve product truth and legal meaning.
- Localize screenshot overlays and web pages with the listing.
- Avoid launching many low-quality automated translations.
- Validate character counts after translation.

### 8. Plan Custom Store Listings

Use custom listings only when the segment has a meaningfully different:

- Query intent.
- Feature emphasis.
- Country or cultural context.
- Acquisition source.
- User state.
- Form-factor story.

Avoid near-duplicate variants with no user benefit.

## Output Contract

```markdown
## Query Map
| Cluster | Intent | Market | Evidence | App Fit | Target Asset |
|---|---|---|---|---:|---|

## Metadata Recommendation
### Title
| Variant | Copy | Characters | Strength | Risk |
|---|---|---:|---|---|

Recommended:

### Short Description
| Variant | Copy | Characters | Strength | Risk |
|---|---|---:|---|---|

Recommended:

### Full Description
<ready-to-paste copy>

## Category and Tags
- Recommended category:
- Recommended tags:
- Rejected alternatives:

## Localization and Custom Listings
| Market | Listing Type | Query or Audience | Copy/Asset Change | Validation |
|---|---|---|---|---|
```

## Validation

Before completion:

- Recount all constrained fields.
- Confirm no unsupported claims.
- Confirm title and short description are not redundant.
- Confirm the first full-description paragraph is intelligible without keywords.
- Confirm each target query maps to a real user job.
- Confirm translations are not assumed correct without review.
- Confirm policy-sensitive rules against current official docs.

## Example Invocation

```text
Create metadata variants for a Wear OS barometer app targeting UK and US users. Prioritize watch barometer, pressure trend, and altitude context only where the shipped app supports those jobs.
```

## Quality Bar

- Metadata is readable before it is keyword-rich.
- Character counts are shown.
- Query evidence and app fit are explicit.
- Rejected keywords are documented.
- Localized recommendations are market-specific.
