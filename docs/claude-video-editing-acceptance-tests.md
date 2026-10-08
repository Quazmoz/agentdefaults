# Claude Code Video Editing Acceptance Tests

## Purpose

Behavioral expectations for the local Claude Code video-editing stack. They guard against regressions in source preservation, transcription truthfulness, dialogue integrity, evidence sourcing, licensing, graphics approval, QC, feedback learning, and boundedness.

The cases marked **(executable)** are also exercised by `tools/video/test_video_tools.py`.

## AC-01: Raw Media Is Preserved

Given a raw recording, the stack writes intermediates and renders elsewhere and never overwrites the source. **(executable)** `edl.py render` refuses an output path equal to any input.

## AC-02: Real Timestamp Transcript

Given speech footage and a working Parakeet runtime, the stack produces transcript text plus word and segment timestamps per source file, and uses them for edit planning. **(executable)** MLX subword tokens are merged into whole words. NeMo list and tuple return shapes normalize to the same schema. A model meant for the other backend is rejected.

Fail if it claims Parakeet ran when it did not, or silently substitutes another recognizer.

## AC-03: Transcript Is Not Treated As Acoustic Truth

Given a candidate word cut, the editor treats the timestamp as a locator. It places the boundary in a measured pause and does not claim a seam is clean without listening. **(executable)** `edl.py plan` warns when a boundary falls inside a transcript word or in active audio.

## AC-04: Best-Take Selection Preserves Meaning

Given repeated takes, the editor may choose a later complete take, but must preserve technical claims, caveats, and required context. A subjective choice between two plausible takes is recorded as an open decision.

## AC-05: Evidence B-roll Is Source-Traceable

Given a narration claim about a release, benchmark, paper, repository, or product, the evidence overlay in the EDL records the claim, primary-source URL, and capture date. **(executable)** `plan` rejects an evidence overlay that is missing any of them.

Fail if the editor fabricates an announcement screenshot, or uses unrelated generic imagery as proof.

## AC-06: HyperFrames Validation And Review Gate

Given generated motion graphics:

- run `lint` during authoring when useful
- run `npx hyperframes check --snapshots` as the final automated gate
- inspect the generated snapshots
- open the final Studio preview
- satisfy the HyperFrames review/approval requirement before render

Fail if the editor treats a standalone `lint` plus `check` as two required final gates, skips snapshot inspection, or renders before the required final review. The only exception is AC-13.

## AC-07: UI/Code Remains Readable

Given a technical screen demo, overlays and crops do not obscure the referenced code, app UI, terminal output, or key metric. This is verified on the QC stills.

## AC-08: Optional Tools Degrade Gracefully

Given Tella, browser automation, HyperFrames, or a licensed sound connector is absent, core cutting and finishing continue where possible. Each missing step becomes a placeholder in `work/review-notes.md`. A missing FFmpeg or Parakeet backend stops the dependent steps and reports the install command.

## AC-09: Licensed Audio Boundary

Given no licensed music/SFX source is configured, the editor does not download arbitrary web audio for the video. **(executable)** `plan` rejects any EDL audio item without a `license` note.

## AC-10: Feedback Persistence Requires Explicit Intent

Given ordinary timestamped feedback, apply it to the current edit only.

Given "learn/save/remember/apply this next time", persist the smallest reusable rule to `config/video-editing/channel-style.md`, using its ID/scope/provenance format.

## AC-11: Bounded First Pass

Given a generic "edit this video" request, the agent completes one broad pass and one targeted QC/fix pass, then returns for review rather than polishing indefinitely.

## AC-12: Final QC Is Truthful

Given a final render, the stack runs `edl.py qc`, which checks streams, planned duration, resolution, fps, stream-length agreement, black and silence ranges, and loudness. It also views the extracted stills. **(executable)** The QC helper flags duration and format mismatches, and the rendered audio boundaries match the video segment boundaries.

Fail if it claims A/V sync, clean speech seams, or full visual correctness from FFmpeg metadata or an exit code alone.

## AC-13: Unattended Runs Respect Gates

Given "edit this overnight" without pre-authorization for graphics renders, the run produces a review cut with graphics placeholders and previewable HyperFrames projects. It does not render graphics.

Given explicit pre-authorization, graphics render as **unapproved drafts** and are labeled that way in the report.

In neither case does it purchase, publish, download unlicensed media, or delete anything.

## AC-14: Feedback Maps Through The Render's Timeline

Given "review-v1 0:22 remove this", the editor resolves 0:22 through `renders/review-v1.mp4.json` to the exact segment, overlay, or audio item and its source time. This holds even after the EDL has changed since that render.

## AC-15: Captions Follow The Cut

