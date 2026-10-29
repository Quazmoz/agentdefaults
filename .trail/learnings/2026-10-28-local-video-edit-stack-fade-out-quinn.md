---
title: "Local video edit stack: fade-out EOF pop, odd-crop rawvideo drift, 12 blur slices OK"
author: Quinn
date: 2026-10-28
branch: main
cost: { minutes: 49, tokens: 835871 }
id: l-512e1856
scope: repo
status: active
src: agent
touches:
  - tools/video/edl.py
---

## Decided
- End fades in tools/video/edl.py: use a black alpha overlay whose source is longer than its EDL duration (e.g. 1.6 s file, 0.8 s ramp, duration ending one frame past program end). An overlay exactly as long as the tail hits EOF one frame early and eof_action=pass pops the last frame back to full brightness.
- Privacy verification by frame-exact normalized-correlation template scans works well: render an unredacted proxy (same EDL with redactions/overlays stripped, privacy.required=false, never delivered) as the positive control, then scan the review render with templates taken from the proxy. Each sensitive region: control must hit, output must score 0 runs.
- Twelve blur slices (incl. two full-frame blurs) rendered in one edl.py pass in ~5-9 min on FFmpeg 8.1.1 at 2560x1440p60 sources, no stall; the earlier >~14-slice stall threshold still stands as the ceiling.

## Tried and ruled out
- Timing sensitive UI from contact sheets / guessed source times: off by ~2 s for one page and missed a 0.4 s re-appearance. Locate them with the template scan on the source instead.
- ffmpeg `-i X -ss T` (output-side seek) with signalstats: printed pts are not offset by T; use input-side -ss and add T yourself.

## Watch out
- Raw-frame scans: use even crop x/y/w/h. An odd crop on yuv420 gets rounded and the rawvideo pipe reads misaligned frames (correlation alternates around 0, positive control fails).
- Browser window open/close animations expose tab/bookmark text for a few frames outside a static redaction box; cover the animation with a short full-frame blur.
- ImageMagick Avenir has no "→" glyph; it renders as blank.
- zsh does not word-split unquoted $var in `set -- $spec`; run such loops under bash.
