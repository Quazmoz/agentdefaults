# Shutterstock Contributor: Hark -> Mac -> Codex

## Goal
Run a bounded local three-photo pilot from Hark's Google Photos export, producing stock-ready photographs and an auditable metadata package. Optionally stage draft uploads through an authenticated Shutterstock Contributor browser and later submit only with separate explicit approval.

## Canonical files
- [Skill](../../skills/shutterstock-contributor-workflow.md) — behavior, trust model, provider QA, state and approval semantics.
- [Codex skill entrypoint](../../.agents/skills/shutterstock-contributor/SKILL.md) — discovery and routing.
- [Three-photo pilot prompt](../../prompts/implementation/shutterstock-photo-pilot.md) — copy-paste invocation.
- [Acceptance scenarios](../shutterstock-contributor-acceptance-tests.md) — behavioral checks.

## MacBook instructions
1. Clone or pull AgentDefaults into a local checkout, then open that checkout in Codex. The .agents/skills directory is repository-scoped; a GitHub link by itself does not make a skill available to a different working directory.
2. Download Hark's three original photos plus metadata to the Mac. Put the trusted received ZIP at ~/Downloads/shutterstock-google-photos-pilot.zip, or tell Codex the explicit local directory.
3. Review [the pilot prompt](../../prompts/implementation/shutterstock-photo-pilot.md) and run it in **PREPARE** mode. Codex must not upload or submit during this run.
4. Review the actual photos, contact sheet, description/keywords/categories, rights assessment, and batch ID. The output lives outside Git under ~/Pictures/ShutterstockPilot.
5. If satisfied, send the prompt's exact UPLOAD_DRAFT follow-up using the generated batch ID/digest and filenames. Be signed into your own contributor account in the browser the automation can actually control. Do not enter credentials into Codex.
6. Inspect the live **Not submitted** entries. Only then can a separate, fresh SUBMIT_APPROVED request authorize clicking Submit for review. You can instead finish manually.

## Access and automation
- Supported upload methods per Shutterstock: website and FTPS. Website upload is a suitable pilot path; do not invent a contributor management API.
- Browser automation must be tested with the installed client before claiming it works. It may require installing an authorized browser tool or using manual browser steps. Handle MFA/CAPTCHA manually. Stop rather than attempting evasion.
- FTPS is a later bulk-transfer option, not evidence that metadata or submission is completed automatically.
- Shutterstock may delete files left not submitted after its stated retention window. Confirm current policy before depending on the draft queue as durable storage.

## Privacy and scale
Do not commit personal photos, EXIF/GPS, ZIP files, credentials, release forms, generated CSVs, or the local ledger to AgentDefaults. Keep originals byte-identical, and prepare privacy-safe upload copies. Scale to larger batches only after three images and duplicate-safe recovery have been verified.

## Authority
PREPARE -> no remote changes.
UPLOAD_DRAFT -> requires specific separate upload approval for a prepared batch.
SUBMIT_APPROVED -> requires an additional fresh approval and remote read-back.
An approved upload is not an approved submission.

## Sources
- https://submit.shutterstock.com/help/en/articles/10594645-how-do-i-submit-photos-for-review
- https://submit.shutterstock.com/help/en/articles/10617486-how-do-i-include-existing-metadata-with-my-content-submission
- https://submit.shutterstock.com/help/en/articles/10617390-what-are-the-technical-requirements-for-images
- https://submit.shutterstock.com/help/en/articles/10617414-portfolio-preparing-your-uploaded-content-for-submission
