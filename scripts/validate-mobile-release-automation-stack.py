#!/usr/bin/env python3
"""Validate the Mobile Release and Monetization Automation stack and routing."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest import mock
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

STACK_NAME = "Mobile Release and Monetization Automation"
STACK = {
    "quickstart": "docs/quickstarts/mobile-release-automation.md",
    "agent": "agents/mobile-release-automation-engineer.md",
    "prompt": "prompts/implementation/mobile-release-automation-task.md",
    "schema": "schemas/mobile-release-automation-task.schema.json",
    "example": "examples/mobile-release-automation-task.yaml",
    "acceptance_tests": "docs/mobile-release-automation-acceptance-tests.md",
    "wrapper": ".github/agents/mobile-release-automation-engineer.agent.md",
}

SKILLS = [
    "skills/mobile-release-automation-orchestration.md",
    "skills/google-play-release-automation.md",
    "skills/revenuecat-monetization-automation.md",
    "skills/admob-inventory-automation.md",
]

TOOLKIT_FILES = [
    "tools/mobile-release-automation/README.md",
    "tools/mobile-release-automation/pyproject.toml",
    "tools/mobile-release-automation/requirements.txt",
    "tools/mobile-release-automation/mra/__init__.py",
    "tools/mobile-release-automation/mra/config.py",
    "tools/mobile-release-automation/mra/auth.py",
    "tools/mobile-release-automation/mra/play.py",
    "tools/mobile-release-automation/mra/admob.py",
    "tools/mobile-release-automation/mra/revenuecat.py",
    "tools/mobile-release-automation/mra/revenuecat_cli.py",
    "tools/mobile-release-automation/mra/cli.py",
    "tools/mobile-release-automation/mra/mcp_server.py",
    "tools/mobile-release-automation/tests/test_play.py",
    "tools/mobile-release-automation/tests/test_admob.py",
    "tools/mobile-release-automation/tests/test_revenuecat.py",
    "tools/mobile-release-automation/tests/test_revenuecat_cli.py",
    "tools/mobile-release-automation/tests/test_safety.py",
    "tools/mobile-release-automation/tests/test_mcp_server.py",
]

ROUTING_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "ENGINEERING_AGENTS_INDEX.md",
    "INDEX.md",
]

PERMISSION_CLASSES = ["observe", "propose", "mutate_reversible", "mutate_irreversible"]
MODES = ["assess", "setup", "release", "monetize", "inventory", "diagnose"]
PLATFORMS = ["google_play", "revenuecat", "admob"]
PROBE_STATES = ["denied", "likely", "unknown", "not_probed"]

ADMOB_INVARIANTS = [
    "limited access",
    "account manager",
    "OAuth",
]

REVENUECAT_INVARIANTS = [
    "OAuth",
    "official RevenueCat CLI",
    "project-scoped",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def load_json(path: str) -> dict[str, Any]:
    value = json.loads(read(path))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def check_required_files(failures: list[str]) -> None:
    required = set(STACK.values()) | set(SKILLS) | set(TOOLKIT_FILES) | set(ROUTING_FILES)
    required |= {
        "agentdefaults.manifest.json",
        "scripts/validate-agentdefaults.py",
        "scripts/validate-mobile-release-automation-stack.py",
    }
    for path in sorted(required):
        if not (ROOT / path).is_file():
            failures.append(f"missing mobile-release-automation stack file: {path}")


def check_manifest(failures: list[str]) -> None:
    manifest = load_json("agentdefaults.manifest.json")
    stack = next(
        (
            entry
            for entry in manifest.get("featured_stacks", [])
            if isinstance(entry, dict) and entry.get("name") == STACK_NAME
        ),
        None,
    )
    if stack is None:
        failures.append(f"manifest is missing featured stack: {STACK_NAME}")
        return

    for key, expected in STACK.items():
        if key == "prompt":
            if expected not in stack.get("prompts", []):
                failures.append(f"manifest {STACK_NAME}.prompts should include {expected}")
            continue
        if stack.get(key) != expected:
            failures.append(f"manifest {STACK_NAME}.{key} should be {expected}")

    declared = stack.get("skills")
    if declared != SKILLS:
        failures.append(f"manifest {STACK_NAME}.skills should list exactly {SKILLS}")


def check_schema(failures: list[str]) -> None:
    schema = load_json(STACK["schema"])

    if schema.get("additionalProperties") is not False:
        failures.append("task schema must reject unknown top-level keys")

    required = schema.get("required", [])
    for field in ("goal", "mode", "platforms", "app", "authority", "acceptance"):
        if field not in required:
            failures.append(f"task schema must require {field}")

    properties = schema.get("properties", {})

    modes = properties.get("mode", {}).get("enum", [])
    if sorted(modes) != sorted(MODES):
        failures.append(f"task schema modes should be {MODES}")

    platforms = properties.get("platforms", {}).get("items", {}).get("enum", [])
    if sorted(platforms) != sorted(PLATFORMS):
        failures.append(f"task schema platforms should be {PLATFORMS}")

    permission = (
        properties.get("authority", {}).get("properties", {}).get("permission_class", {})
    )
    if sorted(permission.get("enum", [])) != sorted(PERMISSION_CLASSES):
        failures.append(f"task schema permission_class should be {PERMISSION_CLASSES}")

    probe = (
        properties.get("execution", {})
        .get("properties", {})
        .get("admob_access_probed", {})
    )
    if sorted(probe.get("enum", [])) != sorted(PROBE_STATES):
        failures.append(f"task schema admob_access_probed should be {PROBE_STATES}")

    release = properties.get("release", {})
    if not any(
        rule.get("if", {}).get("properties", {}).get("status", {}).get("const") == "inProgress"
        and "user_fraction" in rule.get("then", {}).get("required", [])
        for rule in release.get("allOf", [])
    ):
        failures.append("task schema must require user_fraction when status is inProgress")

    if not any(
        "admob" in json.dumps(rule.get("if", {}))
        and "execution" in json.dumps(rule.get("then", {}))
        for rule in schema.get("allOf", [])
    ):
        failures.append("task schema must require an AdMob probe result for AdMob work")


def check_agent_contract(failures: list[str]) -> None:
    agent = read(STACK["agent"])

    for permission in PERMISSION_CLASSES:
        if permission not in agent:
            failures.append(f"agent must define permission class {permission}")

    for mode in MODES:
        if mode not in agent:
            failures.append(f"agent must define mode {mode}")

    for invariant in ADMOB_INVARIANTS:
        if invariant not in agent:
            failures.append(f"agent must state the AdMob constraint: {invariant}")

    for invariant in REVENUECAT_INVARIANTS:
        if invariant not in agent:
            failures.append(f"agent must state the RevenueCat auth constraint: {invariant}")

    for term, label in (
        ("Tool availability is not authorization", "authorization boundary"),
        ("promote", "promotion semantics"),
        ("read back", "platform read-back requirement"),
    ):
        if term not in agent:
            failures.append(f"agent must state the {label} ({term!r})")


def check_skill_contracts(failures: list[str]) -> None:
    orchestration = read("skills/mobile-release-automation-orchestration.md")
    for term in ("dependency", "dry run", "authoriz"):
        if term.lower() not in orchestration.lower():
            failures.append(f"orchestration skill must cover {term}")

    play = read("skills/google-play-release-automation.md")
    for term in ("uploadType=media", "edit", "version code"):
        if term not in play:
            failures.append(f"Play skill must cover {term}")

    revenuecat = read("skills/revenuecat-monetization-automation.md")
    for term in ("mcp.revenuecat.ai", "entitlement", "store_identifier", "rc auth login"):
        if term not in revenuecat:
            failures.append(f"RevenueCat skill must cover {term}")
    if "bootstrap key" not in revenuecat.lower() or "do not" not in revenuecat.lower():
        failures.append("RevenueCat skill must explicitly reject an sk_ bootstrap-key design")

    admob = read("skills/admob-inventory-automation.md")
    for invariant in ADMOB_INVARIANTS:
        if invariant not in admob:
            failures.append(f"AdMob skill must state the constraint: {invariant}")
    if "service account" not in admob.lower():
        failures.append("AdMob skill must state that service accounts do not work")
    if "console" not in admob.lower():
        failures.append("AdMob skill must forbid scripting the AdMob console")


def check_toolkit_safety(failures: list[str]) -> None:
    """The toolkit's safety properties are load-bearing for the agent contract."""
    cli = read("tools/mobile-release-automation/mra/cli.py")
    if "--yes" not in cli or "def confirm" not in cli:
        failures.append("CLI must gate mutating commands behind an explicit --yes")

    mcp_server = read("tools/mobile-release-automation/mra/mcp_server.py")
    if "confirm: bool = False" not in mcp_server:
        failures.append("MCP server mutating tools must default confirm to False")
    if "dry_run: bool = True" not in mcp_server:
        failures.append("MCP server publish must default dry_run to True")

    config = read("tools/mobile-release-automation/mra/config.py")
    if "_require_private" not in config:
        failures.append("config must refuse group/world readable credential files")

    admob = read("tools/mobile-release-automation/mra/admob.py")
    if "AdMobAccessDenied" not in admob:
        failures.append("AdMob client must distinguish access denial from other errors")

    play = read("tools/mobile-release-automation/mra/play.py")
    if "_delete_edit_quietly" not in play:
        failures.append("Play client must clean up edits that are not committed")

    rc_cli = read("tools/mobile-release-automation/mra/revenuecat_cli.py")
    for term in ("RC_API_KEY", "REVENUECAT_V2_SECRET_KEY", "rc auth login"):
        if term not in rc_cli:
            failures.append(f"RevenueCat OAuth transport must enforce {term!r}")
    check_revenuecat_oauth_enforcement(failures)
    check_data_safety_is_never_claimed_verified(failures)

    rc_client = read("tools/mobile-release-automation/mra/revenuecat.py")
    if "revenuecat_cli.api_call" not in rc_client:
        failures.append("RevenueCat client must route production calls through official CLI OAuth")

