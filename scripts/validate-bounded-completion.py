#!/usr/bin/env python3
"""Adversarial regression tests for the deterministic bounded completion control plane."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from bounded_completion.core import (  # noqa: E402
    Paths, PipelineError, add_finding, advance_iteration, approve, dispose_finding,
    effective_limits, evaluate_gate, initialize, load_json, read_active, record_criterion,
    record_diff, record_integrity, record_review, record_visual, resolve_finding,
    verify,
)

CONFIG = {
    "version": 2,
    "require_distinct_reviewer_model": True,
    "preferred_model_labels": {"lead": "Qwen3 Coder Next Q6", "reviewer": "Qwen 3.6 35B Vision"},
    "limits": {
        "max_full_loop_iterations": 12,
        "max_unchanged_failure_attempts": 2,
        "max_plan_review_rounds": 2,
        "max_final_review_rounds": 3,
        "verification_timeout_seconds": 30,
        "subagent_timeout_seconds": 30,
        "max_retained_verification_logs": 3,
        "max_unchanged_state_iterations": 2,
        "max_stop_hook_continuations": 1,
    },
}

REQUIRED_REPOSITORY_FILES = [
    "agents/bounded-completion-lead.md",
    "agents/bounded-completion-reviewer.md",
    "skills/bounded-completion-orchestration.md",
    "prompts/orchestration/start-bounded-completion.md",
    "prompts/orchestration/resume-bounded-completion.md",
    "prompts/orchestration/reset-bounded-completion.md",
    "prompts/orchestration/escalate-bounded-completion.md",
    "prompts/review/bounded-completion-review.md",
    "schemas/bounded-completion-task.schema.json",
    "schemas/bounded-completion-state.schema.json",
    "schemas/bounded-completion-findings.schema.json",
    "examples/bounded-completion-task.json",
    "config/bounded-completion.json",
    "scripts/bounded-completion.py",
    "scripts/bounded_completion/__init__.py",
    "scripts/bounded_completion/common.py",
    "scripts/bounded_completion/verification.py",
    "scripts/bounded_completion/evidence.py",
    "scripts/bounded_completion/gate.py",
    "scripts/bounded_completion/core.py",
    "scripts/bounded_completion/cli.py",
    "scripts/validate-bounded-completion.py",
    "docs/quickstarts/bounded-completion.md",
    "docs/bounded-completion-acceptance-tests.md",
    ".github/agents/bounded-completion-lead.agent.md",
    ".github/agents/bounded-completion-reviewer.agent.md",
    ".github/prompts/start-bounded-completion.prompt.md",
    ".github/prompts/resume-bounded-completion.prompt.md",
    ".github/prompts/review-bounded-completion.prompt.md",
]


def test_repository_stack_structure() -> None:
    missing = [path for path in REQUIRED_REPOSITORY_FILES if not (ROOT / path).is_file()]
    assert not missing, f"missing bounded completion files: {missing}"
    for path in [
        "config/bounded-completion.json",
        "schemas/bounded-completion-task.schema.json",
        "schemas/bounded-completion-state.schema.json",
        "schemas/bounded-completion-findings.schema.json",
        "examples/bounded-completion-task.json",
    ]:
        load_json(ROOT / path)
    for path in [
        "agents/bounded-completion-lead.md",
        "agents/bounded-completion-reviewer.md",
        "skills/bounded-completion-orchestration.md",
        "prompts/orchestration/start-bounded-completion.md",
        "prompts/orchestration/resume-bounded-completion.md",
        "prompts/orchestration/reset-bounded-completion.md",
        "prompts/orchestration/escalate-bounded-completion.md",
        "prompts/review/bounded-completion-review.md",
        "docs/quickstarts/bounded-completion.md",
        "docs/bounded-completion-acceptance-tests.md",
        ".github/agents/bounded-completion-lead.agent.md",
        ".github/agents/bounded-completion-reviewer.agent.md",
    ]:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert "## Purpose" in text, f"{path} missing ## Purpose"
    lead = (ROOT / ".github/agents/bounded-completion-lead.agent.md").read_text(encoding="utf-8")
    reviewer = (ROOT / ".github/agents/bounded-completion-reviewer.agent.md").read_text(encoding="utf-8")
    for token in [
        "tools: ['agent', 'edit', 'execute', 'read', 'search', 'web']",
        "agents: ['Bounded Completion Reviewer']",
        "Stop:",
        "stop-hook",
        "windows:",
        "linux:",
        "osx:",
        "chat.useCustomAgentHooks",
    ]:
        assert token in lead, f"lead adapter missing {token}"
    for token in [
        "tools: ['browser', 'read', 'search', 'web']",
        "agents: []",
        "Qwen 3.6 35B Vision",
    ]:
        assert token in reviewer, f"reviewer adapter missing {token}"
    assert "model:" not in lead.split("---", 2)[1], "lead adapter must not guess a model identifier"
    assert "model:" not in reviewer.split("---", 2)[1], "reviewer adapter must not guess a model identifier"
    for prompt in [
        ROOT / ".github/prompts/start-bounded-completion.prompt.md",
        ROOT / ".github/prompts/resume-bounded-completion.prompt.md",
        ROOT / ".github/prompts/review-bounded-completion.prompt.md",
    ]:
        text = prompt.read_text(encoding="utf-8")
        assert "agent:" in text and "model:" not in text.split("---", 2)[1]
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".agent-loop/" in gitignore, ".agent-loop runtime state must be ignored"
    manifest = load_json(ROOT / "agentdefaults.manifest.json")
    stack = next((x for x in manifest.get("featured_stacks", []) if x.get("name") == "Bounded Two-Agent Completion"), None)
    assert stack is not None, "bounded completion stack not registered in manifest"
    assert stack.get("agent") == "agents/bounded-completion-lead.md"
    assert stack.get("wrapper") == ".github/agents/bounded-completion-lead.agent.md"
    assert stack.get("acceptance_tests") == "docs/bounded-completion-acceptance-tests.md"


def test_approval_requires_trusted_provenance() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        payload = make_contract()
        payload["required_approvals"] = ["production-change"]
        write_json(contract, payload)
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        try:
            approve(paths, "production-change", "agent-asserted", "model says approved")
        except PipelineError:
            pass
        else:
            raise AssertionError("untrusted approval provenance was accepted")
        approve(paths, "production-change", "operator-confirmed", "User explicitly approved production-change in the active task")
        _, _, state, _ = read_active(paths)
        assert state["approval_evidence"]["production-change"]["source"] == "operator-confirmed"


def test_cli_exit_codes() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        entry = str(ROOT / "scripts/bounded-completion.py")
        init = run(root, sys.executable, entry, "--root", str(root), "init", "--contract", str(contract), check=False)
        assert init.returncode == 0, init.stderr
        ok = run(root, sys.executable, entry, "--root", str(root), "verify", check=False)
        assert ok.returncode == 0, ok.stderr
        (root / "verify_fixture.py").write_text("raise SystemExit(9)\n", encoding="utf-8")
        bad = run(root, sys.executable, entry, "--root", str(root), "verify", check=False)
        assert bad.returncode == 1, (bad.stdout, bad.stderr)


def run(root: Path, *args: str, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(list(args), cwd=root, text=True, input=input_text, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if check and proc.returncode != 0:
        raise AssertionError(f"command failed ({proc.returncode}): {' '.join(args)}\nstdout={proc.stdout}\nstderr={proc.stderr}")
    return proc


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def make_contract(task_id: str = "task-1", *, visual: bool = False, command: list[str] | None = None, limits: dict[str, int] | None = None) -> dict:
    return {
        "task_id": task_id,
        "title": "Fixture task",
        "description": "Exercise the deterministic bounded completion control plane.",
        "required_outcome": "Fixture reaches the expected deterministic state.",
        "acceptance_criteria": [{
            "id": "AC-1",
            "description": "Fixture criterion",
            "expected_evidence": "Recorded deterministic evidence",
            "status": "PENDING",
            "verification_method": "Fixture verifier",
            "required": True,
            "visual": visual,
        }],
        "verification": {
            "canonical_command": command or [sys.executable, "verify_fixture.py"],
            "required_checks": [],
        },
        "required_approvals": [],
        "iteration_limits": limits or {},
    }


def fixture() -> tuple[tempfile.TemporaryDirectory[str], Path, Paths]:
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "config").mkdir()
    write_json(root / "config/bounded-completion.json", CONFIG)
    (root / "verify_fixture.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    (root / "tracked.txt").write_text("base\n", encoding="utf-8")
    run(root, "git", "init", "-q")
    run(root, "git", "config", "user.email", "fixture@example.invalid")
    run(root, "git", "config", "user.name", "Fixture")
    run(root, "git", "add", ".")
    run(root, "git", "commit", "-qm", "fixture base")
    return tmp, root, Paths(root)


def prepare_success(root: Path, paths: Paths, contract_path: Path, *, visual_artifact: Path | None = None) -> None:
    initialize(paths, contract_path, False)
    record_review(paths, "plan", "Plan challenged with no blockers.", None, None, False)
    if visual_artifact is not None:
        record_visual(paths, "AC-1", visual_artifact, "reviewer", "Artifact inspected and meets criteria.")
    record_criterion(paths, "AC-1", "SATISFIED", "Fixture evidence recorded.")
    result = verify(paths)
    assert result["result"] == "PASS"
    record_diff(paths, "Current diff inspected.")
    record_integrity(paths, "Integrity assertions checked.", True, True, True, True)
    record_review(paths, "final", "Current diff independently reviewed.", "Qwen 3.6 35B Vision", "operator-confirmed", True)


def assert_contains(values: list[str], needle: str) -> None:
    if not any(needle in item for item in values):
        raise AssertionError(f"expected {needle!r} in {values!r}")


def test_success() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "add contract")
        prepare_success(root, paths, contract)
        passed, reasons, state = evaluate_gate(paths)
        assert passed and not reasons and state["status"] == "COMPLETE"


def test_unresolved_critical_blocks_and_resolution_preserves_disposition() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "add contract")
        prepare_success(root, paths, contract)
        finding = {
            "id": "F-1", "title": "Blocking defect", "severity": "critical", "blocking": True,
            "acceptance_criterion": "AC-1", "location": "tracked.txt:1", "evidence": "fixture evidence",
            "procedure": "inspect tracked.txt", "expected": "safe", "actual": "unsafe",
            "recommended_correction": "fix fixture", "owner": "lead", "hypothesis": False,
        }
        add_finding(paths, finding)
        dispose_finding(paths, "F-1", "accepted-blocking", "accepted after reproduction")
        passed, reasons, _ = evaluate_gate(paths)
        assert not passed
        assert_contains(reasons, "F-1")
        resolved = resolve_finding(paths, "F-1", "corrected and reverified")
        assert resolved["disposition"] == "accepted-blocking"
        assert resolved["resolution_evidence"]
        passed, reasons, _ = evaluate_gate(paths)
        assert passed, reasons


def test_stale_verification_review_diff_integrity() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "add contract")
        prepare_success(root, paths, contract)
        (root / "tracked.txt").write_text("changed after evidence\n", encoding="utf-8")
        passed, reasons, _ = evaluate_gate(paths)
        assert not passed
        assert_contains(reasons, "verification is stale")
        assert_contains(reasons, "final diff inspection")
        assert_contains(reasons, "integrity audit")
        assert_contains(reasons, "final independent review")


def test_visual_requires_real_current_artifact() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract(visual=True))
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "add contract")
        initialize(paths, contract, False)
        record_review(paths, "plan", "visual plan reviewed", None, None, False)
        record_criterion(paths, "AC-1", "SATISFIED", "source inspection alone")
        verify(paths)
        record_diff(paths, "diff inspected")
        record_integrity(paths, "integrity checked", True, True, True, True)
        record_review(paths, "final", "reviewed", "Qwen 3.6 35B Vision", "operator-confirmed", True)
        passed, reasons, _ = evaluate_gate(paths)
        assert not passed
        assert_contains(reasons, "no inspected artifact")
        artifact = root / "artifact.png"
        artifact.write_bytes(b"fixture-image")
        record_visual(paths, "AC-1", artifact, "Qwen 3.6 35B Vision", "actual artifact inspected")
        verify(paths)
        record_diff(paths, "diff and artifact inspected")
        record_integrity(paths, "integrity checked", True, True, True, True)
        record_review(paths, "final", "reviewed current artifact/diff", "Qwen 3.6 35B Vision", "operator-confirmed", True)
        passed, reasons, _ = evaluate_gate(paths)
        assert passed, reasons
        (root / "tracked.txt").write_text("post-screenshot change\n", encoding="utf-8")
        passed, reasons, _ = evaluate_gate(paths)
        assert not passed
        assert_contains(reasons, "visual criterion AC-1 review is stale")


def test_distinct_model_required() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "add contract")
        initialize(paths, contract, False)
        record_review(paths, "plan", "plan review", None, None, False)
        record_criterion(paths, "AC-1", "SATISFIED", "evidence")
        verify(paths)
        record_diff(paths, "diff")
        record_integrity(paths, "integrity", True, True, True, True)
        record_review(paths, "final", "same-model review", None, None, False)
        passed, reasons, _ = evaluate_gate(paths)
        assert not passed
        assert_contains(reasons, "distinct reviewer-model")


def test_archive_reset() -> None:
    tmp, root, paths = fixture()
    with tmp:
        c1 = root / "contract1.json"
        c2 = root / "contract2.json"
        write_json(c1, make_contract("one"))
        write_json(c2, make_contract("two"))
        run(root, "git", "add", "contract1.json", "contract2.json")
        run(root, "git", "commit", "-qm", "contracts")
        initialize(paths, c1, False)
        initialize(paths, c2, True)
        state = load_json(paths.state)
        assert state["task_id"] == "two"
        archives = list(paths.archive.iterdir())
        assert len(archives) == 1
        assert (archives[0] / "state.json").is_file()
        assert load_json(archives[0] / "state.json")["task_id"] == "one"


def test_unavailable_required_check_escalates() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract(command=["definitely-not-a-real-command-bcp"]))
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        result = verify(paths)
        assert result["result"] == "FAIL"
        state = load_json(paths.state)
        assert state["status"] == "ESCALATED"
        assert result["checks"][0]["status"] == "UNAVAILABLE"


def test_repeated_failure_requires_diagnosis_before_more_same_strategy() -> None:
    tmp, root, paths = fixture()
    with tmp:
        (root / "verify_fixture.py").write_text("raise SystemExit(7)\n", encoding="utf-8")
        run(root, "git", "add", "verify_fixture.py")
        run(root, "git", "commit", "-qm", "failing verifier")
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        verify(paths)
        verify(paths)
        state = load_json(paths.state)
        assert state["requires_independent_diagnosis"] is True
        sig = state["last_failure_signature"]
        record_review(paths, "diagnosis", "Independent root-cause diagnosis with discriminating observation.", "Qwen 3.6 35B Vision", "operator-confirmed", True, sig)
        state = load_json(paths.state)
        assert state["requires_independent_diagnosis"] is False
        assert state["repeated_failure_count"] == 0


def test_limits_cannot_be_widened_and_unchanged_state_escalates() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract_data = make_contract(limits={"max_full_loop_iterations": 999, "max_unchanged_state_iterations": 1})
        limits = effective_limits(CONFIG, contract_data)
        assert limits["max_full_loop_iterations"] == CONFIG["limits"]["max_full_loop_iterations"]
        assert limits["max_unchanged_state_iterations"] == 1
        contract = root / "contract.json"
        write_json(contract, contract_data)
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        advance_iteration(paths, "discussion only")
        state = load_json(paths.state)
        assert state["status"] == "ESCALATED"


def test_contract_tamper_detected() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        active = load_json(paths.contract)
        active["title"] = "tampered"
        write_json(paths.contract, active)
        try:
            verify(paths)
        except PipelineError as exc:
            assert "changed outside control-plane" in str(exc)
        else:
            raise AssertionError("tampered active task contract was accepted")


def test_stop_hook_json_and_recursion_guard() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        entry = str(ROOT / "scripts/bounded-completion.py")
        first = run(root, sys.executable, entry, "--root", str(root), "stop-hook", check=False, input_text=json.dumps({"stop_hook_active": False}))
        assert first.returncode == 0, first.stderr
        payload = json.loads(first.stdout)
        assert payload["hookSpecificOutput"]["decision"] == "block"
        second = run(root, sys.executable, entry, "--root", str(root), "stop-hook", check=False, input_text=json.dumps({"stop_hook_active": True}))
        assert second.returncode == 0, second.stderr
        assert json.loads(second.stdout) == {}
        state = load_json(paths.state)
        assert state["status"] == "ESCALATED"


def test_log_retention() -> None:
    tmp, root, paths = fixture()
    with tmp:
        contract = root / "contract.json"
        write_json(contract, make_contract())
        run(root, "git", "add", "contract.json")
        run(root, "git", "commit", "-qm", "contract")
        initialize(paths, contract, False)
        for _ in range(6):
            verify(paths)
        logs = list((paths.logs / "task-1").glob("verification-*.log"))
        assert len(logs) <= CONFIG["limits"]["max_retained_verification_logs"]


def main() -> int:
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_") and callable(value)]
    failures: list[str] = []
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
        except Exception as exc:  # deliberate validator harness boundary
            failures.append(f"{test.__name__}: {exc}")
            print(f"FAIL: {test.__name__}: {exc}")
    if failures:
        print("\nBounded completion validation: FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"\nBounded completion validation: PASS ({len(tests)} scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
