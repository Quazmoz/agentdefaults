#!/usr/bin/env python3
"""Transcribe one audio file with NVIDIA Parakeet and emit timestamped JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_MODEL = "nvidia/parakeet-tdt-0.6b-v3"


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe audio with NVIDIA Parakeet using NeMo timestamps."
    )
    parser.add_argument("audio", type=Path, help="Input audio file (16 kHz mono WAV recommended).")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path; defaults to stdout.")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"NeMo/HF model name (default: {DEFAULT_MODEL}).")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.audio.is_file():
        raise SystemExit(f"Input audio not found: {args.audio}")

    try:
        import nemo.collections.asr as nemo_asr
    except ModuleNotFoundError as exc:
        raise SystemExit(
            'NeMo ASR is not installed. Create a video venv and run: '
            'python -m pip install "nemo_toolkit[asr]"'
        ) from exc

    model = nemo_asr.models.ASRModel.from_pretrained(model_name=args.model)
    hypothesis = model.transcribe([str(args.audio)], timestamps=True)[0]
    stamps = getattr(hypothesis, "timestamp", {}) or {}

    result = {
        "model": args.model,
        "audio": str(args.audio),
        "text": getattr(hypothesis, "text", ""),
        "segments": _plain(stamps.get("segment", [])),
        "words": _plain(stamps.get("word", [])),
    }

    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
