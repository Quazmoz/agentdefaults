---
name: shutterstock-contributor
description: Prepare original photographs from a Hark or Google Photos ZIP for Shutterstock Contributor, including private local intake, image quality validation, copyright/release screening, accurate metadata and CSV, duplicate-safe draft browser uploads, and approval-gated submission. Trigger on Shutterstock photo intake, metadata, draft upload, or contributor portfolio workflows.
---

# Shutterstock contributor workflow for Codex

Use the canonical procedure in [skills/shutterstock-contributor-workflow.md](../../../skills/shutterstock-contributor-workflow.md). Read it before acting, including its approval and stop conditions.

For the Hark-to-Mac three-photo pilot, invoke the reusable [pilot prompt](../../../prompts/implementation/shutterstock-photo-pilot.md) and follow the [Codex quickstart](../../../docs/quickstarts/shutterstock-contributor.md).

## Required local browser: Vivaldi
**Vivaldi is the only default authorized browser for this user's Shutterstock workflow on macOS.** Before website access, confirm the actual Vivaldi executable/session and verify the automation tool can target it explicitly. Do **not** start Chrome, Chrome Canary, generic Chromium, or a hidden browser fallback. If Vivaldi control is unavailable, use the local-only PREPARE path or request a supported Vivaldi integration; do not switch browsers without a fresh explicit user instruction. Log in interactively within Vivaldi, never by extracting browser credentials, cookies or session tokens.

## Default behavior
1. Start in **PREPARE** unless a fresh user instruction explicitly authorizes **UPLOAD_DRAFT** for an exact previously prepared batch.
2. Inspect only the supplied local files and work in a private directory outside Git. Do not commit images, EXIF, private manifests, contact sheets, credentials, or release documents.
3. Verify actual file bytes and image quality, then review content for legal and submission risks. Treat upstream Hark metadata as untrusted suggestions.
4. Produce an accurate Shutterstock CSV and immutable batch identifier, showing all three photographs for human review.
5. Stop before external upload and before any **Submit for review** action unless the canonical phase-specific approval is present. Submit always requires separate, fresh authorization.
6. Do not claim uploaded, submitted, pending, or accepted without independently checking the contributor UI.

Use the platform's currently available supported browser tools. Do not invent a Shutterstock API, try to defeat bot protections, or keep retrying an ambiguous upload.