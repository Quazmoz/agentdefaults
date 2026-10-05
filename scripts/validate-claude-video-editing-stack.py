#!/usr/bin/env python3
"""Validate the Claude Code Local Video Editing stack and routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

STACK_NAME = "Claude Code Local Video Editing"
STACK = {
    "quickstart": "docs/quickstarts/claude-video-editing.md",
    "agent": "agents/claude-code-video-editor-agent.md",
    "skill": "skills/claude-code-video-editing.md",
    "prompt": "prompts/video-editing/quick-youtube-edit.md",
    "acceptance_tests": "docs/claude-video-editing-acceptance-tests.md",
    "wrapper": ".claude/skills/youtube-edit/SKILL.md",
    "style": "config/video-editing/channel-style.md",
    "transcriber": "tools/video/parakeet_transcribe.py",
}

ROUTING_FILES = [
    "README.md",
    "INDEX.md",
    "CLAUDE.md",
    ".claude/README.md",
    "docs/quickstarts/claude.md",
    "skills/README.md",
    "config/README.md",
    "prompts/README.md",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, Any]:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def require_terms(text: str, terms: list[str], label: str, failures: list[str]) -> None:
    lowered = text.lower()
    for term in terms:
        if term.lower() not in lowered:
            failures.append(f"{label}: missing required concept {term!r}")


def check_required_files(failures: list[str]) -> None:
    required = set(STACK.values()) | set(ROUTING_FILES) | {
        "agentdefaults.manifest.json",
        "scripts/validate-agentdefaults.py",
        "scripts/validate-claude-video-editing-stack.py",
    }
    for path in sorted(required):
        if not (ROOT / path).is_file():
            failures.append(f"missing Claude video-editing stack file: {path}")


def check_manifest(failures: list[str]) -> None:
    manifest = load_json("agentdefaults.manifest.json")
    stacks = manifest.get("featured_stacks", [])
    stack = next(
        (
            item
            for item in stacks
            if isinstance(item, dict) and item.get("name") == STACK_NAME
        ),
        None,
    )
    if stack is None:
        failures.append(f"manifest missing stack: {STACK_NAME}")
        return

    for field in ("quickstart", "agent", "acceptance_tests", "wrapper"):
        expected = STACK[field]
        if stack.get(field) != expected:
            failures.append(f"manifest {STACK_NAME} {field} must be {expected!r}")
    if stack.get("skills") != [STACK["skill"]]:
        failures.append(f"manifest {STACK_NAME} must reference only {STACK['skill']}")
    if stack.get("prompts") != [STACK["prompt"]]:
        failures.append(f"manifest {STACK_NAME} must reference only {STACK['prompt']}")


def check_routing(failures: list[str]) -> None:
    agent_ref = STACK["agent"]
    skill_ref = STACK["skill"]
    quickstart_ref = STACK["quickstart"]
    wrapper_ref = STACK["wrapper"]

    claude = read("CLAUDE.md")
    for ref in (agent_ref, skill_ref, quickstart_ref, wrapper_ref):
        if ref not in claude:
            failures.append(f"CLAUDE.md: missing local video-editing route {ref}")

    index = read("INDEX.md")
    for ref in (quickstart_ref,):
        if ref not in index:
            failures.append(f"INDEX.md: missing local video-editing reference {ref}")

    readme = read("README.md")
    if quickstart_ref not in readme:
        failures.append(f"README.md: missing local video-editing reference {quickstart_ref}")

    skills_readme = read("skills/README.md")
    for ref in (agent_ref, STACK["style"]):
        relative = "../" + ref
        if relative not in skills_readme:
            failures.append(f"skills/README.md: missing local video-editing reference {relative}")

    claude_readme = read(".claude/README.md")
    if "skills/youtube-edit/SKILL.md" not in claude_readme:
        failures.append(".claude/README.md: missing native youtube-edit skill reference")


def check_native_skill(failures: list[str]) -> None:
    text = read(STACK["wrapper"])
    require_terms(
        text,
        [
            "name: youtube-edit",
            STACK["agent"],
            STACK["skill"],
            STACK["style"],
            "/youtube-edit",
            "Parakeet",
            "HyperFrames",
            "FFmpeg",
        ],
        STACK["wrapper"],
        failures,
    )


def check_agent_and_skill(failures: list[str]) -> None:
    agent = read(STACK["agent"])
    skill = read(STACK["skill"])

    require_terms(
        agent,
        [
            "NVIDIA Parakeet",
            "HyperFrames",
            "FFmpeg",
            "ffprobe",
            "source-manifest.md",
            "browser",
            "Tella",
            "Epidemic Sound",
            "raw media immutable",
            "timestamp",
            "explicitly ask",
            "black-frame",
            "silence",
        ],
        STACK["agent"],
        failures,
    )
    require_terms(
        skill,
        [
            "Parakeet timestamp transcript",
            "HyperFrames",
            "FFmpeg",
            "source URL",
            "licensed",
            "channel-style.md",
            "explicitly asks",
            "raw footage",
            "black sections",
        ],
        STACK["skill"],
        failures,
    )


def check_transcriber(failures: list[str]) -> None:
    text = read(STACK["transcriber"])
    require_terms(
        text,
        [
            "nvidia/parakeet-tdt-0.6b-v3",
            "mlx-community/parakeet-tdt-0.6b-v3",
            "parakeet_mlx",
            "nemo.collections.asr",
            "timestamps=True",
            "--backend",
            '"segments"',
            '"words"',
        ],
        STACK["transcriber"],
        failures,
    )


def check_acceptance_tests(failures: list[str]) -> None:
    text = read(STACK["acceptance_tests"])
    case_count = text.count("\n## AC-")
    if case_count < 12:
        failures.append(
            f"{STACK['acceptance_tests']}: expected at least 12 acceptance cases, found {case_count}"
        )
    require_terms(
        text,
        [
            "Raw Media Is Preserved",
            "Real Timestamp Transcript",
            "Transcript Is Not Treated As Acoustic Truth",
            "Evidence B-roll Is Source-Traceable",
            "HyperFrames Validation Runs",
            "Licensed Audio Boundary",
            "Feedback Persistence Requires Explicit Intent",
            "Final QC Is Truthful",
        ],
        STACK["acceptance_tests"],
        failures,
    )


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)

    if not failures:
        try:
            check_manifest(failures)
            check_routing(failures)
            check_native_skill(failures)
            check_agent_and_skill(failures)
            check_transcriber(failures)
            check_acceptance_tests(failures)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            failures.append(str(exc))

    print("Claude Code Local Video Editing stack validation")
    print("================================================")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    print("PASS: required stack files")
    print("PASS: manifest registration")
    print("PASS: Claude and repository routing")
    print("PASS: native /youtube-edit skill contract")
    print("PASS: Parakeet, HyperFrames, FFmpeg, evidence, licensing, and style-learning invariants")
    print("PASS: timestamped Parakeet helper contract")
    print("PASS: acceptance-test coverage")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