def check_data_safety_is_never_claimed_verified(failures: list[str]) -> None:
    """Google publishes no read for safety labels, so this write is unverifiable.

    Asserted behaviorally: a result that omitted this marker would let an agent
    report a compliance declaration as platform verified when nothing can read
    it back.
    """
    sys.path.insert(0, str(ROOT / "tools/mobile-release-automation"))
    try:
        from mra import play as play_module, play_management
    except Exception as exc:  # noqa: BLE001
        failures.append(f"Play management surface is not importable: {exc}")
        return

    manager = play_management.PlayManagementClient(
        "com.example.app", client=play_module.PlayClient("com.example.app", session=object())
    )
    for dry_run in (True, False):
        try:
            result = manager.set_data_safety_labels("", dry_run=dry_run)
        except play_module.PlayError:
            continue  # an empty declaration must be refused, never submitted
        except Exception as exc:  # noqa: BLE001
            failures.append(
                f"empty data safety CSV raised {type(exc).__name__}, expected PlayError"
            )
            continue
        failures.append(f"empty data safety CSV was accepted (dry_run={dry_run}): {result}")

    probe = manager.set_data_safety_labels("field,value\n", dry_run=True)
    if probe.get("read_back") != "unsupported_by_api":
        failures.append(
            "data safety result must report read_back 'unsupported_by_api', "
            f"got {probe.get('read_back')!r}"
        )
    if probe.get("submitted") is not False:
        failures.append("a data safety dry run must not report itself as submitted")


