#!/usr/bin/env python3
"""Validate the DevSecOps Security Engineer stack and routing."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

STACK_NAME = "DevSecOps Security Engineering"
STACK = {
    "quickstart": "docs/quickstarts/devsecops-security-engineer.md",
    "agent": "agents/devsecops-security-engineer.md",
    "skill": "skills/devsecops-security-engineering.md",
    "prompt": "prompts/implementation/devsecops-security-task.md",
    "schema": "schemas/devsecops-security-task.schema.json",
    "example": "examples/devsecops-security-task.yaml",
    "acceptance_tests": "docs/devsecops-security-engineer-acceptance-tests.md",
    "wrapper": ".github/agents/devsecops-security-engineer.agent.md",
}

ROUTING_FILES = [
    "AGENTS.md",
    "ENGINEERING_AGENTS_INDEX.md",
    "INDEX.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
]

PERMISSION_CLASSES = [
    "observe",
    "propose",
    "mutate_reversible",
    "mutate_irreversible",
]

REQUIRED_PLATFORMS = [
    "terraform",
    "ansible",
    "automation_platform",
    "jenkins",
]


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
        "scripts/validate-agentdefaults.py",
        "scripts/validate-devsecops-security-stack.py",
    }
    for path in sorted(required):
        if not (ROOT / path).is_file():
            failures.append(f"missing DevSecOps security stack file: {path}")


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

    permission_enum = (
        props.get("authority", {})
        .get("properties", {})
        .get("maximum_permission_class", {})
        .get("enum", [])
    )
    if permission_enum != PERMISSION_CLASSES:
        failures.append(f"{path}: permission enum drifted from canonical order")

    platform_enum = props.get("platforms", {}).get("items", {}).get("enum", [])
    for platform in REQUIRED_PLATFORMS:
        if platform not in platform_enum:
            failures.append(f"{path}: platforms missing {platform}")

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
        for field in ("required_checks", "security_postconditions", "adversarial_cases", "rollback_checks"):
            if field not in verification.get("required", []):
                failures.append(f"{path}: release verification must require {field}")
            if verification.get("properties", {}).get(field, {}).get("minItems") != 1:
                failures.append(f"{path}: release verification {field} must be non-empty")

    incident = find_mode_rule(schema, "incident")
    if incident is None:
        failures.append(f"{path}: missing incident-mode threat-model contract")
    else:
        threat_model = incident.get("then", {}).get("properties", {}).get("threat_model", {})
        for field in ("assets", "trust_boundaries", "privileged_identities", "realistic_threats"):
            if field not in threat_model.get("required", []):
                failures.append(f"{path}: incident threat_model must require {field}")

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

    for term in (
        "Terraform / OpenTofu",
        "Ansible / Automation Platform",
        "Jenkins",
        "THREAT MODEL",
        "P0",
        "P1",
        "no_log",
        ".terraform.lock.hcl",
        "CSRF",
        "principal-devops-engineer.md",
    ):
        if term not in agent:
            failures.append(f"{STACK['agent']}: missing required concept {term!r}")

    skill_lower = skill.lower()
    for term in (
        "attacker-controlled",
        "privileged identities",
        "terraform",
        "ansible",
        "jenkins",
        "ambiguous success",
        "secret exfiltration",
    ):
        if term not in skill_lower:
            failures.append(f"{STACK['skill']}: missing required concept {term!r}")

    for term in ("AUTHORITY", "Authorized mutations:", "THREAT MODEL", "VERIFICATION", "ADVERSARIAL PASS", "DONE WHEN"):
        if term not in prompt:
            failures.append(f"{STACK['prompt']}: missing contract term {term!r}")

    for term in ("Terraform / OpenTofu", "Ansible / Automation Platform", "Jenkins", "untrusted"):
        if term not in quickstart:
            failures.append(f"{STACK['quickstart']}: missing required concept {term!r}")

    acceptance_lower = acceptance.lower()
    for term in (
        "untrusted pr credential boundary",
        "jenkins controller isolation",
        "terraform sensitive misunderstanding",
        "ansible vault false confidence",
        "aap rbac and credential graph",
        "security control weakening",
        "incident evidence preservation",
        "truthful completion",
    ):
        if term not in acceptance_lower:
            failures.append(f"{STACK['acceptance_tests']}: missing acceptance scenario {term!r}")

    for term in (STACK["agent"], STACK["skill"], STACK["prompt"], STACK["schema"]):
        if term not in wrapper:
            failures.append(f"{STACK['wrapper']}: missing canonical reference {term}")


def check_routing(failures: list[str]) -> None:
    agent_ref = STACK["agent"]
    skill_ref = STACK["skill"]
    for path in ROUTING_FILES:
        text = read(path)
        if agent_ref not in text:
            failures.append(f"{path}: missing DevSecOps agent route {agent_ref}")
        if path in {"AGENTS.md", "ENGINEERING_AGENTS_INDEX.md"} and skill_ref not in text:
            failures.append(f"{path}: missing DevSecOps skill route {skill_ref}")


def check_primary_validator(failures: list[str]) -> None:
    text = read("scripts/validate-agentdefaults.py")
    if "validate-devsecops-security-stack.py" not in text:
        failures.append("scripts/validate-agentdefaults.py must include validate-devsecops-security-stack.py")


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

    print("AgentDefaults DevSecOps security stack validation")
    print("=================================================")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    print("PASS: DevSecOps security stack files and manifest registration")
    print("PASS: security task schema authority/platform/verification contracts")
    print("PASS: canonical DevSecOps agent/skill/prompt/acceptance invariants")
    print("PASS: engineering and cross-tool DevSecOps routing")
    print("PASS: primary validation suite includes DevSecOps validation")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
