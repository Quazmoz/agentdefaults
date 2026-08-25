# Resume Bounded Completion Loop

## Purpose

Resume an existing bounded completion loop from durable repository state without discarding unresolved evidence.

## Prompt

Resume the active bounded completion loop. Read `.agent-loop/current/task-contract.json`, durable state, current findings, latest verification log, and current Git diff. Confirm the recorded state against repository evidence before continuing. Proceed from the recorded next action. If the same failure has repeated without material progress, request an independent diagnosis from the `Bounded Completion Reviewer` before making another similar change. Continue until the objective completion gate passes or an escalation condition occurs. Do not reset active state, discard unresolved findings, weaken verification, or claim stale evidence as current.
