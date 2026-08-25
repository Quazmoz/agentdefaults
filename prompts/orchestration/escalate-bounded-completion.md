# Escalate Bounded Completion

## Purpose

Record a safe terminal escalation when autonomous completion is no longer justified.

Use:

```bash
python3 scripts/bounded-completion.py escalate --reason "<specific blocker>"
```

Report the current status, incomplete acceptance criteria, active blocking findings, verification failures and log paths, actions attempted, why further autonomous attempts are unlikely to help, the smallest user decision/input required, safe options, and whether the task can resume from existing state.
