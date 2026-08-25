from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import (
    SEVERITIES, VALID_DISPOSITIONS, Paths, PipelineError, read_active, sha256_file,
    utc_now, workspace_fingerprint, write_json,
)


def record_criterion(paths: Paths, criterion_id: str, status: str, evidence: str) -> dict[str, Any]:
    _, _, state, _ = read_active(paths)
    if criterion_id not in state["criteria"]:
        raise PipelineError(f"unknown acceptance criterion: {criterion_id}")
    if status not in {"PENDING", "SATISFIED", "BLOCKED", "NOT_APPLICABLE"}:
        raise PipelineError("invalid criterion status")
    if status in {"SATISFIED", "NOT_APPLICABLE"} and not evidence.strip():
        raise PipelineError("criterion disposition requires concrete evidence")
    state["criteria"][criterion_id]["status"] = status
    state["criteria"][criterion_id]["evidence"].append({"at": utc_now(), "detail": evidence})
    state["criteria"][criterion_id]["updated_at"] = utc_now()
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return state["criteria"][criterion_id]


def record_review(paths: Paths, kind: str, summary: str, reviewer_model: str | None, identity_source: str | None, distinct: bool, failure_signature: str | None = None) -> dict[str, Any]:
    config, _, state, _ = read_active(paths)
    if kind not in {"plan", "diagnosis", "final"}:
        raise PipelineError("review kind must be plan, diagnosis, or final")
    if kind == "plan" and len(state["plan_reviews"]) >= state["limits"]["max_plan_review_rounds"]:
        raise PipelineError("maximum plan-review rounds reached")
    if kind == "final" and len(state["final_reviews"]) >= state["limits"]["max_final_review_rounds"]:
        raise PipelineError("maximum final-review rounds reached")
    if distinct and identity_source not in {"operator-confirmed", "runtime-reported"}:
        raise PipelineError("distinct-model confirmation requires operator-confirmed or runtime-reported identity source")
    if distinct and (not reviewer_model or not reviewer_model.strip()):
        raise PipelineError("distinct-model confirmation requires a reviewer model label")
    expected = config.get("preferred_model_labels", {}).get("reviewer")
    if distinct and expected and reviewer_model != expected:
        raise PipelineError(f"distinct reviewer model must match configured label: {expected}")
    review = {
        "kind": kind, "summary": summary, "reviewer_model": reviewer_model,
        "reviewer_identity_source": identity_source, "distinct_model_confirmed": bool(distinct),
        "workspace_fingerprint": workspace_fingerprint(paths.root),
        "failure_signature": failure_signature, "recorded_at": utc_now(),
    }
    target = {"plan": "plan_reviews", "diagnosis": "diagnostic_reviews", "final": "final_reviews"}[kind]
    state[target].append(review)
    if kind == "diagnosis" and failure_signature and failure_signature == state.get("last_failure_signature"):
        state["requires_independent_diagnosis"] = False
        state["repeated_failure_count"] = 0
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return review


def add_finding(paths: Paths, finding: dict[str, Any]) -> dict[str, Any]:
    _, _, state, findings_doc = read_active(paths)
    required = ["id", "title", "severity", "blocking", "acceptance_criterion", "location", "evidence", "procedure", "expected", "actual", "recommended_correction", "owner", "hypothesis"]
    missing = [key for key in required if key not in finding]
    if missing:
        raise PipelineError(f"finding missing required fields: {', '.join(missing)}")
    if finding["severity"] not in SEVERITIES:
        raise PipelineError("invalid finding severity")
    for field in ["id", "title", "location", "evidence", "procedure", "expected", "actual", "recommended_correction", "owner"]:
        if not isinstance(finding.get(field), str) or not finding[field].strip():
            raise PipelineError(f"finding field {field} must be a non-empty string")
    if any(item.get("id") == finding["id"] for item in findings_doc["findings"]):
        raise PipelineError(f"finding ID already exists: {finding['id']}")
    if finding["blocking"] and finding["hypothesis"] and finding["severity"] not in {"critical", "high"}:
        raise PipelineError("an unvalidated hypothesis may only be precautionary-blocking at critical/high severity")
    item = dict(finding)
    item.update({
        "disposition": "unresolved", "disposition_evidence": None,
        "iteration_first_observed": state["current_iteration"],
        "iteration_last_observed": state["current_iteration"],
        "iteration_resolved": None, "resolution_evidence": None,
        "workspace_fingerprint_first_observed": workspace_fingerprint(paths.root),
    })
    findings_doc["findings"].append(item)
    write_json(paths.findings, findings_doc)
    return item


