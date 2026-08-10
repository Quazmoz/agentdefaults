#!/usr/bin/env python3
"""Validate AgentDefaults structure, schemas, manifests, stack integrity, and local links."""

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

AGENT_BUILDER_REQUIRED_FILES = [
    "agents/agent-architect-builder.md",
    "skills/agent-design-and-build.md",
    "prompts/planning/build-ai-agent.md",
    "schemas/agent-build-brief.schema.json",
    "examples/agent-build-brief.yaml",
    "docs/quickstarts/agent-builder.md",
    "docs/agent-builder-acceptance-tests.md",
    "docs/patterns/agent.md",
    ".github/agents/agent-architect-builder.agent.md",
]

AUTOMATION_PLATFORM_REQUIRED_FILES = [
    "AUTOMATION_PLATFORM_INDEX.md",
    "agents/automation-platform-selection-advisor.md",
    "skills/automation-platform-capability-taxonomy.md",
    "skills/automation-platform-decision-framework.md",
    "skills/automation-platform-candidate-discovery.md",
    "skills/automation-platform-evidence-and-confidence.md",
    "skills/automation-platform-migration-and-economics.md",
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

PERMISSION_CLASSES = [
    "observe",
    "propose",
    "mutate_reversible",
    "mutate_irreversible",
]

AGENT_BUILD_MODES = [
    "blueprint",
    "build",
    "stack",
    "audit",
]

AGENT_ARCHITECTURES = [
    "auto",
    "single_agent",
    "single_agent_with_skills",
    "multi_agent",
]

CANONICAL_CAPABILITY_CLASSES = [
    "infrastructure_as_code",
    "configuration_management",
    "ci_cd",
    "gitops_continuous_delivery",
    "runbook_automation",
    "managed_iac_execution",
    "durable_workflow_orchestration",
    "verification_and_reporting",
    "adjacent_capability",
    "unsupported_capability",
]

OUTPUT_DEPTHS = [
    "quick_triage",
    "standard",
    "full_architecture_review",
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
LOCAL_REF_PATTERN = re.compile(r"^#/$defs/([A-Za-z0-9_-]+)$")


def print_fail(title: str, failures: Iterable[str]) -> int:
    print(f"FAIL: {title}")
    for failure in failures:
        print(f"  - {failure}")
    return 1


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def check_required_files() -> int:
    required = (
        CORE_REQUIRED_FILES
        + AGENT_BUILDER_REQUIRED_FILES
        + AUTOMATION_PLATFORM_REQUIRED_FILES
    )
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


def iter_local_refs(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref
        for child in value.values():
            yield from iter_local_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_local_refs(child)


def check_json_files() -> int:
    failures: list[str] = []
    paths = json_files()
    for path in paths:
        try:
            value = load_json(path)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"{path.relative_to(ROOT)}: {exc}")
            continue

        if path.parent.name == "schemas":
            defs = value.get("$defs", {}) if isinstance(value, dict) else {}
            for ref in iter_local_refs(value):
                match = LOCAL_REF_PATTERN.fullmatch(ref)
                if match and match.group(1) not in defs:
                    failures.append(
                        f"{path.relative_to(ROOT)}: unresolved local schema reference {ref}"
                    )

    if failures:
        return print_fail("JSON files", failures)
    print(f"PASS: JSON files and local references ({len(paths)} checked)")
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


def require_terms(text: str, terms: Iterable[str], label: str, failures: list[str]) -> None:
    for term in terms:
        if term not in text:
            failures.append(f"{label} missing required term: {term}")


def check_agent_builder_stack() -> int:
    failures: list[str] = []

    manifest = load_json(ROOT / "agentdefaults.manifest.json")
    stacks = manifest.get("featured_stacks", [])
    stack = next(
        (
            item for item in stacks
            if isinstance(item, dict)
            and item.get("name") == "Agent Architect and Builder"
        ),
        None,
    )

    if stack is None:
        failures.append("agent builder stack is not registered")
    else:
        expected = {
            "quickstart": "docs/quickstarts/agent-builder.md",
            "agent": "agents/agent-architect-builder.md",
            "schema": "schemas/agent-build-brief.schema.json",
            "example": "examples/agent-build-brief.yaml",
            "acceptance_tests": "docs/agent-builder-acceptance-tests.md",
            "wrapper": ".github/agents/agent-architect-builder.agent.md",
        }
        for field, value in expected.items():
            if stack.get(field) != value:
                failures.append(
                    f"agent builder manifest {field} must be {value!r}"
                )
        if stack.get("skills") != ["skills/agent-design-and-build.md"]:
            failures.append("agent builder manifest skills are not canonical")
        if stack.get("prompts") != ["prompts/planning/build-ai-agent.md"]:
            failures.append("agent builder manifest prompt is not canonical")

    schema = load_json(ROOT / "schemas/agent-build-brief.schema.json")
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    defs = schema.get("$defs", {})

    for name in ["target", "runtime", "authority", "validation"]:
        if name not in properties or name not in required:
            failures.append(f"agent build schema must require {name}")

    permission_enum = defs.get("permissionClass", {}).get("enum", [])
    if permission_enum != PERMISSION_CLASSES:
        failures.append("agent build schema permissionClass enum is not canonical or ordered")

    target_properties = properties.get("target", {}).get("properties", {})
    build_mode_enum = target_properties.get("build_mode", {}).get("enum", [])
    if build_mode_enum != AGENT_BUILD_MODES:
        failures.append("agent build schema build_mode enum is not canonical or ordered")

    architecture_enum = target_properties.get("architecture_preference", {}).get("enum", [])
    if architecture_enum != AGENT_ARCHITECTURES:
        failures.append("agent build schema architecture enum is not canonical or ordered")

    runtime_capability_schema = (
        properties.get("runtime", {})
        .get("properties", {})
        .get("capabilities", {})
    )
    runtime_capabilities = runtime_capability_schema.get("items", {}).get("enum", [])
    if runtime_capability_schema.get("minItems") != 1:
        failures.append("agent build schema runtime.capabilities must require at least one value")
    for capability in [
        "background_execution",
        "persistent_memory",
        "structured_output",
        "subagents",
        "unknown",
    ]:
        if capability not in runtime_capabilities:
            failures.append(f"agent build schema lacks runtime capability: {capability}")

    schema_text = json.dumps(schema, sort_keys=True)
    if '"const": "mutate_irreversible"' not in schema_text:
        failures.append("agent build schema lacks irreversible-action conditional validation")
    if '"const": true' not in schema_text or "approval_required" not in schema_text:
        failures.append("agent build schema does not require approval for irreversible tools")
    authority_text = json.dumps(properties.get("authority", {}), sort_keys=True)
    if "approval_gates" not in authority_text or '"minItems": 1' not in authority_text:
        failures.append("agent build schema does not require an approval gate for irreversible authority")

    agent_text = (ROOT / "agents/agent-architect-builder.md").read_text(encoding="utf-8")
    skill_text = (ROOT / "skills/agent-design-and-build.md").read_text(encoding="utf-8")
    prompt_text = (ROOT / "prompts/planning/build-ai-agent.md").read_text(encoding="utf-8")
    acceptance_text = (ROOT / "docs/agent-builder-acceptance-tests.md").read_text(encoding="utf-8")
    example_text = (ROOT / "examples/agent-build-brief.yaml").read_text(encoding="utf-8")
    pattern_text = (ROOT / "docs/patterns/agent.md").read_text(encoding="utf-8")
    quickstart_text = (ROOT / "docs/quickstarts/agent-builder.md").read_text(encoding="utf-8")
    wrapper_text = (ROOT / ".github/agents/agent-architect-builder.agent.md").read_text(encoding="utf-8")

    for token in PERMISSION_CLASSES:
        for label, text in [
            ("agent builder", agent_text),
            ("agent design skill", skill_text),
            ("agent build prompt", prompt_text),
            ("agent pattern", pattern_text),
        ]:
            require_terms(text, [token], label, failures)

    for mode in AGENT_BUILD_MODES:
        require_terms(agent_text, [mode], "agent builder", failures)

    for term in [
        "authoritative",
        "idempotency",
        "stop",
        "unverified",
        "retrieved content",
    ]:
        require_terms(agent_text, [term], "agent builder", failures)
        require_terms(skill_text, [term], "agent design skill", failures)

    require_terms(
        pattern_text,
        [
            "## Completion and Stop Contract",
            "## Acceptance Tests",
            "postcondition_check",
            "mutate_irreversible",
        ],
        "agent pattern",
        failures,
    )

    require_terms(
        example_text,
        [
            "target:",
            "runtime:",
            "maximum_permission_class:",
            "postcondition_check:",
            "duplicate_suppression:",
            "completion_criteria:",
        ],
        "agent build example",
        failures,
    )

    require_terms(
        quickstart_text,
        [
            "schemas/agent-build-brief.schema.json",
            "docs/agent-builder-acceptance-tests.md",
            "docs/patterns/agent.md",
            "Not verified:",
        ],
        "agent builder quickstart",
        failures,
    )

    require_terms(
        wrapper_text,
        [
            "agents/agent-architect-builder.md",
            "skills/agent-design-and-build.md",
            "Not verified:",
        ],
        "agent builder wrapper",
        failures,
    )

    for scenario in range(1, 23):
        if f"### {scenario}." not in acceptance_text:
            failures.append(f"agent builder acceptance tests missing scenario {scenario}")

    require_terms(
        acceptance_text,
        [
            "Fictional Runtime Capability",
            "Unnecessary Multi-Agent Design",
            "Retrieved Prompt Injection",
            "Ambiguous Non-Idempotent Timeout",
            "Validation Truthfulness",
            "Tool Authority Ambiguity",
        ],
        "agent builder acceptance tests",
        failures,
    )

    if failures:
        return print_fail("agent builder stack", failures)
    print("PASS: agent builder stack integrity")
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
        failures.append("automation platform stack is not registered")
    else:
        registered = set(stack.get("skills", []))
        required_skills = {
            path for path in AUTOMATION_PLATFORM_REQUIRED_FILES
            if path.startswith("skills/")
        }
        missing_skills = sorted(required_skills - registered)
        failures.extend(f"automation skill missing from manifest: {path}" for path in missing_skills)

    schema = load_json(ROOT / "schemas/automation-platform-decision-brief.schema.json")
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    defs = schema.get("$defs", {})

    if "platform_selection" not in properties or "platform_selection" not in required:
        failures.append("decision schema must require platform_selection")

    capability_enum = defs.get("capabilityClass", {}).get("enum", [])
    if capability_enum != CANONICAL_CAPABILITY_CLASSES:
        failures.append("decision schema capabilityClass enum is not canonical or ordered")

    selection = properties.get("platform_selection", {})
    selection_properties = selection.get("properties", {})
    for name in [
        "candidate_policy",
        "output_depth",
        "decision_horizon_months",
        "risk_tolerance",
        "shortlist_limit",
        "allowed_hosting_models",
        "minimum_evidence_coverage",
        "custom_weights",
    ]:
        if name not in selection_properties:
            failures.append(f"decision schema has no platform_selection.{name}")

    output_depth_enum = selection_properties.get("output_depth", {}).get("enum", [])
    if output_depth_enum != OUTPUT_DEPTHS:
        failures.append("decision schema output-depth enum is not canonical or ordered")

    all_of = selection.get("allOf", [])
    selection_text = json.dumps(selection, sort_keys=True)
    if len(all_of) < 2 or "self_hosted_required" not in selection_text:
        failures.append("decision schema lacks self-hosted consistency validation")
    if "air_gapped_required" not in selection_text or '"const": "air_gapped"' not in selection_text:
        failures.append("decision schema lacks air-gapped consistency validation")

    taxonomy_text = (ROOT / "skills/automation-platform-capability-taxonomy.md").read_text(encoding="utf-8")
    framework_text = (ROOT / "skills/automation-platform-decision-framework.md").read_text(encoding="utf-8")
    agent_text = (ROOT / "agents/automation-platform-selection-advisor.md").read_text(encoding="utf-8")
    orchestrator_text = (ROOT / "skills/automation-platform-selection-orchestrator.md").read_text(encoding="utf-8")
    prompt_text = (ROOT / "prompts/planning/select-automation-platform.md").read_text(encoding="utf-8")
    acceptance_text = (ROOT / "docs/automation-platform-selection-acceptance-tests.md").read_text(encoding="utf-8")
    example_text = (ROOT / "examples/automation-platform-decision-brief.yaml").read_text(encoding="utf-8")

    for token in CANONICAL_CAPABILITY_CLASSES:
        require_terms(taxonomy_text, [token], "taxonomy", failures)
        require_terms(framework_text, [token], "decision framework", failures)

    forbidden_tokens = ["GitOps_continuous_delivery"]
    for token in forbidden_tokens:
        for label, text in [
            ("taxonomy", taxonomy_text),
            ("decision framework", framework_text),
            ("agent", agent_text),
            ("orchestrator", orchestrator_text),
            ("planning prompt", prompt_text),
        ]:
            if token in text:
                failures.append(f"{label} contains noncanonical capability token: {token}")

    require_terms(
        agent_text,
        [
            "GitHub Actions",
            "Azure Pipelines",
            "Puppet",
            "Chef Infra",
            "OpenTofu",
            "Pulumi",
            "Argo CD",
            "Flux",
            "evidence coverage",
            "do-nothing baseline",
            "quick_triage",
            "full_architecture_review",
        ],
        "automation advisor",
        failures,
    )

    for mode in OUTPUT_DEPTHS:
        require_terms(orchestrator_text, [mode], "orchestrator", failures)
        require_terms(prompt_text, [mode], "planning prompt", failures)

    require_terms(
        example_text,
        [
            "platform_selection:",
            "output_depth:",
            "decision_horizon_months:",
            "risk_tolerance:",
            "shortlist_limit:",
            "minimum_evidence_coverage:",
            "custom_weights:",
            "evidence_ledger",
            "migration_economics",
            "reversibility_plan",
        ],
        "automation example",
        failures,
    )

    for scenario in range(1, 26):
        if f"### {scenario}." not in acceptance_text:
            failures.append(f"acceptance tests missing scenario {scenario}")

    require_terms(
        acceptance_text,
        [
            "Unknown evidence is not failure",
            "Effective scoring tie",
            "Migration economics reverse the feature winner",
            "Output-depth discipline",
            "Contradictory hosting constraints",
        ],
        "acceptance tests",
        failures,
    )

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
        + check_agent_builder_stack()
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
