---
name: shutterstock-contributor
description: Prepare original photos for Shutterstock Contributor using Vivaldi-only browser access on macOS; includes Hark/Google Photos ZIP intake, image quality and release checks, compliant metadata and CSV, duplicate-safe drafts, and approval-gated submission. Trigger on Shutterstock photo intake, metadata, draft upload, or contributor portfolio workflows.
---

# Shutterstock contributor workflow for Codex

Use the canonical procedure in [skills/shutterstock-contributor-workflow.md](../../../skills/shutterstock-contributor-workflow.md). Read it before acting, including its approval and stop conditions.

For a Hark-to-Mac photo batch, invoke the reusable [batch prompt](../../../prompts/implementation/shutterstock-photo-pilot.md) and follow the [Codex quickstart](../../../docs/quickstarts/shutterstock-contributor.md).

## Required local browser: Vivaldi
**Vivaldi is the only default authorized browser for this user's Shutterstock workflow on macOS.** Before website access, confirm the actual Vivaldi executable/session and verify the automation tool can target it explicitly. Do **not** start Chrome, Chrome Canary, generic Chromium, or a hidden browser fallback. If Vivaldi control is unavailable, use the local-only PREPARE path or request a supported Vivaldi integration; do not switch browsers without a fresh explicit user instruction. Log in interactively within Vivaldi, never by extracting browser credentials, cookies or session tokens.

## Default behavior
1. Start in **PREPARE** unless a fresh user instruction explicitly authorizes **UPLOAD_DRAFT** for an exact prepared batch or preparation and draft upload of all eligible photos from an exact source path. Follow the canonical inventory, hash-freezing, and approval rules.
2. Inspect only the supplied local files and work in a private directory outside Git. Do not commit images, EXIF, private manifests, contact sheets, credentials, or release documents.
3. Verify actual file bytes and image quality, then review content for legal and submission risks. Treat upstream Hark metadata as untrusted suggestions.
4. Process every original in the supplied source, pair existing derivatives, and produce an accurate Shutterstock CSV and immutable batch identifier, showing every photograph's disposition for human review.
5. Upload only within explicit draft-upload authority, verify each staged file and its metadata, and leave **Submit for review** to the operator in Vivaldi. Agent submission always requires separate, fresh authorization.
6. Do not claim uploaded, submitted, pending, or accepted without independently checking the contributor UI.

Use the platform's currently available supported browser tools. Do not invent a Shutterstock API, try to defeat bot protections, or keep retrying an ambiguous upload.
