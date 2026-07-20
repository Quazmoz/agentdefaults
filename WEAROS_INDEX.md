# Wear OS AgentDefaults Index

## Purpose

Fast lookup for the Wear OS release-readiness pack: the release-engineer agent, the Play Store readiness skill, the release-review prompt, the composed stack, and copy-in tool configs. Use it when preparing an existing Wear OS app for Play Store submission. For building or fixing features, see [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md).

## Quick Selection

| Need | Start With | Add Skills |
|------|------------|------------|
| Prepare a Wear OS app for Play Store release | `agents/android-wearos-release-engineer.md` | `skills/wearos-playstore-readiness.md`, `skills/token-efficient-response-compression.md` |
| Make the release review output concise | `agents/token-efficient-response-agent.md` | `skills/token-efficient-response-compression.md` |
| Generate a one-shot repo review task | `prompts/review/wearos-release-readiness-review.md` | `skills/wearos-playstore-readiness.md` |
| Configure Codex for a Wear OS app repo | `examples/tool-configs/wearos-codex-AGENTS.md` | Copy to target repo as `AGENTS.md` |
| Configure Claude Code for a Wear OS app repo | `examples/tool-configs/wearos-CLAUDE.md` | Copy to target repo as `CLAUDE.md` |

## Files Added

### Agent

- `agents/android-wearos-release-engineer.md` — full Wear OS release engineer agent profile.

### Skill

- `skills/wearos-playstore-readiness.md` — reusable release-readiness checklist and output format.

### Prompt

- `prompts/review/wearos-release-readiness-review.md` — copy-paste prompt for a coding agent to review and fix a Wear OS repo.

### Stack Example

- `examples/stacks/wearos-playstore-release.md` — composed stack showing which agent, skill, behavior layer, and prompt to combine.

### Tool Config Examples

- `examples/tool-configs/wearos-codex-AGENTS.md` — copy into an app repo as `AGENTS.md` for Codex.
- `examples/tool-configs/wearos-CLAUDE.md` — copy into an app repo as `CLAUDE.md` for Claude Code.

## Recommended Stack

```text
Base agent:
  agents/android-wearos-release-engineer.md

Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/wearos-playstore-readiness.md
  skills/token-efficient-response-compression.md

Task prompt:
  prompts/review/wearos-release-readiness-review.md
```

## Best For

- Wear OS Play Store release readiness
- Google Play rejection fixes
- round-screen clipping fixes
- missing scrollbar fixes
- font scaling checks
- touch target checks
- black background checks
- Tile and complication review
- foreground service and ongoing activity review
- screenshot and Play listing review
- privacy policy alignment
- billing readiness checks

## Relationship To Wear OS Development Pack

Use this release pack (`agents/android-wearos-release-engineer.md`) for final Play Store readiness: listing, screenshots, privacy, target SDK, packaging, and upload checks.

Use the development pack while building or fixing features:

```text
agents/wearos-app-developer.md
skills/wearos-screen-edge-safety.md
WEAROS_DEVELOPMENT_INDEX.md
```

For Play Console issues about clipped content, use both packs together.

## Minimal Use In A Target Repo

### Codex

```bash
cp examples/tool-configs/wearos-codex-AGENTS.md /path/to/app/AGENTS.md
cd /path/to/app
codex "Review this Wear OS app for Play Store release readiness and fix safe blockers."
```

### Claude Code

```bash
cp examples/tool-configs/wearos-CLAUDE.md /path/to/app/CLAUDE.md
cd /path/to/app
claude
```

Then ask:

```text
Review this Wear OS app for Play Store release readiness and fix safe blockers.
```
