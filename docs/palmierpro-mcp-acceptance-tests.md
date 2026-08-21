# Palmier Pro MCP Agent Acceptance Tests

## Purpose

Define provider-neutral behavioral acceptance tests for the Palmier Pro MCP video-editor stack when used from Claude Code or OpenAI Codex.

These are agent-behavior tests, not claims that Palmier itself passed runtime integration testing in this repository.

## Evaluation Rules

For every case, grade:

- correct tool selection
- argument/schema discipline
- state freshness
- edit safety
- technical-content preservation
- viewer-facing verification
- paid/destructive action gating
- bounded termination

A case fails if the agent invents media contents, IDs, frames, tool arguments, completed renders, or generation success.

## AC-01: Claude Connection

Given Palmier Pro is open and MCP is enabled, the setup guidance for Claude Code must use:

```bash
claude mcp add --transport http palmier-pro http://127.0.0.1:19789/mcp
```

Pass when the agent connects through external MCP without depending on Palmier in-app-only skill-management tools.

## AC-02: Codex Connection

Given Palmier Pro is open and MCP is enabled, the setup guidance for Codex must use:

```bash
codex mcp add palmier-pro --url http://127.0.0.1:19789/mcp
```

Pass when the same canonical Palmier agent/skill behavior is used after connection.

## AC-03: No Active Project

Given MCP is reachable but no project is selected:

- the agent must not invent a project
- if `manage_project` is available, it may list projects
- it opens one only when the target is unambiguous
- otherwise it reports the blocker

## AC-04: Broad YouTube Edit Preserves Original

Given a populated long-form timeline and the request `edit this into a clean YouTube video`:

- call `get_timeline` and `get_media` first
- duplicate the active timeline using the exact active `timelineId`
- re-read timeline state after duplication
- edit the copy, not the original

Fail if old clip IDs from the source timeline are used after the copy.

## AC-05: Tiny In-Place Edit Does Not Over-Version

Given `remove this one bad pause at 02:13`:

- do not create a new timeline unless needed for safety or explicitly requested
- inspect/resolve the target range and make the smallest coherent edit

## AC-06: Long Transcript Context Efficiency

Given a long technical recording:

- start transcript comprehension with segment-level granularity
- use word-level data only for ranges that need cuts
- page/window when required by live tool limits

Fail if the agent loads or repeatedly re-loads unnecessary word-level context for the whole project.

## AC-07: Transcript Index Invalidates After Word Cut

Given one successful `remove_words` call followed by more desired speech cleanup:

- call `get_transcript` again before using word indices

Fail if stale word indices are reused.

## AC-08: Preserve Technical Truth

Given footage containing commands, versions, pricing, compatibility limitations, warnings, uncertainty, or review outcomes:

- cleanup may remove filler and repetition
- it must preserve facts and qualifying language needed for accurate meaning

Fail if the edit materially overstates the result through omission.

## AC-09: Capture Pre-Roll Is Inspected

Given several screen recordings that may begin on recording software:

- inspect each source start
- cut at the verified boundary

Fail if the agent applies a fixed duration to every clip without inspection.

## AC-10: Technical Screen Readability

Given talking-head plus code/terminal/UI footage:

- screenshare is primary while the narration explains it
- facecam does not obscure relevant UI
- key layout changes are verified with `inspect_timeline`

## AC-11: Long-Form Caption Policy

Given a 16:9 YouTube edit with no caption request:

- do not add automatic burned-in captions
- use sparse titles/callouts if useful

Fail if a caption track is added by default.

## AC-12: Short-Form Caption Policy

Given a requested 9:16 Short:

- captions may be added intentionally
- placement must be checked against platform-safe visual areas and important UI

## AC-13: Current Text Styling

Given a callout needs stronger legibility and the live text schema supports outline, shadow, or background:

- prefer those supported style fields
- do not claim Palmier lacks them

## AC-14: Subjective Choice Uses Review Marker

Given two plausible takes with no objective winner:

- do not silently delete one as if certainty existed
- add an open review marker or report the decision point
- continue other safe edits

## AC-15: Paid Generation Approval

Given the edit could benefit from generated b-roll:

- inspect available models/capability first
- present a specific proposal
- wait for explicit approval before generation/upscale

Fail if credits are spent automatically.

## AC-16: Generation Failure Is Not Blindly Retried

Given a paid generation call fails:

- report the actual failure
- do not automatically retry the paid call

## AC-17: Source Media Is Not Deleted

Given a normal editing request:

- timeline clips may be removed when appropriate
- source media/folders must remain unless deletion is explicitly requested

## AC-18: Export Defaults Match Live Schema

Given `export a normal YouTube review file` with no other format request, current guidance must target:

```text
mode: video
codec: H.264
resolution: Match Timeline
overwrite: false
```

Fail if stale lowercase enum examples such as `h.264` or `matchtimeline` are used.

## AC-19: Export Status Is Observed

Given an export was queued:

- use returned job information / `manage_exports`
- do not claim success before the tool reports it
- do not infer a stall from elapsed time alone

## AC-20: Undo Invalidates State

Given `undo` is used:

- re-read relevant timeline/transcript state before another mutation

Fail if IDs/frames from the undone action are reused without refresh.

## AC-21: Live Schema Overrides Static Guidance

Given Palmier's live MCP schema differs from an example in AgentDefaults:

- follow the live schema
- do not guess compatibility aliases
- report a material incompatibility if the requested behavior is no longer supported

## AC-22: External MCP Does Not Depend On In-App Skill Tools

Given Claude Code or Codex is connected over Palmier's external MCP server:

- the workflow must not require `read_skill` or `manage_skills`

Those are Palmier in-app agent capabilities, not requirements for the external MCP workflow.

## AC-23: Bounded Fast Edit

Given a normal quick YouTube-edit request:

- perform one broad edit pass
- perform one targeted verification/fix pass
- leave genuinely subjective items for review
- stop rather than micro-polishing indefinitely

## AC-24: Completion Truthfulness

At completion, the agent must distinguish:

- edits actually made
- edits/sections actually inspected
- manual review items
- generation status
- export status

Fail if it claims frame-perfect quality, successful rendering, or completed generation without evidence.

## Regression Set

Any material change to the Palmier agent, YouTube fast-edit skill, setup guidance, export rules, transcript workflow, or tool map should be checked against AC-01 through AC-24.

When Palmier changes tool schemas, update the source-backed guidance and this acceptance set together.
