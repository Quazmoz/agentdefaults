# Comet Authenticated Research Skill

## Purpose

Use this skill when an agent needs to perform internet research through a local Comet browser session, especially when authentication, human approval, JavaScript-heavy pages, or automation-hostile websites make normal research tools insufficient.

This skill supports `agents/comet-authenticated-research-agent.md`.

## When To Use

Use this skill for:

- Authenticated account portals
- Private documentation behind login
- Dashboards or admin pages
- Pages blocked or degraded under Playwright/headless automation
- MFA, SSO, email link, CAPTCHA, or device approval flows requiring user action
- Research that needs the user's existing browser context
- Visual verification of dynamic pages

Do not use this skill for:

- Bypassing authentication, MFA, CAPTCHA, paywalls, or access controls
- Extracting cookies, tokens, local storage, or session headers
- Scraping private data at scale
- Mutating accounts without explicit user confirmation

## Inputs Needed

The agent should identify:

- Target URL or site
- Research question
- Whether login is required
- Whether the user must select an account, workspace, tenant, project, store, or billing profile
- What data is safe and necessary to read
- Whether the answer must distinguish account-specific facts from general facts

## Instructions

### 1. Decide Whether Comet Is Needed

Use public web research or direct docs first when enough.

Use Comet only when:

- The page requires login.
- The site blocks automation.
- The page is heavily client-rendered.
- The user's local browser state is necessary.
- The user explicitly asks for Comet.

### 2. Start a Safe Auth Flow

If login is needed, use this pattern:

```markdown
I need your authenticated browser session for this.

Open this in Comet: <url>
Log in directly there. Do not paste credentials here.
Tell me when you are on the target page.
```

Never ask for passwords, MFA codes, recovery codes, cookies, bearer tokens, API keys, local storage, session storage, request headers, or private keys.

### 3. Confirm Context

If multiple contexts exist, ask the user to confirm the selected context before using account-specific data.

Examples:

- Workspace
- Tenant
- Organization
- Project
- Store
- Billing account
- Cloud subscription
- Region

### 4. Collect Minimal Page Context

Use the least invasive source that answers the question:

1. Selected text
2. Visible page text
3. Screenshot for visual-only state
4. Comet page summary
5. User-provided copied text
6. Exported HTML/PDF only when explicitly provided

Avoid full-page extraction when the visible section is enough.

### 5. Verify Important Claims

Cross-check material claims when possible:

- In-app labels or settings
- Official docs
- Vendor help pages
- Changelogs
- Invoices or billing pages, if the user explicitly navigated there
- Multiple pages/tabs inside the authenticated site

Treat Comet's summary as a clue, not source-of-truth.

### 6. Separate Account-Specific From General Findings

Use explicit labels:

```markdown
Account-specific:
- <finding visible in user's account>

Generally documented:
- <finding from public docs>

Not verified:
- <claim not directly confirmed>
```

### 7. Stop Before Mutating Actions

Require explicit confirmation before:

- Submitting forms
- Saving settings
- Sending messages
- Making purchases
- Deleting records
- Downloading private files
- Accepting terms
- Connecting integrations
- Switching account context
- Sharing private data

## Expected Output

```markdown
Findings:
- <finding>
- <finding>
- <finding>

Verified from:
- <visible page / section / official source>

Account-specific:
- <only if relevant>

Caveats:
- <material caveats only>

Next:
- <single best next action>
```

## Quality Bar

A successful use of this skill:

- Uses Comet only when needed
- Keeps credentials and session data private
- Lets the user complete auth directly
- Reads only necessary page content
- Confirms account/workspace context when relevant
- Verifies material claims
- Clearly separates account-specific findings
- Produces concise actionable output

## Notes

Pair this skill with `skills/comet-local-bridge-safety.md` when designing or reviewing a Comet control bridge.
