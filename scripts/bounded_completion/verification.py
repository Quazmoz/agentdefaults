from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import (
    TERMINAL, Paths, PipelineError, prune_logs, read_active, sha256_bytes,
    utc_now, workspace_fingerprint, write_json,
)


def verification_checks(contract: dict[str, Any]) -> list[dict[str, Any]]:
    verification = contract["verification"]
    checks = [{"id": "canonical", "command": verification["canonical_command"], "required": True}]
    for item in verification.get("required_checks", []) or []:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise PipelineError("verification.required_checks entries must be objects with stable id")
        checks.append({"id": item["id"], "command": item.get("command"), "required": item.get("required", True)})
    ids = [item["id"] for item in checks]
    if len(ids) != len(set(ids)):
        raise PipelineError("verification check IDs must be unique")
    return checks


def _run_check(root: Path, argv: list[str], timeout: int) -> tuple[str, int | None, str, str]:
    try:
        proc = subprocess.run(argv, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    except FileNotFoundError as exc:
        return "UNAVAILABLE", None, "", str(exc)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(errors="replace")
        stderr = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(errors="replace")
        return "TIMEOUT", None, stdout, stderr
    return ("PASS" if proc.returncode == 0 else "FAIL", proc.returncode, proc.stdout, proc.stderr)


def verify(paths: Paths) -> dict[str, Any]:
    _, contract, state, _ = read_active(paths)
    if state["status"] in TERMINAL:
        raise PipelineError(f"cannot verify a terminal task in state {state['status']}")
    timeout = state["limits"]["verification_timeout_seconds"]
    state["status"] = state["phase"] = "VERIFYING"
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    fingerprint = workspace_fingerprint(paths.root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    task_log_dir = paths.logs / state["task_id"].replace("/", "-")
    log_path = task_log_dir / f"verification-{stamp}-{int(time.time_ns() % 1_000_000):06d}.log"
    task_log_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"task_id={state['task_id']}\nworkspace_fingerprint={fingerprint}\nstarted_at={utc_now()}\n")
        for check in verification_checks(contract):
            command = check.get("command")
            if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
                status, code, stdout, stderr = "UNAVAILABLE", None, "", "No executable argv configured for required check."
            else:
                status, code, stdout, stderr = _run_check(paths.root, command, timeout)
            digest = sha256_bytes((stdout[-4096:] + "\n" + stderr[-4096:]).encode(errors="replace"))
            result = {
                "id": check["id"], "required": bool(check["required"]), "status": status,
                "returncode": code, "command": command, "output_sha256": digest,
            }
            results.append(result)
            log.write(f"\n=== {check['id']} status={status} required={bool(check['required'])} returncode={code} ===\n")
            if command:
                log.write("command=" + json.dumps(command) + "\n")
            log.write("--- stdout ---\n" + stdout + "\n--- stderr ---\n" + stderr + "\n")
    required_bad = [r for r in results if r["required"] and r["status"] != "PASS"]
    overall = "PASS" if not required_bad else "FAIL"
    sig_data = [(r["id"], r["status"], r["returncode"], r["output_sha256"]) for r in results if r["required"]]
    signature = sha256_bytes(json.dumps(sig_data, sort_keys=True).encode()) if overall == "FAIL" else None
    if overall == "FAIL":
        state["repeated_failure_count"] = state["repeated_failure_count"] + 1 if signature == state.get("last_failure_signature") else 1
        state["last_failure_signature"] = signature
        state["requires_independent_diagnosis"] = state["repeated_failure_count"] >= state["limits"]["max_unchanged_failure_attempts"]
        if any(r["status"] == "UNAVAILABLE" for r in required_bad):
            state["status"] = state["phase"] = "ESCALATED"
            state["known_blockers"].append("required verification command unavailable")
        elif state["repeated_failure_count"] > state["limits"]["max_unchanged_failure_attempts"]:
            state["status"] = state["phase"] = "ESCALATED"
            state["known_blockers"].append("maximum unchanged verification failure attempts exceeded")
        else:
            state["status"] = state["phase"] = "FIXING"
    else:
        state["repeated_failure_count"] = 0
        state["last_failure_signature"] = None
        state["requires_independent_diagnosis"] = False
        state["status"] = state["phase"] = "REVIEWING"
    state["last_verification"] = {
        "result": overall, "workspace_fingerprint": fingerprint,
        "log_path": str(log_path.relative_to(paths.root)), "checks": results,
        "completed_at": utc_now(),
    }
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    prune_logs(paths, state["limits"]["max_retained_verification_logs"], state["task_id"])
    return state["last_verification"]
