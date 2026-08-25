from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TERMINAL = {"COMPLETE", "ESCALATED"}
VALID_DISPOSITIONS = {
    "accepted-blocking", "accepted-non-blocking", "rejected-with-evidence",
    "duplicate-resolved", "requires-user-input", "deferred-out-of-scope",
}
SEVERITIES = {"critical", "high", "medium", "low", "informational"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(value, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def contract_hash(contract: dict[str, Any]) -> str:
    return sha256_bytes(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode())


@dataclass(frozen=True)
class Paths:
    root: Path

    @property
    def config(self) -> Path:
        return self.root / "config/bounded-completion.json"

    @property
    def loop(self) -> Path:
        return self.root / ".agent-loop"

    @property
    def current(self) -> Path:
        return self.loop / "current"

    @property
    def archive(self) -> Path:
        return self.loop / "archive"

    @property
    def logs(self) -> Path:
        return self.loop / "logs"

    @property
    def contract(self) -> Path:
        return self.current / "task-contract.json"

    @property
    def state(self) -> Path:
        return self.current / "state.json"

    @property
    def findings(self) -> Path:
        return self.current / "findings.json"


class PipelineError(RuntimeError):
    pass


def validate_contract(contract: dict[str, Any]) -> None:
    required = ["task_id", "title", "description", "required_outcome", "acceptance_criteria", "verification"]
    missing = [key for key in required if key not in contract]
    if missing:
        raise PipelineError(f"task contract missing required fields: {', '.join(missing)}")
    criteria = contract.get("acceptance_criteria")
    if not isinstance(criteria, list) or not criteria:
        raise PipelineError("task contract acceptance_criteria must be a non-empty list")
    ids: list[str] = []
    for item in criteria:
        if not isinstance(item, dict):
            raise PipelineError("each acceptance criterion must be an object")
        for field in ("id", "description", "expected_evidence", "verification_method"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise PipelineError(f"acceptance criterion missing non-empty {field}")
        if item.get("status") != "PENDING":
            raise PipelineError("acceptance criterion status must start as PENDING; mutable status belongs in durable state")
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise PipelineError("acceptance criterion IDs must be unique")
    verification = contract.get("verification")
    if not isinstance(verification, dict):
        raise PipelineError("verification must be an object")
    command = verification.get("canonical_command")
    if not isinstance(command, list) or not command or not all(isinstance(x, str) and x for x in command):
        raise PipelineError("verification.canonical_command must be a non-empty argv array")


def effective_limits(config: dict[str, Any], contract: dict[str, Any]) -> dict[str, int]:
    defaults = config["limits"]
    overrides = contract.get("iteration_limits", {}) or {}
    result: dict[str, int] = {}
    for key, default in defaults.items():
        if not isinstance(default, int) or default < 1:
            raise PipelineError(f"invalid configured limit {key}")
        requested = overrides.get(key, default)
        if not isinstance(requested, int) or requested < 1:
            raise PipelineError(f"invalid task-specific limit {key}")
        result[key] = min(default, requested)
    return result


def _git(root: Path, args: list[str]) -> bytes:
    proc = subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise PipelineError(f"git {' '.join(args)} failed: {proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout


def workspace_fingerprint(root: Path) -> str:
    head = _git(root, ["rev-parse", "HEAD"]).strip()
    changed = _git(root, ["ls-files", "-m", "-d", "-o", "--exclude-standard", "-z"]).split(b"\0")
    h = hashlib.sha256()
    h.update(b"HEAD\0" + head + b"\0")
    for raw in sorted(p for p in changed if p):
        rel = raw.decode("utf-8", errors="surrogateescape")
        if rel == ".agent-loop" or rel.startswith(".agent-loop/"):
            continue
        h.update(rel.encode("utf-8", errors="surrogateescape") + b"\0")
        path = root / rel
        if path.is_symlink():
            h.update(b"SYMLINK\0" + os.readlink(path).encode(errors="surrogateescape"))
        elif path.is_file():
            h.update(b"FILE\0" + sha256_file(path).encode())
        elif not path.exists():
            h.update(b"DELETED")
        else:
            h.update(b"OTHER")
        h.update(b"\0")
    return h.hexdigest()


def read_active(paths: Paths) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if not paths.state.is_file() or not paths.contract.is_file() or not paths.findings.is_file():
        raise PipelineError("no active bounded-completion task; run init first")
    config = load_json(paths.config)
    contract = load_json(paths.contract)
    state = load_json(paths.state)
    findings = load_json(paths.findings)
    if contract_hash(contract) != state.get("task_contract_hash"):
        raise PipelineError("active task contract changed outside control-plane initialization; start a new task or restore the archived contract")
    return config, contract, state, findings


def archive_current(paths: Paths) -> Path | None:
    if not paths.current.exists() or not any(paths.current.iterdir()):
        return None
    state = load_json(paths.state) if paths.state.is_file() else {}
    task_id = str(state.get("task_id", "unknown")).replace("/", "-")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = paths.archive / f"{stamp}-{task_id}"
    suffix = 1
    while target.exists():
        target = paths.archive / f"{stamp}-{task_id}-{suffix}"
        suffix += 1
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(paths.current), str(target))
    return target


def prune_logs(paths: Paths, keep: int, task_id: str) -> None:
    task_logs = paths.logs / task_id.replace("/", "-")
    task_logs.mkdir(parents=True, exist_ok=True)
    logs = sorted(task_logs.glob("verification-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for path in logs[keep:]:
        path.unlink(missing_ok=True)


def initialize(paths: Paths, source_contract: Path, replace_active: bool) -> dict[str, Any]:
    config = load_json(paths.config)
    contract = load_json(source_contract)
    validate_contract(contract)
    limits = effective_limits(config, contract)
    if paths.state.exists():
        if not replace_active:
            raise PipelineError("an active task already exists; use --replace-active to archive it and start a new task")
        archive_current(paths)
    paths.current.mkdir(parents=True, exist_ok=True)
    write_json(paths.contract, contract)
    criteria = {
        item["id"]: {"status": "PENDING", "evidence": [], "updated_at": utc_now()}
        for item in contract["acceptance_criteria"]
    }
    state = {
        "task_id": contract["task_id"],
        "task_contract_path": str(paths.contract.relative_to(paths.root)),
        "task_contract_hash": contract_hash(contract),
        "status": "PLANNING",
        "phase": "PLANNING",
        "integration_owner": "Bounded Completion Lead",
        "reviewer": "Bounded Completion Reviewer",
        "current_iteration": 0,
        "limits": limits,
        "repeated_failure_count": 0,
        "unchanged_state_iterations": 0,
        "stop_hook_continuations": 0,
        "criteria": criteria,
        "plan_reviews": [],
        "diagnostic_reviews": [],
        "final_reviews": [],
        "visual_reviews": {},
        "last_verification": None,
        "last_failure_signature": None,
        "requires_independent_diagnosis": False,
        "final_diff_inspection": None,
        "integrity_audit": None,
        "active_blocking_findings": [],
        "resolved_findings": [],
        "rejected_findings": [],
        "known_blockers": [],
        "delegations_in_progress": [],
        "approvals": [],
        "approval_evidence": {},
        "next_action": "Map acceptance criteria to evidence and request plan challenge.",
        "last_material_progress": {
            "at": utc_now(),
            "fingerprint": workspace_fingerprint(paths.root),
            "description": "Task initialized",
        },
        "completion_gate": {"passed": False, "reasons": ["not evaluated"], "evaluated_at": None},
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    findings = {"task_id": contract["task_id"], "findings": []}
    write_json(paths.state, state)
    write_json(paths.findings, findings)
    prune_logs(paths, limits["max_retained_verification_logs"], contract["task_id"])
    return state


def advance_iteration(paths: Paths, description: str) -> dict[str, Any]:
    _, _, state, _ = read_active(paths)
    if state["status"] in TERMINAL:
        raise PipelineError(f"cannot advance a terminal task in state {state['status']}")
    state["current_iteration"] += 1
    fingerprint = workspace_fingerprint(paths.root)
    previous = state.get("last_material_progress", {}).get("fingerprint")
    if fingerprint == previous:
        state["unchanged_state_iterations"] += 1
    else:
        state["unchanged_state_iterations"] = 0
        state["last_material_progress"] = {"at": utc_now(), "fingerprint": fingerprint, "description": description}
    if state["current_iteration"] > state["limits"]["max_full_loop_iterations"]:
        state["status"] = state["phase"] = "ESCALATED"
        state["known_blockers"].append("maximum full-loop iteration count exceeded")
    if state["unchanged_state_iterations"] >= state["limits"]["max_unchanged_state_iterations"]:
        state["status"] = state["phase"] = "ESCALATED"
        state["known_blockers"].append("maximum unchanged-state iterations reached")
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return state