def check_revenuecat_oauth_enforcement(failures: list[str]) -> None:
    """Prove the production RevenueCat path rejects API-key authentication.

    This is asserted behaviorally, not by grepping for an implementation shape:
    the CLI's `auth status` payload format has already changed once, and a source
    string that stops matching says nothing about whether the invariant holds.
    """
    sys.path.insert(0, str(ROOT / "tools/mobile-release-automation"))
    try:
        from mra import config as mra_config, revenuecat_cli
    except Exception as exc:  # noqa: BLE001 - import failure is itself a contract break
        failures.append(f"RevenueCat OAuth transport is not importable: {exc}")
        return

    def auth_status_for(data: dict[str, Any]) -> Any:
        completed = SimpleNamespace(
            returncode=0, stdout=json.dumps({"data": data}), stderr=""
        )
        with mock.patch.object(revenuecat_cli.shutil, "which", return_value="/usr/bin/rc"), \
             mock.patch.object(revenuecat_cli.subprocess, "run", return_value=completed):
            return revenuecat_cli.auth_status()

    must_reject = {
        "api-key method": {"authenticated": True, "method": "api_key"},
        # credential_source is the stable discriminator and must outrank a
        # decorated method string that merely looks like OAuth.
        "api-key credential_source": {
            "authenticated": True,
            "credential_source": "api_key",
            "method": "oauth (expires 2026-09-18 19:04)",
        },
        "unauthenticated session": {"authenticated": False, "method": "oauth"},
    }
    for label, data in must_reject.items():
        try:
            auth_status_for(data)
        except mra_config.ConfigError:
            continue
        except Exception as exc:  # noqa: BLE001
            failures.append(
                f"RevenueCat {label} must raise ConfigError, raised {type(exc).__name__}: {exc}"
            )
        else:
            failures.append(f"RevenueCat OAuth transport accepted {label}")

    must_accept = {
        "plain oauth": {"authenticated": True, "method": "oauth"},
        "cli-decorated oauth": {
            "authenticated": True,
            "credential_source": "oauth",
            "method": "oauth (expires 2026-09-18 19:04)",
        },
    }
    for label, data in must_accept.items():
        try:
            status = auth_status_for(data)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"RevenueCat OAuth transport rejected {label}: {exc}")
            continue
        if status.get("status") != "ready" or status.get("method") != revenuecat_cli.OAUTH_METHOD:
            failures.append(f"RevenueCat OAuth transport did not report {label} as ready OAuth")


