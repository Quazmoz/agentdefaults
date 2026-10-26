# YouTube Channel Editing Style

## Purpose

This is the mutable taste profile shared by both video-editing stacks: the Claude Code local stack (`agents/claude-code-video-editor-agent.md`) and the Palmier Pro MCP stack (`agents/palmierpro-mcp-video-editor-agent.md`). Prompts in `prompts/palmierpro/` and `prompts/video-editing/` read channel identity and hook style from here instead of hardcoding them. It covers AI engineering, DevOps, Claude/Codex/agent workflows, Android and Wear OS apps, demos, comparisons, tutorials, and app launch/update videos.

Workflow and safety rules belong in the canonical agent and skill. Nothing here can override truthfulness, licensing, raw-media, or approval gates. Defaults are the baseline. Learned rules refine or override them, with the more specific scope winning.

## Channel Profile

Who the videos are for and what they should feel like. Prompts refer to "the channel" and read this section. Fork this repo and replace it with your own channel.

```text
creator:        Quinn Favo
positioning:    a real AI/DevOps engineer and automation builder showing the actual workflow, not a generic AI influencer
viewers:        AI builders, DevOps engineers, app builders, technical creators
topics:         AI engineering, DevOps, coding agents, MCP workflows, local AI (NPU/GPU, OpenVINO), Android and Wear OS apps,
                Google Play releases, open-source tooling, automation experiments
proof moments:  a working agent result, a working app or demo, a Play Store approval or rejection lesson, a local-AI benchmark,
                an MCP workflow changing real state, a repo/terminal result, a before/after automation
hook style:     short, accurate, all-caps when on screen ("AI EDITED THIS", "PLAY STORE RESULT", "LOCAL AI TEST",
                "MCP WORKFLOW", "THIS AGENT DID IT"), used only when the footage supports it
never imply:    free, unlimited, a hack, guaranteed approval, medical or therapy benefits, or performance the footage does not show
```

## Brand Tokens

Unset until the user supplies them or approves values taken from existing channel assets. Do not invent brand colors or fonts.

```text
primary color:     <unset>
accent color:      <unset>
background:        <unset>
heading font:      <unset>
body / code font:  <unset>
logo / watermark:  <unset; path to an authentic asset>
```

## Approved Motion Patterns

These are reusable HyperFrames compositions or registry blocks the user has approved. Reuse them before authoring new motion. Add an entry only when the user approves a graphic for reuse.

```text
- <name> — <path to composition or `hyperframes add <block>`> — use for: <context> — approved YYYY-MM-DD
```

## Defaults

### Story

- Open with a concrete result, a surprising capability, a failure, a benchmark, or visible proof when the footage supports it.
- Establish quickly why the viewer should care. Keep setup short and spend the time on the demo, build, or result.
- Preserve real limitations and failures instead of polishing them away.
- End naturally. Avoid long generic outros and hype the footage does not support.

### Pacing

- Tighten dead air and repeated takes without making speech robotic. Do not cut every breath or filler.
- Leave screen recordings up long enough to read the important UI, code, terminal output, or metric.

### Motion Graphics

- Clean, modern, technical. Short titles, diagrams, comparison cards, key numbers, and repo/product names tied to the narration.
- No generic "AI neon", excessive glow, random particles, or constant motion.
- Never cover the important part of an app or demo screen.
- Use authentic logos and icons, not regenerated approximations.

### B-roll

- Real product UI, repositories, release notes, benchmark pages, primary research, and original announcements.
- For technical claims, use claim-specific captures rather than generic stock footage.
- For the creator's own apps, use real app footage or screenshots rather than synthetic device UI.

### Captions

- Long-form 16:9: deliver an SRT. Burn captions in only on request.
- Shorts/vertical: readable burned-in captions, kept clear of the platform UI zones (see Shorts Safe Zones).
- Correct technical terms, app names, model names, commands, and acronyms by hand.

### Shorts Safe Zones

For a 1080x1920 YouTube Short, the player UI covers the bottom of the frame (title, channel, description) and a right-hand action rail (like, comment, share, remix). TikTok and Reels are similar. Keep captions, hook text, facecam, and the proof itself inside the safe area:

```text
top     ~ 0-250 px       avoid (status bar, search, top controls)
bottom  ~ 1500-1920 px   avoid (title, channel, description)
right   ~ 900-1080 px    avoid from y ~ 700 down (action rail)
safe    ~ x 60-900, y 250-1500   captions, hook text, facecam, key UI
```

Place captions in the lower third of the safe area (around y 1150-1450), not at the very bottom. These are working values, not platform-published specs; verify on a real device preview before publishing.

### Sound

- Dialogue is always primary.
- The hook can be slightly more energetic or suspenseful. Main instructional sections get a subtle low bed, or silence.
- SFX mark meaningful visual events only. No busy "YouTube automation" sound design.

## Learned Rules

Rules are added only after the user explicitly asks to learn, save, remember, or apply feedback next time.

Format (one rule per entry; keep the wording general, never tied to one video's script):

```text
- R-NNN [category] [scope] — <normative rule>
  source: YYYY-MM-DD, <video slug> @ <render timestamp>; status: active | superseded by R-MMM
```

- **category:** story | pacing | graphics | b-roll | captions | sound | color | shorts
- **scope:** all | long-form | shorts | hook | tutorial | demo | launch. Use the narrowest scope that matches the feedback.

Maintenance:

1. **Before adding**, search for an existing rule in the same category. Refine that rule in place and append the new source. Do not add a near-duplicate.
2. **Contradictions:** if new feedback conflicts with an active rule, ask whether it is a one-off for this video or a replacement. For a replacement, mark the old rule `superseded by R-MMM` and remove superseded entries during the next prune.
3. **Cap:** at most 40 active rules. When adding would exceed it, propose merges or removals to the user instead of growing the file.
4. **Rules, not examples:** a rule states what to do ("Section-title reveals: 6–10 frame ease-out, no impact SFX unless the title marks an act break"). Do not paste transcripts or private details.

<!-- No learned rules yet. -->
