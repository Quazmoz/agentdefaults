#!/usr/bin/env python3
"""Statically validate the repo-local Ponytail + Graft installer contract."""

from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
SIDECAR = ROOT / ".agent-tools" / "ponytail-graft"
BOOTSTRAP = SIDECAR / "bootstrap.cjs"
CORE = SIDECAR / "bootstrap-core.cjs"
PACKAGE = SIDECAR / "package.json"
LOCK = SIDECAR / "package-lock.json"
GUIDE = ROOT / "prompts" / "ponytail-graft" / "README.md"
HANDOFF = ROOT / "prompts" / "ponytail-graft" / "CROSS_REPO_HANDOFF.md"
ROUTER = ROOT / "prompts" / "ponytail-graft" / "ponytail-graft.md"
BASELINE = ROOT / "prompts" / "ponytail-graft" / "multi-repo-ponytail-graft.md"
HARDENING = ROOT / "prompts" / "ponytail-graft" / "HARDENING.md"

EXPECTED_PACKAGES = {
    "@dietrichgebert/ponytail",
    "@nanonets/graft",
}


def fail(message: str) -> int:
    print(f"FAIL: Ponytail + Graft installer: {message}")
    return 1


def main() -> int:
    required = [
        BOOTSTRAP,
        CORE,
        PACKAGE,
        LOCK,
        GUIDE,
        HANDOFF,
        ROUTER,
        BASELINE,
        HARDENING,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        return fail(f"missing required files: {', '.join(missing)}")

    bootstrap = BOOTSTRAP.read_text(encoding="utf-8")
    guide = GUIDE.read_text(encoding="utf-8")
    handoff = HANDOFF.read_text(encoding="utf-8")
    router = ROUTER.read_text(encoding="utf-8")
    hardening = HARDENING.read_text(encoding="utf-8")

    required_bootstrap_fragments = [
        "bootstrap-core.cjs",
        "rejectSymlinkComponents",
        "fs.lstatSync",
        "npm', ['ci'",
        "package-lock.json",
        "['repo', 'workspace']",
        "DO_NOT_TRACK",
        "graftHealthCheck",
        "['--help']",
        "['init', '--list-agents']",
        "runNpmCiRepair",
        "repo-local Graft runtime is unhealthy despite matching package pins",
    ]
    for fragment in required_bootstrap_fragments:
        if fragment not in bootstrap:
            return fail(f"bootstrap is missing hardening fragment {fragment!r}")

    if "--ignore-scripts" in bootstrap:
        return fail("bootstrap contains forbidden --ignore-scripts install behavior")

    # The health check and bounded repair must execute before bootstrap-core is delegated to.
    health_pos = bootstrap.find("let health = graftHealthCheck()")
    core_exec_pos = bootstrap.find("execFileSync(process.execPath, [CORE")
    if health_pos < 0 or core_exec_pos < 0 or health_pos > core_exec_pos:
        return fail("runtime health gate does not execute before bootstrap-core delegation")

    forbidden_canonical_fragments = [
        "npm install -g @nanonets/graft",
        "npm install -g @dietrichgebert/ponytail",
        "npx -y @nanonets/graft",
    ]
    for path, text in [
        (BOOTSTRAP, bootstrap),
        (GUIDE, guide),
        (HANDOFF, handoff),
        (ROUTER, router),
        (HARDENING, hardening),
    ]:
        for fragment in forbidden_canonical_fragments:
            if fragment in text:
                return fail(
                    f"{path.relative_to(ROOT)} contains forbidden canonical "
                    f"global/floating install command {fragment!r}"
                )

    if "multi-repo-ponytail-graft.md" not in router or "HARDENING.md" not in router:
        return fail("compatibility prompt does not route to both portable baseline and hardening contract")
    if "explicit repository choice" not in hardening or "must not automatically install" not in hardening:
        return fail("hardening contract does not preserve the opt-in boundary")

    required_runtime_contract = [
        "Do not use `--ignore-scripts`",
        "Runtime health gate",
        "graft.cjs --help",
        "graft.cjs init --list-agents",
        "one** clean `npm ci --no-audit --no-fund` repair",
    ]
    for fragment in required_runtime_contract:
        if fragment not in hardening:
            return fail(f"hardening contract is missing runtime-safety requirement {fragment!r}")

    if "never use `--ignore-scripts`" not in router:
        return fail("compatibility prompt does not forbid noncanonical --ignore-scripts sidecar installs")

    # Cross-repository transport regression: a fresh target is allowed to start without
    # AgentDefaults source files or the managed sidecar. The handoff must resolve one
    # coherent AgentDefaults source snapshot rather than searching the target/its origin.
    required_handoff_fragments = [
        "https://github.com/Quazmoz/agentdefaults",
        "TARGET_DIR",
        "git rev-parse HEAD",
        "prompts/ponytail-graft/ponytail-graft.md",
        "prompts/ponytail-graft/multi-repo-ponytail-graft.md",
        "prompts/ponytail-graft/HARDENING.md",
        "Their absence in `TARGET_DIR` is **expected before installation and is not a blocker**",
        "Do not search TARGET_DIR or the target repository's origin",
        "Do not require .agent-tools/ponytail-graft to exist before the installer creates it.",
        "Do not misdiagnose the situation as the target repository missing required setup artifacts.",
        "one coherent AgentDefaults source snapshot",
    ]
    for fragment in required_handoff_fragments:
        if fragment not in handoff:
            return fail(f"cross-repo handoff is missing regression requirement {fragment!r}")

    if "CROSS_REPO_HANDOFF.md" not in guide:
        return fail("setup guide does not expose the cross-repository handoff")

    required_guide_fragments = [
        "relative links in `ponytail-graft.md` navigate the **AgentDefaults source tree**",
        "They are not prerequisites that must already exist inside `TARGET_DIR`",
        "This is normal on first install",
        "do **not** search the target or its origin for AgentDefaults source files",
    ]
    for fragment in required_guide_fragments:
        if fragment not in guide:
            return fail(f"setup guide is missing cross-repo guidance {fragment!r}")

    package = json.loads(PACKAGE.read_text(encoding="utf-8"))
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    dependencies = package.get("dependencies", {})
    if set(dependencies) != EXPECTED_PACKAGES:
        return fail(f"sidecar dependencies changed: expected {sorted(EXPECTED_PACKAGES)}, got {sorted(dependencies)}")

    for name, version in dependencies.items():
        parts = version.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            return fail(f"{name} is not pinned to an exact x.y.z version: {version!r}")
        locked = lock.get("packages", {}).get(f"node_modules/{name}", {}).get("version")
        if locked != version:
            return fail(f"lock mismatch for {name}: package.json={version}, package-lock.json={locked}")

    print(
        "PASS: Ponytail + Graft installer hardening, runtime health gate, "
        "cross-repo handoff, and pin isolation"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
