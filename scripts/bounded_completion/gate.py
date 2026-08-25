from __future__ import annotations

from typing import Any

from .common import Paths, read_active, sha256_file, utc_now, workspace_fingerprint, write_json


def _finding_blocks(item: dict[str, Any]) -> bool:
    disposition = item.get("disposition", "unresolved")
    if disposition == "requires-user-input":
        return True
    if disposition == "accepted-blocking" and not item.get("resolution_evidence"):
        return True
    return disposition == "unresolved" and bool(item.get("blocking"))


def evaluate_gate(paths: Paths, mutate: bool = True) -> tuple[bool, list[str], dict[str, Any]]:
    config, contract, state, findings_doc = read_active(paths)
    reasons: list[str] = []
    current = workspace_fingerprint(paths.root)
    for item in contract["acceptance_criteria"]:
        record = state["criteria"].get(item["id"], {})
        if item.get("required", True) and record.get("status") != "SATISFIED":
            reasons.append(f"acceptance criterion {item['id']} is not satisfied")
        if item.get("visual", False) and item.get("required", True):
            visual = state["visual_reviews"].get(item["id"])
            if not visual:
                reasons.append(f"visual criterion {item['id']} has no inspected artifact evidence")
            else:
                artifact = paths.root / visual["artifact"]
                if visual.get("workspace_fingerprint") != current:
                    reasons.append(f"visual criterion {item['id']} review is stale relative to the current workspace")
                elif not artifact.is_file() or sha256_file(artifact) != visual.get("artifact_sha256"):
                    reasons.append(f"visual criterion {item['id']} artifact evidence is missing or stale")
    verification = state.get("last_verification")
    if not verification or verification.get("result") != "PASS":
        reasons.append("canonical verification has not passed")
    elif verification.get("workspace_fingerprint") != current:
        reasons.append("canonical verification is stale relative to the current workspace")
    elif any(check.get("required") and check.get("status") != "PASS" for check in verification.get("checks", [])):
        reasons.append("a required verification check did not pass")
    if state.get("requires_independent_diagnosis"):
        reasons.append("repeated failure requires an independent diagnosis before completion")
    blockers = [item for item in findings_doc["findings"] if _finding_blocks(item)]
    if blockers:
        reasons.append("unresolved blocking findings: " + ", ".join(str(x.get("id")) for x in blockers))
    final_diff = state.get("final_diff_inspection")
    if not final_diff or final_diff.get("workspace_fingerprint") != current:
        reasons.append("final diff inspection is missing or stale")
    integrity = state.get("integrity_audit")
    integrity_keys = ["no_unrelated_destructive_change", "no_validation_weakening", "no_unjustified_test_disabling", "no_placeholder_implementation"]
    if not integrity or integrity.get("workspace_fingerprint") != current:
        reasons.append("integrity audit is missing or stale")
    elif not all(integrity.get(key) is True for key in integrity_keys):
        reasons.append("integrity audit contains a failed assertion")
    final_reviews = [r for r in state.get("final_reviews", []) if r.get("workspace_fingerprint") == current]
    if not final_reviews:
        reasons.append("final independent review is missing or stale")
    elif config.get("require_distinct_reviewer_model", True):
        expected = config.get("preferred_model_labels", {}).get("reviewer")
        if not any(
            r.get("distinct_model_confirmed")
            and r.get("reviewer_identity_source") in {"operator-confirmed", "runtime-reported"}
            and (not expected or r.get("reviewer_model") == expected)
            for r in final_reviews
        ):
            reasons.append("final review lacks independently confirmed distinct reviewer-model evidence")
    if not state.get("plan_reviews"):
        reasons.append("initial plan challenge was not recorded")
    if state["current_iteration"] > state["limits"]["max_full_loop_iterations"]:
        reasons.append("maximum full-loop iteration count exceeded")
    approvals = contract.get("required_approvals", []) or []
    recorded = set(state.get("approvals", []))
    approval_evidence = state.get("approval_evidence", {})
    missing_approvals = [approval for approval in approvals if approval not in recorded]
    if missing_approvals:
        reasons.append("required approvals outstanding: " + ", ".join(missing_approvals))
    for approval in approvals:
        if approval not in recorded:
            continue
        item = approval_evidence.get(approval)
        if not isinstance(item, dict) or item.get("source") not in {"operator-confirmed", "runtime-policy"} or not str(item.get("evidence", "")).strip():
            reasons.append(f"required approval lacks trusted provenance: {approval}")
    passed = not reasons
    if mutate:
        state["active_blocking_findings"] = [item["id"] for item in blockers]
        state["completion_gate"] = {
            "passed": passed, "reasons": reasons, "evaluated_at": utc_now(),
            "workspace_fingerprint": current,
        }
        if passed:
            state["status"] = state["phase"] = "COMPLETE"
            state["next_action"] = "None; objective completion gate passed."
        elif state["status"] != "ESCALATED":
            state["status"] = state["phase"] = "BLOCKED"
            state["next_action"] = reasons[0] if reasons else "Resolve completion blockers."
        state["updated_at"] = utc_now()
        write_json(paths.state, state)
    return passed, reasons, state
