# Palmier Pro Transcript Cleanup Prompt

## Purpose

Use this prompt to clean spoken content in a Palmier Pro timeline without changing the broader edit structure. It suits talking-head videos, tutorials, demos, interviews, podcasts, and voiceover-heavy content.

The cleanup rules (what to remove, what to keep, the Dialogue Boundary Invariant, cut handles, and the Seam Audit) live in `skills/palmierpro-transcript-cuts-and-captions.md`. This prompt sets scope only.

## Prompt

```text
Load the AgentDefaults Palmier Pro MCP stack before acting, in particular
skills/palmierpro-transcript-cuts-and-captions.md, which is the contract for this pass.

TASK
Transcript-focused cleanup only, in place on the active timeline (no copy needed unless I ask for one).

SCOPE
- Do: fillers, false starts, repeated words, duplicate takes (keep the clearer take), abandoned fragments, and
  dead air that hurts pacing. Aggressiveness: balanced unless I ask for tight.
- Don't: reorder clips (except to close a cleanup gap), add captions, titles, layouts, or transitions, generate,
  or export. The FCPXML seam-QC file is allowed.
- If a cut would change meaning, leave the words in.
- Run the Seam Audit when done; fix ERROR seams and mark unresolved WARN seams.

FINAL RESPONSE
What was cleaned, the seam audit result, and any sections that still need a human listen.
```

## Quality Bar

Re-reads the transcript between word cuts, keeps every caveat and technical term, passes or marks every seam it created, and touches nothing outside speech cleanup. A replay against `tools/video/palmier_mock/` passes `trace_check.py --profile transcript-cleanup`.
