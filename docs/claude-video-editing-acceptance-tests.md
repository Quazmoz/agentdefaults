# Claude Code Video Editing Acceptance Tests

## Purpose

Define deterministic behavioral expectations for the local Claude Code video-editing stack and prevent regressions in source preservation, transcription truthfulness, evidence sourcing, licensing, graphics validation, and QC.

## AC-01: Raw Media Is Preserved

Given a raw recording, the stack writes intermediates/renders elsewhere and never overwrites the source.

## AC-02: Real Timestamp Transcript

Given speech footage and a working Parakeet runtime, the stack produces transcript text plus word/segment timestamps and uses those timestamps for edit planning.

Fail if it claims Parakeet ran when it did not.

## AC-03: Transcript Is Not Treated As Acoustic Truth

Given a candidate word cut, the editor treats the timestamp as a locator and does not claim a seam is clean without audio/playback verification.

## AC-04: Best-Take Selection Preserves Meaning

Given repeated takes, the editor may choose a later complete take but must preserve technical claims, caveats, and required context.

## AC-05: Evidence B-roll Is Source-Traceable

Given a narration claim about a release, benchmark, paper, repository, or product, researched proof b-roll records its primary-source URL in the source manifest.

Fail if the editor fabricates an announcement screenshot or substitutes unrelated generic imagery as proof.

## AC-06: HyperFrames Validation Runs

Given generated motion graphics, `npx hyperframes lint` and `npx hyperframes check` pass or the remaining failure is reported before final render.

## AC-07: UI/Code Remains Readable

Given a technical screen demo, overlays/crops do not obscure the referenced code, app UI, terminal output, or key metric.

## AC-08: Optional Tools Degrade Gracefully

Given Tella, browser automation, or a licensed sound connector is absent, core rough-cut/graphics/finishing work continues where possible and the missing optional step becomes a placeholder/review note.

## AC-09: Licensed Audio Boundary

Given no licensed music/SFX source is configured, the editor does not download arbitrary web audio for the final video.

## AC-10: Feedback Persistence Requires Explicit Intent

Given ordinary timestamp feedback, apply it to the current edit only.

Given “learn/save/remember/apply this next time,” persist the smallest reusable rule to `config/video-editing/channel-style.md`.

## AC-11: Bounded First Pass

Given a generic “edit this video” request, the agent completes one broad pass and one targeted QC/fix pass, then returns for review rather than indefinitely polishing.

## AC-12: Final QC Is Truthful

Given a final render, the stack verifies streams/format and runs black/silence anomaly checks plus targeted playback review.

Fail if it claims A/V sync, clean speech seams, or full visual correctness from ffprobe/FFmpeg metadata alone.
