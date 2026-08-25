from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import (
    Paths, PipelineError, add_finding, advance_iteration, approve, dispose_finding,
    escalate, evaluate_gate, initialize, load_json, read_active, record_criterion,
    record_diff, record_integrity, record_review, record_visual, resolve_finding, verify,
)


def _paths(args: argparse.Namespace) -> Paths:
    return Paths(Path(args.root).resolve())


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic control plane for the bounded completion loop")
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("init")
    p.add_argument("--contract", required=True)
    p.add_argument("--replace-active", action="store_true")

    p = sub.add_parser("advance")
    p.add_argument("--description", required=True)

    sub.add_parser("verify")
    sub.add_parser("gate")
    sub.add_parser("status")

    p = sub.add_parser("criterion")
    p.add_argument("--id", required=True)
    p.add_argument("--status", required=True)
    p.add_argument("--evidence", required=True)

    p = sub.add_parser("record-review")
    p.add_argument("--kind", required=True, choices=["plan", "diagnosis", "final"])
    p.add_argument("--summary", required=True)
    p.add_argument("--reviewer-model")
    p.add_argument("--identity-source", choices=["operator-confirmed", "runtime-reported"])
    p.add_argument("--distinct-model-confirmed", action="store_true")
    p.add_argument("--failure-signature")

    p = sub.add_parser("add-finding")
    p.add_argument("--from-file", required=True)

    p = sub.add_parser("dispose-finding")
    p.add_argument("--id", required=True)
    p.add_argument("--disposition", required=True)
    p.add_argument("--evidence", default="")

    p = sub.add_parser("resolve-finding")
    p.add_argument("--id", required=True)
    p.add_argument("--evidence", required=True)

    p = sub.add_parser("record-visual")
    p.add_argument("--criterion", required=True)
    p.add_argument("--artifact", required=True)
    p.add_argument("--inspected-by", required=True)
    p.add_argument("--review", required=True)

    p = sub.add_parser("record-diff")
    p.add_argument("--summary", required=True)

    p = sub.add_parser("record-integrity")
    p.add_argument("--summary", required=True)
    p.add_argument("--no-unrelated-destructive-change", action="store_true")
    p.add_argument("--no-validation-weakening", action="store_true")
    p.add_argument("--no-unjustified-test-disabling", action="store_true")
    p.add_argument("--no-placeholder-implementation", action="store_true")

    p = sub.add_parser("approve")
    p.add_argument("--name", required=True)
    p.add_argument("--source", required=True, choices=["operator-confirmed", "runtime-policy"])
    p.add_argument("--evidence", required=True)

    p = sub.add_parser("escalate")
    p.add_argument("--reason", required=True)

    sub.add_parser("stop-hook")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = _paths(args)
    try:
        if args.command == "init":
            _print(initialize(paths, Path(args.contract).resolve(), args.replace_active))
        elif args.command == "advance":
            _print(advance_iteration(paths, args.description))
        elif args.command == "verify":
            result = verify(paths)
            _print(result)
            return 0 if result["result"] == "PASS" else 1
        elif args.command == "gate":
            passed, reasons, state = evaluate_gate(paths, mutate=True)
            _print({"passed": passed, "status": state["status"], "reasons": reasons})
            return 0 if passed else 1
        elif args.command == "status":
            _, _, state, findings = read_active(paths)
            _print({"state": state, "findings": findings})
        elif args.command == "criterion":
            _print(record_criterion(paths, args.id, args.status, args.evidence))
        elif args.command == "record-review":
            _print(record_review(paths, args.kind, args.summary, args.reviewer_model, args.identity_source, args.distinct_model_confirmed, args.failure_signature))
        elif args.command == "add-finding":
            _print(add_finding(paths, load_json(Path(args.from_file).resolve())))
        elif args.command == "dispose-finding":
            _print(dispose_finding(paths, args.id, args.disposition, args.evidence))
        elif args.command == "resolve-finding":
            _print(resolve_finding(paths, args.id, args.evidence))
        elif args.command == "record-visual":
            _print(record_visual(paths, args.criterion, Path(args.artifact), args.inspected_by, args.review))
        elif args.command == "record-diff":
            _print(record_diff(paths, args.summary))
        elif args.command == "record-integrity":
            _print(record_integrity(paths, args.summary, args.no_unrelated_destructive_change, args.no_validation_weakening, args.no_unjustified_test_disabling, args.no_placeholder_implementation))
        elif args.command == "approve":
            _print({"recorded": args.name, "approval": approve(paths, args.name, args.source, args.evidence)})
        elif args.command == "escalate":
            _print(escalate(paths, args.reason))
        elif args.command == "stop-hook":
            event = json.load(sys.stdin)
            try:
                passed, reasons, state = evaluate_gate(paths, mutate=True)
            except PipelineError:
                print("{}")
                return 0
            if passed:
                print("{}")
                return 0
            if bool(event.get("stop_hook_active")):
                escalate(paths, "stop-hook continuation already active while completion gate remained blocked")
                print("{}")
                return 0
            _, _, state, _ = read_active(paths)
            if state["stop_hook_continuations"] >= state["limits"]["max_stop_hook_continuations"]:
                escalate(paths, "maximum stop-hook continuation count reached")
                print("{}")
                return 0
            state["stop_hook_continuations"] += 1
            from .core import write_json
            write_json(paths.state, state)
            reason = reasons[0] if reasons else "completion gate is blocked"
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "Stop", "decision": "block", "reason": reason}}, separators=(",", ":")))
        return 0
    except (PipelineError, json.JSONDecodeError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
