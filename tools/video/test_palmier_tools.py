#!/usr/bin/env python3
"""Behavioral tests for the Palmier seam audit and the mock-MCP eval harness.

    python3 tools/video/test_palmier_tools.py

Model-free and network-free. The FFmpeg level check is exercised only when ffmpeg is present.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "palmier_mock"))
import palmier_seams as ps  # noqa: E402
import mock_palmier as mp  # noqa: E402
import trace_check as tc  # noqa: E402

FIXTURE = json.loads((HERE / "palmier_mock/fixtures/talking-head.json").read_text(encoding="utf-8"))
HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))

FCPXML = """<?xml version="1.0" encoding="UTF-8"?>
<fcpxml version="1.10">
  <resources>
    <format id="r1" frameDuration="1/30s" width="1920" height="1080"/>
    <asset id="r2" name="cam"><media-rep kind="original-media" src="file://{media}"/></asset>
  </resources>
  <library><event><project name="QC"><sequence format="r1"><spine>
    {clips}
  </spine></sequence></project></event></library>
</fcpxml>
"""


def clip(offset: str, start: str, duration: str) -> str:
    return f'<asset-clip ref="r2" offset="{offset}" start="{start}" duration="{duration}"/>'


class SeamAudit(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        (self.dir / "transcripts").mkdir()
        words = [{"text": "deploy", "start": 1.0, "end": 1.5}, {"text": "it", "start": 1.6, "end": 1.8},
                 {"text": "now", "start": 3.0, "end": 3.4}, {"text": "today", "start": 3.5, "end": 4.0}]
        (self.dir / "transcripts/cam.json").write_text(json.dumps({"words": words}), encoding="utf-8")
        self.media = self.dir / "cam.mov"

    def write(self, *clips: str) -> Path:
        path = self.dir / "qc.fcpxml"
        path.write_text(FCPXML.format(media=self.media, clips="\n".join(clips)), encoding="utf-8")
        return path

    def run_audit(self, path: Path):
        return ps.audit(path, self.dir / "transcripts", check_audio=False)

    def test_rational_time(self):
        self.assertAlmostEqual(float(ps.fcp_time("1001/30000s")), 0.033366, places=5)
        self.assertEqual(ps.fcp_time("10s"), 10)

    def test_clean_seam_passes(self):
        # out at 2.2s (0.4s after "it"), in at 2.8s (0.2s before "now")
        report = self.run_audit(self.write(clip("0s", "0s", "11/5s"), clip("11/5s", "14/5s", "6/5s")))
        self.assertEqual(report["seam_count"], 1)
        self.assertEqual(report["errors"], 0)
        self.assertEqual(report["warnings"], 0)
        self.assertEqual(report["seams"][0]["timeline_frame"], 66)

    def test_cut_inside_word_is_error(self):
        # out at 1.3s, inside "deploy"
        report = self.run_audit(self.write(clip("0s", "0s", "13/10s"), clip("13/10s", "14/5s", "1s")))
        self.assertEqual(report["errors"], 1)
        self.assertIn("inside 'deploy'", report["seams"][0]["errors"][0])

    def test_tight_handle_warns(self):
        # in at 2.95s, 0.05s before "now" starts
        report = self.run_audit(self.write(clip("0s", "0s", "11/5s"), clip("11/5s", "59/20s", "1s")))
        self.assertEqual(report["errors"], 0)
        self.assertTrue(any("attack may be clipped" in w for w in report["seams"][0]["warnings"]))

    def test_repeated_content_is_error(self):
        report = self.run_audit(self.write(clip("0s", "0s", "3s"), clip("3s", "2s", "1s")))
        self.assertTrue(any("content repeats" in e for e in report["seams"][0]["errors"]))

    def test_cli_exit_codes(self):
        bad = self.write(clip("0s", "0s", "13/10s"), clip("13/10s", "14/5s", "1s"))
        self.assertEqual(ps.main([str(bad), "--transcripts", str(self.dir / "transcripts"), "--no-audio"]), 1)
        self.assertEqual(ps.main([str(self.dir / "missing.fcpxml")]), 2)

    @unittest.skipUnless(HAVE_FFMPEG, "ffmpeg not installed")
    def test_level_check_flags_active_audio(self):
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                        "sine=frequency=440:duration=5", str(self.media)], check=True)
        report = ps.audit(self.write(clip("0s", "0s", "11/5s"), clip("11/5s", "14/5s", "1s")),
                          self.dir / "transcripts", check_audio=True)
        self.assertTrue(any("active audio" in w for w in report["seams"][0]["warnings"]))


def good_first_pass(mock: mp.MockPalmier) -> None:
    original = mock.call("get_timeline", {})["timelineId"]
    mock.call("get_media", {})
    mock.call("create_timeline", {"from": original, "name": "YouTube Fast Cut"})
    mock.call("get_timeline", {})
    mock.call("get_transcript", {"granularity": "segments"})
    mock.call("get_transcript", {})
    mock.call("remove_words", {"wordIndices": [0]})
    mock.call("get_transcript", {})
    mock.call("remove_words", {"wordIndices": [5]})
    mock.call("get_transcript", {})
    mock.call("export_project", {"mode": "fcpxml", "outputPath": "/tmp/qc.fcpxml"})
    mock.call("inspect_timeline", {"frame": 0})


class MockServer(unittest.TestCase):
    def test_copy_remints_ids_and_stale_ids_fail(self):
        mock = mp.MockPalmier(json.loads(json.dumps(FIXTURE)))
        state = mock.call("get_timeline", {})
        old_clip = state["clips"][0]["clipId"]
        mock.call("create_timeline", {"from": state["timelineId"]})
        result = mock.call("set_clip_properties", {"clipId": old_clip, "volume": 0.5})
        self.assertIn("stale", result["error"])
        new_clip = mock.call("get_timeline", {})["clips"][0]["clipId"]
        self.assertNotEqual(old_clip, new_clip)
        self.assertTrue(mock.call("set_clip_properties", {"clipId": new_clip, "volume": 0.5})["ok"])

    def test_remove_words_shifts_indices(self):
        mock = mp.MockPalmier(json.loads(json.dumps(FIXTURE)))
        mock.call("remove_words", {"wordIndices": [0]})
        words = mock.call("get_transcript", {})["words"]
        self.assertEqual(words[0]["text"], "so")
        self.assertEqual(mock.call("get_transcript", {})["version"], 1)

    def test_http_transport_round_trip(self):
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # loopback; ignore proxy env
        mock = mp.MockPalmier(json.loads(json.dumps(FIXTURE)))
        server = threading.Thread(target=mp.serve, args=(mock, 19797), daemon=True)
        server.start()
        import time
        for _ in range(50):
            try:
                req = urllib.request.Request("http://127.0.0.1:19797/mcp", method="POST",
                                             data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).encode(),
                                             headers={"Content-Type": "application/json"})
                tools = json.loads(opener.open(req, timeout=2).read())["result"]["tools"]
                break
            except OSError:
                time.sleep(0.05)
        else:
            self.fail("mock server did not start")
        self.assertIn("remove_words", {t["name"] for t in tools})
        call = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_timeline", "arguments": {}}}
        req = urllib.request.Request("http://127.0.0.1:19797/mcp", method="POST", data=json.dumps(call).encode(),
                                     headers={"Content-Type": "application/json"})
        body = json.loads(opener.open(req, timeout=2).read())
        self.assertEqual(json.loads(body["result"]["content"][0]["text"])["fps"], 30)
        self.assertEqual(mock.trace[-1]["tool"], "get_timeline")


class TraceCheck(unittest.TestCase):
    def mock(self) -> mp.MockPalmier:
        return mp.MockPalmier(json.loads(json.dumps(FIXTURE)))

    def test_good_first_pass_passes(self):
        mock = self.mock()
        good_first_pass(mock)
        result = tc.check(mock.trace, "first-pass")
        self.assertEqual(result["fail"], [])
        self.assertEqual(result["warn"], [])

    def test_editing_original_fails(self):
        mock = self.mock()
        mock.call("get_timeline", {})
        mock.call("get_media", {})
        mock.call("get_transcript", {})
        mock.call("remove_words", {"wordIndices": [0]})
        mock.call("get_transcript", {})
        mock.call("inspect_timeline", {})
        fails = tc.check(mock.trace, "first-pass")["fail"]
        self.assertTrue(any(f.startswith("preserve-original") for f in fails))

    def test_stale_indices_fail(self):
        mock = self.mock()
        good_first_pass(mock)
        mock.call("remove_words", {"wordIndices": [1]})
        mock.call("remove_words", {"wordIndices": [1]})
        fails = tc.check(mock.trace, "first-pass")["fail"]
        self.assertTrue(any(f.startswith("index-refresh") for f in fails))

    def test_unapproved_generation_and_export_fail(self):
        mock = self.mock()
        good_first_pass(mock)
        mock.call("generate_video", {"prompt": "b-roll"})
        mock.call("export_project", {"mode": "video"})
        fails = tc.check(mock.trace, "first-pass")["fail"]
        self.assertTrue(any(f.startswith("paid-gate") for f in fails))
        self.assertTrue(any(f.startswith("export-gate") for f in fails))
        self.assertFalse(any(f.startswith("export-gate") for f in
                             tc.check(mock.trace, "first-pass", export_requested=True)["fail"]))

    def test_short_must_not_change_project_wide_settings(self):
        mock = self.mock()
        original = mock.call("get_timeline", {})["timelineId"]
        mock.call("get_media", {})
        mock.call("create_timeline", {"from": original, "name": "Short"})
        mock.call("get_timeline", {})
        mock.call("set_project_settings", {"aspectRatio": "9:16"})
        mock.call("add_captions", {})
        mock.call("inspect_timeline", {})
        fails = tc.check(mock.trace, "short")["fail"]
        self.assertTrue(any(f.startswith("project-settings") for f in fails))
        self.assertFalse(any(f.startswith("project-settings") for f in
                             tc.check(mock.trace, "short", settings_scope="timeline")["fail"]))

    def test_long_form_captions_and_retry_loops_fail(self):
        mock = self.mock()
        good_first_pass(mock)
        mock.call("add_captions", {})
        for _ in range(3):
            mock.call("set_clip_properties", {"clipId": "clip-does-not-exist"})
        mock.call("inspect_timeline", {})
        fails = tc.check(mock.trace, "first-pass")["fail"]
        self.assertTrue(any(f.startswith("profile-scope") for f in fails))
        self.assertTrue(any(f.startswith("bounded-retry") for f in fails))

    def test_unaudited_speech_cuts_warn(self):
        mock = self.mock()
        original = mock.call("get_timeline", {})["timelineId"]
        mock.call("get_media", {})
        mock.call("create_timeline", {"from": original})
        mock.call("get_timeline", {})
        mock.call("get_transcript", {})
        mock.call("remove_words", {"wordIndices": [0]})
        mock.call("get_transcript", {})
        mock.call("inspect_timeline", {})
        result = tc.check(mock.trace, "first-pass")
        self.assertEqual(result["fail"], [])
        self.assertTrue(result["warn"][0].startswith("seam-audit"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