def check_routing(failures: list[str]) -> None:
    for path in ROUTING_FILES:
        text = read(path)
        if STACK["agent"] not in text:
            failures.append(f"{path} must route to {STACK['agent']}")
        if SKILLS[0] not in text:
            failures.append(f"{path} must reference {SKILLS[0]}")

    wrapper = read(STACK["wrapper"])
    for path in [STACK["agent"], *SKILLS]:
        if path not in wrapper:
            failures.append(f"wrapper must reference {path}")


def check_acceptance_tests(failures: list[str]) -> None:
    text = read(STACK["acceptance_tests"])
    cases = text.count("\n## Case ")
    if cases < 10:
        failures.append(f"acceptance tests should define at least 10 cases, found {cases}")
    lowered = text.lower()
    for term in ("service account", "limited access", "unverified", "promote"):
        if term not in lowered:
            failures.append(f"acceptance tests must cover {term}")


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)

    if not failures:
        try:
            check_manifest(failures)
            check_schema(failures)
            check_agent_contract(failures)
            check_skill_contracts(failures)
            check_toolkit_safety(failures)
            check_routing(failures)
            check_acceptance_tests(failures)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            failures.append(str(exc))

    print("Mobile Release and Monetization Automation stack validation")
    print("===========================================================")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        print("\nResult: FAIL")
        return 1

    print("PASS: required stack, skill, and toolkit files")
    print("PASS: manifest registration")
    print("PASS: structured task schema contract")
    print("PASS: agent permission, mode, and platform auth invariants")
    print("PASS: per-platform skill contracts")
    print("PASS: toolkit confirmation gates and credential hygiene")
    print("PASS: routing and wrapper references")
    print("PASS: adversarial acceptance-test coverage")
    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
