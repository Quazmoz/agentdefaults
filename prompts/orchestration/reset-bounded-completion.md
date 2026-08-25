# Reset Bounded Completion

## Purpose

Start a new bounded-completion task without deleting evidence from the previous active task.

Use:

```bash
python3 scripts/bounded-completion.py init --contract <new-contract.json> --replace-active
```

The command archives the prior `.agent-loop/current/` directory under `.agent-loop/archive/` before initializing the new task. Never delete `.agent-loop/archive/` merely to clear conversational context.
