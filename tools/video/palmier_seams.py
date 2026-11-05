#!/usr/bin/env python3
"""Audit the dialogue seams of a Palmier Pro timeline from a scratch FCPXML export.

Palmier's MCP surface has no audio-inspection tool, so an agent cannot hear a seam
it created. This tool gives it a mechanical check. Run it on a scratch FCPXML
export of the edited timeline. It finds every cut in the primary storyline, maps
each side back to source time, and checks it against per-source Parakeet word
timestamps and the source audio level.

    # 1. agent: export_project mode=fcpxml outputPath=<scratch dir>/qc.fcpxml   (QC carve-out, not a user export)
    # 2. transcribe sources once: tools/video/parakeet_transcribe.py <source> -o transcripts/<stem>.json
    python3 tools/video/palmier_seams.py qc.fcpxml --transcripts transcripts/ [--source-root /path/to/media] [--json]

Each seam reports the timeline time and frame, so failures can become `manage_markers`
review markers at exact positions. Exit status: 0 = no errors, 1 = at least one ERROR
(a cut inside a word or repeated source content), 2 = bad input. With --strict, a WARN fails too.

Checks per seam (A = outgoing clip's source out point, B = incoming clip's source in point):
  ERROR  A or B lands inside a transcribed word
  ERROR  A and B come from the same source and B < A (content repeats)
  WARN   last word before A ends less than --post-handle seconds before A (decay clipped)
  WARN   first word after B starts less than --pre-handle seconds after B (attack clipped)
  WARN   A or B lands in active audio (mean level above --loud-db over a 40 ms window; needs ffmpeg)
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edl  # noqa: E402  (reuses inside_word, boundary_level, load_transcript_words)

DEFAULT_PRE_HANDLE_S = 0.10   # keep >= ~3 frames at 30 fps before a kept word's onset
DEFAULT_POST_HANDLE_S = 0.15  # keep >= ~4-5 frames at 30 fps after a kept word's offset
CLIP_TAGS = {"asset-clip", "clip", "ref-clip", "sync-clip", "mc-clip"}


class SeamError(Exception):
    pass


def fcp_time(value: str | None) -> Fraction:
    """Parse FCPXML rational time: '1001/30000s', '10s', '0s'."""
    if not value:
        return Fraction(0)
    text = value.strip()
    if not text.endswith("s"):
        raise SeamError(f"unrecognised FCPXML time {value!r}")
    text = text[:-1]
    if "/" in text:
        num, den = text.split("/", 1)
        return Fraction(int(num), int(den))
    return Fraction(text)


def asset_paths(root: ET.Element) -> dict[str, str]:
    paths: dict[str, str] = {}
    for asset in root.iter("asset"):
        src = asset.get("src")
        rep = asset.find("media-rep")
        if rep is not None and rep.get("src"):
            src = rep.get("src")
        if asset.get("id") and src:
            parsed = urlparse(src)
            paths[asset.get("id")] = unquote(parsed.path) if parsed.scheme == "file" else src
    return paths


def sequence_fps(root: ET.Element, sequence: ET.Element) -> float | None:
    fmt_id = sequence.get("format")
    for fmt in root.iter("format"):
        if fmt.get("id") == fmt_id and fmt.get("frameDuration"):
            return float(1 / fcp_time(fmt.get("frameDuration")))
    return None


def clip_source(clip: ET.Element) -> tuple[str | None, Fraction]:
    """Return (asset ref, source in point) for a spine clip."""
    if clip.tag == "asset-clip":
        return clip.get("ref"), fcp_time(clip.get("start"))
    for child in clip:
        if child.tag in {"video", "audio"} and child.get("ref"):
            # nested media start is the source in point; outer start trims within it
            inner = fcp_time(child.get("start"))
            outer = fcp_time(clip.get("start")) if clip.get("start") else inner
            return child.get("ref"), outer
    return clip.get("ref"), fcp_time(clip.get("start"))


def spine_clips(fcpxml: Path) -> tuple[list[dict[str, Any]], float | None]:
    try:
        root = ET.parse(fcpxml).getroot()
    except ET.ParseError as exc:
        raise SeamError(f"{fcpxml}: not valid XML ({exc})") from exc
    sequence = root.find(".//sequence")
    spine = sequence.find("spine") if sequence is not None else None
    if spine is None:
        raise SeamError(f"{fcpxml}: no sequence/spine found")
    paths = asset_paths(root)
    clips: list[dict[str, Any]] = []
    for el in spine:
        if el.tag == "gap":
            clips.append({"gap": True, "offset": fcp_time(el.get("offset")), "duration": fcp_time(el.get("duration"))})
            continue
        if el.tag not in CLIP_TAGS:
            continue
        ref, src_in = clip_source(el)
        duration = fcp_time(el.get("duration"))
        clips.append({"gap": False, "name": el.get("name") or ref, "ref": ref, "path": paths.get(ref or ""),
                      "offset": fcp_time(el.get("offset")), "duration": duration,
                      "src_in": src_in, "src_out": src_in + duration})
    return clips, sequence_fps(root, sequence)


def resolve_media(path: str | None, source_root: Path | None) -> Path | None:
    if not path:
        return None
    candidate = Path(path)
    if source_root is not None:
        remapped = source_root / candidate.name
        if remapped.exists():
            return remapped
    return candidate if candidate.exists() else None


def transcript_for(path: str | None, transcripts: Path | None) -> Path | None:
    if not path or transcripts is None:
        return None
    candidate = transcripts / f"{Path(path).stem}.json"
    return candidate if candidate.exists() else None


def last_word_before(words: list[dict[str, Any]], t: float) -> dict[str, Any] | None:
    before = [w for w in words if w["end"] <= t + edl.WORD_TOLERANCE_S]
    return max(before, key=lambda w: w["end"]) if before else None


def first_word_after(words: list[dict[str, Any]], t: float) -> dict[str, Any] | None:
    after = [w for w in words if w["start"] >= t - edl.WORD_TOLERANCE_S]
    return min(after, key=lambda w: w["start"]) if after else None


def audit(fcpxml: Path, transcripts: Path | None = None, source_root: Path | None = None,
          pre_handle: float = DEFAULT_PRE_HANDLE_S, post_handle: float = DEFAULT_POST_HANDLE_S,
          loud_db: float = edl.LOUD_BOUNDARY_DB, check_audio: bool = True) -> dict[str, Any]:
    clips, fps = spine_clips(fcpxml)
    word_cache: dict[str, list[dict[str, Any]]] = {}
    notes: list[str] = []

    def words_for(clip: dict[str, Any]) -> list[dict[str, Any]] | None:
        tpath = transcript_for(clip.get("path"), transcripts)
        if tpath is None:
            return None
        key = str(tpath)
        if key not in word_cache:
            word_cache[key] = edl.load_transcript_words(tpath)
        return word_cache[key]

    seams: list[dict[str, Any]] = []
    for a, b in zip(clips, clips[1:]):
        if a["gap"] or b["gap"]:
            continue
        at = float(b["offset"])
        seam: dict[str, Any] = {"timeline_seconds": round(at, 3),
                                "timeline_frame": round(at * fps) if fps else None,
                                "out": {"clip": a["name"], "source_seconds": round(float(a["src_out"]), 3)},
                                "in": {"clip": b["name"], "source_seconds": round(float(b["src_in"]), 3)},
                                "errors": [], "warnings": []}
        a_out, b_in = float(a["src_out"]), float(b["src_in"])
        if a["ref"] and a["ref"] == b["ref"] and b_in < a_out - edl.WORD_TOLERANCE_S:
            seam["errors"].append(f"same source re-enters {a_out - b_in:.3f}s before the previous out point; content repeats")

        wa, wb = words_for(a), words_for(b)
        if wa is None or wb is None:
            seam["warnings"].append("no transcript for one side; word checks skipped")
        if wa is not None:
            word = edl.inside_word(wa, a_out)
            if word:
                seam["errors"].append(f"out point cuts inside {word['text']!r} ({word['start']}-{word['end']})")
            else:
                last = last_word_before(wa, a_out)
                if last and a_out - last["end"] < post_handle:
                    seam["warnings"].append(f"only {a_out - last['end']:.3f}s after {last['text']!r} ends; decay may be clipped")
        if wb is not None:
            word = edl.inside_word(wb, b_in)
            if word:
                seam["errors"].append(f"in point cuts inside {word['text']!r} ({word['start']}-{word['end']})")
            else:
                nxt = first_word_after(wb, b_in)
                if nxt and nxt["start"] - b_in < pre_handle:
                    seam["warnings"].append(f"only {nxt['start'] - b_in:.3f}s before {nxt['text']!r} starts; attack may be clipped")

        if check_audio:
            for side, clip, t in (("out", a, a_out), ("in", b, b_in)):
                media = resolve_media(clip.get("path"), source_root)
                if media is None:
                    seam["warnings"].append(f"{side} source media not found; level check skipped")
                    continue
                level = edl.boundary_level(media, t)
                if level is not None and level > loud_db:
                    seam["warnings"].append(f"{side} point lands in active audio ({level:.1f} dBFS); listen to this seam")
        seams.append(seam)

    if fps is None:
        notes.append("sequence frame rate not found; timeline_frame omitted")
    errors = sum(len(s["errors"]) for s in seams)
    warnings = sum(len(s["warnings"]) for s in seams)
    return {"fcpxml": str(fcpxml), "fps": fps, "seam_count": len(seams), "errors": errors,
            "warnings": warnings, "seams": seams, "notes": notes}


def print_report(report: dict[str, Any]) -> None:
    print(f"{report['seam_count']} seams, {report['errors']} errors, {report['warnings']} warnings")
    for seam in report["seams"]:
        where = f"{seam['timeline_seconds']:.3f}s"
        if seam["timeline_frame"] is not None:
            where += f" (frame {seam['timeline_frame']})"
        for msg in seam["errors"]:
            print(f"ERROR {where}: {msg}")
        for msg in seam["warnings"]:
            print(f"WARN  {where}: {msg}")
    for note in report["notes"]:
        print(f"NOTE  {note}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("fcpxml", type=Path)
    p.add_argument("--transcripts", type=Path, help="directory of <source-stem>.json Parakeet transcripts")
    p.add_argument("--source-root", type=Path, help="directory to find source media when FCPXML paths are from another machine")
    p.add_argument("--pre-handle", type=float, default=DEFAULT_PRE_HANDLE_S)
    p.add_argument("--post-handle", type=float, default=DEFAULT_POST_HANDLE_S)
    p.add_argument("--loud-db", type=float, default=edl.LOUD_BOUNDARY_DB)
    p.add_argument("--no-audio", action="store_true", help="skip FFmpeg level checks")
    p.add_argument("--strict", action="store_true", help="fail on warnings too")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    try:
        report = audit(args.fcpxml, args.transcripts, args.source_root, args.pre_handle, args.post_handle,
                       args.loud_db, check_audio=not args.no_audio)
    except (SeamError, OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    if report["errors"] or (args.strict and report["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
