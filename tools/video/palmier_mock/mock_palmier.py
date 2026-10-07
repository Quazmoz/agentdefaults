#!/usr/bin/env python3
"""Dependency-free mock of Palmier Pro's external MCP server, for behavioral evals.

It serves the Palmier tool names from docs/palmierpro-mcp-tool-map.md over MCP
Streamable HTTP (JSON responses), answers from a fixture project, and appends
every tool call to a JSONL trace. Grade the trace afterwards with trace_check.py.

    python3 tools/video/palmier_mock/mock_palmier.py --port 19790 \
        --fixture tools/video/palmier_mock/fixtures/talking-head.json --trace /tmp/trace.jsonl
    claude mcp add --transport http palmier-mock http://127.0.0.1:19790/mcp
    codex mcp add palmier-mock --url http://127.0.0.1:19790/mcp
    # run a prompt from prompts/palmierpro/ against the mock, then:
    python3 tools/video/palmier_mock/trace_check.py /tmp/trace.jsonl --profile first-pass

What it models (enough to catch contract violations, not Palmier's real behavior):
  - create_timeline(from=...) copies the active timeline, makes it active, and re-mints
    every clip and track ID, so reusing an old ID fails as stale
  - remove_words shifts later word indices; the trace records the transcript version
  - generation, export, and media deletion succeed (so the agent is not saved by an error)
  - set_project_settings is project-wide in the default fixture (settings_scope)
"""

from __future__ import annotations

import argparse
import copy
import itertools
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

TOOLS = [
    "manage_project", "get_timeline", "inspect_timeline", "create_timeline", "set_active_timeline",
    "set_project_settings", "manage_markers", "undo", "export_project", "manage_exports",
    "get_media", "inspect_media", "search_media", "import_media", "capture_frame", "organize_media",
    "manage_tracks", "manage_clip_links", "add_clips", "insert_clips", "move_clips", "remove_clips",
    "split_clips", "ripple_delete_ranges", "swap_clip_media", "set_clip_properties", "copy_clip_settings",
    "set_keyframes", "apply_layout", "sync_clips", "manage_multicam", "get_multicam", "change_cam",
    "get_transcript", "remove_words", "remove_silence", "detect_beats", "add_texts", "update_text",
    "add_captions", "inspect_color", "apply_color", "apply_effect", "manage_masks", "denoise_audio",
    "list_models", "generate_image", "generate_video", "generate_audio", "upscale_media", "send_feedback",
]
ID_FIELDS = {"clipId", "clipIds", "trackId", "trackIds", "timelineId"}
PROTOCOL_VERSION = "2025-06-18"


class ToolError(Exception):
    pass


