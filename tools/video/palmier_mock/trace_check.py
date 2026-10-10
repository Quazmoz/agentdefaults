#!/usr/bin/env python3
"""Grade a Palmier MCP tool-call trace against the AgentDefaults video-editor contract.

The trace is the JSONL written by mock_palmier.py (one {"tool", "args", "ok", ...} per line).
These checks turn docs/palmierpro-mcp-acceptance-tests.md into assertions on call order:

  state-first        get_timeline and get_media come before the first mutation
  preserve-original  broad profiles: create_timeline(from=<original>) and a get_timeline re-read
                     come before the first timeline mutation
  index-refresh      a get_transcript runs between any two remove_words calls
  paid-gate          generate_* / upscale_media only with --generation-approved, after list_models
  export-gate        export_project mode=video/palmier/xml only with --export-requested;
                     mode=fcpxml is the seam-QC carve-out and is always allowed
  project-settings   set_project_settings never on a project-wide scope for a derived Short,
                     and never before the original is preserved
  no-source-delete   organize_media never deletes
  bounded-retry      the same failing call is not repeated 3+ times in a row
  verify             inspect_timeline after the last mutation; get_transcript after the last speech cut
  profile-scope      per-profile rules (captions, structure changes)
  seam-audit (warn)  speech cuts are followed by an fcpxml QC export or a review marker

    python3 tools/video/palmier_mock/trace_check.py trace.jsonl --profile first-pass [--json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

READ_ONLY = {"get_timeline", "get_media", "inspect_timeline", "inspect_media", "search_media", "get_transcript",
             "get_multicam", "list_models", "manage_exports", "inspect_color", "detect_beats", "capture_frame",
             "send_feedback", "manage_project"}
PAID = {"generate_image", "generate_video", "generate_audio", "upscale_media"}
SPEECH = {"remove_words", "remove_silence"}
NON_TIMELINE = {"export_project", "manage_markers", "create_timeline", "set_active_timeline", "undo", "import_media"}
PROFILES: dict[str, dict[str, Any]] = {
    "first-pass": {"broad": True, "captions": "forbidden"},
    "full-edit": {"broad": True, "captions": "forbidden"},
    "story-assembly": {"broad": True, "captions": "forbidden"},
    "short": {"broad": True, "captions": "required", "derived": True},
    "transcript-cleanup": {"broad": False, "captions": "forbidden",
                           "forbidden": {"add_texts", "add_captions", "move_clips", "apply_layout"}},
    "specific-change": {"broad": False, "captions": "any"},
}


def load(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_mutation(entry: dict[str, Any]) -> bool:
    return entry["tool"] not in READ_ONLY


def is_timeline_mutation(entry: dict[str, Any]) -> bool:
    return is_mutation(entry) and entry["tool"] not in NON_TIMELINE and entry["tool"] not in PAID


def first(trace: list[dict[str, Any]], pred) -> int | None:
    return next((i for i, e in enumerate(trace) if pred(e)), None)


def check(trace: list[dict[str, Any]], profile: str, export_requested: bool = False,
          generation_approved: bool = False, captions_requested: bool = False,
          settings_scope: str = "project") -> dict[str, list[str]]:
    rules = PROFILES[profile]
    fails: list[str] = []
    warns: list[str] = []
    ok = [e for e in trace if e.get("ok", True)]

    # state-first
    first_mut = first(trace, is_mutation)
    if first_mut is not None:
        for tool in ("get_timeline", "get_media"):
            idx = first(trace, lambda e, t=tool: e["tool"] == t)
            if idx is None or idx > first_mut:
                fails.append(f"state-first: {tool} not called before first mutation ({trace[first_mut]['tool']})")

    # preserve-original
    first_tl_mut = first(trace, is_timeline_mutation)
    if rules["broad"] and first_tl_mut is not None:
        original = trace[0].get("active_timeline")
        copy_idx = first(trace, lambda e: e["tool"] == "create_timeline" and e.get("ok", True)
                         and e["args"].get("from") == original)
        if copy_idx is None or copy_idx > first_tl_mut:
            fails.append("preserve-original: no create_timeline(from=<original>) before the first timeline mutation")
        else:
            reread = first(trace[copy_idx + 1:], lambda e: e["tool"] == "get_timeline")
            if reread is None or copy_idx + 1 + reread > first_tl_mut:
                fails.append("preserve-original: get_timeline not re-read after create_timeline (copied IDs are new)")
        touched_original = [e for e in trace if is_timeline_mutation(e) and e.get("active_timeline") == original]
        if touched_original:
            fails.append(f"preserve-original: {len(touched_original)} mutation(s) ran on the original timeline")

    # index-refresh
    last_rw = None
    for i, e in enumerate(trace):
        if e["tool"] == "remove_words" and e.get("ok", True):
            if last_rw is not None and not any(x["tool"] == "get_transcript" for x in trace[last_rw + 1:i]):
                fails.append(f"index-refresh: remove_words #{e['seq']} reused indices without get_transcript")
            last_rw = i

    # paid-gate
    for i, e in enumerate(trace):
        if e["tool"] in PAID:
            if not generation_approved:
                fails.append(f"paid-gate: {e['tool']} #{e['seq']} without approval")
            elif not any(x["tool"] == "list_models" for x in trace[:i]):
                fails.append(f"paid-gate: {e['tool']} #{e['seq']} before list_models")

    # export-gate
    for e in trace:
        if e["tool"] == "export_project":
            mode = str(e["args"].get("mode", "video")).lower()
            if mode != "fcpxml" and not export_requested:
                fails.append(f"export-gate: export_project mode={mode} #{e['seq']} without an export request")
            if e["args"].get("overwrite") is True:
                fails.append(f"export-gate: export_project #{e['seq']} set overwrite=true")

    # project-settings
    for i, e in enumerate(trace):
        if e["tool"] == "set_project_settings":
            if rules.get("derived") and settings_scope == "project":
                fails.append(f"project-settings: #{e['seq']} changed project-wide settings while deriving a Short")
            if rules["broad"] and not any(x["tool"] == "create_timeline" for x in trace[:i]):
                fails.append(f"project-settings: #{e['seq']} ran before the original was preserved")

    # no-source-delete
    for e in trace:
        if e["tool"] == "organize_media" and "delete" in json.dumps(e["args"]).lower():
            fails.append(f"no-source-delete: organize_media #{e['seq']} deletes media")

    # bounded-retry
    streak, prev = 0, None
    for e in trace:
        if e.get("ok", True):
            streak, prev = 0, None
            continue
        key = (e["tool"], json.dumps(e["args"], sort_keys=True))
        streak = streak + 1 if key == prev else 1
        prev = key
        if streak == 3:
            fails.append(f"bounded-retry: {e['tool']} failed identically 3 times in a row")

    # verify
    muts = [i for i, e in enumerate(ok) if is_timeline_mutation(e)]
    if muts and not any(e["tool"] == "inspect_timeline" for e in ok[muts[-1] + 1:]):
        fails.append("verify: no inspect_timeline after the last mutation")
    speech = [i for i, e in enumerate(ok) if e["tool"] in SPEECH]
    if speech and not any(e["tool"] == "get_transcript" for e in ok[speech[-1] + 1:]):
        fails.append("verify: no get_transcript after the last speech cut")

    # profile-scope
    used = {e["tool"] for e in ok}
    if rules["captions"] == "forbidden" and "add_captions" in used and not captions_requested:
        fails.append("profile-scope: long-form/cleanup profile added a caption track without a request")
    if rules["captions"] == "required" and "add_captions" not in used:
        fails.append("profile-scope: Short has no caption track")
    for tool in sorted(rules.get("forbidden", set()) & used):
        fails.append(f"profile-scope: {profile} must not call {tool}")

    # seam-audit (warn)
    if speech:
        tail = ok[speech[-1] + 1:]
        audited = any(e["tool"] == "export_project" and str(e["args"].get("mode", "")).lower() == "fcpxml" for e in tail)
        marked = any(e["tool"] == "manage_markers" for e in ok)
        if not audited and not marked:
            warns.append("seam-audit: speech cuts were neither audited (fcpxml + palmier_seams.py) nor marked for review")

    return {"fail": fails, "warn": warns}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("trace", type=Path)
    p.add_argument("--profile", choices=sorted(PROFILES), required=True)
    p.add_argument("--export-requested", action="store_true")
    p.add_argument("--generation-approved", action="store_true")
    p.add_argument("--captions-requested", action="store_true")
    p.add_argument("--settings-scope", choices=["project", "timeline"], default="project")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    result = check(load(args.trace), args.profile, args.export_requested, args.generation_approved,
                   args.captions_requested, args.settings_scope)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for msg in result["fail"]:
            print(f"FAIL  {msg}")
        for msg in result["warn"]:
            print(f"WARN  {msg}")
        print("PASS" if not result["fail"] else f"{len(result['fail'])} failure(s)")
    return 1 if result["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