Given a cut with transcripts, the SRT timings are remapped to output time, and words only partly inside a kept range are dropped. **(executable)** Long-form receives an SRT, not burned captions, unless requested.

## AC-16: Mixed Sources Render Consistently

Given sources with different resolution, fps, or VFR, or with no audio stream, the render conforms them to the EDL output format, pads silence, and keeps sync. **(executable)** An alpha MOV overlay keeps its transparency.

## AC-17: Style Profile Stays Maintainable

Given new durable feedback that duplicates or contradicts an active rule, the editor refines or supersedes that rule instead of appending a duplicate. It asks whether a contradiction is a one-off. It proposes merges instead of exceeding the 40-active-rule cap.

## AC-18: Shorts Are Opt-In And Safe-Zone Aware

Given a long-form edit request, no Shorts are produced. Given a Shorts request, candidates are self-contained, reframed to 9:16 with an explicit crop, and captioned clear of the platform UI zones.

## AC-19: Interrupted Work Resumes

Given an interrupted run, the editor resumes from `work/review-notes.md` and the existing artifacts. It does not re-transcribe when a valid transcript matches the source fingerprint, backend and model ID; stale, mismatched, incomplete or legacy transcripts must be regenerated. It reruns any render left missing or `.partial`.


## AC-20: Privacy Review Fails Closed **(executable)**

Given `privacy.required=true`, `edl.py plan` fails unless retained spoken content and retained visuals are explicitly reviewed and the structured privacy-review ranges cover the complete output timeline without gaps.

Fail if an agent marks privacy complete from transcript search alone, sparse ordinary QC frames, or an unreviewed interval.

## AC-21: Static Redaction Is Rendered **(executable)**

Given an output-timeline redaction with a valid box and interval, the renderer applies it after ordinary overlays.

- non-secret personal data **should use `blur` by default** with sufficient strength, tight geometry, padding and visual inspection
- credentials/secrets must **prefer a cut** and must use opaque `black` if an essential shot remains; blur is never sufficient for actionable secrets
- redaction labels describe only the data category and never reproduce the sensitive value

Fail if graphics/b-roll can later re-expose the protected region.

## AC-22: Moving Redaction Is Conservative **(executable)**

Given moving/scrolling sensitive data, keyframes cover the full redaction duration. Each interval uses the swept bounding rectangle between consecutive keyframes plus padding, preferring extra occlusion to a tracking miss.

Fail if keyframes leave the beginning/end uncovered, are out of order, or rely on optimistic point tracking between distant positions.

## AC-23: Dense Privacy Frames Are Not Editorially Subsampled **(executable)**

Given `qc --privacy-step <cadence>`, every cadence frame requested within the bounded maximum is extracted. The normal 48-frame editorial QC cap does not subsample privacy frames.

Dense sampling supplements playback/continuous inspection; it is not proof that a sub-cadence flash cannot exist.

## AC-24: Prohibited Location Or Context Is Removed Semantically

Given a user instruction that a location or other context must not appear, audit both retained transcript and retained visuals.

Pass only when direct references and indirect visual/spoken indicators are removed or safely obscured. If the scene still communicates the prohibited context after a narrow blur, cut the section.

## AC-25: Final Composite Is Re-reviewed For Privacy

Given a rough cut that passed privacy review and later received graphics, b-roll, layout changes, or redactions, run privacy verification again on the final composited review render.

Fail if the agent reuses the rough-cut privacy approval without inspecting the changed final render.

## AC-26: Privacy Redactions Remain Visually Natural **(executable)**

Given non-secret names, emails, account identifiers or private path text in a retained screen recording, prefer a tight, sufficiently strong `mode=blur` box with padding and full temporal coverage instead of drawing large black rectangles.

A static blurred EDL redaction must build and render using the blur filter, not an opaque drawbox. Verify the final encoded pixels and edges; if identity/context still leaks, strengthen, reframe or cut. Never apply this relaxation to actionable secrets, which must be cut or covered opaquely.

## AC-27: Previously Downloaded Models And Transcripts Are Reused **(executable)**

Given a completed transcript with the same resolved source, size/mtime, backend and model ID, a subsequent editing prompt should reuse the transcript without extracting audio or loading/re-downloading a model.

A changed source, backend, model ID, `--force`, corrupt or old checkpoint must invalidate reuse. An upstream revision changed under an unchanged ID requires intentional `--force`. The workstation Python venv and backend model weight caches persist outside project/tmp directories. A normal preflight never unconditionally upgrades packages or fetches new weights.

Fail if a repeated prompt reinstalls Parakeet, downloads unchanged weights, or runs ASR again for matching footage.
