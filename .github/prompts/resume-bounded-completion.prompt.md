---
name: resume-bounded-completion
description: Resume the current bounded completion loop without discarding durable evidence.
agent: 'Bounded Completion Lead'
---

# Purpose

Resume the active bounded completion loop. Read the active task contract, durable state, current findings, latest verification log, and current Git diff. Confirm recorded state against repository evidence before continuing. Proceed from the recorded next action. If the same failure repeated without material progress, request an independent diagnosis from the Bounded Completion Reviewer before another similar change. Continue until the completion gate passes or an escalation condition occurs. Do not reset active state or discard unresolved findings.
