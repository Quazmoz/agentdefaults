#!/usr/bin/env python3
"""Behavioral tests for tools/video: python3 tools/video/test_video_tools.py

Model-free: Parakeet backends are exercised with fake result objects. FFmpeg tests
render tiny synthetic media and are skipped when ffmpeg/ffprobe are absent.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

sys.path.insert(0, str(Path(__file__).resolve().parent))
import edl  # noqa: E402
import parakeet_transcribe as pt  # noqa: E402

HAVE_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def ff(*args: str) -> None:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def pixel(video: Path, t: float, x: int, y: int) -> tuple[int, int, int]:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", str(video), "-frames:v", "1",
                          "-vf", f"format=rgb24,crop=1:1:{x}:{y}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return raw[0], raw[1], raw[2]


class ParakeetNormalization(unittest.TestCase):
    def test_mlx_subword_tokens_merge_into_words(self):
        tokens = [NS(text=" Deploy", start=0.0, end=0.3, confidence=0.9), NS(text="ing", start=0.3, end=0.5, confidence=0.7),
                  NS(text=" now", start=0.6, end=0.8, confidence=1.0), NS(text=".", start=0.8, end=0.85, confidence=1.0)]
        result = NS(text=" Deploying now.", sentences=[NS(text=" Deploying now.", start=0.0, end=0.85, confidence=0.8, tokens=tokens)])
        out = pt.normalize_mlx(result)
        self.assertEqual([w["text"] for w in out["words"]], ["Deploying", "now."])
        self.assertEqual((out["words"][0]["start"], out["words"][0]["end"], out["words"][0]["confidence"]), (0.0, 0.5, 0.7))
        self.assertEqual(out["segments"][0]["text"], "Deploying now.")
        self.assertEqual(out["text"], "Deploying now.")

    def test_mlx_without_confidence_and_empty_result(self):
        out = pt.normalize_mlx(NS(text=" Hi", sentences=[NS(text=" Hi", start=0, end=0.2, tokens=[NS(text=" Hi", start=0, end=0.2)])]))
        self.assertNotIn("confidence", out["words"][0])
        self.assertEqual(pt.normalize_mlx(NS(text="", sentences=[])), {"text": "", "segments": [], "words": []})

    def test_nemo_list_tuple_and_offsets_only(self):
        stamps = {"word": [{"word": "hello", "start": 0.1, "end": 0.4, "start_offset": 1, "end_offset": 5},
                           {"word": "frames-only", "start_offset": 6, "end_offset": 9}],
                  "segment": [{"segment": "hello", "start": 0.1, "end": 0.4}]}
        hyp = NS(text="hello", timestamp=stamps)
        for output in ([hyp], ([hyp], [[hyp]]), [[hyp]]):
            out = pt.normalize_nemo(output)
            self.assertEqual(out["words"], [{"text": "hello", "start": 0.1, "end": 0.4}])
        with self.assertRaises(SystemExit):
            pt.normalize_nemo([NS(text="x", timestep={})])

    def test_backend_model_mismatch_is_rejected(self):
        with self.assertRaises(SystemExit):
            pt.check_model("mlx", pt.NEMO_MODEL)
        with self.assertRaises(SystemExit):
            pt.check_model("nemo", pt.MLX_MODEL)
        pt.check_model("mlx", pt.MLX_MODEL)


@unittest.skipUnless(HAVE_FFMPEG, "ffmpeg/ffprobe not installed")
class EdlPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="edl-test-"))
        t = cls.tmp
        (t / "raw").mkdir()
        # A: blue 1280x720@30 with tone in [0,2) and [3,6), silence in [2,3)
        ff("-f", "lavfi", "-i", "color=c=blue:s=1280x720:r=30:d=6",
           "-f", "lavfi", "-i", "aevalsrc='if(lt(mod(t,3),2),0.5*sin(2*PI*440*t),0)':s=48000:d=6",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(t / "raw/a.mp4"))
        # B: green 640x480@25, no audio stream
        ff("-f", "lavfi", "-i", "color=c=green:s=640x480:r=25:d=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(t / "raw/b.mp4"))
        ff("-f", "lavfi", "-i", "color=c=red:s=200x100", "-frames:v", "1", str(t / "card.png"))
        ff("-f", "lavfi", "-i", "sine=f=220:d=4:sample_rate=48000", str(t / "bed.wav"))
        words = [{"text": "hello", "start": 0.6, "end": 0.9}, {"text": "world.", "start": 1.0, "end": 1.4},
                 {"text": "cut", "start": 1.9, "end": 2.2}, {"text": "again", "start": 3.5, "end": 3.8}]
        (t / "a.json").write_text(json.dumps({"schema": 2, "words": words, "segments": []}))
        cls.edl = {
            "output": {"width": 640, "height": 360, "fps": 30, "sample_rate": 48000},
            "sources": {"a": {"path": "raw/a.mp4", "transcript": "a.json"}, "b": {"path": "raw/b.mp4"}},
            "segments": [{"source": "a", "start": 0.5, "end": 2.0, "note": "hook"},
                         {"source": "b", "start": 1.0, "end": 2.0},
                         {"source": "a", "start": "0:03.2", "end": "0:05.0"}],
            "overlays": [{"file": "card.png", "at": 0.5, "duration": 1.0, "box": [100, 100, 200, 100], "kind": "graphic"}],
            "audio": [{"file": "bed.wav", "at": 0, "gain_db": -30, "fade_out": 0.5, "license": "test tone, generated"}],
        }
        cls.edl_path = t / "edit.json"
        cls.edl_path.write_text(json.dumps(cls.edl))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def write(self, name: str, **changes) -> Path:
        path = self.tmp / name
        path.write_text(json.dumps({**self.edl, **changes}))
        return path

    def test_plan_timeline_and_boundary_warnings(self):
        plan = edl.build_plan(self.edl_path)
        self.assertEqual(plan["errors"], [])
        self.assertEqual([s["frames"] for s in plan["segments"]], [45, 30, 54])
        self.assertAlmostEqual(plan["duration"], 4.3, places=6)
        self.assertAlmostEqual(plan["segments"][2]["out_start"], 2.5, places=6)
        text = "\n".join(plan["warnings"])
        self.assertIn("inside word 'cut'", text)
        self.assertIn("no audio stream", text)
        self.assertIn("mixed resolution/fps", text)
        self.assertIn("lands in active audio", text)  # 0.5 s is mid-tone

    def test_plan_rejects_unlicensed_unsourced_and_out_of_range(self):
        bad = self.write("bad.json",
                         segments=[{"source": "a", "start": 5.0, "end": 7.0}, {"source": "zzz", "start": 0, "end": 1}],
                         overlays=[{"file": "card.png", "at": 0, "duration": 1, "kind": "evidence", "evidence": {"claim": "x"}}],
                         audio=[{"file": "bed.wav", "at": 0}])
        errors = "\n".join(edl.build_plan(bad, check_audio=False)["errors"])
        self.assertIn("exceeds source duration", errors)
        self.assertIn("unknown or missing source 'zzz'", errors)
        self.assertIn("needs a license", errors)
        bad2 = self.write("bad2.json", overlays=[{"file": "card.png", "at": 0, "duration": 1, "kind": "evidence",
                                                   "evidence": {"claim": "x"}}])
        self.assertIn("missing url, captured", "\n".join(edl.build_plan(bad2, check_audio=False)["errors"]))


    def test_privacy_gate_redactions_and_dense_review_frames(self):
        incomplete = self.write(
            "privacy-gap.json",
            privacy={"required": True, "visual_reviewed": True, "transcript_reviewed": True, "review_step": 0.5,
                     "reviews": [{"start": 0, "end": 2.0, "status": "clear", "method": "dense-frames+transcript"}]},
        )
        errors = "\n".join(edl.build_plan(incomplete, check_audio=False)["errors"])
        self.assertIn("privacy: reviews leave uncovered output", errors)

        privacy = {"required": True, "visual_reviewed": True, "transcript_reviewed": True, "review_step": 0.5,
                   "reviews": [{"start": 0, "end": 4.3, "status": "redacted", "method": "dense-frames+transcript"}]}
        redactions = [{"at": 0.2, "duration": 1.0, "mode": "black", "box": [100, 100, 100, 100],
                       "padding": 0, "label": "account identifier"}]
        path = self.write("privacy-good.json", privacy=privacy, redactions=redactions, overlays=[], audio=[])
        plan = edl.build_plan(path, check_audio=False)
        self.assertEqual(plan["errors"], [])
        out = self.tmp / "renders/privacy.mp4"
        self.assertEqual(edl.main(["render", str(path), "-o", str(out), "--preset", "ultrafast"]), 0)
        self.assertTrue(max(pixel(out, 0.6, 120, 120)) < 40)
        r, g, b = pixel(out, 0.6, 300, 200)
        self.assertTrue(b > 150 and r < 80, (r, g, b))
        r, g, b = pixel(out, 1.4, 120, 120)
        self.assertTrue(b > 150 and r < 80, (r, g, b))

        report = edl.qc(out, plan, self.tmp / "privacy-frames", privacy_step=1.0)
        self.assertEqual(report["issues"], [])
        self.assertEqual(report["privacy_step"], 1.0)
        self.assertGreaterEqual(report["privacy_frames_generated"], 5)

    def test_moving_privacy_redaction_uses_conservative_swept_region(self):
        privacy = {"required": True, "visual_reviewed": True, "transcript_reviewed": True, "review_step": 0.5,
                   "reviews": [{"start": 0, "end": 4.3, "status": "redacted", "method": "dense-frames+transcript"}]}
        moving = [{"at": 0.2, "duration": 1.0, "mode": "blur", "padding": 8, "label": "moving personal data",
                   "keyframes": [{"at": 0.0, "box": [100, 100, 20, 20]},
                                 {"at": 1.0, "box": [200, 100, 20, 20]}]}]
        path = self.write("privacy-moving.json", privacy=privacy, redactions=moving, overlays=[], audio=[])
        plan = edl.build_plan(path, check_audio=False)
        self.assertEqual(plan["errors"], [])
        self.assertEqual(plan["redactions"][0]["slices"][0]["box"], [92, 92, 136, 36])
        command = " ".join(edl.build_render_command(plan, self.tmp / "moving.mp4", 23, "ultrafast"))
        self.assertIn("boxblur=", command)

    def test_captions_remap_to_output_time_and_drop_partial_words(self):
        cues = edl.caption_cues(edl.build_plan(self.edl_path, check_audio=False), 42, 5.0)
        self.assertEqual([c[2] for c in cues], ["hello world.", "again"])
        self.assertAlmostEqual(cues[0][0], 0.1, places=3)
        self.assertAlmostEqual(cues[1][0], 2.8, places=3)
        self.assertIn("00:00:00,100 --> 00:00:00,900\nhello world.", edl.srt(cues))

    def test_render_composites_and_passes_qc(self):
        out = self.tmp / "renders/review.mp4"
        main_rc = edl.main(["render", str(self.edl_path), "-o", str(out), "--preset", "ultrafast"])
        self.assertEqual(main_rc, 0)
        self.assertTrue(out.is_file() and not (self.tmp / "renders/review.partial.mp4").exists())
        r, g, b = pixel(out, 0.2, 200, 150)
        self.assertTrue(b > 150 and r < 80, (r, g, b))         # source A before the overlay
        r, g, b = pixel(out, 1.0, 200, 150)
        self.assertTrue(r > 150 and g < 80 and b < 80, (r, g, b))  # overlay box
        r, g, b = pixel(out, 2.0, 320, 180)
        self.assertTrue(g > 100 and r < 80, (r, g, b))         # source B, overlay ended
        r, g, b = pixel(out, 2.0, 2, 2)
        self.assertTrue(max(r, g, b) < 40, (r, g, b))          # 4:3 source pillarboxed into 16:9
        report = edl.qc(out, json.loads((self.tmp / "renders/review.mp4.json").read_text()), self.tmp / "frames")
        self.assertEqual(report["issues"], [])
        self.assertEqual(report["probe"]["audio"][0]["sample_rate"], 48000)
        self.assertGreaterEqual(len(report["frames"]), 4)
        self.assertIsNotNone(report["integrated_lufs"])
        # Audio edits land on the video segment boundaries: B (silent source) occupies 1.5-2.5 s.
        gaps = edl.silences(out, -35, 0.5)
        self.assertTrue(any(abs(a - 1.5) < 0.05 and abs(b - 2.5) < 0.05 for a, b in gaps), gaps)

    def test_alpha_mov_overlay_keeps_transparency(self):
        # HyperFrames `render --format mov` emits ProRes 4444 with alpha; left half opaque red, right half clear.
        mov = self.tmp / "alpha.mov"
        ff("-f", "lavfi", "-i", "color=c=red:s=640x360:r=30:d=1,format=rgba,geq=r=255:g=0:b=0:a='if(lt(X,320),255,0)'",
           "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", str(mov))
        path = self.write("alpha.json", overlays=[{"file": "alpha.mov", "at": 3.0, "kind": "graphic"}], audio=[])
        out = self.tmp / "renders/alpha.mp4"
        self.assertEqual(edl.main(["render", str(path), "-o", str(out), "--preset", "ultrafast"]), 0)
        r, g, b = pixel(out, 3.5, 100, 180)
        self.assertTrue(r > 150 and b < 80, (r, g, b))
        r, g, b = pixel(out, 3.5, 500, 180)
        self.assertTrue(b > 150 and r < 80, (r, g, b))

    def test_segment_at_source_end_with_loudnorm_keeps_exact_length(self):
        # Regression: a segment past the last video frame (video track shorter than audio, as recorders
        # often write) lost a frame, and loudnorm added an audio tail.
        ff("-f", "lavfi", "-i", "color=c=blue:s=1280x720:r=30:d=3", "-f", "lavfi", "-i", "sine=f=440:d=3.05:sample_rate=48000",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(self.tmp / "raw/c.mp4"))
        path = self.write("eof.json", output={**self.edl["output"], "loudness": -14}, overlays=[], audio=[],
                          sources={"a": self.edl["sources"]["a"], "c": {"path": "raw/c.mp4"}},
                          segments=[{"source": "a", "start": 0.5, "end": 2.0}, {"source": "c", "start": 1.0, "end": 3.03}])
        out = self.tmp / "renders/eof.mp4"
        self.assertEqual(edl.main(["render", str(path), "-o", str(out), "--preset", "ultrafast"]), 0)
        streams = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,nb_frames,duration",
                                             "-of", "json", str(out)], capture_output=True, check=True).stdout)["streams"]
        video = next(s for s in streams if s["codec_type"] == "video")
        audio = next(s for s in streams if s["codec_type"] == "audio")
        self.assertEqual(int(video["nb_frames"]), 45 + 61)
        self.assertLess(abs(float(audio["duration"]) - float(video["duration"])), 0.03)

    def test_render_refuses_to_overwrite_source(self):
        plan = edl.build_plan(self.edl_path, check_audio=False)
        with self.assertRaises(SystemExit):
            edl.render(plan, self.tmp / "raw/a.mp4", 18, "ultrafast")

    def test_silences_and_transcriber_audio_extraction(self):
        gaps = edl.silences(self.tmp / "raw/a.mp4", -35, 0.25)
        self.assertTrue(any(abs(a - 2.0) < 0.1 and abs(b - 3.0) < 0.1 for a, b in gaps), gaps)
        wav = self.tmp / "x.wav"
        self.assertAlmostEqual(pt.extract_wav(self.tmp / "raw/a.mp4", wav), 6.0, delta=0.1)
        with self.assertRaises(SystemExit):
            pt.extract_wav(self.tmp / "raw/b.mp4", wav)  # no audio stream


if __name__ == "__main__":
    unittest.main(verbosity=2)
