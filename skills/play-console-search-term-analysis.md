# Play Console Search Term Analysis

## Purpose

Analyze the user's own Google Play Console search-term and acquisition data through a secure human-authenticated session or an approved export.

## When To Use

Use this skill when the user asks to analyze search terms, acquisition channels, keyword performance, country differences, or listing gaps for their own Play Console apps.

## Inputs Needed

- App or portfolio scope.
- Date range.
- Country and traffic-source filters.
- Desired metrics.
- Approved export location.
- Output directory.
- Whether downloading a private report is authorized.

## Preconditions

- Apply [`browser-research-foundations.md`](browser-research-foundations.md).
- Use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) for login and account selection.
- Save the target app, date range, country, and traffic-source context.
- Prefer official exports or APIs over table scraping.
- Confirm before downloading potentially sensitive business data.

## Preferred Source Order

1. Official Play Console export.
2. Official API, when available and appropriate.
3. Browser extraction only when the required data is not exposed by export or API.

## Workflow

1. Hand off authentication to the user.
2. Confirm the selected developer account and app using non-sensitive visible indicators.
3. Navigate only to the user-specified app or portfolio scope.
4. Apply and record date, country, and traffic-source filters.
5. Determine whether an official export provides the needed fields.
6. Explain the export and request confirmation before downloading.
7. Parse exported CSV files instead of repeatedly scraping paginated tables.
8. Preserve source metadata and do not mix apps, countries, date ranges, or traffic sources.
9. Mark unavailable, sampled, or privacy-thresholded metrics.
10. Generate performance and keyword-gap reports from the approved data.

## Human Handoff Points

Hand off for:

- Login, account selection, passkey, CAPTCHA, and multifactor authentication.
- Selecting the correct developer account or app when ambiguous.
- Consent or privilege elevation.
- Approval before downloading a private export.
- Any change to app configuration or publishing state.

This skill is read-only by default.

## Authentication Behavior

Follow [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md). Never request or store credentials, codes, cookies, session material, or API secrets.

## Output Contract

Create:

- `play_console_search_terms.csv`
- `search_term_performance.md`
- `keyword_gaps.md`
- `console_export_metadata.json`

Metadata must include:

```text
developer_account_context
app_context
date_range
countries
traffic_sources
exported_at
source_method
available_metrics
unavailable_metrics
sampling_or_threshold_notes
private_artifact
```

## Checkpoint Format

```json
{
  "skill": "play-console-search-term-analysis",
  "stage": "auth|scope|filters|export|parse|report",
  "app_context": "non-sensitive label",
  "date_range": "string",
  "countries": [],
  "traffic_sources": [],
  "status": "in_progress",
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

- Wrong app or account: stop and request user correction.
- Export unavailable: document the limitation and consider browser extraction.
- Mixed filters: discard the mixed result and rerun with one recorded context.
- Download missing: ask the user to locate or approve the exported file.
- Sampled metric: label it clearly.
- Session expiration: checkpoint and repeat authenticated handoff.
- Any publishing or configuration page: do not mutate it.

## Privacy and Safety Requirements

- Treat exports and reports as private.
- Do not commit generated Console artifacts.
- Do not mix data across apps without explicit portfolio scope.
- Do not download sensitive user-level exports.
- Do not change releases, prices, declarations, users, tax, banking, or security settings.

## Example Invocation

```text
Analyze search-term acquisition for my selected app in Play Console for GB and US over the last 90 days. Prefer an official CSV export, preserve filters, and stop for my confirmation before downloading it.
```

## Example Successful Result

```text
Parsed the approved export for one app, two countries, and one date range. Produced search-term performance and keyword-gap reports with sampled metrics labeled.
```

## Example Partial Result

```text
Authentication and app scope are confirmed. The workflow is waiting for explicit approval before downloading the private CSV export.
```

## Example Failure Result

```text
Stopped because the visible page was for a different app than the saved scope. No data was mixed or exported.
```

## Quality Bar

- Human-controlled authentication.
- Official export preferred.
- Filters and app scope preserved.
- Private data remains private.
- Read-only unless a separate action is explicitly authorized.
