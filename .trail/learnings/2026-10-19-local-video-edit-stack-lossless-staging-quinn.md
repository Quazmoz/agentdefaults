---
title: "Local video edit stack: lossless staging and overlay/redaction frame edges"
author: Quinn
date: 2026-10-19
branch: main
cost: { minutes: 30, tokens: 171413 }
---

## Decided
- Stage edl.py renders losslessly for masters: wrap build_render_command and swap only codec args (x264 -qp 0, pcm_s24le in .mov); encode deliverables once from the last stage. render_stages.sh-style CRF 10 chains put audio through AAC once per stage.
- Smooth zooms on screen recordings: render picture-only overlay clips from the source with separable cubic resampling (numpy matmul on yuv420p planes), eased about the shared fixed point; keep zooms in time ranges where no redaction is needed and assert it in the EDL generator.
- On macOS use aac_at -aac_at_mode cbr for 320k; FFmpeg's native aac undershot to ~246k on speech.

## Tried and ruled out
- Highlight rings over UI the creator already text-selects on screen: duplicate emphasis, dropped.
- Comparing encodes against a stream-copied or MKV reference: timestamp pairing drifts (ms timebase), PSNR looks flat across CRF. Pair frames with setpts=N against a .mov/.mp4 lossless reference.

## Watch out
- edl.py enables overlays and redactions with between(t, at, end), inclusive at both ends. Rounding `at` to 3 dp UP (40.6667 -> 40.667) skips the overlay's first frame and shifts a video overlay one frame late for its whole span (webcam PiP lip-sync). Round overlay starts DOWN.
- Redaction run ends are exclusive frame times: pad them back half a frame, not forward, or the blur box lands on the first frame of the next shot.
