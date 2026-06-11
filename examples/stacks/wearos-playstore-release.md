# Wear OS Play Store Release Stack

## Purpose

Use this composed stack when preparing an Android / Wear OS app for Google Play release or resubmission.

## Stack

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

- Wear OS release-readiness review
- Google Play rejection fixes
- round-screen UI clipping fixes
- missing scrollbar fixes
- screenshot and listing review
- Tile, complication, foreground service, and ongoing activity checks
- privacy policy and Play Data safety alignment
- paid-app or billing readiness review

## Inputs To Provide

```text
Target repo:
Target branch:
Package name:
App name:
Is this watch-only or phone + watch:
Play Console rejection text, if any:
Known emulator/device results:
Release target: internal / closed / open / production:
```

## Suggested Codex Prompt

```text
Use the Wear OS Play Store Release Stack from AgentDefaults.

Read these instruction files from the agentdefaults repository or from the copied local files:

- agents/android-wearos-release-engineer.md
- agents/token-efficient-response-agent.md
- skills/wearos-playstore-readiness.md
- skills/token-efficient-response-compression.md
- prompts/review/wearos-release-readiness-review.md

Then inspect this repository and make safe changes needed for Google Play Wear OS release readiness. Prioritize Play review blockers, build/release packaging, round-screen visual quality, scrollbars, font scaling, touch targets, black backgrounds, Tiles, complications, foreground services, privacy/listing consistency, and screenshot readiness.

Final output must include release status, changed files, remaining blockers, validation commands, manual Wear OS checks, and Play Console notes.
```

## Suggested Claude Code Prompt

```text
Use the Wear OS Play Store Release Stack from AgentDefaults.

Read these instruction files from the agentdefaults repository or from the copied local files:

- agents/android-wearos-release-engineer.md
- agents/token-efficient-response-agent.md
- skills/wearos-playstore-readiness.md
- skills/token-efficient-response-compression.md
- prompts/review/wearos-release-readiness-review.md

Then inspect this repository and make safe changes needed for Google Play Wear OS release readiness. Prioritize Play review blockers, build/release packaging, round-screen visual quality, scrollbars, font scaling, touch targets, black backgrounds, Tiles, complications, foreground services, privacy/listing consistency, and screenshot readiness.

Use plan mode for broad changes. Ask before major rewrites or dependency upgrades. Final output must include release status, changed files, remaining blockers, validation commands, manual Wear OS checks, and Play Console notes.
```

## Minimal Expected Final Response

```markdown
Done / Mostly done / Not ready.

Changed:
- `path` — summary

Remaining blockers:
- item, or `None found from repo review`

Validate:
```bash
./gradlew clean assembleDebug lintDebug
./gradlew assembleRelease
```

Manual checks:
- 192dp small round
- 227dp large round
- large font size
- screenshot capture
```

## Notes

Use this stack with app repos, not inside AgentDefaults itself. For persistent tool behavior, copy or import the stack into `AGENTS.md` for Codex and `CLAUDE.md` for Claude Code.
