#!/usr/bin/env python3
"""Validate AgentDefaults cross-tool entrypoints and engineering routing integrity."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

ENGINEERING_STACKS = {
    "Principal DevOps Engineering": {
        "agent": "agents/principal-devops-engineer.md",
        "skill": "skills/production-devops-engineering.md",
        "quickstart": "docs/quickstarts/principal-devops-engineer.md",
        "wrapper": ".github/agents/principal-devops-engineer.agent.md",
    },
    "Principal AI Engineering": {
        "agent": "agents/principal-ai-engineer.md",
        "skill": "skills/production-ai-engineering.md",
        "quickstart": "docs/quickstarts/principal-ai-engineer.md",
        "wrapper": ".github/agents/principal-ai-engineer.agent.md",
    },
    "Principal AI and DevOps Engineering": {
        "agent": "agents/principal-ai-devops-engineer.md",
        "skill": "skills/production-ai-devops-engineering.md",
        "quickstart": "docs/quickstarts/principal-ai-devops-engineer.md",
        "wrapper": ".github/agents/principal-ai-devops-engineer.agent.md",
    },
}

REQUIRED_FILES = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "ENGINEERING_AGENTS_INDEX.md",
    "INDEX.md",
    "agentdefaults.manifest.json",
    "docs/quickstarts/codex.md",
    "docs/quickstarts/claude.md",
    "docs/tool-integration-guide.md",
    ".github/copilot-instructions.md",
    "scripts/validate-agentdefaults.py",
    "scripts/validate-cross-tool-routing.py",
}
for stack in ENGINEERING_STACKS.values():
    REQUIRED_FILES.update(stack.values())


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_terms(text: str, terms: Iterable[str], label: str, failures: list[str]) -> None:
    for term in terms:
        if term not in text:
            failures.append(f"{label} missing required reference: {term}")


def check_files(failures: list[str]) -> None:
    for path in sorted(REQUIRED_FILES):
        if not (ROOT / path).is_file():
            failures.append(f"missing required cross-tool file: {path}")


def check_entrypoints(failures: list[str]) -> None:
    agents = read("AGENTS.md")
    claude = read("CLAUDE.md")
    engineering = read("ENGINEERING_AGENTS_INDEX.md")
    codex = read("docs/quickstarts/codex.md")
    claude_quickstart = read("docs/quickstarts/claude.md")
    tool_guide = read("docs/tool-integration-guide.md")

    canonical_agents = [stack["agent"] for stack in ENGINEERING_STACKS.values()]
    canonical_skills = [stack["skill"] for stack in ENGINEERING_STACKS.values()]

    require_terms(
        agents,
        [
            "ENGINEERING_AGENTS_INDEX.md",
            *canonical_agents,
            *canonical_skills,
            "agents/",
            "skills/",
            "prompts/",
            "schemas/",
            "scripts/validate-agentdefaults.py",
            "scripts/validate-cross-tool-routing.py",
        ],
        "AGENTS.md",
        failures,
    )

    if not re.search(r"(?m)^@AGENTS\.md\s*$", claude):
        failures.append("CLAUDE.md must import shared repository rules with a standalone @AGENTS.md")
    require_terms(
        claude,
        ["ENGINEERING_AGENTS_INDEX.md", *canonical_agents, *canonical_skills],
        "CLAUDE.md",
        failures,
    )

    require_terms(
        engineering,
        [*canonical_agents, *canonical_skills, "agents/agent-architect-builder.md", "agents/automation-platform-selection-advisor.md"],
        "ENGINEERING_AGENTS_INDEX.md",
        failures,
    )

    require_terms(
        codex,
        ["AGENTS.md", "ENGINEERING_AGENTS_INDEX.md", *canonical_agents, "nested `AGENTS.md`", "scripts/validate-agentdefaults.py"],
        "Codex quickstart",
        failures,
    )
    require_terms(
        claude_quickstart,
        ["CLAUDE.md", "@AGENTS.md", "ENGINEERING_AGENTS_INDEX.md", *canonical_agents, "scripts/validate-agentdefaults.py"],
        "Claude quickstart",
        failures,
    )

    require_terms(
        tool_guide,
        [
            "OpenAI Codex",
            "Claude Code",
            "GitHub Copilot",
            "Gemini",
            "Generic repo-aware agent",
            "AGENTS.md",
            "CLAUDE.md",
            ".github/agents/*.agent.md",
            "GEMINI.md",
            "ENGINEERING_AGENTS_INDEX.md",
            *canonical_agents,
        ],
        "tool integration guide",
        failures,
    )


def check_manifest(failures: list[str]) -> None:
    try:
        manifest = json.loads(read("agentdefaults.manifest.json"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        failures.append(f"cannot parse agentdefaults.manifest.json: {exc}")
        return

    if manifest.get("primary_entrypoint") != "AGENTS.md":
        failures.append("manifest primary_entrypoint must remain AGENTS.md")

    stacks = manifest.get("featured_stacks", [])
    by_name = {
        item.get("name"): item
        for item in stacks
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    for name, expected in ENGINEERING_STACKS.items():
        stack = by_name.get(name)
        if stack is None:
            failures.append(f"manifest missing engineering stack: {name}")
            continue
        for field in ("agent", "quickstart", "wrapper"):
            if stack.get(field) != expected[field]:
                failures.append(
                    f"manifest {name} {field} must be {expected[field]!r}, got {stack.get(field)!r}"
                )
        skills = stack.get("skills")
        if not isinstance(skills, list) or expected["skill"] not in skills:
            failures.append(f"manifest {name} must reference skill {expected['skill']}")


def check_copilot_wrappers(failures: list[str]) -> None:
    for name, stack in ENGINEERING_STACKS.items():
        text = read(stack["wrapper"])
        require_terms(
            text,
            [stack["agent"], stack["skill"]],
            f"{name} Copilot wrapper",
            failures,
        )

    forbidden_adapter_copies = [
        "agents/principal-devops-engineer-codex.md",
        "agents/principal-devops-engineer-claude.md",
        "agents/principal-ai-engineer-codex.md",
        "agents/principal-ai-engineer-claude.md",
        "agents/principal-ai-devops-engineer-codex.md",
        "agents/principal-ai-devops-engineer-claude.md",
    ]
    for path in forbidden_adapter_copies:
        if (ROOT / path).exists():
            failures.append(f"tool-specific canonical-agent copy must not exist: {path}")


def main() -> int:
    failures: list[str] = []
    check_files(failures)
    if failures:
        print("AgentDefaults cross-tool routing validation")
        print("===========================================")
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    check_entrypoints(failures)
    check_manifest(failures)
    check_copilot_wrappers(failures)

    print("AgentDefaults cross-tool routing validation")
    print("===========================================")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    print(f"PASS: required files ({len(REQUIRED_FILES)} checked)")
    print("PASS: Codex/generic AGENTS.md routing")
    print("PASS: Claude @AGENTS.md import and engineering routing")
    print("PASS: engineering index and quickstarts")
    print("PASS: manifest engineering stack registration")
    print("PASS: principal Copilot wrapper mappings")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
