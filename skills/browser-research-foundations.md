# Browser Research Foundations

## Purpose

Provide the shared reliability, provenance, checkpoint, privacy, and human-collaboration rules for browser-capable research agents.

Use this skill with every public or authenticated browser-research skill in the app-market research stack. Platform-specific adapters may change navigation mechanics, but they must not weaken these rules.

## When To Use

Use this skill when an agent:

- Navigates websites to collect structured research.
- Extracts data from dynamic pages.
- Produces CSV, JSON, Markdown, screenshots, or browser walkthroughs.
- Needs resumable execution.
- May encounter login, CAPTCHA, consent, rate limits, or consequential actions.

## Inputs Needed

- Research run ID.
- Target sources and allowed domains.
- Locale, country, language, and date-range context.
- Output root.
- Evidence requirements.
- Retry limits.
- User-approved authenticated scope, if any.

## Preconditions

1. Confirm the task is research, not an account-changing workflow.
2. Confirm the output directory is isolated for the run.
3. Record the initial URL, locale, and current workflow stage.
4. Load any existing checkpoint before navigation.
5. Use [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md) whenever authentication, CAPTCHA, passkey, consent, or multifactor authentication appears.

## Workflow

### 1. Create Run State

Use a stable run identifier such as:

```text
2026-07-14T081500Z-wear-os-market-gb-us
```

Create or logically reserve:

```text
research-runs/<run-id>/
  brief.yaml
  manifest.json
  checkpoints/
  evidence/
  screenshots/
  reports/
  logs/
```

### 2. Navigate Conservatively

- Verify the visible domain after each cross-domain navigation.
- Prefer accessibility labels, roles, headings, links, and semantic structure.
- Use coordinate clicks only as a documented fallback.
- Wait for a verifiable page state, not a fixed sleep, whenever possible.
- Detect wrong tabs, stale pages, consent screens, account selectors, and unexpected redirects.
- Use bounded exponential backoff for transient failures.
- Stop after the configured retry limit.

### 3. Record Provenance

Every material observation must retain:

- Source URL.
- Page or app title.
- Collection timestamp.
- Query or seed.
- Search position, when applicable.
- Locale and country.
- Visible evidence.
- Extraction method.
- Confidence.
- Status: `observed`, `derived`, `inferred`, or `unknown`.

Never promote an inference to an observed fact.

### 4. Save Checkpoints

Save progress after each completed unit such as a seed, keyword, app, thread, export, or cluster.

A checkpoint should be idempotent: resuming it must not duplicate completed records.

### 5. Produce Reviewable Artifacts

- Preserve raw observed values and normalized values separately.
- Keep deduplication relationships instead of discarding source context.
- Include failure and uncertainty logs.
- Capture screenshots only when they add evidence or resolve ambiguity.
- Redact or omit private information.
- Mark authenticated artifacts as private.

## Human Handoff Points

Pause after saving state when the user must:

- Log in.
- Select an account, app, workspace, or tenant.
- Complete CAPTCHA, passkey, security-key, consent, or multifactor authentication.
- Correct ambiguous navigation.
- Open an inaccessible page.
- Confirm a potentially sensitive export.
- Approve a consequential action.

After takeover, inspect the current page and resume from the saved workflow stage.

## Authentication Behavior

Do not collect credentials, one-time codes, cookies, local-storage values, session headers, API tokens, recovery codes, or backup codes.

Authentication must follow [`authenticated-browser-handoff.md`](authenticated-browser-handoff.md).

## Output Contract

Every run must produce or update:

```json
{
  "run_id": "string",
  "status": "complete|partial|blocked|failed",
  "started_at": "RFC3339 timestamp",
  "updated_at": "RFC3339 timestamp",
  "sources": [],
  "artifacts": [],
  "completed_units": [],
  "pending_units": [],
  "failures": [],
  "limitations": []
}
```

## Checkpoint Format

```json
{
  "run_id": "string",
  "skill": "string",
  "stage": "string",
  "unit_key": "string",
  "status": "pending|in_progress|complete|blocked|failed",
  "source_url": "string|null",
  "page_title": "string|null",
  "locale": "string|null",
  "attempts": 0,
  "records_written": 0,
  "last_error": "string|null",
  "updated_at": "RFC3339 timestamp"
}
```

## Error Handling

Classify failures as:

- `transient`: retry with bounded backoff.
- `layout_changed`: try a semantic fallback, then request review.
- `auth_required`: invoke authenticated handoff.
- `captcha`: stop and request human takeover.
- `rate_limited`: slow down, record the limit, and defer the unit.
- `access_denied`: do not bypass controls.
- `data_unavailable`: record `unknown`.
- `unsafe_action`: refuse or request explicit confirmation.

Never fabricate a result because a page failed.

## Privacy and Safety Requirements

- Collect only data needed for the stated research purpose.
- Do not bypass robots, authentication, paywalls, access controls, CAPTCHA, or anti-bot systems.
- Respect platform terms and conservative navigation rates.
- Prefer official exports and APIs over browser extraction.
- Do not store browser profiles, cookies, session data, or private exports in source control.
- Paraphrase long copyrighted discussions and preserve only short evidence excerpts.

## Example Invocation

```text
Apply browser-research-foundations to a resumable Wear OS market-research run for GB and US sources. Save provenance, failure logs, and checkpoints after every seed, app, and thread.
```

## Example Successful Result

```text
Run complete: 42 seeds, 73 apps, and 118 discussion signals processed. All observations include URLs, locale, timestamps, evidence status, and extraction method.
```

## Example Partial Result

```text
Public research complete. Play Console analysis is blocked at human login. The checkpoint is saved at stage console_auth.
```

## Example Failure Result

```text
Stopped after three bounded retries because the page layout no longer exposed a stable result list. No inferred records were written.
```

## Quality Bar

- Resumable without duplicate work.
- Auditable provenance for every material claim.
- Clear separation of observed, derived, inferred, and unknown values.
- No credential or session-secret capture.
- No silent bypass of access controls.