def dispose_finding(paths: Paths, finding_id: str, disposition: str, evidence: str) -> dict[str, Any]:
    _, _, state, findings_doc = read_active(paths)
    if disposition not in VALID_DISPOSITIONS:
        raise PipelineError("invalid finding disposition")
    item = next((f for f in findings_doc["findings"] if f.get("id") == finding_id), None)
    if item is None:
        raise PipelineError(f"unknown finding: {finding_id}")
    if not evidence.strip():
        raise PipelineError("finding disposition requires evidence or rationale")
    item["disposition"] = disposition
    item["disposition_evidence"] = evidence
    item["iteration_last_observed"] = state["current_iteration"]
    if disposition in {"accepted-non-blocking", "rejected-with-evidence", "duplicate-resolved", "deferred-out-of-scope"}:
        item["iteration_resolved"] = state["current_iteration"]
        item["resolution_evidence"] = evidence
    elif disposition in {"accepted-blocking", "requires-user-input"}:
        item["resolution_evidence"] = None
    write_json(paths.findings, findings_doc)
    return item


def resolve_finding(paths: Paths, finding_id: str, evidence: str) -> dict[str, Any]:
    _, _, state, findings_doc = read_active(paths)
    item = next((f for f in findings_doc["findings"] if f.get("id") == finding_id), None)
    if item is None:
        raise PipelineError(f"unknown finding: {finding_id}")
    if item.get("disposition") != "accepted-blocking":
        raise PipelineError("only accepted-blocking findings use resolve-finding")
    if not evidence.strip():
        raise PipelineError("resolution evidence is required")
    item["iteration_last_observed"] = state["current_iteration"]
    item["iteration_resolved"] = state["current_iteration"]
    item["resolution_evidence"] = evidence
    write_json(paths.findings, findings_doc)
    return item


def record_visual(paths: Paths, criterion_id: str, artifact: Path, inspected_by: str, review: str) -> dict[str, Any]:
    _, contract, state, _ = read_active(paths)
    criterion = next((c for c in contract["acceptance_criteria"] if c["id"] == criterion_id), None)
    if criterion is None:
        raise PipelineError(f"unknown acceptance criterion: {criterion_id}")
    if not criterion.get("visual", False):
        raise PipelineError(f"criterion {criterion_id} is not marked visual")
    if not inspected_by.strip() or not review.strip():
        raise PipelineError("visual evidence requires a non-empty inspector and review")
    artifact = artifact.resolve()
    try:
        rel = artifact.relative_to(paths.root.resolve())
    except ValueError as exc:
        raise PipelineError("visual artifact must be inside the repository workspace") from exc
    if not artifact.is_file():
        raise PipelineError("visual artifact does not exist")
    evidence = {
        "artifact": str(rel), "artifact_sha256": sha256_file(artifact),
        "inspected_by": inspected_by, "review": review, "recorded_at": utc_now(),
        "workspace_fingerprint": workspace_fingerprint(paths.root),
    }
    state["visual_reviews"][criterion_id] = evidence
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return evidence


def record_diff(paths: Paths, summary: str) -> dict[str, Any]:
    _, _, state, _ = read_active(paths)
    item = {"summary": summary, "workspace_fingerprint": workspace_fingerprint(paths.root), "recorded_at": utc_now()}
    state["final_diff_inspection"] = item
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return item


def record_integrity(paths: Paths, summary: str, no_unrelated_destructive_change: bool, no_validation_weakening: bool, no_unjustified_test_disabling: bool, no_placeholder_implementation: bool) -> dict[str, Any]:
    _, _, state, _ = read_active(paths)
    item = {
        "summary": summary, "workspace_fingerprint": workspace_fingerprint(paths.root), "recorded_at": utc_now(),
        "no_unrelated_destructive_change": bool(no_unrelated_destructive_change),
        "no_validation_weakening": bool(no_validation_weakening),
        "no_unjustified_test_disabling": bool(no_unjustified_test_disabling),
        "no_placeholder_implementation": bool(no_placeholder_implementation),
    }
    state["integrity_audit"] = item
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return item


def approve(paths: Paths, approval: str, source: str, evidence: str) -> dict[str, Any]:
    _, contract, state, _ = read_active(paths)
    allowed = set(contract.get("required_approvals", []) or [])
    if approval not in allowed:
        raise PipelineError(f"approval is not declared by the task contract: {approval}")
    if source not in {"operator-confirmed", "runtime-policy"}:
        raise PipelineError("approval source must be operator-confirmed or runtime-policy")
    if not evidence.strip():
        raise PipelineError("approval evidence is required")
    approvals = set(state.get("approvals", []))
    approvals.add(approval)
    state["approvals"] = sorted(approvals)
    record = {"source": source, "evidence": evidence.strip(), "recorded_at": utc_now()}
    state.setdefault("approval_evidence", {})[approval] = record
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return record


def escalate(paths: Paths, reason: str) -> dict[str, Any]:
    _, _, state, _ = read_active(paths)
    state["status"] = state["phase"] = "ESCALATED"
    if reason not in state["known_blockers"]:
        state["known_blockers"].append(reason)
    state["next_action"] = "User input or external capability required."
    state["updated_at"] = utc_now()
    write_json(paths.state, state)
    return state
