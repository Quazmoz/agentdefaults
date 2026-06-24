# Context Window Diet Skill

## Purpose

Use this skill to reduce input/context tokens before an agent starts work. It helps agents choose the smallest useful context packet: enough to complete the task, not enough to drown the model.

This skill is model-agnostic and applies to chat prompts, IDE coding agents, RAG systems, memory tools, MCP tool results, API workflows, and local LLM pipelines.

## When To Use

Use this skill when:

- A prompt includes large pasted files, docs, logs, or prior conversation history.
- A coding agent is reading too much of a repository.
- A retrieval system returns too many chunks.
- A memory system injects irrelevant facts.
- A tool response is verbose and needs extraction.
- A multi-agent handoff is bloated.
- You want to measure input-token savings.

Do not use this skill to remove mandatory policy, security, user constraints, or data needed for correctness.

## Inputs Needed

- User goal.
- Hard constraints.
- Current error or task state.
- Candidate context blocks: files, docs, logs, memories, prior messages, tool outputs.
- Required output shape.
- Safety/compliance constraints.

## Instructions

### 1. Build a Context Ledger

```text
source | why included | action
```

Actions:

- `keep`: required as-is.
- `snippet`: include only exact lines or facts.
- `summary`: replace with compact summary.
- `pointer`: cite path/URL/tool location; read only if needed.
- `drop`: irrelevant, duplicate, stale, or risky.
- `redact`: contains secrets/private data.

### 2. Use the Minimum Context Packet

A good packet contains:

```markdown
Goal: <one sentence>
Hard constraints:
- <constraint>
Current state:
- <error/fact/path>
Relevant context:
- `<source>` — <exact useful fact>
Validation:
- <expected check>
Excluded:
- <dropped source> — <reason>
```

### 3. Prefer Facts Over Bulk Text

Replace full documents with:

- Exact error lines.
- Function or config names.
- File paths.
- Version numbers.
- User constraints.
- Small snippets directly tied to the task.

### 4. Scope Repository Reads

For coding tasks:

- Start with `README`, manifests, tests, failing file, route/entrypoint, and exact error.
- Search symbols before reading full files.
- Read neighbors only after a concrete dependency appears.
- Avoid full tree scans unless architecture is unknown and required.

### 5. Scope Retrieval/RAG

For retrieval systems:

- Retrieve narrowly by entity, timeframe, and task intent.
- Cap chunks per source.
- Prefer diverse high-confidence sources over many near-duplicates.
- Summarize retrieved chunks into a fact table before generation.
- Include citation/source IDs, not full documents, unless the answer needs exact wording.

### 6. Scope Memory Injection

For memory systems:

- Include memories only when they affect the current answer.
- Prefer durable preferences and project facts over random history.
- Drop outdated or contradictory memory unless the task is about resolving it.
- Separate user preference, project state, and temporary session state.

### 7. Redact Risky Context

Never include unnecessary:

- Passwords.
- API keys.
- OAuth tokens.
- Cookies.
- Session/local storage.
- Private keys.
- MFA codes.
- Raw PII unrelated to the task.
- Full customer/user records when a synthetic or summarized example works.

## Measurement

Use exact token counts when available. Otherwise estimate.

```text
before_input_tokens=
after_input_tokens=
savings_percent=
quality_result=<pass|partial|fail>
omissions=<none|list>
```

Savings formula:

```text
savings_percent = ((before_input_tokens - after_input_tokens) / before_input_tokens) * 100
```

A diet is successful only when quality remains acceptable.

## Expected Output

```markdown
Context diet result: <exact/approx savings>

Keep:
- <source> — <reason>

Compress:
- <source> — <replacement>

Drop:
- <source> — <reason>

Reduced context packet:
<copy-paste-ready packet>
```

## Quality Bar

A good context diet:

- Preserves all hard constraints.
- Removes irrelevant, duplicate, stale, and risky context.
- Produces a usable reduced packet.
- Includes a before/after measurement.
- Does not rely on one model's tokenizer or vendor API.

## Copy-Paste Skill Prompt

```text
Apply a context window diet. Build a ledger of all context blocks and tag each as keep, snippet, summary, pointer, drop, or redact. Keep the user goal, hard constraints, current state, relevant paths/errors/facts, validation expectations, and safety boundaries. Replace bulk files, docs, logs, retrieved chunks, and memories with exact snippets or compact facts. Drop irrelevant, duplicate, stale, and risky context. Never include secrets, cookies, tokens, private keys, MFA codes, or unnecessary PII. Return a reduced context packet and before/after token estimate.
```
