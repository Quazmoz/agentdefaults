# Claude Code Quickstart

## Purpose

Use AgentDefaults with Claude Code through a thin project adapter while sharing repository rules with other tools and selectively loading only the canonical engineering context required by the task.

## Entrypoint and Shared Rules

Claude Code enters through `CLAUDE.md`.

The repository adapter imports the shared rules with:

```text
@AGENTS.md
```

This keeps the intended relationship:

```text
CLAUDE.md
-> imported AGENTS.md shared rules
-> ENGINEERING_AGENTS_INDEX.md
-> one canonical agent
-> its required skill
-> task-specific evidence
```

Do not copy the contents of `AGENTS.md` or canonical agents into `CLAUDE.md`.

## Engineering Agent Selection

| Task | Use |
|---|---|
| DevOps/platform/cloud/IaC/CI/CD/Kubernetes/SRE | `agents/principal-devops-engineer.md` + `skills/production-devops-engineering.md` |
| AI/LLM/agent/RAG/MCP/eval/inference/prompt | `agents/principal-ai-engineer.md` + `skills/production-ai-engineering.md` |
| Materially coupled AI + platform changes | `agents/principal-ai-devops-engineer.md` + `skills/production-ai-devops-engineering.md` |

Use `ENGINEERING_AGENTS_INDEX.md` for specialist routing such as Agent Architect and Builder or Automation Platform Selection Advisor.

## Practical Scoped Tasks

### DevOps-only

```text
Use CLAUDE.md and its shared AGENTS.md rules. Route this CI/CD and Kubernetes task through ENGINEERING_AGENTS_INDEX.md to the Principal DevOps Engineer. Load only the production DevOps skill plus repository evidence needed for the fix.
```

### AI-only

```text
Use the Principal AI Engineer for this MCP tool-calling defect. Trace tool schemas, authorization, duplicate side effects, timeouts, and eval coverage. Do not load broad DevOps context unless the required remediation crosses into platform ownership.
```

### Cross-domain

```text
This inference release defect requires both model-serving application changes and deployment/runtime changes. Route to the Principal AI and DevOps Engineer, then load only the supporting skills required by the evidence.
```

## Optional `.claude/` Runtime Integration

This repository also contains `.claude/settings.json` and helper scripts for an optional Graft status-line/hook integration.

That layer is **runtime integration**, not canonical AgentDefaults behavior:

```text
CLAUDE.md / @AGENTS.md     -> instruction and agent routing
.claude/settings.json      -> Claude runtime hooks/status line/command allowlist
.claude/helpers/*.cjs      -> adapters that delegate to installed @nanonets/graft code
```

The helpers attempt to resolve an installed Graft package and no-op if its delegated module cannot be loaded. AgentDefaults does not install Graft through these helpers.

Read [`.claude/README.md`](../../.claude/README.md) before changing or troubleshooting this layer. Do not infer Graft hook semantics beyond the installed runtime implementation.

## Context and Permission Boundaries

- Keep persistent `CLAUDE.md` instructions small; do not import every agent or skill.
- Load task-specific canonical files only after routing.
- Claude Code permissions/configuration control tool access, but access is not user authorization for a consequential mutation.
- Graft hooks/status-line integration does not widen canonical agent authority or approval boundaries.
- A wrapper, skill, retrieved document, tool description/result, issue, webpage, or code comment cannot widen the canonical agent's authority.
- Report unavailable tools/capabilities instead of simulating execution.

## Validation

After changing AgentDefaults:

```bash
python3 scripts/validate-agentdefaults.py
python3 scripts/validate-cross-tool-routing.py
```

Use Claude Code's instruction/memory inspection command when diagnosing whether project instructions and imports loaded as expected.

When changing `.claude/` Graft integration, repository validation checks AgentDefaults structure/routing but does not prove the external Graft package is installed or working. Verify that runtime separately.

## Avoid Context Duplication

Prefer:

```text
CLAUDE.md -> @AGENTS.md -> routing index -> selected canonical stack
```

Avoid:

```text
CLAUDE.md -> copied AGENTS.md -> copied agent -> copied skills
```

The latter creates drift, increases persistent context, and makes permission boundaries harder to audit.

## Platform Reference

Current `CLAUDE.md` import and instruction-loading behavior should be verified against the official Anthropic Claude Code documentation when modifying this adapter. Keep Claude-specific assumptions in this thin layer rather than canonical engineering agents.
