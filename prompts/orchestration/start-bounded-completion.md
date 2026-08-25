# Start Bounded Completion Loop

## Purpose

Start a new repository-backed bounded completion loop without inheriting stale task state.

## Prompt

Start a new bounded completion loop for the active task contract. Initialize or safely reset the current loop state while preserving prior task history. Map each acceptance criterion to concrete evidence. Ask the `Bounded Completion Reviewer` to challenge the plan before major implementation begins. Act as the Integration Owner. Implement the task in coherent increments, run deterministic verification through `scripts/bounded-completion.py verify`, request independent review, disposition every finding, and resolve all blocking findings. Continue until `scripts/bounded-completion.py gate` passes or a documented escalation condition occurs. Do not weaken validation, bypass tests, claim unsupported visual review, invent model/runtime capabilities, or declare completion based only on agent confidence.
