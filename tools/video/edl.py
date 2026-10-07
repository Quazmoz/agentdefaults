#!/usr/bin/env python3
"""Plan, render, caption, and QC a local video edit from one JSON edit decision list (EDL).

Subcommands:
  probe       summarize source media (duration, streams, fps/VFR, HDR) for intake
  silences    list silent gaps in a file (cut-point candidates)
  transcript  compact view of a parakeet_transcribe.py JSON (segments, or words in a window)
  plan        validate an EDL and print the output timeline and boundary warnings (no render)
  render      render an EDL with FFmpeg: cuts, overlays, licensed audio beds, loudness
  captions    write an SRT for the edited output from per-source transcripts
  qc          machine checks on a render plus still frames for visual review

EDL (paths relative to the EDL file; times are seconds or "m:ss.s" strings):

  {"output":   {"width": 1920, "height": 1080, "fps": 30, "sample_rate": 48000, "loudness": -14},
   "sources":  {"cam": {"path": "../raw/a.mp4", "transcript": "transcripts/cam.json"}},
   "segments": [{"source": "cam", "start": "0:12.40", "end": "0:45.10", "note": "hook", "crop": [x, y, w, h]}],
   "overlays": [{"file": "../graphics/title.mov", "at": 1.0, "duration": 3, "kind": "graphic",
                 "box": [x, y, w, h], "fade": 0.2, "start": 0},
                {"file": "../broll/notes.png", "at": 20, "duration": 4, "kind": "evidence",
                 "evidence": {"claim": "...", "url": "https://...", "captured": "2026-10-05"}}],
   "audio":    [{"file": "../audio/bed.wav", "at": 0, "gain_db": -24, "fade_in": 1, "fade_out": 2,
                 "license": "Epidemic Sound subscription, track <id>"}]}

Overlay kinds: graphic (own HyperFrames render), evidence (needs evidence.claim/url/captured),
broll (needs license). Every audio item needs license. Overlays are picture-only.
Redactions are output-timeline regions applied after overlays. `mode=black` is required for secrets/credentials;
`mode=blur` is appropriate only for non-secret personal data. Moving redactions use relative keyframes and
conservative swept rectangles between keyframes so uncertain tracking fails toward over-redaction.
When privacy.required is true, `plan` fails unless transcript and visual review are explicitly complete and the
privacy review intervals cover the entire output timeline.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
DEFAULT_OUTPUT = {"width": 1920, "height": 1080, "fps": 30, "sample_rate": 48000, "loudness": None}
SEAM_FADE_S = 0.01  # micro-fade against clicks only; never a fix for a bad speech boundary
WORD_TOLERANCE_S = 0.02
LOUD_BOUNDARY_DB = -35.0
MAX_QC_FRAMES = 48
MAX_PRIVACY_QC_FRAMES = 20000
PRIVACY_EPS_S = 0.05


class EdlError(Exception):
    pass


def need(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        raise SystemExit(f"{tool} not found on PATH (install FFmpeg: brew install ffmpeg / apt install ffmpeg).")
    return path


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def seconds(value: Any) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).strip().split(":")
    try:
        total = 0.0
        for part in parts:
            total = total * 60 + float(part)
        return total
    except ValueError:
        raise EdlError(f"invalid time {value!r}") from None


def clock(t: float) -> str:
    minutes, secs = divmod(max(t, 0.0), 60)
    return f"{int(minutes)}:{secs:05.2f}"


# --- probing -----------------------------------------------------------------

def probe(path: Path) -> dict[str, Any]:
    proc = run([need("ffprobe"), "-v", "error", "-print_format", "json", "-show_format", "-show_streams", str(path)])
    if proc.returncode != 0:
        raise EdlError(f"ffprobe failed for {path}: {proc.stderr.strip()}")
    data = json.loads(proc.stdout)
    info: dict[str, Any] = {"path": str(path), "duration": float(data.get("format", {}).get("duration") or 0.0),
                            "video": None, "audio": []}
    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and info["video"] is None and stream.get("disposition", {}).get("attached_pic") != 1:
            r_fps, avg_fps = Fraction(stream.get("r_frame_rate") or "0/1"), Fraction(stream.get("avg_frame_rate") or "0/1")
            info["video"] = {
                "codec": stream.get("codec_name"), "width": stream.get("width"), "height": stream.get("height"),
                "fps": round(float(r_fps), 3), "avg_fps": round(float(avg_fps), 3),
                "vfr": bool(avg_fps) and abs(float(r_fps) - float(avg_fps)) > 0.01,
                "pix_fmt": stream.get("pix_fmt"),
                "hdr": stream.get("color_transfer") in {"smpte2084", "arib-std-b67"},
                "duration": float(stream.get("duration") or 0.0),
            }
        elif stream.get("codec_type") == "audio":
            info["audio"].append({"codec": stream.get("codec_name"), "sample_rate": int(stream.get("sample_rate") or 0),
                                  "channels": stream.get("channels"),
                                  "duration": float(stream.get("duration") or 0.0)})
    return info


def probe_warnings(infos: list[dict[str, Any]]) -> list[str]:
    warnings = []
    for info in infos:
        video, name = info["video"], info["path"]
        if not video and not info["audio"]:
            warnings.append(f"{name}: no audio or video stream")
        if not info["audio"]:
            warnings.append(f"{name}: no audio stream (render pads silence)")
        if video and video["vfr"]:
            warnings.append(f"{name}: variable frame rate ({video['avg_fps']} avg vs {video['fps']}); render converts to CFR")
        if video and video["hdr"]:
            warnings.append(f"{name}: HDR transfer; render does not tone-map, colors will look washed out")
    shapes = {(i["video"]["width"], i["video"]["height"], i["video"]["fps"]) for i in infos if i["video"]}
    if len(shapes) > 1:
        warnings.append(f"mixed resolution/fps across sources {sorted(shapes)}; render scales/pads to the output format")
    return warnings


SILENCE_RE = re.compile(r"silence_(start|end): (-?[\d.]+)")
BLACK_RE = re.compile(r"black_start:(-?[\d.]+) black_end:(-?[\d.]+)")


def parse_silences(stderr: str, duration: float) -> list[list[float]]:
    gaps: list[list[float]] = []
    for kind, value in SILENCE_RE.findall(stderr):
        t = round(max(float(value), 0.0), 3)
        if kind == "start":
            gaps.append([t, round(duration, 3)])  # open until an end arrives
        elif gaps:
            gaps[-1][1] = t
    return gaps


def silences(path: Path, noise_db: float, min_s: float) -> list[list[float]]:
    proc = run([need("ffmpeg"), "-hide_banner", "-nostats", "-i", str(path), "-vn",
                "-af", f"silencedetect=n={noise_db}dB:d={min_s}", "-f", "null", "-"])
    if proc.returncode != 0:
        raise EdlError(f"silencedetect failed for {path}: {proc.stderr.strip()[-400:]}")
    return parse_silences(proc.stderr, probe(path)["duration"])


def boundary_level(path: Path, t: float, half: float = 0.02) -> float | None:
    """Mean dBFS in a 40 ms window around t: loud means the cut lands inside sound."""
    proc = run([need("ffmpeg"), "-hide_banner", "-nostats", "-ss", f"{max(t - half, 0):.3f}", "-t", f"{2 * half:.3f}",
                "-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"])
    match = re.search(r"mean_volume: (-?[\d.]+|-inf) dB", proc.stderr)
    return None if not match or match.group(1) == "-inf" else float(match.group(1))


# --- planning ----------------------------------------------------------------

def load_transcript_words(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [w for w in data.get("words", []) if isinstance(w, dict) and "start" in w and "end" in w]


def inside_word(words: list[dict[str, Any]], t: float) -> dict[str, Any] | None:
    for word in words:
        if word["start"] + WORD_TOLERANCE_S < t < word["end"] - WORD_TOLERANCE_S:
            return word
    return None


def _normalize_box(box: Any, width: int, height: int, label: str, errors: list[str]) -> list[int] | None:
    if not isinstance(box, list) or len(box) != 4:
        errors.append(f"{label}: box must be [x, y, width, height]")
        return None
    try:
        x, y, w, h = [int(round(float(v))) for v in box]
    except (TypeError, ValueError):
        errors.append(f"{label}: box values must be numeric")
        return None
    if w < 1 or h < 1 or x < 0 or y < 0 or x + w > width or y + h > height:
        errors.append(f"{label}: box {[x, y, w, h]} outside output frame {width}x{height}")
        return None
    return [x, y, w, h]


def _pad_box(box: list[int], padding: int, width: int, height: int) -> list[int]:
    x, y, w, h = box
    x0, y0 = max(0, x - padding), max(0, y - padding)
    x1, y1 = min(width, x + w + padding), min(height, y + h + padding)
    return [x0, y0, max(1, x1 - x0), max(1, y1 - y0)]


def _swept_box(a: list[int], b: list[int]) -> list[int]:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    x0, y0 = min(ax, bx), min(ay, by)
    x1, y1 = max(ax + aw, bx + bw), max(ay + ah, by + bh)
    return [x0, y0, x1 - x0, y1 - y0]


def _build_redactions(edl: dict[str, Any], out: dict[str, Any], duration: float,
                      errors: list[str]) -> list[dict[str, Any]]:
    width, height = int(out["width"]), int(out["height"])
    redactions: list[dict[str, Any]] = []
    for i, item in enumerate(edl.get("redactions") or []):
        label = f"redaction {i}"
        category = str(item.get("label", "")).strip()
        if not category:
            errors.append(f"{label}: label is required and must describe the category, not reproduce the sensitive value")
        mode = str(item.get("mode", "blur"))
        if mode not in {"blur", "black"}:
            errors.append(f"{label}: unsupported mode {mode!r}; use 'blur' or 'black'")
            continue
        try:
            at, dur = seconds(item.get("at", 0)), seconds(item["duration"])
            padding = int(item.get("padding", 8))
        except (KeyError, TypeError, ValueError, EdlError) as exc:
            errors.append(f"{label}: invalid timing/padding: {exc}")
            continue
        if at < 0 or dur <= 0 or at + dur > duration + PRIVACY_EPS_S:
            errors.append(f"{label}: {at}+{dur}s does not fit the {duration:.2f}s program")
            continue
        if padding < 0 or padding > max(width, height):
            errors.append(f"{label}: invalid padding {padding}")
            continue

        slices: list[dict[str, Any]] = []
        keyframes = item.get("keyframes")
        if keyframes is not None:
            if not isinstance(keyframes, list) or len(keyframes) < 2:
                errors.append(f"{label}: moving redactions need at least two keyframes")
                continue
            parsed: list[tuple[float, list[int]]] = []
            for j, keyframe in enumerate(keyframes):
                if not isinstance(keyframe, dict):
                    errors.append(f"{label} keyframe {j}: must be an object")
                    continue
                try:
                    rel = seconds(keyframe["at"])
                except (KeyError, EdlError) as exc:
                    errors.append(f"{label} keyframe {j}: {exc}")
                    continue
                box = _normalize_box(keyframe.get("box"), width, height, f"{label} keyframe {j}", errors)
                if box is not None:
                    parsed.append((rel, box))
            if len(parsed) != len(keyframes):
                continue
            if abs(parsed[0][0]) > PRIVACY_EPS_S or abs(parsed[-1][0] - dur) > PRIVACY_EPS_S:
                errors.append(f"{label}: keyframes must cover the full redaction interval from 0 to duration ({dur:.3f}s)")
                continue
            if any(a[0] < -PRIVACY_EPS_S or a[0] > dur + PRIVACY_EPS_S for a in parsed):
                errors.append(f"{label}: keyframe time outside 0..{dur:.3f}s")
                continue
            if any(b[0] <= a[0] for a, b in zip(parsed, parsed[1:])):
                errors.append(f"{label}: keyframe times must be strictly increasing")
                continue
            for (t0, box0), (t1, box1) in zip(parsed, parsed[1:]):
                swept = _pad_box(_swept_box(box0, box1), padding, width, height)
                slices.append({"start": at + t0, "end": at + t1, "box": swept})
        else:
            box = _normalize_box(item.get("box"), width, height, label, errors)
            if box is None:
                continue
            slices.append({"start": at, "end": at + dur, "box": _pad_box(box, padding, width, height)})

        redactions.append({"index": i, "at": at, "duration": dur, "mode": mode, "label": category,
                           "padding": padding, "moving": keyframes is not None, "slices": slices})
    return redactions


def _build_privacy(edl: dict[str, Any], duration: float, errors: list[str]) -> dict[str, Any]:
    spec = edl.get("privacy") or {}
    required = bool(spec.get("required", False))
    privacy: dict[str, Any] = {"required": required}
    if not required:
        return privacy

    if spec.get("visual_reviewed") is not True:
        errors.append("privacy: visual_reviewed must be true after actual retained-output inspection")
    if spec.get("transcript_reviewed") is not True:
        errors.append("privacy: transcript_reviewed must be true after spoken-content review")

    try:
        review_step = float(spec["review_step"])
    except (KeyError, TypeError, ValueError):
        review_step = 0.0
        errors.append("privacy: review_step is required")
    if review_step and not 0.1 <= review_step <= 1.0:
        errors.append("privacy: review_step must be between 0.1 and 1.0 seconds for a fail-closed visual sweep")

    reviews: list[dict[str, Any]] = []
    for i, item in enumerate(spec.get("reviews") or []):
        label = f"privacy review {i}"
        try:
            start, end = seconds(item["start"]), seconds(item["end"])
        except (KeyError, EdlError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        status = str(item.get("status", ""))
        method = str(item.get("method", "")).strip()
        if status not in {"clear", "redacted"}:
            errors.append(f"{label}: status must be 'clear' or 'redacted'")
        if not method:
            errors.append(f"{label}: method is required")
        if start < 0 or end <= start or end > duration + PRIVACY_EPS_S:
            errors.append(f"{label}: invalid range {start}-{end} for {duration:.2f}s program")
            continue
        reviews.append({"start": max(0.0, start), "end": min(duration, end), "status": status, "method": method})

    if not reviews:
        errors.append("privacy: reviews must cover the complete output timeline")
    else:
        cursor = 0.0
        for item in sorted(reviews, key=lambda x: (x["start"], x["end"])):
            if item["start"] > cursor + PRIVACY_EPS_S:
                errors.append(f"privacy: reviews leave uncovered output {cursor:.3f}-{item['start']:.3f}s")
                break
            cursor = max(cursor, item["end"])
        if cursor < duration - PRIVACY_EPS_S:
            errors.append(f"privacy: reviews leave uncovered output {cursor:.3f}-{duration:.3f}s")

    privacy.update({"visual_reviewed": spec.get("visual_reviewed") is True,
                    "transcript_reviewed": spec.get("transcript_reviewed") is True,
                    "review_step": review_step, "reviews": reviews,
                    "forbidden_terms": list(spec.get("forbidden_terms") or [])})
    return privacy

def build_plan(edl_path: Path, check_audio: bool = True) -> dict[str, Any]:
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    base = edl_path.resolve().parent
    out = {**DEFAULT_OUTPUT, **edl.get("output", {})}
    fps = Fraction(str(out["fps"])).limit_denominator(1001)
    errors: list[str] = []
    warnings: list[str] = []

    sources: dict[str, dict[str, Any]] = {}
    for sid, spec in (edl.get("sources") or {}).items():
        path = (base / str(spec.get("path", ""))).resolve()
        if not spec.get("path") or not path.is_file():
            errors.append(f"source {sid}: missing file {path}")
            continue
        info = probe(path)
        words = []
        if spec.get("transcript"):
            tpath = (base / spec["transcript"]).resolve()
            if tpath.is_file():
                words = load_transcript_words(tpath)
            else:
                warnings.append(f"source {sid}: transcript {tpath} not found; word-boundary checks skipped")
        sources[sid] = {"path": path, "info": info, "words": words}
    if sources:
        warnings += probe_warnings([s["info"] for s in sources.values()])

    segments: list[dict[str, Any]] = []
    cursor = 0  # output frames
    for i, seg in enumerate(edl.get("segments") or []):
        label = f"segment {i} ({seg.get('note', seg.get('source'))})"
        src = sources.get(seg.get("source"))
        if src is None:
            errors.append(f"{label}: unknown or missing source {seg.get('source')!r}")
            continue
        try:
            start, end = seconds(seg["start"]), seconds(seg["end"])
        except (KeyError, EdlError) as exc:
            errors.append(f"{label}: {exc}")
            continue
        frames = round((end - start) * fps)
        if start < 0 or frames < 1:
            errors.append(f"{label}: invalid range {start}-{end}")
            continue
        if end > src["info"]["duration"] + 0.05:
            errors.append(f"{label}: end {end} exceeds source duration {src['info']['duration']:.3f}")
            continue
        video = src["info"]["video"]
        crop = seg.get("crop")
        if crop and (not video or len(crop) != 4 or crop[0] < 0 or crop[1] < 0
                     or crop[0] + crop[2] > video["width"] or crop[1] + crop[3] > video["height"]):
            errors.append(f"{label}: crop {crop} outside source frame")
        for edge, t in (("start", start), ("end", end)):
            word = inside_word(src["words"], t)
            if word:
                warnings.append(f"{label}: {edge} {t:.3f} cuts inside word {word['text']!r} ({word['start']}-{word['end']})")
            if check_audio and src["info"]["audio"] and 0 < t < src["info"]["duration"] - 0.02:
                level = boundary_level(src["path"], t)
                if level is not None and level > LOUD_BOUNDARY_DB:
                    warnings.append(f"{label}: {edge} {t:.3f} lands in active audio ({level:.1f} dBFS); listen to this seam")
        segments.append({"index": i, "source": seg["source"], "path": str(src["path"]), "start": start, "end": end,
                         "frames": frames, "out_start": float(cursor / fps), "out_end": float((cursor + frames) / fps),
                         "has_audio": bool(src["info"]["audio"]), "has_video": bool(video), "crop": crop,
                         "note": seg.get("note", "")})
        cursor += frames
    if not segments and not errors:
        errors.append("EDL has no segments")
    duration = float(cursor / fps)

    for a, b in zip(segments, segments[1:]):
        if a["source"] == b["source"] and b["start"] < a["end"] and a["start"] < b["end"]:
            warnings.append(f"segments {a['index']} and {b['index']} overlap in source {a['source']}; content repeats")

    overlays = []
    for i, ov in enumerate(edl.get("overlays") or []):
        label = f"overlay {i} ({Path(str(ov.get('file'))).name})"
        path = (base / str(ov.get("file"))).resolve()
        kind = ov.get("kind", "graphic")
        if not path.is_file():
            errors.append(f"{label}: missing file {path}")
            continue
        if kind == "evidence":
            missing = [k for k in ("claim", "url", "captured") if not (ov.get("evidence") or {}).get(k)]
            if missing:
                errors.append(f"{label}: evidence overlay missing {', '.join(missing)}")
        elif kind == "broll" and not ov.get("license"):
            errors.append(f"{label}: broll overlay needs a license note")
        elif kind not in {"graphic", "evidence", "broll"}:
            errors.append(f"{label}: unknown kind {kind!r}")
        at, src_start = seconds(ov.get("at", 0)), seconds(ov.get("start", 0))
        is_image = path.suffix.lower() in IMAGE_EXTS
        if "duration" in ov:
            dur = seconds(ov["duration"])
        elif is_image:
            errors.append(f"{label}: still images need a duration")
            continue
        else:
            dur = probe(path)["duration"] - src_start
        if dur <= 0 or at < 0 or at + dur > duration + 0.05:
            errors.append(f"{label}: {at}+{dur}s does not fit the {duration:.2f}s program")
            continue
        box = ov.get("box") or [0, 0, out["width"], out["height"]]
        overlays.append({"index": i, "path": str(path), "kind": kind, "at": at, "duration": dur, "start": src_start,
                         "image": is_image, "box": box, "fade": float(ov.get("fade", 0)),
                         "evidence": ov.get("evidence"), "license": ov.get("license")})

    redactions = _build_redactions(edl, out, duration, errors)
    privacy = _build_privacy(edl, duration, errors)

    audio = []
    for i, item in enumerate(edl.get("audio") or []):
        label = f"audio {i} ({Path(str(item.get('file'))).name})"
        path = (base / str(item.get("file"))).resolve()
        if not path.is_file():
            errors.append(f"{label}: missing file {path}")
            continue
        if not item.get("license"):
            errors.append(f"{label}: needs a license note (user-owned or licensed library); unknown-license audio is not allowed")
        at, src_start = seconds(item.get("at", 0)), seconds(item.get("start", 0))
        available = probe(path)["duration"] - src_start
        dur = min(seconds(item["duration"]) if "duration" in item else available, available, duration - at)
        if dur <= 0:
            errors.append(f"{label}: starts after the program ends or past the file end")
            continue
        audio.append({"index": i, "path": str(path), "at": at, "start": src_start, "duration": dur,
                      "gain_db": float(item.get("gain_db", -20)), "fade_in": float(item.get("fade_in", 0)),
                      "fade_out": float(item.get("fade_out", 0)), "license": item.get("license")})

    return {"edl": str(edl_path.resolve()), "output": {**out, "fps": str(fps)}, "duration": duration,
            "segments": segments, "overlays": overlays, "redactions": redactions, "privacy": privacy,
            "audio": audio, "errors": errors, "warnings": warnings}


def print_plan(plan: dict[str, Any]) -> None:
    out = plan["output"]
    print(f"output {out['width']}x{out['height']} @ {out['fps']} fps, {clock(plan['duration'])} ({plan['duration']:.2f}s)")
    for seg in plan["segments"]:
        print(f"  [{clock(seg['out_start'])}-{clock(seg['out_end'])}] seg {seg['index']:>3} "
              f"{seg['source']} {clock(seg['start'])}-{clock(seg['end'])}  {seg['note']}")
    for ov in plan["overlays"]:
        extra = f" <- {ov['evidence']['url']}" if ov.get("evidence") else ""
        print(f"  [{clock(ov['at'])}-{clock(ov['at'] + ov['duration'])}] {ov['kind']:<8} {Path(ov['path']).name}{extra}")
    for au in plan["audio"]:
        print(f"  [{clock(au['at'])}-{clock(au['at'] + au['duration'])}] audio    {Path(au['path']).name} {au['gain_db']} dB")
    for warning in plan["warnings"]:
        print(f"WARN  {warning}")
    for error in plan["errors"]:
        print(f"ERROR {error}")


# --- rendering ---------------------------------------------------------------

def _has_decoder(name: str) -> bool:
    return f" {name} " in run([need("ffmpeg"), "-hide_banner", "-decoders"]).stdout


def build_render_command(plan: dict[str, Any], output: Path, crf: int, preset: str) -> list[str]:
    out = plan["output"]
    W, H, sr = int(out["width"]), int(out["height"]), int(out["sample_rate"])
    fps = Fraction(out["fps"])
    cmd = [need("ffmpeg"), "-hide_banner", "-nostdin", "-y"]
    graph: list[str] = []
    n = 0
    # ponytail: one decoder input per segment; chunk into intermediate renders if an EDL reaches hundreds of segments.
    for i, seg in enumerate(plan["segments"]):
        dur = seg["frames"] / fps
        cmd += ["-ss", f"{seg['start']:.6f}", "-t", f"{float(dur) + 0.5:.6f}", "-i", seg["path"]]
        crop = f"crop={seg['crop'][2]}:{seg['crop'][3]}:{seg['crop'][0]}:{seg['crop'][1]}," if seg["crop"] else ""
        if seg["has_video"]:
            graph.append(f"[{n}:v:0]setpts=PTS-STARTPTS,{crop}scale={W}:{H}:force_original_aspect_ratio=decrease:"
                         f"force_divisible_by=2,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps},"
                         # clone-pad so a segment ending at the source's last frame still yields exactly N frames
                         f"tpad=stop_mode=clone:stop_duration=0.5,trim=end_frame={seg['frames']},format=yuv420p[v{i}]")
        else:
            graph.append(f"color=c=black:s={W}x{H}:r={fps},trim=end_frame={seg['frames']},format=yuv420p[v{i}]")
        d = f"{float(dur):.6f}"
        if seg["has_audio"]:
            graph.append(f"[{n}:a:0]asetpts=PTS-STARTPTS,aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo,"
                         f"atrim=end={d},apad=whole_dur={d},afade=t=in:d={SEAM_FADE_S},"
                         f"afade=t=out:st={float(dur) - SEAM_FADE_S:.6f}:d={SEAM_FADE_S}[a{i}]")
        else:
            graph.append(f"anullsrc=r={sr}:cl=stereo,atrim=end={d}[a{i}]")
        n += 1
    count = len(plan["segments"])
    graph.append("".join(f"[v{i}][a{i}]" for i in range(count)) + f"concat=n={count}:v=1:a=1[vb0][ab]")

    vp9_alpha = None
    for k, ov in enumerate(plan["overlays"]):
        if ov["image"]:
            cmd += ["-loop", "1", "-framerate", str(fps), "-t", f"{ov['duration']:.6f}", "-i", ov["path"]]
        else:
            if ov["path"].lower().endswith(".webm"):
                vp9_alpha = _has_decoder("libvpx-vp9") if vp9_alpha is None else vp9_alpha
                if vp9_alpha:
                    cmd += ["-c:v", "libvpx-vp9"]  # FFmpeg's native vp9 decoder drops alpha
            cmd += ["-ss", f"{ov['start']:.6f}", "-t", f"{ov['duration']:.6f}", "-i", ov["path"]]
        bx, by, bw, bh = ov["box"]
        fade = ""
        if ov["fade"] > 0:
            fade = (f",fade=t=in:st=0:d={ov['fade']}:alpha=1,"
                    f"fade=t=out:st={ov['duration'] - ov['fade']:.6f}:d={ov['fade']}:alpha=1")
        graph.append(f"[{n}:v:0]fps={fps},scale={bw}:{bh}:force_original_aspect_ratio=decrease:force_divisible_by=2,format=yuva420p{fade},"
                     f"setpts=PTS-STARTPTS+{ov['at']:.6f}/TB[o{k}]")
        graph.append(f"[vb{k}][o{k}]overlay=x={bx}+({bw}-w)/2:y={by}+({bh}-h)/2:eof_action=pass:"
                     f"enable='between(t,{ov['at']:.6f},{ov['at'] + ov['duration']:.6f})'[vb{k + 1}]")
        n += 1

    video_label = f"[vb{len(plan['overlays'])}]"
    redaction_no = 0
    for redaction in plan["redactions"]:
        for slice_ in redaction["slices"]:
            start, end = slice_["start"], slice_["end"]
            bx, by, bw, bh = slice_["box"]
            next_label = f"vr{redaction_no + 1}"
            if redaction["mode"] == "black":
                graph.append(f"{video_label}drawbox=x={bx}:y={by}:w={bw}:h={bh}:color=black@1:t=fill:"
                             f"enable='between(t,{start:.6f},{end:.6f})'[{next_label}]")
            else:
                base_label, crop_label, blur_label = f"vr{redaction_no}b", f"vr{redaction_no}c", f"vr{redaction_no}x"
                radius = max(1, min(20, bw // 4, bh // 4))
                graph.append(f"{video_label}split=2[{base_label}][{crop_label}]")
                graph.append(f"[{crop_label}]crop={bw}:{bh}:{bx}:{by},boxblur={radius}:2[{blur_label}]")
                graph.append(f"[{base_label}][{blur_label}]overlay=x={bx}:y={by}:eof_action=pass:"
                             f"enable='between(t,{start:.6f},{end:.6f})'[{next_label}]")
            video_label = f"[{next_label}]"
            redaction_no += 1
    graph.append(f"{video_label}format=yuv420p[vout]")

    beds = []
    for k, au in enumerate(plan["audio"]):
        cmd += ["-ss", f"{au['start']:.6f}", "-t", f"{au['duration']:.6f}", "-i", au["path"]]
        chain = f"[{n}:a:0]aresample={sr},aformat=sample_fmts=fltp:channel_layouts=stereo,volume={au['gain_db']}dB"
        if au["fade_in"] > 0:
            chain += f",afade=t=in:d={au['fade_in']}"
        if au["fade_out"] > 0:
            chain += f",afade=t=out:st={max(au['duration'] - au['fade_out'], 0):.6f}:d={au['fade_out']}"
        # ponytail: fixed-gain beds, no sidechain ducking; keep beds low or add sidechaincompress if needed.
        graph.append(f"{chain},adelay=delays={round(au['at'] * 1000)}:all=1[b{k}]")
        beds.append(f"[b{k}]")
        n += 1
    audio_label = "[ab]"
    if beds:
        graph.append(f"[ab]{''.join(beds)}amix=inputs={len(beds) + 1}:duration=first:normalize=0[amix]")
        audio_label = "[amix]"
    if out.get("loudness") is not None:
        # ponytail: single-pass loudnorm; measure with `qc` and switch to two-pass if the result misses the target.
        audio_label += f"loudnorm=I={out['loudness']}:TP=-1.5:LRA=11,aresample={sr},"
    # loudnorm flushes a short tail; clamp so audio and video end on the same frame
    graph.append(f"{audio_label}atrim=end={plan['duration']:.6f}[aout]")

    cmd += ["-filter_complex", ";".join(graph), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "192k", "-ar", str(sr), "-movflags", "+faststart", str(output)]
    return cmd


def render(plan: dict[str, Any], output: Path, crf: int, preset: str) -> None:
    inputs = {Path(s["path"]).resolve() for s in plan["segments"]} | {Path(o["path"]).resolve() for o in plan["overlays"]}
    if output.resolve() in inputs:
        raise SystemExit(f"refusing to overwrite an input: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.stem + ".partial" + output.suffix)
    proc = subprocess.run(build_render_command(plan, partial, crf, preset), capture_output=True, text=True)
    if proc.returncode != 0:
        partial.unlink(missing_ok=True)
        raise SystemExit(f"ffmpeg render failed:\n{proc.stderr.strip()[-2000:]}")
    os.replace(partial, output)
    # Sidecar timeline so review timestamps on this exact render map back to sources after the EDL changes.
    sidecar = {k: plan[k] for k in ("edl", "output", "duration", "segments", "overlays", "redactions", "privacy", "audio", "warnings")}
    output.with_name(output.name + ".json").write_text(json.dumps(sidecar, indent=2) + "\n", encoding="utf-8")


# --- captions ----------------------------------------------------------------

def caption_cues(plan: dict[str, Any], max_chars: int, max_seconds: float) -> list[tuple[float, float, str]]:
    edl = json.loads(Path(plan["edl"]).read_text(encoding="utf-8"))
    base = Path(plan["edl"]).parent
    cache: dict[str, list[dict[str, Any]]] = {}
    words: list[tuple[float, float, str]] = []
    for seg in plan["segments"]:
        spec = edl["sources"][seg["source"]]
        if not spec.get("transcript"):
            continue
        if seg["source"] not in cache:
            cache[seg["source"]] = load_transcript_words((base / spec["transcript"]).resolve())
        for w in cache[seg["source"]]:
            # Only words wholly inside the kept range; a partial word is a boundary problem, not a caption.
            if w["start"] >= seg["start"] - WORD_TOLERANCE_S and w["end"] <= seg["end"] + WORD_TOLERANCE_S:
                shift = seg["out_start"] - seg["start"]
                words.append((max(w["start"] + shift, seg["out_start"]), min(w["end"] + shift, seg["out_end"]), w["text"]))
    cues: list[tuple[float, float, str]] = []
    current: list[tuple[float, float, str]] = []
    for word in words:
        if current:
            text = " ".join(x[2] for x in current + [word])
            gap = word[0] - current[-1][1]
            if len(text) > max_chars or word[1] - current[0][0] > max_seconds or gap > 0.6 \
                    or current[-1][2].endswith((".", "?", "!")):
                cues.append((current[0][0], current[-1][1], " ".join(x[2] for x in current)))
                current = []
        current.append(word)
    if current:
        cues.append((current[0][0], current[-1][1], " ".join(x[2] for x in current)))
    return cues


def srt(cues: list[tuple[float, float, str]]) -> str:
    def ts(t: float) -> str:
        ms = round(t * 1000)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return "".join(f"{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n" for i, (a, b, text) in enumerate(cues, 1))


# --- QC ----------------------------------------------------------------------

def qc(path: Path, plan: dict[str, Any] | None, frames_dir: Path | None,
       privacy_step: float | None = None) -> dict[str, Any]:
    info = probe(path)
    issues: list[str] = []
    review: list[str] = []
    if not info["video"]:
        issues.append("no video stream")
    if not info["audio"]:
        issues.append("no audio stream")
    elif info["video"] and info["video"]["duration"] and info["audio"][0]["duration"] \
            and abs(info["video"]["duration"] - info["audio"][0]["duration"]) > 0.05:
        issues.append(f"audio/video stream durations differ ({info['audio'][0]['duration']:.3f}s vs "
                      f"{info['video']['duration']:.3f}s): truncation or drift")
    proc = run([need("ffmpeg"), "-hide_banner", "-nostats", "-i", str(path), "-vf", "blackdetect=d=0.20:pix_th=0.10",
                "-af", "silencedetect=n=-50dB:d=1.0,ebur128=peak=true", "-f", "null", "-"])
    if proc.returncode != 0:
        issues.append(f"decode failed: {proc.stderr.strip()[-300:]}")
    black = [[float(a), float(b)] for a, b in BLACK_RE.findall(proc.stderr)]
    silent = parse_silences(proc.stderr, info["duration"])
    lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", proc.stderr)
    peak = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", proc.stderr)
    review += [f"black {clock(a)}-{clock(b)}" for a, b in black]
    review += [f"silence {clock(a)}-{clock(b)}" for a, b in silent]
    report: dict[str, Any] = {"file": str(path), "probe": info, "black": black, "silence": silent,
                              "integrated_lufs": float(lufs[-1]) if lufs else None,
                              "true_peak_dbfs": float(peak[-1]) if peak and peak[-1] != "-inf" else None}
    if report["true_peak_dbfs"] is not None and report["true_peak_dbfs"] > -1.0:
        review.append(f"true peak {report['true_peak_dbfs']} dBFS is above -1 dBFS (clipping risk after transcoding)")
    if plan:
        out = plan["output"]
        tolerance = float(1 / Fraction(out["fps"])) + 0.05
        if abs(info["duration"] - plan["duration"]) > tolerance:
            issues.append(f"duration {info['duration']:.3f}s != planned {plan['duration']:.3f}s")
        video = info["video"] or {}
        if (video.get("width"), video.get("height")) != (int(out["width"]), int(out["height"])):
            issues.append(f"resolution {video.get('width')}x{video.get('height')} != {out['width']}x{out['height']}")
        if video and abs(video["fps"] - float(Fraction(out["fps"]))) > 0.01:
            issues.append(f"fps {video['fps']} != {out['fps']}")

    if frames_dir:
        times = {min(1.0, info["duration"] / 2), max(info["duration"] - 1.0, 0.0)}
        if plan:
            times |= {s["out_start"] + 0.15 for s in plan["segments"][1:]}
            times |= {o["at"] + o["duration"] / 2 for o in plan["overlays"]}
            for redaction in plan.get("redactions", []):
                for slice_ in redaction.get("slices", []):
                    start, end = slice_["start"], slice_["end"]
                    times |= {start + 0.01, start + (end - start) / 2, max(start + 0.01, end - 0.01)}
            if privacy_step is None and plan.get("privacy", {}).get("required"):
                privacy_step = float(plan["privacy"].get("review_step") or 0)
        if privacy_step is not None:
            if privacy_step <= 0:
                issues.append("privacy_step must be positive")
            else:
                count = int(info["duration"] / privacy_step) + 1
                if count > MAX_PRIVACY_QC_FRAMES:
                    issues.append(f"dense privacy sweep would create {count} frames; raise review_step or split the review")
                else:
                    times |= {min(i * privacy_step, max(info["duration"] - 0.001, 0.0)) for i in range(count)}
        ordered = sorted(t for t in times if 0 <= t < info["duration"])
        if privacy_step is None and len(ordered) > MAX_QC_FRAMES:
            step = len(ordered) / MAX_QC_FRAMES
            ordered = [ordered[int(i * step)] for i in range(MAX_QC_FRAMES)]
        frames_dir.mkdir(parents=True, exist_ok=True)
        stills = []
        for t in ordered:
            still = frames_dir / f"frame-{t:08.2f}.jpg"
            run([need("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", str(path),
                 "-frames:v", "1", "-vf", "scale=960:-2", "-q:v", "4", str(still)])
            if still.is_file():
                stills.append(str(still))
        report["frames"] = stills
        report["privacy_step"] = privacy_step
        report["privacy_frames_generated"] = len(stills) if privacy_step is not None else 0
    report["issues"], report["review"] = issues, review
    return report


# --- transcript view ---------------------------------------------------------

def transcript_view(path: Path, words: bool, start: float, end: float) -> str:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("words" if words else "segments", [])
    lines = []
    for row in rows:
        if row["end"] >= start and row["start"] <= end:
            if words:
                lines.append(f"{row['start']:9.3f} {row['end']:9.3f}  {row['text']}")
            else:
                lines.append(f"[{clock(row['start'])}-{clock(row['end'])}] {row['text']}")
    return "\n".join(lines)


# --- CLI ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe", help="summarize source media")
    p.add_argument("files", nargs="+", type=Path)
    p = sub.add_parser("silences", help="list silent gaps (cut-point candidates)")
    p.add_argument("file", type=Path)
    p.add_argument("--noise-db", type=float, default=-35.0)
    p.add_argument("--min", type=float, default=0.25, dest="min_s")
    p = sub.add_parser("transcript", help="compact transcript view")
    p.add_argument("file", type=Path)
    p.add_argument("--words", action="store_true", help="word rows instead of segments")
    p.add_argument("--from", dest="start", default="0")
    p.add_argument("--to", dest="end", default="99999")
    for name in ("plan", "render", "captions"):
        p = sub.add_parser(name)
        p.add_argument("edl", type=Path)
        if name == "plan":
            p.add_argument("--skip-audio-check", action="store_true", help="skip per-boundary loudness probes")
        if name == "render":
            p.add_argument("-o", "--output", type=Path, required=True)
            p.add_argument("--crf", type=int, default=18)
            p.add_argument("--preset", default="medium")
        if name == "captions":
            p.add_argument("-o", "--output", type=Path, required=True)
            p.add_argument("--max-chars", type=int, default=42, help="use ~20 for vertical Shorts")
            p.add_argument("--max-seconds", type=float, default=5.0)
    p = sub.add_parser("qc", help="machine QC of a render")
    p.add_argument("file", type=Path)
    p.add_argument("--edl", type=Path, help="EDL to compare against (default: the render's .json sidecar)")
    p.add_argument("--frames", type=Path, help="write review stills here (seams, overlays, head, tail)")
    p.add_argument("--privacy-step", type=float,
                   help="dense visual privacy sweep cadence in seconds; never subsampled (recommended 0.5)")
    args = parser.parse_args(argv)

    try:
        if args.cmd == "probe":
            infos = [probe(f) for f in args.files]
            print(json.dumps({"files": infos, "warnings": probe_warnings(infos)}, indent=2))
        elif args.cmd == "silences":
            print(json.dumps(silences(args.file, args.noise_db, args.min_s)))
        elif args.cmd == "transcript":
            print(transcript_view(args.file, args.words, seconds(args.start), seconds(args.end)))
        elif args.cmd == "qc":
            plan = None
            sidecar = args.file.with_name(args.file.name + ".json")
            if args.edl:
                plan = build_plan(args.edl, check_audio=False)
            elif sidecar.is_file():
                plan = json.loads(sidecar.read_text(encoding="utf-8"))
            report = qc(args.file, plan, args.frames, args.privacy_step)
            print(json.dumps(report, indent=2))
            return 1 if report["issues"] else 0
        else:
            plan = build_plan(args.edl, check_audio=args.cmd == "plan" and not args.skip_audio_check)
            print_plan(plan)
            if plan["errors"]:
                return 1
            if args.cmd == "render":
                render(plan, args.output, args.crf, args.preset)
                print(f"rendered {args.output} ({plan['duration']:.2f}s); now run: edl.py qc {args.output} --frames <dir>")
            elif args.cmd == "captions":
                cues = caption_cues(plan, args.max_chars, args.max_seconds)
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(srt(cues), encoding="utf-8")
                print(f"wrote {len(cues)} cues to {args.output}")
    except EdlError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
