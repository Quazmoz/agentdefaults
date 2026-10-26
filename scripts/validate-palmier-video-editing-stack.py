#!/usr/bin/env python3
"""Validate the Palmier Pro MCP video-editing stack.

Structural contracts that keep the stack single-sourced and safe, plus the behavioral
tests for the seam audit and the mock-MCP trace grader.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_INVARIANT = "skills/palmierpro-transcript-cuts-and-captions.md"
PALMIER_FILES = sorted(
    [*ROOT.glob("agents/palmierpro-*.md"), *ROOT.glob("skills/palmierpro-*.md"), *ROOT.glob("prompts/palmierpro/*.md"),
     ROOT / ".github/agents/palmierpro-video-editor.agent.md"]
)
BROAD_PROMPTS = ["quick-youtube-edit.md", "full-edit-pass.md", "youtube-short-from-long-form.md",
                 "story-assembly-from-project-media.md"]
DERIVED_PROMPTS = ["youtube-short-from-long-form.md"]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def main() -> int:
    failures: list[str] = []
    texts = {rel(p): p.read_text(encoding="utf-8") for p in PALMIER_FILES}

    # 1. The dialogue invariant has exactly one home.
    for name, text in texts.items():
        if name != CANONICAL_INVARIANT and "Never knowingly cut:" in text:
            failures.append(f"{name}: restates the Dialogue Boundary Invariant; point to {CANONICAL_INVARIANT}")
    if "Never knowingly cut:" not in texts.get(CANONICAL_INVARIANT, ""):
        failures.append(f"{CANONICAL_INVARIANT}: canonical invariant missing")
    if "## Seam Audit" not in texts.get(CANONICAL_INVARIANT, ""):
        failures.append(f"{CANONICAL_INVARIANT}: Seam Audit section missing")

    # 2. Broad prompts preserve the original; derived prompts run the settings scope check.
    for name in BROAD_PROMPTS:
        text = texts.get(f"prompts/palmierpro/{name}", "")
        if "create_timeline" not in text and "copy of the" not in text:
            failures.append(f"prompts/palmierpro/{name}: broad edit without timeline preservation")
    for name in DERIVED_PROMPTS:
        text = texts.get(f"prompts/palmierpro/{name}", "")
        if "scope check" not in text:
            failures.append(f"prompts/palmierpro/{name}: set_project_settings without the scope check")

    # 3. One transition default.
    for name, text in texts.items():
        if "dip-to-black at major scene changes" in text:
            failures.append(f"{name}: scene-change dips as a default; use the canonical Transitions table")
    if "This section is the canonical transition default" not in texts.get("skills/palmierpro-timeline-editing.md", ""):
        failures.append("skills/palmierpro-timeline-editing.md: canonical Transitions section missing")

    # 4. Grading specs stay out of the runtime stack; persona stays in the style profile.
    agent = texts.get("agents/palmierpro-mcp-video-editor-agent.md", "")
    stack = agent.split("## Recommended Stack", 1)[-1].split("##", 1)[0]
    if "Load at runtime" not in stack or "acceptance-tests.md\n" in stack.split("```")[1]:
        failures.append("agent Recommended Stack loads the acceptance tests at runtime")
    for name in (n for n in texts if n.startswith("prompts/palmierpro/")):
        if "Quinn" in texts[name]:
            failures.append(f"{name}: hardcoded creator identity; read config/video-editing/channel-style.md")

    # 5. Generated marketing prompts are current.
    result = subprocess.run([sys.executable, str(ROOT / "scripts/build-marketing-prompts.py"), "--check"],
                            cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        failures.append("marketing prompts are stale:\n" + result.stdout.strip())

    # 6. Behavioral tests.
    result = subprocess.run([sys.executable, str(ROOT / "tools/video/test_palmier_tools.py")],
                            cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        failures.append("tools/video/test_palmier_tools.py failed:\n" + result.stderr[-2000:])

    if failures:
        print("Palmier video-editing stack validation: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"Palmier video-editing stack validation: PASS ({len(PALMIER_FILES)} files, behavioral tests green)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
