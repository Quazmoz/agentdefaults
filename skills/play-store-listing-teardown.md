# Play Store Listing Teardown

## Purpose

Reverse-engineer the visible positioning, feature presentation, monetization, screenshot strategy, review themes, and update themes of Google Play listings without copying proprietary creative assets.

## When To Use

Use this skill after competitor discovery or when the user supplies Play listing URLs or package names.

## Inputs Needed

- Listing URLs or package names.
- Fields to extract.
- Screenshot-analysis depth.
- Maximum reviews to sample.
- Locale and country.
- Output directory.

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Confirm public or authenticated scope.
- Load completed package checkpoints.
- Define review sampling method and maximum.
- Keep observed listing text separate from interpretation.

## Workflow

For each app, extract visibly available:

- App title and developer.
- Short and full description.
- Category and tags.
- Rating, review count, install range, price.
- In-app purchases and advertising declaration.
- Last update date and recent update text.
- Data safety summary.
- Device compatibility and Wear OS support.
- Major and premium features.
- Paywall and trial model.
- Screenshot captions and readable visible text.
- Feature graphic messaging.
- Recurring phrases and keywords.
- Review themes, complaints, and workarounds.

For screenshots:

1. Inspect each screenshot visually.
2. Extract only readable marketing copy.
3. Describe the primary promise and layout pattern.
4. Note reusable design patterns without reproducing proprietary assets.
5. Mark unreadable text as unknown.

For reviews:

- Preserve publication date where visible.
- Sample across recent and critical reviews rather than only top-ranked reviews.
- Separate isolated complaints from repeated themes.
- Paraphrase and keep evidence excerpts short.

## Human Handoff Points

Request review when:

- Screenshot text is unreadable.
- Regional listing variants conflict.
- A data-safety or compatibility section is collapsed or inaccessible.
- Review sorting cannot be verified.
- CAPTCHA or authentication appears.

## Authentication Behavior

Prefer public listings. Use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) only when an authenticated view is necessary and approved.

## Output Contract

Create:

- `teardowns/<package-name>.md`
- `listing_comparison.csv`
- `listing_comparison.json`
- `positioning_matrix.md`
- `screenshots/<package-name>/`
- `source_uncertainty_log.md`

Every teardown must include:

```text
Observed facts
Positioning
Feature presentation
Monetization
Screenshot narrative
Review themes
Common complaints
Recent update themes
Opportunities and caveats
Sources and uncertainty
```

## Checkpoint Format

```json
{
  "skill": "play-store-listing-teardown",
  "package_name": "example.package",
  "locale": "en-US",
  "status": "complete",
  "screenshots_reviewed": 8,
  "reviews_sampled": 20,
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Unreadable screenshot: mark unknown and preserve the image reference.
- Hidden field: record unavailable rather than guessing.
- Conflicting locale values: retain each locale variant.
- Review loading failure: produce a listing teardown with a review limitation.
- Removed listing: record removal status and source URL.
- Dynamic page change: use semantic fallback and queue manual review.

## Privacy and Safety Requirements

- Do not reproduce full descriptions or long review text.
- Do not copy competitor screenshots into derivative marketing assets.
- Do not collect reviewer personal information.
- Keep account-specific listing previews private.

## Example Invocation

```text
Teardown the ten most relevant Wear OS timer listings. Extract positioning, paywall model, screenshot promises, recurring keywords, recent review complaints, and verified watch support.
```

## Example Successful Result

```text
Created ten app teardowns, a comparison table, a positioning matrix, and an uncertainty log with source-linked evidence.
```

## Example Partial Result

```text
All listing metadata and screenshots are complete. Review sampling is partial for two apps because review pagination stopped loading.
```

## Example Failure Result

```text
The listing was unavailable in the requested locale. A removal record was written and no fields were inferred.
```

## Quality Bar

- Observed listing facts and analysis are clearly separated.
- Screenshot claims are readable and evidenced.
- Review themes are sampled and qualified.
- Copyrighted text is minimally quoted.
