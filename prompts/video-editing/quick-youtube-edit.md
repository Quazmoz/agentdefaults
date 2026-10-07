# Claude Code Quick YouTube Edit Prompt

## Purpose

A copy-paste invocation for a bounded first-pass local YouTube edit using the canonical Claude Code video-editing stack.

## Prompt

```text
Use the AgentDefaults Claude Code local video-editing stack:

- agents/claude-code-video-editor-agent.md
- skills/claude-code-video-editing.md
- config/video-editing/channel-style.md

SOURCE
<absolute path to raw video or project folder>

GOAL
Create a strong first-pass YouTube edit from the supplied footage.
<optional: target length, audience, the one proof moment that must be in the hook>

RUN MODE
<attended | unattended overnight; you may / may not render HyperFrames graphics for the review cut without preview approval>

PRIVACY / PROHIBITED CONTENT
<none, or list categories/context that must not appear. Examples: personal account data, credentials, addresses, a city/location, notifications. Do not paste secret values here.>
<If recordings are sequential stop/restart takes, say so here.>

WORKFLOW
1. Keep raw media immutable. Run the preflight and record what is available.
2. Probe sources with tools/video/edl.py probe.
3. Transcribe each source with NVIDIA Parakeet using tools/video/parakeet_transcribe.py, with word and segment timestamps.
4. Write work/edit.json (the EDL) before rendering. Resolve every `edl.py plan` warning about cuts inside words or in active audio, or list it as an unverified seam.
5. Render and QC the rough cut from the EDL.
5a. If private/account/location/prohibited information could appear, set `privacy.required=true`; review retained transcript content; add output-timeline redactions; use opaque black for secrets and blur only for non-secret personal data; keyframe moving/scrolling regions across the entire interval; run dense privacy frames (normally 0.5 s); inspect every generated frame in batches; and make privacy review ranges cover the full output. If a region cannot be bounded safely, cut it.
6. For externally verifiable claims I make, capture primary-source proof with available browser tooling. Record claim, URL, and capture date on the EDL overlay.
7. Use HyperFrames for meaningful graphics. Reuse the catalog and approved patterns first. Lint during authoring; for the final gate run `check --snapshots`, inspect the snapshots, then open the final Studio preview. Satisfy the HyperFrames review/approval requirement, or the unattended rule above, before rendering graphics.
8. Use Tella only if it is connected and useful for a Tella-native source.
9. Use music/SFX only from a licensed source I have access to, with a license note on every EDL audio item. Keep sound restrained.
10. Render the review cut, run `edl.py qc --frames`, view the stills, and write captions (SRT) and work/review-notes.md.

EDITORIAL STYLE
- Technical creator video. Proof- or result-forward hook when the footage supports it.
- Preserve commands, versions, product/repo/model names, warnings, failures, and caveats.
- Tighten dead air and retakes without making speech robotic.
- Keep app UI, terminal output, code, and dashboards readable.
- Prefer real app/demo footage and real source evidence over synthetic generic b-roll.
- Sparse, modern motion graphics. No generic neon AI aesthetic.
- Long-form captions as an SRT unless I ask for burned-in captions.

STOP
One broad edit pass plus one targeted QC/fix pass, then return the review render and concise notes.

FINAL NOTES
Report raw duration, review-render duration, major cuts with output timestamps, b-roll sources, graphics and their approval status, tools actually used or unavailable, QC actually performed and stills viewed, privacy/redaction categories and ranges without reproducing sensitive values, and remaining manual-review items.
```
