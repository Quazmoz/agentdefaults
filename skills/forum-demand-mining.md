# Forum Demand Mining

## Purpose

Find authentic public user statements that reveal unmet needs, frustrations, missing features, app-search intent, and current workarounds.

## When To Use

Use this skill for Reddit, XDA, Google support forums, manufacturer forums, public GitHub issues, and other publicly accessible communities.

## Inputs Needed

- Topic or device.
- Allowed communities or domains.
- Date range.
- Intent phrases.
- Maximum threads and comments.
- Locale.
- Excluded terms.
- Output directory.

Default intent phrases should include variants of:

```text
looking for an app
is there an app
does anyone know an app
wish there was
why is there no
missing feature
alternative to
recommend an app
Wear OS app for
Pixel Watch app for
Galaxy Watch app for
```

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Confirm sources are public.
- Define the date range and query plan.
- Load completed thread checkpoints.
- Exclude private communities and unnecessary personal data.

## Workflow

1. Search titles and comments using topic and intent phrases.
2. Capture surrounding context, not isolated phrases.
3. Record source URL, publication date, community, device, and engagement signal.
4. Distinguish original requests from replies recommending existing products.
5. Classify each signal as solved, partly solved, unresolved, or unknown.
6. Record requested solution, current workaround, and recommended existing app.
7. Deduplicate cross-posts and quoted copies.
8. Redact usernames from the main report unless attribution is materially necessary.
9. Paraphrase long passages and preserve only short evidence excerpts.
10. Save a checkpoint after each thread.

## Human Handoff Points

Request help when:

- A source requires login or consent.
- CAPTCHA appears.
- A thread is ambiguous or context is missing.
- The user needs to choose between broad and narrow communities.
- Access would require joining a private community.

Do not enter private communities solely for research automation.

## Authentication Behavior

Public research is preferred. If the user explicitly authorizes an authenticated public-community session, use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md). Do not scrape private messages, private groups, or user profiles.

## Output Contract

Create:

- `demand_signals.csv`
- `demand_signals.json`
- `unmet_needs.md`
- `source_index.md`
- `manual_review_queue.md`

Fields:

```text
source,thread_title,thread_url,published_at,community,device,user_problem,requested_solution,current_workaround,recommended_existing_app,solved_status,engagement_signal,evidence_excerpt,confidence,tags,collected_at
```

## Checkpoint Format

```json
{
  "skill": "forum-demand-mining",
  "thread_url": "https://...",
  "query": "Pixel Watch app for",
  "status": "complete",
  "signals_written": 3,
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Deleted thread: preserve metadata and mark content unavailable.
- Duplicate discussion: link to the canonical signal.
- Missing date: mark unknown.
- Rate limit: stop, slow the source schedule, and preserve remaining queries.
- CAPTCHA or access control: request human help and do not bypass.
- Ambiguous recommendation: queue for manual review.

## Privacy and Safety Requirements

- Collect only public, necessary content.
- Do not collect unnecessary usernames or profile details.
- Do not bypass site restrictions.
- Do not treat post count as market size.
- Prefer paraphrase over long quotation.
- Respect source rate limits and terms.

## Example Invocation

```text
Mine public Reddit and XDA discussions from the past 24 months for Wear OS timer, medication, fidget, offline utility, and phone-monitoring needs. Capture context, workarounds, and whether each request appears solved.
```

## Example Successful Result

```text
Captured 118 deduplicated demand signals from 74 threads, including 43 unresolved and 29 partly solved requests.
```

## Example Partial Result

```text
Reddit research is complete. XDA paused after rate limiting with 17 queries checkpointed.
```

## Example Failure Result

```text
The selected community is private. No attempt was made to bypass access controls.
```

## Quality Bar

- Context preserved.
- Public sources only.
- Solved status distinguished.
- Duplicates and cross-posts collapsed.
- Personal information minimized.
