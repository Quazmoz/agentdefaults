#!/usr/bin/env python3
"""Validate the GitHub Actions Engineer stack, contracts, and routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

STACK_NAME = "GitHub Actions Engineering"
STACK = {
    "quickstart": "docs/quickstarts/github-actions-engineer.md",
    "agent": "agents/github-actions-engineer.md",
    "skill": "skills/github-actions-engineering.md",
    "prompt": "prompts/implementation/github-actions-task.md",
    "schema": "schemas/github-actions-task.schema.json",
    "example": "examples/github-actions-task.yaml",
    "acceptance_tests": "docs/github-actions-engineer-acceptance-tests.md",
    "wrapper": ".github/agents/github-actions-engineer.agent.md",
}

ROUTING_FILES = [
    "AGENTS.md",
    "ENGINEERING_AGENTS_INDEX.md",
    "INDEX.md",
    "README.md",
    "agents/README.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    "docs/tool-integration-guide.md",
]

PERMISSION_CLASSES = [
    "observe",
    "propose",
    "mutate_reversible",
    "mutate_irreversible",
]

MODES = ["investigate", "review", "design", "implement", "incident", "release"]


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
        try:
            value = rule["if"]["properties"]["mode"]["const"]
        except (KeyError, TypeError):
            continue
        if value == mode:
            return rule
    return None


def find_irreversible_rule(schema: dict[str, Any]) -> dict[str, Any] | None:
    for rule in schema.get("allOf", []):
        if not isinstance(rule, dict):
            continue
        try:
            value = (
                rule["if"]["properties"]["authority"]["properties"]
                ["maximum_permission_class"]["const"]
            )
        except (KeyError, TypeError):
            continue
        if value == "mutate_irreversible":
            return rule
    return None


def check_required_files(failures: list[str]) -> None:
    required = set(STACK.values()) | set(ROUTING_FILES) | {
        "agentdefaults.manifest.json",
        "scripts/README.md",
        "scripts/validate-agentdefaults.py",
        "scripts/validate-github-actions-stack.py",
    }
    for path in sorted(required):
        if not (ROOT / path).is_file():
            failures.append(f"missing GitHub Actions stack file: {path}")


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

    required = set(schema.get("required", []))
    for field in ("goal", "mode", "target", "trust_model", "authority", "acceptance"):
        if field not in required:
            failures.append(f"{path}: root must require {field}")

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

    trust_model = props.get("trust_model", {})
    trust_required = set(trust_model.get("required", []))
    for field in ("event_actors", "untrusted_inputs", "privileged_identities", "runner_boundaries"):
        if field not in trust_required:
            failures.append(f"{path}: trust_model must require {field}")

    implement = find_mode_rule(schema, "implement")
    if implement is None:
        failures.append(f"{path}: missing implement-mode contract")
    else:
        then = implement.get("then", {})
        if "verification" not in then.get("required", []):
            failures.append(f"{path}: implement mode must require verification")
        then_props = then.get("properties", {})
        auth = then_props.get("authority", {})
        if "authorized_mutations" not in auth.get("required", []):
            failures.append(f"{path}: implement mode must require authorized_mutations")
        if auth.get("properties", {}).get("authorized_mutations", {}).get("minItems") != 1:
            failures.append(f"{path}: implement authorized_mutations must be non-empty")
        if auth.get("properties", {}).get("maximum_permission_class", {}).get("enum") != [
            "mutate_reversible",
            "mutate_irreversible",
        ]:
            failures.append(f"{path}: implement mode must require mutating authority")

        verification = then_props.get("verification", {})
        for field in ("required_checks", "security_postconditions", "adversarial_cases"):
            if field not in verification.get("required", []):
                failures.append(f"{path}: implement verification must require {field}")
            if verification.get("properties", {}).get(field, {}).get("minItems") != 1:
                failures.append(f"{path}: implement verification {field} must be non-empty")

    release = find_mode_rule(schema, "release")
    if release is None:
        failures.append(f"{path}: missing release-mode contract")
    else:
        verification = release.get("then", {}).get("properties", {}).get("verification", {})
        for field in (
            "required_checks",
            "representative_runs",
            "security_postconditions",
            "adversarial_cases",
            "artifact_identity_checks",
            "rollback_checks",
        ):
            if field not in verification.get("required", []):
                failures.append(f"{path}: release verification must require {field}")
            if verification.get("properties", {}).get(field, {}).get("minItems") != 1:
                failures.append(f"{path}: release verification {field} must be non-empty")

    incident = find_mode_rule(schema, "incident")
    if incident is None:
        failures.append(f"{path}: missing incident-mode verification contract")
    else:
        verification = incident.get("then", {}).get("properties", {}).get("verification", {})
        for field in ("required_checks", "adversarial_cases"):
            if field not in verification.get("required", []):
                failures.append(f"{path}: incident verification must require {field}")

    irreversible = find_irreversible_rule(schema)
    if irreversible is None:
        failures.append(f"{path}: missing irreversible authority contract")
    else:
        authority = irreversible.get("then", {}).get("properties", {}).get("authority", {})
        for field in ("approval_required", "approval_gates", "authorized_mutations"):
            if field not in authority.get("required", []):
                failures.append(f"{path}: irreversible authority must require {field}")
        authority_props = authority.get("properties", {})
        if authority_props.get("approval_required", {}).get("const") is not True:
            failures.append(f"{path}: irreversible authority must require approval_required=true")
        if authority_props.get("approval_gates", {}).get("minItems") != 1:
            failures.append(f"{path}: irreversible authority must require non-empty approval_gates")


def check_canonical_content(failures: list[str]) -> None:
    agent = read(STACK["agent"])
    skill = read(STACK["skill"])
    prompt = read(STACK["prompt"])
    quickstart = read(STACK["quickstart"])
    acceptance = read(STACK["acceptance_tests"])
    wrapper = read(STACK["wrapper"])
    example = read(STACK["example"])

    agent_lower = agent.lower()
    for term in (
        "pull_request_target",
        "workflow_run",
        "dependabot",
        "full commit sha",
        "oidc",
        "self-hosted",
        "cache",
        "artifact",
        "concurrency",
        "reusable workflow",
        "permissions can only",
        "job_workflow_ref",
        "timeout-after",
    ):
        if term not in agent_lower:
            failures.append(f"{STACK['agent']}: missing required concept {term!r}")

    skill_lower = skill.lower()
    for term in (
        "pull_request_target",
        "workflow_run",
        "dependabot",
        "full commit sha",
        "oidc",
        "self-hosted",
        "cache poisoning",
        "reusable workflow",
        "ambiguous",
    ):
        if term not in skill_lower:
            failures.append(f"{STACK['skill']}: missing required concept {term!r}")

    for term in (
        "TRUST MODEL",
        "AUTHORITY",
        "REQUIRED ENGINEERING RULES",
        "FIRST: TRACE THE CONTROL PATH",
        "VERIFICATION",
        "ADVERSARIAL PASS",
        "DONE WHEN",
    ):
        if term not in prompt:
            failures.append(f"{STACK['prompt']}: missing contract term {term!r}")

    for term in (
        STACK["agent"],
        STACK["skill"],
        STACK["prompt"],
        STACK["schema"],
        STACK["example"],
        "Secure use reference",
        "Dependabot",
    ):
        if term not in quickstart:
            failures.append(f"{STACK['quickstart']}: missing required concept {term!r}")

    acceptance_lower = acceptance.lower()
    for term in (
        "pwn request",
        "privileged `workflow_run` artifact",
        "dependabot",
        "reusable workflow permission escalation",
        "reusable workflow oidc identity",
        "self-hosted runner",
        "cache poisoning",
        "ambiguous deployment timeout",
        "unsafe `cancel-in-progress`",
        "matrix explosion",
        "truthful completion",
    ):
        if term not in acceptance_lower:
            failures.append(f"{STACK['acceptance_tests']}: missing acceptance scenario {term!r}")

    for term in (
        "dependabot[bot]",
        "verified-full-commit-sha",
        "production oidc",
        "artifact_identity_checks",
    ):
        if term not in example.lower():
            failures.append(f"{STACK['example']}: missing example concept {term!r}")

    for term in (STACK["agent"], STACK["skill"], STACK["prompt"], STACK["schema"], STACK["example"]):
        if term not in wrapper:
            failures.append(f"{STACK['wrapper']}: missing canonical reference {term}")


def check_routing(failures: list[str]) -> None:
    agent_ref = STACK["agent"]
    skill_ref = STACK["skill"]
    for path in ROUTING_FILES:
        text = read(path)
        if agent_ref not in text:
            failures.append(f"{path}: missing GitHub Actions agent route {agent_ref}")
        if path in {"AGENTS.md", "ENGINEERING_AGENTS_INDEX.md", "CLAUDE.md", ".github/copilot-instructions.md"} and skill_ref not in text:
            failures.append(f"{path}: missing GitHub Actions skill route {skill_ref}")


def check_primary_validator(failures: list[str]) -> None:
    text = read("scripts/validate-agentdefaults.py")
    if "validate-github-actions-stack.py" not in text:
        failures.append("scripts/validate-agentdefaults.py must include validate-github-actions-stack.py")
    scripts_readme = read("scripts/README.md")
    if "validate-github-actions-stack.py" not in scripts_readme:
        failures.append("scripts/README.md must document validate-github-actions-stack.py")


def main() -> int:
    failures: list[str] = []
    try:
        check_required_files(failures)
        if not failures:
            check_manifest(failures)
            check_schema(failures)
            check_canonical_content(failures)
            check_routing(failures)
            check_primary_validator(failures)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        failures.append(str(exc))

    print("AgentDefaults GitHub Actions stack validation")
    print("=============================================")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    print("PASS: GitHub Actions stack files and manifest registration")
    print("PASS: Actions task schema authority/trust/verification contracts")
    print("PASS: canonical agent/skill/prompt/example/acceptance invariants")
    print("PASS: engineering and cross-tool GitHub Actions routing")
    print("PASS: primary validation suite includes GitHub Actions validation")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
