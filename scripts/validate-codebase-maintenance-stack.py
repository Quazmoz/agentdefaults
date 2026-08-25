#!/usr/bin/env python3
"""Validate the Codebase Maintenance and De-Slop Engineer stack and routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

STACK_NAME = "Codebase Maintenance and De-Slop Engineering"
STACK = {
    "quickstart": "docs/quickstarts/codebase-maintenance-engineer.md",
    "agent": "agents/codebase-maintenance-engineer.md",
    "skill": "skills/codebase-de-slop-and-refactoring.md",
    "prompt": "prompts/implementation/codebase-de-slop-task.md",
    "schema": "schemas/codebase-maintenance-task.schema.json",
    "example": "examples/codebase-maintenance-task.yaml",
    "acceptance_tests": "docs/codebase-maintenance-engineer-acceptance-tests.md",
    "wrapper": ".github/agents/codebase-maintenance-engineer.agent.md",
}

ROUTING_FILES = [
    "AGENTS.md",
    "ENGINEERING_AGENTS_INDEX.md",
    "INDEX.md",
    "README.md",
]

PERMISSION_CLASSES = [
    "observe",
    "propose",
    "mutate_reversible",
    "mutate_irreversible",
]

MODES = ["audit", "de_slop", "refactor", "comment_reconcile", "efficiency"]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, Any]:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def check_required_files(failures: list[str]) -> None:
    required = set(STACK.values()) | set(ROUTING_FILES) | {
        "agentdefaults.manifest.json",
        "scripts/validate-agentdefaults.py",
        "scripts/validate-codebase-maintenance-stack.py",
    }
    for path in sorted(required):
        if not (ROOT / path).is_file():
            failures.append(f"missing codebase-maintenance stack file: {path}")


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

    for field in ("quickstart", "agent", "schema", "example", "acceptance_tests", "wrapper"):
        expected = STACK[field]
        if stack.get(field) != expected:
            failures.append(f"manifest {STACK_NAME} {field} must be {expected!r}")
    if stack.get("skills") != [STACK["skill"]]:
        failures.append(f"manifest {STACK_NAME} must reference only {STACK['skill']}")
    if stack.get("prompts") != [STACK["prompt"]]:
        failures.append(f"manifest {STACK_NAME} must reference only {STACK['prompt']}")


def check_schema(failures: list[str]) -> None:
    path = STACK["schema"]
    schema = load_json(path)
    props = schema.get("properties", {})

    if schema.get("additionalProperties") is not False:
        failures.append(f"{path}: root additionalProperties must be false")

    mode_enum = props.get("mode", {}).get("enum", [])
    if mode_enum != MODES:
        failures.append(f"{path}: mode enum drifted from canonical order")

    permission_enum = (
        props.get("authority", {})
        .get("properties", {})
        .get("maximum_permission_class", {})
        .get("enum", [])
    )
    if permission_enum != PERMISSION_CLASSES:
        failures.append(f"{path}: permission enum drifted from canonical order")

    behavior = props.get("behavior_policy", {})
    behavior_required = behavior.get("required", [])
    for field in ("allow_behavior_changes", "reconcile_touched_comments"):
        if field not in behavior_required:
            failures.append(f"{path}: behavior_policy must require {field}")

    rules = schema.get("allOf", [])
    non_audit_rule = None
    behavior_change_rule = None
    efficiency_rule = None
    irreversible_rule = None

    for rule in rules:
        if not isinstance(rule, dict):
            continue
        condition = rule.get("if", {})
        try:
            mode_rule = condition["properties"]["mode"]
        except (KeyError, TypeError):
            mode_rule = None
        if isinstance(mode_rule, dict):
            if mode_rule.get("enum") == ["de_slop", "refactor", "comment_reconcile", "efficiency"]:
                non_audit_rule = rule
            if mode_rule.get("const") == "efficiency":
                efficiency_rule = rule
        try:
            allow_changes = (
                condition["properties"]["behavior_policy"]["properties"]
                ["allow_behavior_changes"]["const"]
            )
        except (KeyError, TypeError):
            allow_changes = None
        if allow_changes is True:
            behavior_change_rule = rule
        try:
            permission = (
                condition["properties"]["authority"]["properties"]
                ["maximum_permission_class"]["const"]
            )
        except (KeyError, TypeError):
            permission = None
        if permission == "mutate_irreversible":
            irreversible_rule = rule

    if non_audit_rule is None:
        failures.append(f"{path}: missing mutating-mode verification/authority contract")
    else:
        then = non_audit_rule.get("then", {})
        if "verification" not in then.get("required", []):
            failures.append(f"{path}: mutating modes must require verification")
        then_props = then.get("properties", {})
        authority = then_props.get("authority", {})
        if "authorized_mutations" not in authority.get("required", []):
            failures.append(f"{path}: mutating modes must require authorized_mutations")
        if authority.get("properties", {}).get("authorized_mutations", {}).get("minItems") != 1:
            failures.append(f"{path}: authorized_mutations must be non-empty")
        verification = then_props.get("verification", {})
        for field in ("required_checks", "postconditions"):
            if field not in verification.get("required", []):
                failures.append(f"{path}: mutating verification must require {field}")
            if verification.get("properties", {}).get(field, {}).get("minItems") != 1:
                failures.append(f"{path}: mutating verification {field} must be non-empty")
        reconcile = (
            then_props.get("behavior_policy", {})
            .get("properties", {})
            .get("reconcile_touched_comments", {})
            .get("const")
        )
        if reconcile is not True:
            failures.append(f"{path}: mutating modes must require reconcile_touched_comments=true")

    if behavior_change_rule is None:
        failures.append(f"{path}: missing explicit behavior-change authorization contract")
    else:
        behavior_then = (
            behavior_change_rule.get("then", {})
            .get("properties", {})
            .get("behavior_policy", {})
        )
        if "authorized_behavior_changes" not in behavior_then.get("required", []):
            failures.append(f"{path}: allow_behavior_changes=true must require authorized_behavior_changes")
        if behavior_then.get("properties", {}).get("authorized_behavior_changes", {}).get("minItems") != 1:
            failures.append(f"{path}: authorized_behavior_changes must be non-empty")

    if efficiency_rule is None:
        failures.append(f"{path}: missing efficiency evidence contract")
    else:
        verification = (
            efficiency_rule.get("then", {})
            .get("properties", {})
            .get("verification", {})
        )
        if "performance_evidence" not in verification.get("required", []):
            failures.append(f"{path}: efficiency mode must require performance_evidence")
        if verification.get("properties", {}).get("performance_evidence", {}).get("minItems") != 1:
            failures.append(f"{path}: efficiency performance_evidence must be non-empty")

    if irreversible_rule is None:
        failures.append(f"{path}: missing irreversible approval contract")
    else:
        authority = (
            irreversible_rule.get("then", {})
            .get("properties", {})
            .get("authority", {})
        )
        for field in ("approval_required", "approval_gates"):
            if field not in authority.get("required", []):
                failures.append(f"{path}: irreversible authority must require {field}")
        authority_props = authority.get("properties", {})
        if authority_props.get("approval_required", {}).get("const") is not True:
            failures.append(f"{path}: irreversible authority must require approval_required=true")
        if authority_props.get("approval_gates", {}).get("minItems") != 1:
            failures.append(f"{path}: irreversible authority must require non-empty approval_gates")


def require_terms(text: str, terms: list[str], label: str, failures: list[str]) -> None:
    for term in terms:
        if term not in text:
            failures.append(f"{label}: missing required concept {term!r}")


def check_content(failures: list[str]) -> None:
    agent = read(STACK["agent"])
    skill = read(STACK["skill"])
    prompt = read(STACK["prompt"])
    quickstart = read(STACK["quickstart"])
    acceptance = read(STACK["acceptance_tests"])
    wrapper = read(STACK["wrapper"])

    require_terms(
        agent,
        [
            "The Agentic-Code Rot Model",
            "Comment and Documentation Contract",
            "Cross-Language Adaptation",
            "second-pass de-slop review",
            "Text search alone is not proof",
            "behavior-preserving",
        ],
        STACK["agent"],
        failures,
    )

    require_terms(
        skill,
        [
            "Comment drift",
            "Abstraction inflation",
            "Failure-handling slop",
            "Efficiency slop",
            "Language-Aware Verification",
            "Second-Pass Agentic Slop Check",
            "reflection",
            "N+1",
        ],
        STACK["skill"],
        failures,
    )

    require_terms(
        prompt,
        [
            "SLOP INVENTORY",
            "REFACTOR INVARIANT",
            "COMMENT CONTRACT",
            "second-pass de-slop review",
            "VERIFICATION",
            "DONE WHEN",
        ],
        STACK["prompt"],
        failures,
    )

    require_terms(
        quickstart,
        [
            "stale comments",
            "Cross-Language Behavior",
            "Safe Dead-Code Removal",
            "Efficiency Work",
        ],
        STACK["quickstart"],
        failures,
    )

    acceptance_lower = acceptance.lower()
    for term in [
        "false dead code under reflection/di",
        "test weakening",
        "public serialization rename",
        "abstraction inflation",
        "security-preserving simplification",
        "second-pass fresh slop",
        "performance evidence honesty",
        "truthful completion",
    ]:
        if term not in acceptance_lower:
            failures.append(f"{STACK['acceptance_tests']}: missing adversarial case {term!r}")

    require_terms(
        wrapper,
        [STACK["agent"], STACK["skill"], "Comment Contract", "second-pass"],
        STACK["wrapper"],
        failures,
    )


def check_routing(failures: list[str]) -> None:
    agent_ref = STACK["agent"]
    skill_ref = STACK["skill"]
    quickstart_ref = STACK["quickstart"]

    for path in ("AGENTS.md", "ENGINEERING_AGENTS_INDEX.md"):
        text = read(path)
        for ref in (agent_ref, skill_ref):
            if ref not in text:
                failures.append(f"{path}: missing codebase-maintenance route {ref}")

    index = read("INDEX.md")
    for ref in (agent_ref, quickstart_ref):
        if ref not in index:
            failures.append(f"INDEX.md: missing codebase-maintenance reference {ref}")

    readme = read("README.md")
    for ref in (agent_ref, quickstart_ref):
        if ref not in readme:
            failures.append(f"README.md: missing codebase-maintenance reference {ref}")


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    if not failures:
        try:
            check_manifest(failures)
            check_schema(failures)
            check_content(failures)
            check_routing(failures)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            failures.append(str(exc))

    print("Codebase Maintenance stack validation")
    print("=====================================")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    print("PASS: required files and manifest registration")
    print("PASS: structured maintenance task contract")
    print("PASS: comment/refactor/efficiency safety invariants")
    print("PASS: routing and wrapper references")
    print("PASS: adversarial acceptance-test coverage")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
