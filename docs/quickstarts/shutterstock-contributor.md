# Shutterstock Contributor: Hark -> Mac -> Codex

## Purpose
Prepare every original photo in a supplied Hark export, stage eligible photos with verified metadata, and review and submit them manually in Vivaldi. PREPARE remains available for local-only work.

## Canonical files
- [Skill](../../skills/shutterstock-contributor-workflow.md) — behavior, trust model, provider QA, state and approval semantics.
- [Codex skill entrypoint](../../.agents/skills/shutterstock-contributor/SKILL.md) — discovery and routing.
- [Photo batch prompt](../../prompts/implementation/shutterstock-photo-pilot.md) — copy-paste invocation; the existing path is retained.
- [Acceptance scenarios](../shutterstock-contributor-acceptance-tests.md) — behavioral checks.

## MacBook instructions
1. Clone or pull AgentDefaults into a local checkout, then open that checkout in Codex. The .agents/skills directory is repository-scoped; a GitHub link by itself does not make a skill available to a different working directory.
2. Download the original photos and metadata to the Mac and give Codex the exact ZIP or directory path. Every original is inventoried; existing upload derivatives are paired with originals rather than uploaded twice.
3. Invoke [the batch prompt](../../prompts/implementation/shutterstock-photo-pilot.md) with that source. Its **UPLOAD_DRAFT** mode authorizes preparing the frozen source inventory, uploading every PASS file, and applying metadata. Codex records the resulting batch digest and that instruction as approval; it does not ask again within that scope. To inspect locally first, explicitly request **PREPARE** instead.
4. Review the photos, contact sheet, descriptions/keywords/categories, per-file holds, and batch ID. The output lives outside Git under ~/Pictures/ShutterstockPilot. HOLD, REJECT, and duplicate files are reported and excluded from upload.
5. For a PREPARE-only run, use the filled-in UPLOAD_DRAFT follow-up to authorize the exact prepared batch later. Sign in interactively in the Vivaldi session Codex can actually control; do not enter credentials into Codex.
6. Inspect the live **Not submitted** entries and their metadata, then manually click **Submit for review** in Shutterstock when satisfied. Draft-upload authority never authorizes Codex to submit.

## Vivaldi authentication and browser selection
- **Use Vivaldi, not Chrome, on the MacBook.** Confirm `/Applications/Vivaldi.app` exists (or ask for its actual location); an automation tool must be explicitly configured to target the Vivaldi executable/session. Never rely on a tool's Chrome/default-browser selection.
- Sign in interactively at https://submit.shutterstock.com **in Vivaldi**. Already being signed into Vivaldi does not prove automation can control that session; test a read-only page visit before any upload approval.
- Never copy/extract session cookies, use the user's profile as an unapproved debugging target, or expose a remote debugging endpoint. If a safe automation-controlled Vivaldi session requires separate authorization or authentication, ask for it.
- If the installed browser controller only supports Chrome, **stop** and report the limitation; do not launch Chrome, Chromium, or an alternative without the operator's new explicit approval.
- For an authentication-only smoke test, use [the Vivaldi preflight prompt](../../prompts/implementation/shutterstock-vivaldi-auth-preflight.md). It makes no Shutterstock mutations.

## Access and automation
- Supported upload methods per Shutterstock: website and FTPS. Website upload is a suitable pilot path; do not invent a contributor management API.
- Browser automation must be tested with the installed client before claiming it works. It may require installing an authorized browser tool or using manual browser steps. Handle MFA/CAPTCHA manually. Stop rather than attempting evasion.
- FTPS is a later bulk-transfer option, not evidence that metadata or submission is completed automatically.
- Shutterstock may delete files left not submitted after its stated retention window. Confirm current policy before depending on the draft queue as durable storage.

## Privacy and scale
Do not commit personal photos, EXIF/GPS, ZIP files, credentials, release forms, generated CSVs, or the local ledger to AgentDefaults. Keep originals byte-identical and prepare privacy-safe upload copies. Record finite source counts and bytes, process larger batches in bounded chunks, and reconcile uncertain uploads before retrying.

## Authority
PREPARE -> no remote changes.
UPLOAD_DRAFT -> requires explicit authority for an exact prepared batch or preparation and draft upload from an exact frozen source inventory.
Manual review/submission -> operator inspects Not submitted and clicks Submit in Vivaldi.
SUBMIT_APPROVED -> agent submission, if separately requested, still requires fresh exact approval and remote read-back.
An approved upload is not an approved submission.

## Sources
- https://submit.shutterstock.com/help/en/articles/10594645-how-do-i-submit-photos-for-review
- https://submit.shutterstock.com/help/en/articles/10617486-how-do-i-include-existing-metadata-with-my-content-submission
- https://submit.shutterstock.com/help/en/articles/10617390-what-are-the-technical-requirements-for-images
- https://submit.shutterstock.com/help/en/articles/10617414-portfolio-preparing-your-uploaded-content-for-submission
