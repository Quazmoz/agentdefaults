#!/usr/bin/env python3
"""Run the complete AgentDefaults validation suite."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VALIDATORS = [
    ROOT / "scripts/validate-agentdefaults-core.py",
    ROOT / "scripts/validate-cross-tool-routing.py",
    ROOT / "scripts/validate-engineering-contracts.py",
    ROOT / "scripts/validate-documentation-stack.py",
    ROOT / "scripts/validate-devsecops-security-stack.py",
    ROOT / "scripts/validate-codebase-maintenance-stack.py",
    ROOT / "scripts/validate-bounded-completion.py",
]


def main() -> int:
    failed: list[str] = []
    for validator in VALIDATORS:
        print(f"\n==> {validator.relative_to(ROOT)}", flush=True)
        result = subprocess.run([sys.executable, str(validator)], cwd=ROOT, check=False)
        if result.returncode != 0:
            failed.append(str(validator.relative_to(ROOT)))

    if failed:
        print("\nAgentDefaults validation suite: FAIL")
        for validator in failed:
            print(f"  - {validator}")
        return 1

    print("\nAgentDefaults validation suite: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
