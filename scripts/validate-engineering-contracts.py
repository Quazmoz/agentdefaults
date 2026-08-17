#!/usr/bin/env python3
"""Validate principal engineering contracts and CI enforcement."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

PERMISSION_CLASSES = [
    "observe",
    "propose",
    "mutate_reversible",
    "mutate_irreversible",
]

ENGINEERING_STACKS = {
    "Principal DevOps Engineering": {
        "agent": "agents/principal-devops-engineer.md",
        "skill": "skills/production-devops-engineering.md",
        "prompt": "prompts/implementation/principal-devops-task.md",
        "schema": "schemas/principal-devops-task.schema.json",
        "example": "examples/principal-devops-task.yaml",
        "acceptance_tests": "docs/principal-devops-engineer-acceptance-tests.md",
        "wrapper": ".github/agents/principal-devops-engineer.agent.md",
    },
    "Principal AI Engineering": {
        "agent": "agents/principal-ai-engineer.md",
        "skill": "skills/production-ai-engineering.md",
        "prompt": "prompts/implementation/principal-ai-engineer-task.md",
        "schema": "schemas/principal-ai-engineer-task.schema.json",
        "example": "examples/principal-ai-engineer-task.yaml",
        "acceptance_tests": "docs/principal-ai-engineer-acceptance-tests.md",
        "wrapper": ".github/agents/principal-ai-engineer.agent.md",
    },
    "Principal AI and DevOps Engineering": {
        "agent": "agents/principal-ai-devops-engineer.md",
        "skill": "skills/production-ai-devops-engineering.md",
        "prompt": "prompts/implementation/principal-ai-devops-task.md",
        "schema": "schemas/principal-ai-devops-task.schema.json",
        "example": "examples/principal-ai-devops-task.yaml",
        "acceptance_tests": "docs/principal-ai-devops-engineer-acceptance-tests.md",
        "wrapper": ".github/agents/principal-ai-devops-engineer.agent.md",
    },
}

VALIDATION_SUITE = [
    "scripts/validate-agentdefaults.py",
    "scripts/validate-cross-tool-routing.py",
    "scripts/validate-engineering-contracts.py",
]

ENTRYPOINTS = [
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".cursor/rules/agentdefaults.mdc",
    ".windsurfrules",
]

WORKFLOW = ".github/workflows/validate.yml"
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"


def fail(title: str, failures: list[str]) -> int:
    print(f"FAIL: {title}")
    for failure in failures:
        print(f"  - {failure}")
    return 1


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, Any]:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def find_mode_rule(schema: dict[str, Any], mode: str) -> dict[str, Any] | None:
    for rule in schema.get("allOf", []):
        if not isinstance(rule, dict):
            continue
        condition = rule.get("if", {})
        try:
            value = condition["properties"]["mode"]["const"]
        except (KeyError, TypeError):
            continue
        if value == mode:
            return rule
    return None


def find_irreversible_rule(schema: dict[str, Any]) -> dict[str, Any] | None:
    for rule in schema.get("allOf", []):
        if not isinstance(rule, dict):
            continue
        condition = rule.get("if", {})
        try:
            value = (
                condition["properties"]["authority"]["properties"]
                ["maximum_permission_class"]["const"]
            )
        except (KeyError, TypeError):
            continue
        if value == "mutate_irreversible":
            return rule
    return None


def check_files(failures: list[str]) -> None:
    required = {WORKFLOW, *VALIDATION_SUITE, *ENTRYPOINTS}
    for stack in ENGINEERING_STACKS.values():
        required.update(stack.values())
    for path in sorted(required):
        if not (ROOT / path).is_file():
            failures.append(f"missing required engineering-contract file: {path}")


def check_manifest(failures: list[str]) -> None:
    manifest = load_json("agentdefaults.manifest.json")
    if manifest.get("validation") != "scripts/validate-agentdefaults.py":
        failures.append("manifest validation entrypoint must remain scripts/validate-agentdefaults.py")
    if manifest.get("validation_suite") != VALIDATION_SUITE:
        failures.append("manifest validation_suite must list the canonical validators in order")

    stacks = manifest.get("featured_stacks", [])
    by_name = {
        item.get("name"): item
        for item in stacks
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    for name, expected in ENGINEERING_STACKS.items():
        actual = by_name.get(name)
        if not isinstance(actual, dict):
            failures.append(f"manifest missing principal engineering stack: {name}")
            continue
        for field in ("agent", "schema", "example", "acceptance_tests", "wrapper"):
            if actual.get(field) != expected[field]:
                failures.append(
                    f"manifest {name} {field} must be {expected[field]!r}"
                )
        skills = actual.get("skills")
        if skills != [expected["skill"]]:
            failures.append(f"manifest {name} must reference only {expected['skill']}")
        prompts = actual.get("prompts")
        if prompts != [expected["prompt"]]:
            failures.append(f"manifest {name} must reference only {expected['prompt']}")


def check_schema(path: str, failures: list[str]) -> None:
    schema = load_json(path)
    properties = schema.get("properties", {})
    authority = properties.get("authority", {})
    permission_enum = (
        authority.get("properties", {})
        .get("maximum_permission_class", {})
        .get("enum", [])
    )
    if permission_enum != PERMISSION_CLASSES:
        failures.append(f"{path}: permission enum drifted from canonical order")

    if schema.get("additionalProperties") is not False:
        failures.append(f"{path}: root additionalProperties must be false")

    implement = find_mode_rule(schema, "implement")
    if implement is None:
        failures.append(f"{path}: missing implement-mode contract")
    else:
        then = implement.get("then", {})
        if "verification" not in then.get("required", []):
            failures.append(f"{path}: implement mode must require verification")
        then_props = then.get("properties", {})
        auth_then = then_props.get("authority", {})
        if "authorized_mutations" not in auth_then.get("required", []):
            failures.append(f"{path}: implement mode must require authorized_mutations")
        auth_props = auth_then.get("properties", {})
        if auth_props.get("authorized_mutations", {}).get("minItems") != 1:
            failures.append(f"{path}: implement authorized_mutations must be non-empty")
        allowed = auth_props.get("maximum_permission_class", {}).get("enum")
        if allowed != ["mutate_reversible", "mutate_irreversible"]:
            failures.append(f"{path}: implement mode must require mutating authority")

        verification = then_props.get("verification", {})
        required = verification.get("required", [])
        for field in ("required_checks", "postconditions"):
            if field not in required:
                failures.append(f"{path}: implement verification must require {field}")
            if verification.get("properties", {}).get(field, {}).get("minItems") != 1:
                failures.append(f"{path}: implement verification {field} must be non-empty")

    release = find_mode_rule(schema, "release")
    if release is None:
        failures.append(f"{path}: missing release-mode verification contract")
    else:
        then = release.get("then", {})
        if "verification" not in then.get("required", []):
            failures.append(f"{path}: release mode must require verification")
        verification = then.get("properties", {}).get("verification", {})
        for field in ("required_checks", "postconditions"):
            if field not in verification.get("required", []):
                failures.append(f"{path}: release verification must require {field}")
            if verification.get("properties", {}).get(field, {}).get("minItems") != 1:
                failures.append(f"{path}: release verification {field} must be non-empty")

    irreversible = find_irreversible_rule(schema)
    if irreversible is None:
        failures.append(f"{path}: missing irreversible-mutation approval contract")
    else:
        authority_then = (
            irreversible.get("then", {})
            .get("properties", {})
            .get("authority", {})
        )
        required = authority_then.get("required", [])
        for field in ("approval_required", "approval_gates", "authorized_mutations"):
            if field not in required:
                failures.append(f"{path}: irreversible authority must require {field}")
        auth_props = authority_then.get("properties", {})
        if auth_props.get("approval_required", {}).get("const") is not True:
            failures.append(f"{path}: irreversible authority must require approval_required=true")
        if auth_props.get("approval_gates", {}).get("minItems") != 1:
            failures.append(f"{path}: irreversible authority must require a non-empty approval gate")
        if auth_props.get("authorized_mutations", {}).get("minItems") != 1:
            failures.append(f"{path}: irreversible authority must require explicit mutations")


def check_stack_documents(failures: list[str]) -> None:
    for name, stack in ENGINEERING_STACKS.items():
        prompt = read(stack["prompt"])
        for term in ("AUTHORITY", "Authorized mutations:", "VERIFICATION", "DONE WHEN"):
            if term not in prompt:
                failures.append(f"{name} prompt missing contract term: {term}")

        acceptance = read(stack["acceptance_tests"])
        for term in ("permission", "verification"):
            if term.lower() not in acceptance.lower():
                failures.append(f"{name} acceptance tests missing concept: {term}")

        wrapper = read(stack["wrapper"])
        for term in (stack["agent"], stack["skill"]):
            if term not in wrapper:
                failures.append(f"{name} wrapper missing canonical reference: {term}")


def check_entrypoints(failures: list[str]) -> None:
    for path in ENTRYPOINTS:
        text = read(path)
        if "scripts/validate-engineering-contracts.py" not in text:
            failures.append(f"{path}: missing engineering-contract validator reference")


def check_workflow(failures: list[str]) -> None:
    text = read(WORKFLOW)
    required_terms = [
        "pull_request:",
        "push:",
        "workflow_dispatch:",
        "permissions:",
        "contents: read",
        "timeout-minutes:",
        "persist-credentials: false",
        CHECKOUT_SHA,
        SETUP_PYTHON_SHA,
        *VALIDATION_SUITE,
    ]
    for term in required_terms:
        if term not in text:
            failures.append(f"{WORKFLOW}: missing required term {term!r}")


def main() -> int:
    failures: list[str] = []
    try:
        check_files(failures)
        if not failures:
            check_manifest(failures)
            for stack in ENGINEERING_STACKS.values():
                check_schema(stack["schema"], failures)
            check_stack_documents(failures)
            check_entrypoints(failures)
            check_workflow(failures)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        failures.append(str(exc))

    print("AgentDefaults engineering contract validation")
    print("============================================")
    if failures:
        return fail("engineering contracts", failures)

    print("PASS: principal engineering files and manifest registration")
    print("PASS: implement/release/irreversible schema contracts")
    print("PASS: canonical prompts, wrappers, and acceptance-test anchors")
    print("PASS: cross-tool entrypoints reference the full validation suite")
    print("PASS: CI workflow is least-privilege and runs all validators")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
