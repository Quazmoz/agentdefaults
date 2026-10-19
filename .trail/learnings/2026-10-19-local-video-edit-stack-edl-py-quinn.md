---
title: "Local video edit stack: edl.py limits found on a privacy-required screen recording"
author: Quinn
date: 2026-10-19
branch: main
cost: { minutes: 28, tokens: 1010900 }
---

## Decided
- Render privacy-heavy EDLs in stages: one pass for cuts/overlays/graphics, then identity passes with <=7 blur redactions each (intermediates CRF 10). A single edl.py render with >~14 blur slices stalls FFmpeg 8.1 (0 bytes written, CPU busy forever).
- Caption the final render's own Parakeet transcript (one identity segment) instead of remapping source transcripts: edl.py captions drops any word whose ASR span straddles a seam.
- Verify account-identifier redactions with a frame-exact template-correlation scan over every frame (positive-controlled on unredacted clips), in addition to the 0.5 s dense sweep.
- Gain-stage quiet sources (e.g. -34 LUFS screen recordings) into a dialogue intermediate before planning; edl.py's active-audio seam check is a fixed -35 dBFS.

## Tried and ruled out
- Tracked keyframed blur per scroll: too many slices for one FFmpeg graph; static box over the whole header block per visible run instead.
- Trusting Parakeet word edges for cut points: they run up to ~0.3 s late; use energy dips plus splice-and-retranscribe tests. Parakeet returns nothing for clips under ~2 s.

## Watch out
- edl.py qc privacy_frames_generated counts duplicate timestamps; report unique frame files, not that number.
- When computing redaction timing from source times, map cut points end-exclusively and pad frame-exact edges by half a frame; snapping to zero padding at a cut exposed a header for one frame.
- Single-file projects live in <stem>-edit/ next to the raw file; never write review renders over earlier versions.
