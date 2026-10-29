---
title: "Local video edit stack: fade-out EOF pop, frame-exact redaction edges, odd-crop drift"
author: Quinn
date: 2026-10-28
branch: main
cost: { minutes: 28, tokens: 435430 }
id: l-4b5bd788
scope: repo
status: active
replaces: l-512e1856
src: agent
touches:
  - tools/video/edl.py
---

## Decided
- End fades in tools/video/edl.py: black alpha overlay with a source longer than its EDL duration (1.6 s file, 0.8 s ramp). One exactly as long as the tail hits EOF early and eof_action=pass pops the last frame back.
- Verify redaction edges frame-exactly: render an unredacted proxy (same EDL, redactions/overlays stripped), then per frame index compare template-match on the proxy (sensitive) with output-vs-proxy difference (blur active). Every sensitive frame must be blurred. Redaction enable is inclusive between(t,start,end), so end = last sensitive frame + half a frame.
- 12 blur slices in one edl.py render were fine (5-9 min, FFmpeg 8.1.1).

## Tried and ruled out
- Judging edges from `ffmpeg -ss <t>` stills: seek can land one frame later, which led to trimming a blur too far and leaking a frame. Select frames by index instead.
- Remapping redaction times with ad hoc half-frame pads: produced 1-2 frame spills onto zoomed/next screens. Use measured sensitive frames.

## Watch out
- A run end printed as "first non-matching frame" is easy to misread as the last match.
- Raw-frame scans need even crop values; odd ones misalign the rawvideo pipe.
- Browser open/close animations expose tab text outside a static box; add a short full-frame blur.
- ImageMagick Avenir lacks "→". zsh doesn't word-split `set -- $spec`; use bash.
