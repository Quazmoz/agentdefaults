# Play Store Competitor Discovery

## Purpose

Identify direct competitors, substitutes, and adjacent applications for a set of Google Play keywords while preserving search rank and verification evidence.

## When To Use

Use this skill when:

- Mapping a Google Play category.
- Checking whether an app idea is already served.
- Comparing Wear OS and phone alternatives.
- Building a candidate list for deeper listing teardown.

## Inputs Needed

- Search keyword list.
- Country or locale.
- Maximum results per keyword.
- Optional Wear OS-only filter.
- Optional minimum rating or install threshold.
- Known apps to include or exclude.
- Output directory.

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Confirm locale and platform scope.
- Load prior keyword and package checkpoints.
- Define direct competitor, substitute, and adjacent product criteria.

## Workflow

1. Search Google Play for each keyword.
2. Capture visible ranked results before opening listings.
3. Record app name, package name or stable listing URL, developer, rank, and keyword.
4. Open the most relevant listings.
5. Classify each app as direct, substitute, adjacent, or uncertain.
6. Verify Wear OS support from listing text, device indicators, screenshots, or linked official documentation.
7. Do not infer watch support from keyword presence alone.
8. Record price model, rating, review count, installs, update date, ads, and in-app purchases only when visible.
9. Deduplicate by package name or stable listing identity while retaining every keyword-rank relationship.
10. Queue uncertain claims for manual verification.

## Human Handoff Points

Request help when:

- Search results are personalized or ambiguous.
- Device support indicators are unclear.
- The listing is region-restricted.
- CAPTCHA or consent blocks navigation.
- The user must confirm whether a known app should be included.

## Authentication Behavior

Prefer public Play listings. If authentication is required for a region or device view, use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) and keep account-specific details out of artifacts.

## Output Contract

Create:

- `competitors.csv`
- `competitors.json`
- `competitor_discovery.md`
- `screenshots/`
- `manual_verification.md`

Core fields:

```text
app_name,package_name,developer,listing_url,source_keyword,search_rank,direct_or_substitute,device_support,wear_os_verified,price_model,rating,review_count,installs_if_visible,last_updated_if_visible,contains_ads,in_app_purchases,evidence,confidence,collected_at
```

## Checkpoint Format

```json
{
  "skill": "play-store-competitor-discovery",
  "keyword": "wear os medication reminder",
  "locale": "en-GB",
  "status": "complete",
  "ranked_results_captured": 10,
  "listings_verified": 6,
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Missing package name: retain the stable listing URL and mark identity confidence.
- Inconsistent ranks: preserve the observed session rank and timestamp.
- Unsupported device claim: mark `unknown` and add manual verification.
- Region restriction: record the restriction without bypassing it.
- Duplicate app: merge app identity and append keyword-rank relationships.
- Page failure: do not populate fields from prior knowledge.

## Privacy and Safety Requirements

- Collect public listing data only unless authenticated scope is explicitly requested.
- Do not copy proprietary creative assets into reports.
- Do not treat ratings, installs, or rank as permanent facts.
- Preserve timestamps for volatile values.

## Example Invocation

```text
Find up to ten competitors for each of five Wear OS utility keywords in GB and US. Separate direct competitors from phone-only substitutes and verify watch support with visible evidence.
```

## Example Successful Result

```text
Found 31 unique apps across 50 ranked relationships. Twelve had verified Wear OS support, nine were phone-only substitutes, and ten require manual device-support review.
```

## Example Partial Result

```text
Ranked results are complete, but four listings are unavailable in GB and remain unverified.
```

## Example Failure Result

```text
Stopped after the result page repeatedly redirected to an unsupported locale. No ranks were inferred.
```

## Quality Bar

- Rank captured before listing navigation.
- Wear OS support explicitly verified.
- Direct, substitute, adjacent, and uncertain classes separated.
- Duplicate identities retain all discovery relationships.
