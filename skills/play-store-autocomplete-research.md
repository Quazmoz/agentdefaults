# Play Store Autocomplete Research

## Purpose

Collect visible Google Play autocomplete suggestions from seed keywords and preserve query, locale, rank, provenance, and checkpoint relationships.

## When To Use

Use this skill for:

- App keyword discovery.
- Google Play search-language research.
- Wear OS, phone, tablet, or general Android market exploration.
- Alphabetical or modifier expansion of known seeds.

Do not use it to invent suggestions or treat autocomplete volume as market size.

## Inputs Needed

- Seed keyword list.
- Country or locale.
- Language.
- Device category.
- Optional expansion set such as `a-z`, digits, or modifiers.
- Maximum suggestions per seed.
- Output directory.
- Retry limit.

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Confirm the intended Google Play locale and language.
- Load prior checkpoints and completed seed relationships.
- Confirm that suggestions will be recorded only when visibly returned.

## Workflow

1. Open Google Play search for the requested locale.
2. Enter one seed or expanded seed.
3. Wait for the suggestion list to become visibly stable.
4. Capture every visible suggestion in order.
5. Preserve the original string and a normalized comparison string.
6. Record rank, seed, expanded seed, locale, collection time, and evidence method.
7. Deduplicate normalized suggestions while retaining every source-seed relationship.
8. Save progress after each seed.
9. Capture a screenshot when the UI is ambiguous, truncated, or inconsistent.
10. Record empty results and failures instead of inferring missing suggestions.

Normalization may trim surrounding whitespace, collapse repeated spaces, and create a case-folded comparison value. It must not rewrite the observed phrase.

## Human Handoff Points

Request human help when:

- CAPTCHA appears.
- The wrong country, language, or account context cannot be corrected safely.
- Suggestions are visually present but inaccessible to semantic extraction.
- A consent screen blocks the search interface.
- The user must verify an ambiguous suggestion.

## Authentication Behavior

Public autocomplete collection should not require authentication. If Google requests authentication, use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) or continue publicly when the task can be completed without login.

## Output Contract

Create:

- `play_store_autocomplete.csv`
- `play_store_autocomplete.json`
- `autocomplete_summary.md`
- `screenshots/`
- `autocomplete_failures.jsonl`

CSV fields:

```text
seed,expanded_seed,suggestion,normalized_suggestion,rank,locale,language,device_category,collected_at,status,source_url,evidence_method,notes
```

## Checkpoint Format

```json
{
  "skill": "play-store-autocomplete-research",
  "seed": "wear os timer",
  "expanded_seed": "wear os timer a",
  "locale": "en-GB",
  "status": "complete",
  "suggestion_count": 8,
  "attempts": 1,
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Empty list: retry once after clearing and re-entering the seed, then record empty.
- Layout change: try semantic labels and list roles, then request review.
- Rate limit: stop expansion, slow the run, and checkpoint remaining seeds.
- CAPTCHA: hand off to the user.
- Locale mismatch: do not write results until corrected.
- Duplicate suggestion: retain the relationship and deduplicate only in the normalized aggregate.

## Privacy and Safety Requirements

- Do not bypass rate limits or anti-bot controls.
- Do not capture account-specific information.
- Do not claim a suggestion appeared unless it was visibly returned.
- Keep screenshots focused on the suggestion UI.

## Example Invocation

```text
Collect Google Play autocomplete suggestions for "wear os timer", "wear os medication", and "wear os fidget" in en-GB and en-US. Expand each seed with a-z and save a checkpoint after every expanded seed.
```

## Example Successful Result

```text
Collected 186 visible seed relationships representing 74 unique normalized suggestions across GB and US locales.
```

## Example Partial Result

```text
GB complete. US expansion paused after rate limiting at seed "wear os timer m"; remaining seeds are checkpointed.
```

## Example Failure Result

```text
No records written because the page stayed on a consent interstitial and human takeover was unavailable.
```

## Quality Bar

- Visible suggestions only.
- Stable rank and locale provenance.
- Resumable per seed.
- Deduplicated without losing source relationships.
