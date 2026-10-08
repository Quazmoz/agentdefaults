#!/usr/bin/env python3
"""Transcribe one audio/video file with NVIDIA Parakeet and emit normalized timestamp JSON.

Output (schema 2), times in seconds relative to the start of the input file:

    {"schema": 2, "backend", "model", "audio", "duration", "text",
     "segments": [{"text", "start", "end", "confidence"?}],
     "words":    [{"text", "start", "end", "confidence"?}],
     "source_fingerprint": {"size_bytes", "mtime_ns"}}

Completed transcripts are reused when the source fingerprint, backend, and model
match. Model weights remain in the backend's normal persistent cache; this tool
does not download them into a per-project temporary folder.

`words` are real words for both backends: parakeet-mlx returns SentencePiece
subword tokens, which are merged here on their leading-space word marker.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any

NEMO_MODEL = "nvidia/parakeet-tdt-0.6b-v3"
MLX_MODEL = "mlx-community/parakeet-tdt-0.6b-v3"
# Model card: full attention handles ~24 min (A100 80GB); local attention up to ~3 h.
NEMO_FULL_ATTENTION_MAX_S = 20 * 60
MLX_CHUNK_S = 120.0  # parakeet-mlx CLI default; the Python API does not chunk unless asked.
MLX_OVERLAP_S = 15.0


def _num(value: Any) -> float:
    if hasattr(value, "item"):
        value = value.item()
    return round(float(value or 0.0), 3)


def _item(text: str, start: Any, end: Any, confidence: Any = None) -> dict[str, Any]:
    out: dict[str, Any] = {"text": text.strip(), "start": _num(start), "end": _num(end)}
    if confidence is not None:
        out["confidence"] = round(float(confidence), 3)
    return out


def _auto_backend() -> str:
    if platform.system() == "Darwin" and platform.machine().lower() in {"arm64", "aarch64"}:
        return "mlx"
    return "nemo"


def merge_subword_tokens(tokens: list[Any]) -> list[dict[str, Any]]:
    """Merge parakeet-mlx AlignedTokens (leading space starts a word) into words."""
    words: list[dict[str, Any]] = []
    for token in tokens:
        text = str(getattr(token, "text", ""))
        confidence = getattr(token, "confidence", None)
        if not text.strip():
            continue
        if words and not text[0].isspace():
            word = words[-1]
            word["text"] += text
            word["end"] = _num(getattr(token, "end", word["end"]))
            if confidence is not None and "confidence" in word:
                word["confidence"] = min(word["confidence"], round(float(confidence), 3))
            continue
        words.append(_item(text, getattr(token, "start", 0.0), getattr(token, "end", 0.0), confidence))
    return words


def normalize_mlx(result: Any) -> dict[str, Any]:
    segments, words = [], []
    for sentence in getattr(result, "sentences", None) or []:
        segments.append(
            _item(
                str(getattr(sentence, "text", "")),
                getattr(sentence, "start", 0.0),
                getattr(sentence, "end", 0.0),
                getattr(sentence, "confidence", None),
            )
        )
        words.extend(merge_subword_tokens(list(getattr(sentence, "tokens", None) or [])))
    return {"text": str(getattr(result, "text", "") or "").strip(), "segments": segments, "words": words}


def _nemo_items(items: Any, text_key: str) -> list[dict[str, Any]]:
    out = []
    for raw in items or []:
        if not isinstance(raw, dict) or "start" not in raw:
            continue  # offsets-only entries (pre-2.2 NeMo) carry no seconds
        out.append(_item(str(raw.get(text_key, raw.get("text", ""))), raw["start"], raw.get("end", raw["start"])))
    return out


def normalize_nemo(output: Any) -> dict[str, Any]:
    # NeMo 2.0/2.1 returned (best, all); beam search can return a list per file.
    if isinstance(output, tuple):
        output = output[0]
    hypothesis = output[0] if isinstance(output, list) else output
    if isinstance(hypothesis, list):
        hypothesis = hypothesis[0]
    stamps = getattr(hypothesis, "timestamp", None)
    if not isinstance(stamps, dict):
        raise SystemExit("NeMo returned no timestamp dict; nemo_toolkit[asr]>=2.2 is required.")
    return {
        "text": str(getattr(hypothesis, "text", "") or "").strip(),
        "segments": _nemo_items(stamps.get("segment"), "segment"),
        "words": _nemo_items(stamps.get("word"), "word"),
    }


def _transcribe_mlx(wav: Path, model_name: str, duration: float) -> dict[str, Any]:
    try:
        from parakeet_mlx import from_pretrained
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Parakeet MLX is not installed. On Apple Silicon run: python -m pip install -U 'parakeet-mlx>=0.5'"
        ) from exc
    model = from_pretrained(model_name)
    kwargs: dict[str, Any] = {}
    if duration > MLX_CHUNK_S:
        kwargs = {"chunk_duration": MLX_CHUNK_S, "overlap_duration": MLX_OVERLAP_S}
    return normalize_mlx(model.transcribe(str(wav), **kwargs))


def _transcribe_nemo(wav: Path, model_name: str, duration: float) -> dict[str, Any]:
    try:
        import nemo.collections.asr as nemo_asr
    except ModuleNotFoundError as exc:
        raise SystemExit(
            'NeMo ASR is not installed. Create a video venv and run: python -m pip install "nemo_toolkit[asr]>=2.2"'
        ) from exc
    model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)
    if duration > NEMO_FULL_ATTENTION_MAX_S:
        model.change_attention_model(self_attention_model="rel_pos_local_attn", att_context_size=[256, 256])
    return normalize_nemo(model.transcribe([str(wav)], timestamps=True))


def extract_wav(source: Path, wav: Path) -> float:
    """Decode any ffmpeg-readable input to 16 kHz mono PCM; return its duration in seconds."""
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required to extract 16 kHz mono audio (brew install ffmpeg / apt install ffmpeg).")
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
           "-map", "0:a:0", "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"ffmpeg could not extract an audio stream from {source}:\n{proc.stderr.strip()}")
    with wave.open(str(wav)) as handle:
        return handle.getnframes() / handle.getframerate()


def check_model(backend: str, model: str) -> None:
    if backend == "mlx" and model.startswith("nvidia/"):
        raise SystemExit(f"{model} is a NeMo checkpoint; the MLX backend needs an MLX conversion such as {MLX_MODEL}.")
    if backend == "nemo" and model.startswith("mlx-community/"):
        raise SystemExit(f"{model} is an MLX conversion; the NeMo backend needs a NeMo checkpoint such as {NEMO_MODEL}.")


def source_fingerprint(path: Path) -> dict[str, int]:
    """Fast invalidation for a source file, without reading multi-GB video into memory."""
    stat = path.stat()
    return {"size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def transcript_cache_hit(output: Path, audio: Path, backend: str, model: str,
                         fingerprint: dict[str, int]) -> bool:
    """Reuse only complete schema-2 output for this exact source and model.

    Legacy transcripts without a fingerprint are regenerated once. --force also
    overrides the cache when a remote checkpoint or runtime has been upgraded.
    """
    try:
        cached = json.loads(output.read_text(encoding="utf-8"))
        return (isinstance(cached, dict)
                and cached.get("schema") == 2
                and cached.get("backend") == backend
                and cached.get("model") == model
                and isinstance(cached.get("audio"), str)
                and Path(cached["audio"]).resolve() == audio.resolve()
                and cached.get("source_fingerprint") == fingerprint
                and isinstance(cached.get("text"), str)
                and isinstance(cached.get("words"), list)
                and isinstance(cached.get("segments"), list)
                and isinstance(cached.get("duration"), (int, float)))
    except (OSError, ValueError, TypeError):
        return False


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio/video with NVIDIA Parakeet (MLX or NeMo) to timestamp JSON.")
    parser.add_argument("audio", type=Path, help="Input media file; audio is extracted to 16 kHz mono with ffmpeg.")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path; defaults to stdout.")
    parser.add_argument("--backend", choices=("auto", "mlx", "nemo"), default="auto",
                        help="Parakeet runtime. auto prefers MLX on Apple Silicon and NeMo elsewhere.")
    parser.add_argument("--model", help="Override the backend's default Parakeet model identifier.")
    parser.add_argument("--force", action="store_true",
                        help="Regenerate a matching transcript after a model/runtime update or to correct an earlier result.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.audio.is_file():
        raise SystemExit(f"Input media not found: {args.audio}")
    backend = _auto_backend() if args.backend == "auto" else args.backend
    model = args.model or (MLX_MODEL if backend == "mlx" else NEMO_MODEL)
    check_model(backend, model)
    fingerprint = source_fingerprint(args.audio)
    if args.output and not args.force and transcript_cache_hit(args.output, args.audio, backend, model, fingerprint):
        print(f"reusing transcript: {args.output} (source, backend and model unchanged)", file=sys.stderr)
        return 0

    with tempfile.TemporaryDirectory(prefix="parakeet-") as tmp:
        wav = Path(tmp) / "audio.wav"
        duration = extract_wav(args.audio, wav)
        transcribe = _transcribe_mlx if backend == "mlx" else _transcribe_nemo
        try:
            body = transcribe(wav, model, duration)
        except (RuntimeError, ValueError, MemoryError) as exc:
            raise SystemExit(f"Parakeet {backend} transcription failed for {args.audio}: {exc}") from exc

    result = {"schema": 2, "backend": backend, "model": model, "audio": str(args.audio.resolve()),
              "source_fingerprint": fingerprint, "duration": round(duration, 3), **body}
    if not result["words"]:
        print(f"warning: no speech recognized in {args.audio}", file=sys.stderr)

    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if not args.output:
        sys.stdout.write(payload)
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Unique same-directory temporary files avoid collisions from concurrent runs.
    partial: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=args.output.parent,
                                         prefix=f".{args.output.name}.", suffix=".partial",
                                         delete=False) as handle:
            partial = Path(handle.name)
            handle.write(payload)
        os.replace(partial, args.output)  # never leave a truncated transcript behind
    finally:
        if partial is not None:
            partial.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