class MockPalmier:
    def __init__(self, fixture: dict[str, Any], trace_path: Path | None = None):
        self.fixture = fixture
        self.trace_path = trace_path
        self.trace: list[dict[str, Any]] = []
        self._ids = itertools.count(1)
        self.timelines: dict[str, dict[str, Any]] = {}
        self.active = self._new_timeline("Main", fixture)
        self.markers: list[dict[str, Any]] = []
        self.exports: list[dict[str, Any]] = []

    # --- state ---------------------------------------------------------------
    def _mint(self, prefix: str) -> str:
        return f"{prefix}-{next(self._ids)}"

    def _new_timeline(self, name: str, source: dict[str, Any]) -> str:
        tid = self._mint("tl")
        track_ids = {t["key"]: self._mint("trk") for t in source["tracks"]}
        tracks = [{**t, "trackId": track_ids[t["key"]]} for t in source["tracks"]]
        clips = [{**c, "clipId": self._mint("clip"), "trackId": track_ids[c["track"]]} for c in source["clips"]]
        self.timelines[tid] = {"timelineId": tid, "name": name, "tracks": tracks, "clips": clips,
                               "words": copy.deepcopy(source["words"]), "transcript_version": 0}
        return tid

    @property
    def tl(self) -> dict[str, Any]:
        return self.timelines[self.active]

    def _check_ids(self, args: dict[str, Any]) -> None:
        live = {c["clipId"] for c in self.tl["clips"]} | {t["trackId"] for t in self.tl["tracks"]} | set(self.timelines)
        for key in ID_FIELDS & set(args):
            values = args[key] if isinstance(args[key], list) else [args[key]]
            stale = [v for v in values if v not in live]
            if stale:
                raise ToolError(f"unknown or stale {key}: {stale}; re-read get_timeline")

    # --- dispatch ------------------------------------------------------------
    def call(self, name: str, args: dict[str, Any] | None) -> dict[str, Any]:
        args = dict(args or {})
        entry: dict[str, Any] = {"seq": len(self.trace) + 1, "t": round(time.time(), 3), "tool": name, "args": args,
                                 "active_timeline": self.active, "transcript_version": self.tl["transcript_version"]}
        try:
            if name not in TOOLS:
                raise ToolError(f"unknown tool {name!r}")
            result = getattr(self, f"_t_{name}", self._generic)(name, args)
            entry["ok"] = True
        except ToolError as exc:
            result = {"error": str(exc)}
            entry["ok"] = False
            entry["error"] = str(exc)
        self.trace.append(entry)
        if self.trace_path:
            with self.trace_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        return result

    def _generic(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        self._check_ids(args)
        return {"ok": True, "tool": name, "note": "mock: accepted, no simulated effect"}

    def _t_get_timeline(self, _n: str, _a: dict[str, Any]) -> dict[str, Any]:
        f = self.fixture
        return {"timelineId": self.active, "name": self.tl["name"], "fps": f["fps"], "width": f["width"],
                "height": f["height"], "canGenerate": f.get("canGenerate", False),
                "projectSettingsScope": f.get("settings_scope", "project"),
                "timelines": [{"timelineId": k, "name": v["name"]} for k, v in self.timelines.items()],
                "tracks": [{k: t[k] for k in ("trackId", "type", "name")} for t in self.tl["tracks"]],
                "clips": [{k: c[k] for k in c if k not in {"key", "track"}} for c in self.tl["clips"]]}

    def _t_get_media(self, _n: str, _a: dict[str, Any]) -> dict[str, Any]:
        return {"media": self.fixture["media"]}

    def _t_create_timeline(self, _n: str, args: dict[str, Any]) -> dict[str, Any]:
        source = args.get("from")
        if source and source not in self.timelines:
            raise ToolError(f"unknown timeline {source!r}")
        base = self.timelines[source] if source else None
        src = {"tracks": [{k: t[k] for k in ("key", "type", "name")} for t in base["tracks"]],
               "clips": [{k: v for k, v in c.items() if k not in {"clipId", "trackId"}} for c in base["clips"]],
               "words": base["words"]} if base else {"tracks": [], "clips": [], "words": []}
        self.active = self._new_timeline(args.get("name") or "Copy", src)
        return {"timelineId": self.active, "note": "copied; all clip and track IDs are new"}

    def _t_set_active_timeline(self, _n: str, args: dict[str, Any]) -> dict[str, Any]:
        if args.get("timelineId") not in self.timelines:
            raise ToolError("unknown timelineId")
        self.active = args["timelineId"]
        return {"timelineId": self.active}

    def _t_get_transcript(self, _n: str, args: dict[str, Any]) -> dict[str, Any]:
        words = [{"index": i, **w} for i, w in enumerate(self.tl["words"])]
        if args.get("granularity") == "segments":
            return {"segments": [{"text": " ".join(w["text"] for w in words),
                                  "start": words[0]["start"] if words else 0, "end": words[-1]["end"] if words else 0}],
                    "version": self.tl["transcript_version"]}
        return {"words": words, "version": self.tl["transcript_version"]}

    def _t_remove_words(self, _n: str, args: dict[str, Any]) -> dict[str, Any]:
        indices = args.get("wordIndices") or args.get("indices") or []
        if not isinstance(indices, list) or not all(isinstance(i, int) for i in indices):
            raise ToolError("wordIndices must be a list of integers")
        bad = [i for i in indices if not 0 <= i < len(self.tl["words"])]
        if bad:
            raise ToolError(f"word index out of range: {bad}")
        self.tl["words"] = [w for i, w in enumerate(self.tl["words"]) if i not in set(indices)]
        self.tl["transcript_version"] += 1
        return {"removed": len(indices), "note": "later word indices have shifted; re-read get_transcript"}

    def _t_manage_markers(self, _n: str, args: dict[str, Any]) -> dict[str, Any]:
        self.markers.append(args)
        return {"markerId": self._mint("mk")}

    def _t_list_models(self, _n: str, _a: dict[str, Any]) -> dict[str, Any]:
        return {"models": [{"id": "mock-video-1", "kind": "video", "paid": True}]}

    def _t_export_project(self, _n: str, args: dict[str, Any]) -> dict[str, Any]:
        job = {"jobId": self._mint("job"), "mode": args.get("mode"), "status": "queued"}
        self.exports.append(job)
        return job

    def _t_manage_exports(self, _n: str, _a: dict[str, Any]) -> dict[str, Any]:
        return {"jobs": [{**j, "status": "completed"} for j in self.exports]}


# --- MCP Streamable HTTP transport (JSON responses only) ----------------------

def rpc(mock: MockPalmier, msg: dict[str, Any]) -> dict[str, Any] | None:
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:  # notification
        return None
    if method == "initialize":
        result: Any = {"protocolVersion": msg.get("params", {}).get("protocolVersion", PROTOCOL_VERSION),
                       "capabilities": {"tools": {}}, "serverInfo": {"name": "palmier-mock", "version": "0.1"}}
    elif method == "tools/list":
        result = {"tools": [{"name": n, "description": f"Mock Palmier {n}",
                             "inputSchema": {"type": "object", "additionalProperties": True}} for n in TOOLS]}
    elif method == "tools/call":
        params = msg.get("params", {})
        out = mock.call(params.get("name", ""), params.get("arguments"))
        result = {"content": [{"type": "text", "text": json.dumps(out)}], "isError": "error" in out}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve(mock: MockPalmier, port: int) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            if self.path.rstrip("/") != "/mcp":
                self.send_error(404)
                return
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            replies = [r for r in (rpc(mock, m) for m in (body if isinstance(body, list) else [body])) if r]
            if not replies:
                self.send_response(202)
                self.end_headers()
                return
            payload = json.dumps(replies if isinstance(body, list) else replies[0]).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def do_GET(self) -> None:  # noqa: N802  (no server-initiated stream)
            self.send_error(405)

        def log_message(self, *_args: Any) -> None:
            pass

    print(f"palmier-mock on http://127.0.0.1:{port}/mcp", file=sys.stderr)
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--fixture", type=Path, default=Path(__file__).parent / "fixtures/talking-head.json")
    p.add_argument("--trace", type=Path, required=True)
    p.add_argument("--port", type=int, default=19790)
    args = p.parse_args(argv)
    args.trace.write_text("", encoding="utf-8")
    serve(MockPalmier(json.loads(args.fixture.read_text(encoding="utf-8")), args.trace), args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
