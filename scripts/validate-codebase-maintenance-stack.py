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
GENERATED_POLICIES = ["source_and_regenerate", "preserve", "direct_edit_authorized"]
CONFIDENCE = ["medium", "high", "very_high"]


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


def find_rule(schema: dict[str, Any], predicate) -> dict[str, Any] | None:
    for rule in schema.get("allOf", []):
        if isinstance(rule, dict) and predicate(rule.get("if", {})):
            return rule
    return None


def check_schema(failures: list[str]) -> None:
    path = STACK["schema"]
    schema = load_json(path)
    props = schema.get("properties", {})

    if schema.get("additionalProperties") is not False:
        failures.append(f"{path}: root additionalProperties must be false")

    for required in ("target", "mode", "goal", "behavior_policy", "evidence_policy", "churn_policy", "authority"):
        if required not in schema.get("required", []):
            failures.append(f"{path}: root must require {required}")

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
    for field in (
        "allow_behavior_changes",
        "reconcile_touched_comments",
        "generated_artifact_policy",
        "require_history_for_ambiguous_intent",
    ):
        if field not in behavior_required:
            failures.append(f"{path}: behavior_policy must require {field}")

    generated_enum = (
        behavior.get("properties", {})
        .get("generated_artifact_policy", {})
        .get("enum", [])
    )
    if generated_enum != GENERATED_POLICIES:
        failures.append(f"{path}: generated_artifact_policy enum drifted")

    characterization_enum = (
        behavior.get("properties", {})
        .get("characterization_policy", {})
        .get("enum", [])
    )
    if characterization_enum != ["contract_only", "review_incidental_before_locking"]:
        failures.append(f"{path}: characterization policy must preserve contractual/incidental distinction")

    evidence = props.get("evidence_policy", {})
    for field in (
        "minimum_removal_confidence",
        "distinguish_contractual_from_incidental_behavior",
        "require_independent_evidence_for_high_blast_radius",
    ):
        if field not in evidence.get("required", []):
            failures.append(f"{path}: evidence_policy must require {field}")
    confidence_enum = (
        evidence.get("properties", {})
        .get("minimum_removal_confidence", {})
        .get("enum", [])
    )
    if confidence_enum != CONFIDENCE:
        failures.append(f"{path}: minimum_removal_confidence enum drifted")

    churn = props.get("churn_policy", {})
    for field in ("allow_unrelated_formatting", "require_independent_slice_verification"):
        if field not in churn.get("required", []):
            failures.append(f"{path}: churn_policy must require {field}")

    focus_enum = props.get("focus", {}).get("items", {}).get("enum", [])
    for focus in ("generated_artifacts", "discoverability_context"):
        if focus not in focus_enum:
            failures.append(f"{path}: focus missing {focus}")

    rules = schema.get("allOf", [])
    non_audit_rule = None
    behavior_change_rule = None
    generated_direct_rule = None
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
            behavior_props = condition["properties"]["behavior_policy"]["properties"]
        except (KeyError, TypeError):
            behavior_props = {}
        if behavior_props.get("allow_behavior_changes", {}).get("const") is True:
            behavior_change_rule = rule
        if behavior_props.get("generated_artifact_policy", {}).get("const") == "direct_edit_authorized":
            generated_direct_rule = rule
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
        for field in ("required_checks", "compatibility_checks", "postconditions"):
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

    if generated_direct_rule is None:
        failures.append(f"{path}: missing direct-generated-edit justification contract")
    else:
        behavior_then = (
            generated_direct_rule.get("then", {})
            .get("properties", {})
            .get("behavior_policy", {})
        )
        if "direct_generated_edit_justification" not in behavior_then.get("required", []):
            failures.append(f"{path}: direct generated edits must require justification")

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
    text_lower = text.lower()
    for term in terms:
        if term.lower() not in text_lower:
            failures.append(f"{label}: missing required concept {term!r}")


def check_content(failures: list[str]) -> None:
    agent = read(STACK["agent"])
    skill = read(STACK["skill"])
    prompt = read(STACK["prompt"])
    quickstart = read(STACK["quickstart"])
    acceptance = read(STACK["acceptance_tests"])
    wrapper = read(STACK["wrapper"])
    example = read(STACK["example"])

    require_terms(
        agent,
        [
            "The Agentic-Code Rot Model",
            "Compatibility Surface Map",
            "Evidence Ladder and Confidence",
            "Generated, Vendored, and Derived Artifacts",
            "Characterization Tests and Incidental Behavior",
            "Maintenance Economics",
            "Comment and Documentation Contract",
            "Cross-Language Adaptation",
            "Future-Agent Context Efficiency",
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
            "Evidence Ladder",
            "Compatibility Surface Map",
            "Characterization Policy",
            "Generated/Vendored/Lockfile Procedure",
            "Maintenance Economics",
            "Comment drift",
            "Abstraction inflation",
            "Failure-handling slop",
            "Efficiency slop",
            "Language-Aware Verification",
            "Future-Agent Context Efficiency",
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
            "COMPATIBILITY SURFACE MAP",
            "EVIDENCE LADDER",
            "SLOP INVENTORY",
            "MAINTENANCE ECONOMICS",
            "REFACTOR INVARIANT",
            "CHARACTERIZATION POLICY",
            "COMMENT CONTRACT",
            "GENERATED / VENDORED / DERIVED ARTIFACT CONTRACT",
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
            "Compatibility Surface Map",
            "Evidence and Confidence",
            "Generated, Vendored, and Lockfile Policy",
            "Characterization Tests",
            "Cross-Language Behavior",
            "Maintenance Economics",
            "Future-Agent Context Efficiency",
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
        "characterization test would freeze a suspected bug",
        "generated source and deterministic regeneration",
        "vendored/minified code exclusion",
        "git history prevents regression",
        "history is not authority",
        "lockfile ownership",
        "public surface compatibility check",
        "churn budget",
        "future-agent discoverability without boundary collapse",
    ]:
        if term not in acceptance_lower:
            failures.append(f"{STACK['acceptance_tests']}: missing adversarial case {term!r}")

    case_count = acceptance_lower.count("## case ")
    if case_count < 40:
        failures.append(f"{STACK['acceptance_tests']}: expected at least 40 adversarial cases, found {case_count}")

    require_terms(
        wrapper,
        [
            STACK["agent"],
            STACK["skill"],
            "compatibility surfaces",
            "characterization",
            "generated",
            "evidence levels/confidence",
            "Comment Contract",
            "second-pass",
        ],
        STACK["wrapper"],
        failures,
    )

    require_terms(
        example,
        [
            "generated_artifact_policy: source_and_regenerate",
            "require_history_for_ambiguous_intent: true",
            "minimum_removal_confidence: high",
            "distinguish_contractual_from_incidental_behavior: true",
            "require_independent_evidence_for_high_blast_radius: true",
            "allow_unrelated_formatting: false",
            "require_independent_slice_verification: true",
            "compatibility_checks:",
            "reproducibility_checks:",
        ],
        STACK["example"],
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
    print("PASS: compatibility/evidence/churn/generated-artifact contracts")
    print("PASS: comment/refactor/efficiency safety invariants")
    print("PASS: routing and wrapper references")
    print("PASS: adversarial acceptance-test coverage (40+ cases)")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
