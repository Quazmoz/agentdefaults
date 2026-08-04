#!/usr/bin/env python3
"""Validate AgentDefaults structure, JSON, manifest references, stack integrity, and Markdown links."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

CORE_REQUIRED_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "INDEX.md",
    "README.md",
    "TRAVEL_INDEX.md",
    "WEAROS_INDEX.md",
    "WEAROS_DEVELOPMENT_INDEX.md",
    "AUTOMATION_PLATFORM_INDEX.md",
    "agentdefaults.manifest.json",
    ".gitignore",
    ".github/FUNDING.yml",
    ".github/copilot-instructions.md",
    ".cursor/rules/agentdefaults.mdc",
    ".windsurfrules",
    "docs/user-guide.md",
    "docs/ux-roadmap.md",
    "docs/tool-integration-guide.md",
    "scripts/validate-agentdefaults.py",
]

AUTOMATION_PLATFORM_REQUIRED_FILES = [
    "AUTOMATION_PLATFORM_INDEX.md",
    "agents/automation-platform-selection-advisor.md",
    "skills/automation-platform-capability-taxonomy.md",
    "skills/automation-platform-decision-framework.md",
    "skills/automation-platform-candidate-discovery.md",
    "skills/terraform-workload-fit-analysis.md",
    "skills/ansible-workload-fit-analysis.md",
    "skills/jenkins-workload-fit-analysis.md",
    "skills/infrastructure-as-code-platform-alternatives-analysis.md",
    "skills/configuration-management-platform-alternatives-analysis.md",
    "skills/ci-cd-platform-alternatives-analysis.md",
    "skills/gitops-runbook-and-workflow-platform-analysis.md",
    "skills/automation-platform-composition-and-boundaries.md",
    "skills/automation-platform-selection-orchestrator.md",
    "prompts/planning/select-automation-platform.md",
    "prompts/review/challenge-automation-platform-choice.md",
    "schemas/automation-platform-decision-brief.schema.json",
    "examples/automation-platform-decision-brief.yaml",
    "docs/quickstarts/automation-platform-selection.md",
    "docs/automation-platform-selection-acceptance-tests.md",
    ".github/agents/automation-platform-selection-advisor.agent.md",
]

PURPOSE_GLOBS = [
    "agents/*.md",
    "skills/*.md",
    "prompts/*/*.md",
    "docs/*.md",
    "docs/quickstarts/*.md",
    "docs/benchmarks/*.md",
    "docs/patterns/*.md",
    "examples/*.md",
    "examples/stacks/*.md",
    ".github/agents/*.agent.md",
]

PURPOSE_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "INDEX.md",
    "TRAVEL_INDEX.md",
    "WEAROS_INDEX.md",
    "WEAROS_DEVELOPMENT_INDEX.md",
    "AUTOMATION_PLATFORM_INDEX.md",
    ".github/copilot-instructions.md",
]

LINK_EXTENSIONS = (
    ".md",
    ".mdc",
    ".agent.md",
    ".windsurfrules",
    ".json",
    ".py",
    ".yml",
    ".yaml",
)

SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def print_fail(title: str, failures: Iterable[str]) -> int:
    print(f"FAIL: {title}")
    for failure in failures:
        print(f"  - {failure}")
    return 1


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_required_files() -> int:
    required = CORE_REQUIRED_FILES + AUTOMATION_PLATFORM_REQUIRED_FILES
    missing = sorted(name for name in set(required) if not (ROOT / name).is_file())
    if missing:
        return print_fail("required files", missing)
    print(f"PASS: required files ({len(set(required))} checked)")
    return 0


def check_purpose_sections() -> int:
    paths: list[Path] = []
    for pattern in PURPOSE_GLOBS:
        paths.extend(ROOT.glob(pattern))
    paths.extend(ROOT / name for name in PURPOSE_FILES)

    failures: list[str] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        if "## Purpose" not in text:
            failures.append(str(path.relative_to(ROOT)))

    if failures:
        return print_fail("Markdown files missing ## Purpose", failures)
    print(f"PASS: Markdown structure ({len(seen)} checked)")
    return 0


def json_files() -> list[Path]:
    paths = [ROOT / "agentdefaults.manifest.json"]
    paths.extend(sorted((ROOT / "schemas").glob("*.json")))
    return paths


def check_json_files() -> int:
    failures: list[str] = []
    paths = json_files()
    for path in paths:
        try:
            load_json(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")

    if failures:
        return print_fail("JSON files", failures)
    print(f"PASS: JSON files ({len(paths)} checked)")
    return 0


def iter_manifest_paths(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {
                "primary_entrypoint",
                "validation",
                "quickstart",
                "agent",
                "schema",
                "example",
                "acceptance_tests",
                "wrapper",
            } and isinstance(child, str):
                yield child
            elif key in {"skills", "prompts"} and isinstance(child, list):
                for item in child:
                    if isinstance(item, str):
                        yield item
            yield from iter_manifest_paths(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_manifest_paths(child)


def check_manifest() -> int:
    path = ROOT / "agentdefaults.manifest.json"
    try:
        manifest = load_json(path)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return print_fail("manifest", [str(exc)])

    failures: list[str] = []

    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
        failures.append(f"version is not semantic x.y.z: {version!r}")

    stacks = manifest.get("featured_stacks")
    if not isinstance(stacks, list) or not stacks:
        failures.append("featured_stacks must be a non-empty list")
        stacks = []

    names: list[str] = []
    for index, stack in enumerate(stacks):
        if not isinstance(stack, dict):
            failures.append(f"featured_stacks[{index}] is not an object")
            continue
        name = stack.get("name")
        if not isinstance(name, str) or not name.strip():
            failures.append(f"featured_stacks[{index}] has no valid name")
        else:
            names.append(name)
        if not isinstance(stack.get("agent"), str):
            failures.append(f"featured_stacks[{index}] has no agent")

    duplicates = sorted({name for name in names if names.count(name) > 1})
    failures.extend(f"duplicate featured stack name: {name}" for name in duplicates)

    missing = sorted({
        ref for ref in iter_manifest_paths(manifest)
        if not (ROOT / ref).is_file()
    })
    failures.extend(f"missing manifest reference: {ref}" for ref in missing)

    if failures:
        return print_fail("manifest", failures)
    print(f"PASS: manifest ({len(stacks)} featured stacks, references valid)")
    return 0


def check_automation_platform_stack() -> int:
    failures: list[str] = []

    manifest = load_json(ROOT / "agentdefaults.manifest.json")
    stacks = manifest.get("featured_stacks", [])
    stack = next(
        (
            item for item in stacks
            if isinstance(item, dict)
            and item.get("name") == "Automation Platform Architecture and Selection"
        ),
        None,
    )
    if stack is None:
        failures.append("expanded automation platform stack is not registered")
    else:
        registered = set(stack.get("skills", []))
        required_skills = {
            path for path in AUTOMATION_PLATFORM_REQUIRED_FILES
            if path.startswith("skills/")
        }
        missing_skills = sorted(required_skills - registered)
        failures.extend(f"automation skill missing from manifest: {path}" for path in missing_skills)

    schema_path = ROOT / "schemas/automation-platform-decision-brief.schema.json"
    schema = load_json(schema_path)
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    if "platform_selection" not in properties:
        failures.append("decision schema has no platform_selection property")
    if "platform_selection" not in required:
        failures.append("decision schema does not require platform_selection")

    platform_selection = properties.get("platform_selection", {})
    selection_properties = platform_selection.get("properties", {})
    if "candidate_policy" not in selection_properties:
        failures.append("decision schema has no candidate_policy")
    if "allowed_hosting_models" not in selection_properties:
        failures.append("decision schema has no allowed_hosting_models")

    agent_text = (ROOT / "agents/automation-platform-selection-advisor.md").read_text(encoding="utf-8")
    required_terms = [
        "GitHub Actions",
        "Azure Pipelines",
        "Puppet",
        "Chef Infra",
        "OpenTofu",
        "Pulumi",
        "Argo CD",
        "Flux",
        "durable workflow",
    ]
    for term in required_terms:
        if term not in agent_text:
            failures.append(f"automation advisor missing product or capability coverage: {term}")

    example_text = (ROOT / "examples/automation-platform-decision-brief.yaml").read_text(encoding="utf-8")
    for marker in [
        "platform_selection:",
        "candidate_policy:",
        "allowed_hosting_models:",
        "evidence_cutoff:",
    ]:
        if marker not in example_text:
            failures.append(f"automation example missing field: {marker}")

    if failures:
        return print_fail("automation platform stack", failures)
    print("PASS: automation platform stack integrity")
    return 0


def should_check_link(target: str) -> bool:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return False
    path_part = target.split("#", 1)[0]
    return bool(path_part) and path_part.endswith(LINK_EXTENSIONS)


def check_links() -> int:
    failures: list[str] = []
    for md in ROOT.rglob("*.md"):
        if ".git" in md.parts:
            continue
        text = md.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = target.strip()
            if not should_check_link(target):
                continue
            path_part = target.split("#", 1)[0]
            if not (md.parent / path_part).resolve().exists():
                failures.append(f"{md.relative_to(ROOT)} -> {target}")

    if failures:
        return print_fail("broken Markdown links", failures)
    print("PASS: Markdown links")
    return 0


def main() -> int:
    print("AgentDefaults validation")
    print("========================")
    failures = (
        check_required_files()
        + check_purpose_sections()
        + check_json_files()
        + check_manifest()
        + check_automation_platform_stack()
        + check_links()
    )
    if failures:
        print("\nResult: FAIL")
        return 1
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
