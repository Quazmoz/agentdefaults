#!/usr/bin/env python3
"""Transcribe one audio file with NVIDIA Parakeet and emit normalized timestamp JSON."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path
from typing import Any

NEMO_MODEL = "nvidia/parakeet-tdt-0.6b-v3"
MLX_MODEL = "mlx-community/parakeet-tdt-0.6b-v3"


def _plain(value: Any) -> Any:
    """Convert tensor/numpy scalar-like values into JSON-safe Python values."""
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass
    return value


def _auto_backend() -> str:
    if platform.system() == "Darwin" and platform.machine().lower() in {"arm64", "aarch64"}:
        return "mlx"
    return "nemo"


def _normalize_mlx_item(item: Any) -> dict[str, Any]:
    return {
        "text": str(getattr(item, "text", "")).strip(),
        "start": float(getattr(item, "start", 0.0)),
        "end": float(getattr(item, "end", 0.0)),
        "duration": float(getattr(item, "duration", 0.0)),
        "confidence": _plain(getattr(item, "confidence", None)),
    }


def _transcribe_mlx(audio: Path, model_name: str) -> dict[str, Any]:
    try:
        from parakeet_mlx import from_pretrained
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Parakeet MLX is not installed. On Apple Silicon run: "
            "python -m pip install -U parakeet-mlx"
        ) from exc

    model = from_pretrained(model_name)
    result = model.transcribe(str(audio))
    segments = []
    words = []
    for sentence in getattr(result, "sentences", []):
        segment = _normalize_mlx_item(sentence)
        if segment["confidence"] is None:
            segment.pop("confidence")
        segments.append(segment)
        for token in getattr(sentence, "tokens", []):
            word = _normalize_mlx_item(token)
            if word["confidence"] is None:
                word.pop("confidence")
            words.append(word)

    return {
        "backend": "mlx",
        "model": model_name,
        "audio": str(audio),
        "text": getattr(result, "text", ""),
        "segments": segments,
        "words": words,
    }


def _normalize_nemo_items(items: list[Any], text_key: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw in items:
        item = _plain(raw)
        if not isinstance(item, dict):
            continue
        start = float(item.get("start", 0.0))
        end = float(item.get("end", start))
        normalized.append(
            {
                "text": str(item.get(text_key, item.get("text", ""))).strip(),
                "start": start,
                "end": end,
                "duration": max(0.0, end - start),
            }
        )
    return normalized


def _transcribe_nemo(audio: Path, model_name: str) -> dict[str, Any]:
    try:
        import nemo.collections.asr as nemo_asr
    except ModuleNotFoundError as exc:
        raise SystemExit(
            'NeMo ASR is not installed. Create a video venv and run: '
            'python -m pip install "nemo_toolkit[asr]"'
        ) from exc

    model = nemo_asr.models.ASRModel.from_pretrained(model_name=model_name)
    hypothesis = model.transcribe([str(audio)], timestamps=True)[0]
    stamps = getattr(hypothesis, "timestamp", {}) or {}

    return {
        "backend": "nemo",
        "model": model_name,
        "audio": str(audio),
        "text": getattr(hypothesis, "text", ""),
        "segments": _normalize_nemo_items(stamps.get("segment", []), "segment"),
        "words": _normalize_nemo_items(stamps.get("word", []), "word"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio with NVIDIA Parakeet using MLX or NeMo timestamps."
    )
    parser.add_argument("audio", type=Path, help="Input audio file (16 kHz mono WAV recommended).")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path; defaults to stdout.")
    parser.add_argument(
        "--backend",
        choices=("auto", "mlx", "nemo"),
        default="auto",
        help="Parakeet runtime. auto prefers MLX on Apple Silicon and NeMo elsewhere.",
    )
    parser.add_argument(
        "--model",
        help="Override the backend's default Parakeet model identifier.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.audio.is_file():
        raise SystemExit(f"Input audio not found: {args.audio}")

    backend = _auto_backend() if args.backend == "auto" else args.backend
    if backend == "mlx":
        result = _transcribe_mlx(args.audio, args.model or MLX_MODEL)
    else:
        result = _transcribe_nemo(args.audio, args.model or NEMO_MODEL)

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
