#!/usr/bin/env python3
"""Render prompts/marketing/*.txt from prompts/marketing/src/.

The marketing prompts are pasted into coding agents running in *other* repositories,
so each output must stay a standalone .txt. Shared policy lives once in
src/_shared-guardrails.txt and is inlined wherever a source file has the line:

    {{include _shared-guardrails.txt}}

    python3 scripts/build-marketing-prompts.py          # write outputs
    python3 scripts/build-marketing-prompts.py --check  # exit 1 if any output is stale (CI)

Edit files in src/, never the generated .txt files.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "prompts/marketing/src"
OUT = ROOT / "prompts/marketing"
INCLUDE = re.compile(r"^\{\{include ([\w.-]+)\}\}$", re.M)


def render(path: Path) -> str:
    def sub(match: re.Match[str]) -> str:
        part = SRC / match.group(1)
        if not part.exists():
            raise SystemExit(f"{path.name}: include {match.group(1)} not found")
        return part.read_text(encoding="utf-8").rstrip("\n")
    return INCLUDE.sub(sub, path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true")
    args = p.parse_args(argv)
    stale = []
    for src in sorted(SRC.glob("*.txt")):
        if src.name.startswith("_"):
            continue
        text = render(src)
        out = OUT / src.name
        if args.check:
            if not out.exists() or out.read_text(encoding="utf-8") != text:
                stale.append(out.relative_to(ROOT))
        else:
            out.write_text(text, encoding="utf-8")
            print(f"wrote {out.relative_to(ROOT)}")
    if stale:
        print("stale generated prompts (run scripts/build-marketing-prompts.py):")
        for path in stale:
            print(f"  - {path}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
