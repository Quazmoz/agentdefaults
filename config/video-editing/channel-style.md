# YouTube Channel Editing Style

## Purpose

Mutable taste/profile file for the Claude Code local YouTube editing stack.

Core workflow and safety rules belong in the canonical agent/skill. This file stores reusable creative preferences learned from review feedback.

## Current Defaults

### Story

- Open with a concrete result, surprising capability, failure, benchmark, or visible proof when the footage supports it.
- Establish why the viewer should care quickly.
- Keep setup short; spend more time on the actual demo/build/result.
- Preserve real limitations and failures instead of polishing them away.
- End naturally; avoid long generic outros.

### Pacing

- Tighten obvious dead air and repeated takes.
- Keep enough pause for technical comprehension.
- Do not cut every breath/filler if the result sounds robotic.
- Screen recordings should remain on screen long enough to read the important UI, code, terminal output, or metric.

### Motion Graphics

- Clean, modern, technical.
- Prefer short titles, diagrams, comparison cards, key numbers, repo/product names, and visual emphasis tied directly to narration.
- Avoid generic “AI neon” visuals, excessive glow, random particles, or constant motion.
- Do not cover the important part of an app/demo screen.
- Logos/icons should be authentic source assets when available, not regenerated approximations.

### B-roll

- Prefer real product UI, repositories, release notes, benchmark pages, primary research, and original announcements.
- Use claim-specific browser captures rather than generic stock footage for technical claims.
- If the current video is about one of the creator's apps, prefer real app footage/screenshots over synthetic device UI.

### Captions

- Long-form 16:9: captions are optional, not automatic.
- Shorts/vertical: readable burned-in captions are generally useful.
- Correct technical terms, app names, model names, commands, and acronyms manually when ASR gets them wrong.

### Sound

- Dialogue is always primary.
- Hook can be slightly more energetic or suspenseful.
- Main instructional sections: subtle low-volume bed or silence.
- SFX should correspond to meaningful visual events, not every animation.
- Avoid busy “YouTube automation” sound-design clichés.

## Learned Rules

Add durable rules here only after explicit user instruction to persist feedback.

Format:

```text
- YYYY-MM-DD — Context: <hook/tutorial/demo/etc.>
  Rule: <general reusable preference>
```
