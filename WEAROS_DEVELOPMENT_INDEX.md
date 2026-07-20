# Wear OS Development AgentDefaults Index

## Purpose

Fast lookup for the Wear OS app development pack: the app-developer agent, the screen-edge safety skill, and the implementation prompt. Use it while building or fixing Wear OS features. For final Play Store release readiness, see [`WEAROS_INDEX.md`](WEAROS_INDEX.md).

## Quick Selection

| Need | Start With | Add Skills |
|------|------------|------------|
| Build or modify a Wear OS app | `agents/wearos-app-developer.md` | `skills/wearos-screen-edge-safety.md`, `skills/token-efficient-response-compression.md` |
| Fix Play Console cut-off screen issues | `agents/wearos-app-developer.md` | `skills/wearos-screen-edge-safety.md` |
| Do final Play Store release review | `agents/android-wearos-release-engineer.md` | `skills/wearos-playstore-readiness.md`, `skills/wearos-screen-edge-safety.md` |
| Generate a one-shot implementation prompt | `prompts/implementation/wearos-app-development.md` | `skills/wearos-screen-edge-safety.md` |

## Files Added

### Agent

- `agents/wearos-app-developer.md` — development-focused Wear OS engineer agent with strong small-round-screen and Play quality guardrails.

### Skill

- `skills/wearos-screen-edge-safety.md` — focused skill for preventing and fixing clipped text, clipped controls, overlap, font-scaling failures, and missing scroll indicators.

### Prompt

- `prompts/implementation/wearos-app-development.md` — copy-paste implementation prompt for Codex, Claude Code, Gemini, or another coding agent.

## Recommended Development Stack

```text
Base agent:
  agents/wearos-app-developer.md

Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/wearos-screen-edge-safety.md
  skills/token-efficient-response-compression.md

Task prompt:
  prompts/implementation/wearos-app-development.md
```

## Best For

- developing Wear OS utility apps
- fixing Play Store watch-shape rejections
- fixing elements cut off by physical screen edges
- fixing overlap caused by large font settings
- adding scrollbars or position indicators
- improving 192dp round-screen safety
- building reusable Wear-safe screen scaffolds
- making Compose for Wear OS screens more release-safe

## Minimal Use

```text
Use the Wear OS Development Stack from AgentDefaults.

Repo:
Feature or issue:
Play Console evidence, if any:
Target screen:

Inspect the repo, then build or fix the feature with special focus on WO-V16 watch-shape safety, 192dp round displays, large font behavior, scroll indicators, and avoiding text/control cutoff.
```

## Relationship To Existing Wear OS Release Pack

Use `agents/wearos-app-developer.md` while building features.

Use `agents/android-wearos-release-engineer.md` when doing final Play Store release readiness, listing, screenshots, privacy, target SDK, packaging, and upload checks.

For Play Console issues about clipped content, use both:

```text
agents/wearos-app-developer.md
skills/wearos-screen-edge-safety.md
skills/wearos-playstore-readiness.md
```
