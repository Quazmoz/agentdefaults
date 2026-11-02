# Codex: Vivaldi-Only Shutterstock Contributor Authentication Preflight

## Purpose
Verify authenticated Vivaldi control without changing the contributor account, then run local PREPARE for the supplied photo source.

## Use with
- Native skill: `.agents/skills/shutterstock-contributor/SKILL.md`
- Canonical behavior: `skills/shutterstock-contributor-workflow.md`
- Quickstart: `docs/quickstarts/shutterstock-contributor.md`

## Copy-paste prompt

~~~text
You are Codex working on my MacBook. Use the AgentDefaults Shutterstock Contributor skill.

OBJECTIVE
Perform a read-only authentication and browser-control preflight for my Shutterstock Contributor account, using **Vivaldi exclusively**. Do not upload, modify, delete, submit, or change account settings.

HARD BROWSER REQUIREMENT
1. The authorized browser is Vivaldi. Do not launch Google Chrome, Chrome Canary, plain Chromium, another browser, or a generic default-browser fallback.
2. Inspect whether Vivaldi is installed (usually /Applications/Vivaldi.app) and identify its actual executable and the browser automation tools currently available to Codex.
3. Confirm the automation tool can explicitly target or safely control Vivaldi before browsing. A Chromium-compatible engine or Playwright/CDP capability does not prove it is using Vivaldi.
4. If the tool defaults to Chrome, requires Chrome only, or cannot verify the selected browser, STOP the browser step and explain which capability is missing. Do not try Chrome as a workaround.
5. Do not read, copy, export, or log passwords, browser profile files, session cookies, OAuth tokens, or 2FA material. Do not enable remote debugging on my personal Vivaldi profile or expose a debugging service without new explicit approval. Ask me to authenticate interactively in an authorized Vivaldi session when required.
6. Never bypass CAPTCHA, MFA, anti-bot challenges, or access restrictions.

READ-ONLY VERIFICATION
- If and only if safely supported through Vivaldi, open https://submit.shutterstock.com and establish that I am authenticated to the contributor dashboard.
- Determine whether the tool can read the dashboard, view Not submitted and Pending statuses, and operate the upload form in principle (without actually uploading any files).
- Verify and report the actual browser identity, tool used, whether the controlled session was authenticated, and whether browser-based file upload automation is supported.
- If capabilities are unavailable, explain the smallest secure and Vivaldi-compatible setup or manual handoff. Do not fabricate a successful test.

STOP CRITERIA
Do not perform any Shutterstock account mutation. Do not use alternate browsers without a fresh explicit user authorization.

OUTPUT
DISCOVERED
VERIFIED
UNVERIFIED
BLOCKERS
USER ACTION
~~~

## Relationship to the photo pilot
After a successful preflight, run `prompts/implementation/shutterstock-photo-pilot.md` in PREPARE mode. PREPARE does not need browser access; draft upload remains gated by separate exact-file approval.
