# AgentDefaults Index

## Purpose

Provide a compact human-readable routing and navigation layer for AgentDefaults while `agentdefaults.manifest.json` remains the authoritative machine-readable featured-stack registry.

## Fast Start

| Need | Start with |
|---|---|
| Operate the bounded loop quickly | [`docs/loops/QUICK_REFERENCE.md`](docs/loops/QUICK_REFERENCE.md) |
| Understand the full bounded lead/reviewer loop | [`docs/loops/README.md`](docs/loops/README.md) |
| Run a bounded lead/reviewer completion loop in VS Code Copilot | [`docs/quickstarts/bounded-completion.md`](docs/quickstarts/bounded-completion.md) |
| Choose among the principal and specialist engineering agents | [`ENGINEERING_AGENTS_INDEX.md`](ENGINEERING_AGENTS_INDEX.md) |
| Engineer or harden GitHub Actions workflows/actions | [`docs/quickstarts/github-actions-engineer.md`](docs/quickstarts/github-actions-engineer.md) |
| Use authenticated Comet browser research | [`docs/quickstarts/comet-authenticated-research.md`](docs/quickstarts/comet-authenticated-research.md) |
| Apply the Token Economy stack | [`docs/quickstarts/token-economy.md`](docs/quickstarts/token-economy.md) |
| Use OpenAI Codex | [`docs/quickstarts/codex.md`](docs/quickstarts/codex.md) |
| Use Claude Code | [`docs/quickstarts/claude.md`](docs/quickstarts/claude.md) |
| Understand Claude project hooks / Graft adapter | [`.claude/README.md`](.claude/README.md) |
| Use GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) |
| Understand Copilot prompt adapters | [`.github/prompts/README.md`](.github/prompts/README.md) |
| Use Gemini / Gemini CLI | [`GEMINI.md`](GEMINI.md) |
| Use a generic repository-aware agent | [`AGENTS.md`](AGENTS.md) |
| Adapt examples safely | [`examples/README.md`](examples/README.md) |
| Understand loop configuration | [`config/README.md`](config/README.md) |
| See all tool mappings | [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md) |
| Validate the repository | [`scripts/validate-agentdefaults.py`](scripts/validate-agentdefaults.py) |

## Bounded Completion Workflow

Use [`docs/quickstarts/bounded-completion.md`](docs/quickstarts/bounded-completion.md) when implementation/qualification work needs a single Integration Owner, independent adversarial review, durable loop state, deterministic verification, bounded continuation, visual-artifact evidence, and an objective completion gate.

For active operation, keep [`docs/loops/QUICK_REFERENCE.md`](docs/loops/QUICK_REFERENCE.md) open. For ownership, state, stale-evidence, approval, Stop-hook, recovery, and loop-design semantics, use the full [`docs/loops/README.md`](docs/loops/README.md).

```text
agents/bounded-completion-lead.md
agents/bounded-completion-reviewer.md
skills/bounded-completion-orchestration.md
schemas/bounded-completion-task.schema.json
config/bounded-completion.json
scripts/bounded-completion.py
.github/agents/bounded-completion-lead.agent.md
.github/agents/bounded-completion-reviewer.agent.md
```

The custom agents intentionally omit `model:` bindings until exact qualified local model identifiers are repository-discoverable. The operator guide documents manual VS Code model-picker selection for the intended Qwen lead/reviewer roles.

## Principal Engineering Routing

| Scope | Canonical agent | Skill | Quickstart | Copilot adapter |
|---|---|---|---|---|
| DevOps/platform | [`agents/principal-devops-engineer.md`](agents/principal-devops-engineer.md) | [`skills/production-devops-engineering.md`](skills/production-devops-engineering.md) | [`docs/quickstarts/principal-devops-engineer.md`](docs/quickstarts/principal-devops-engineer.md) | [`.github/agents/principal-devops-engineer.agent.md`](.github/agents/principal-devops-engineer.agent.md) |
| AI engineering | [`agents/principal-ai-engineer.md`](agents/principal-ai-engineer.md) | [`skills/production-ai-engineering.md`](skills/production-ai-engineering.md) | [`docs/quickstarts/principal-ai-engineer.md`](docs/quickstarts/principal-ai-engineer.md) | [`.github/agents/principal-ai-engineer.agent.md`](.github/agents/principal-ai-engineer.agent.md) |
| Materially cross-domain AI + DevOps | [`agents/principal-ai-devops-engineer.md`](agents/principal-ai-devops-engineer.md) | [`skills/production-ai-devops-engineering.md`](skills/production-ai-devops-engineering.md) | [`docs/quickstarts/principal-ai-devops-engineer.md`](docs/quickstarts/principal-ai-devops-engineer.md) | [`.github/agents/principal-ai-devops-engineer.agent.md`](.github/agents/principal-ai-devops-engineer.agent.md) |

Use the smallest correct owner. Infrastructure hosting an AI workload is still DevOps-only unless AI application behavior also requires material change. GitHub Actions-specific workflow/runtime work should use the specialist route below before the generic DevOps route.

## Specialist Engineering Routes

| Need | Start with |
|---|---|
| GitHub Actions workflow/action engineering, reusable workflows, runner trust, `GITHUB_TOKEN`, OIDC, Dependabot/fork boundaries, Actions release automation, artifacts/caches, concurrency/reruns, or qualification | [`docs/quickstarts/github-actions-engineer.md`](docs/quickstarts/github-actions-engineer.md) · [`agents/github-actions-engineer.md`](agents/github-actions-engineer.md) |
| Work specifically on `Quazmoz/K8SHomelab` Kubernetes/Flux GitOps, app deployment, storage/networking, or cluster incidents | [`docs/quickstarts/kubernetes-homelab-engineer.md`](docs/quickstarts/kubernetes-homelab-engineer.md) · [`agents/kubernetes-homelab-engineer.md`](agents/kubernetes-homelab-engineer.md) |
| Audit or harden DevOps cybersecurity across Terraform/OpenTofu, Ansible/AAP, Jenkins, CI/CD, GitOps, IAM, secrets, runners/agents, state, or software supply chain | [`docs/quickstarts/devsecops-security-engineer.md`](docs/quickstarts/devsecops-security-engineer.md) · [`agents/devsecops-security-engineer.md`](agents/devsecops-security-engineer.md) |
| Create, audit, or reconcile DevOps docs-as-code, runbooks, Markdown, Mermaid, and documentation diagrams | [`docs/quickstarts/devops-documentation-engineer.md`](docs/quickstarts/devops-documentation-engineer.md) · [`agents/devops-documentation-engineer.md`](agents/devops-documentation-engineer.md) |
| De-slop an existing codebase: stale comments/docstrings, duplicate helpers, dead residue, abstraction inflation, brittle tests, dependency/config drift, weak failure handling, or practical efficiency cleanup across languages | [`docs/quickstarts/codebase-maintenance-engineer.md`](docs/quickstarts/codebase-maintenance-engineer.md) · [`agents/codebase-maintenance-engineer.md`](agents/codebase-maintenance-engineer.md) |
| Design, build, or audit another AI agent | [`docs/quickstarts/agent-builder.md`](docs/quickstarts/agent-builder.md) |
| Choose or challenge an automation platform | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |

## GitHub Actions Engineering

```text
docs/quickstarts/github-actions-engineer.md
agents/github-actions-engineer.md
skills/github-actions-engineering.md
prompts/implementation/github-actions-task.md
schemas/github-actions-task.schema.json
examples/github-actions-task.yaml
docs/github-actions-engineer-acceptance-tests.md
.github/agents/github-actions-engineer.agent.md
scripts/validate-github-actions-stack.py
```

This specialist owns GitHub Actions-specific event trust, fork/Dependabot behavior, `pull_request_target`/privileged `workflow_run` risks, token/secret/OIDC scope, reusable-workflow contracts, action/workflow pinning and provenance, GitHub-hosted/self-hosted runner boundaries, caches/artifacts, concurrency/cancellation/reruns, release/deployment automation, artifact identity, and Actions cost controls.

Use `prompts/implementation/github-actions-task.md` for repeatable work and `schemas/github-actions-task.schema.json` when an orchestrator needs a machine-verifiable authority/trust/verification contract.

## Other Featured Stacks

| Need | Start with |
|---|---|
| Google Play growth / ASO | [`docs/quickstarts/google-play-growth.md`](docs/quickstarts/google-play-growth.md) |
| Palmier Pro MCP video editing | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) |
| App-market browser research | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md) |
| Community app-idea validation | [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) |
| Token economy | [`docs/quickstarts/token-economy.md`](docs/quickstarts/token-economy.md) |
| Wear OS development | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) |
| Wear OS Play Store release | [`WEAROS_INDEX.md`](WEAROS_INDEX.md) |
| US-Europe travel preparation | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) |

## Additional Canonical Operator Guides

Some canonical agents are intentionally not registered as featured stacks but still need explicit operating guidance.

| Need | Start with |
|---|---|
| Authenticated local Comet research with human auth handoff and prompt-injection boundaries | [`docs/quickstarts/comet-authenticated-research.md`](docs/quickstarts/comet-authenticated-research.md) |
| Understand all canonical agents and which ones need quickstarts | [`agents/README.md`](agents/README.md) |
| Understand skill families/composition | [`skills/README.md`](skills/README.md) |
| Understand prompt categories | [`prompts/README.md`](prompts/README.md) |

## Featured Stack Registry

The authoritative stack composition is [`agentdefaults.manifest.json`](agentdefaults.manifest.json). It currently registers:

- Agent Architect and Builder
- Codebase Maintenance and De-Slop Engineering
- Bounded Two-Agent Completion
- Principal AI and DevOps Engineering
- Principal DevOps Engineering
- GitHub Actions Engineering
- Kubernetes Homelab Engineering
- DevSecOps Security Engineering
- DevOps Documentation Engineering
- Principal AI Engineering
- Automation Platform Architecture and Selection
- Google Play Growth Optimization
- Palmier Pro MCP Video Editing
- App Market Browser Research
- Community App Idea Validation
- Token Economy
- Wear OS Development
- Wear OS Play Store Release
- US-Europe Travel Prep

## Canonical Content

```text
agents/   complete reusable agent profiles
skills/   composable behavior/task modules
prompts/  reusable task and benchmark prompts
schemas/  machine-readable contracts for structured workflows
```

Tool-specific entrypoints and wrappers route to these files; they are not separate canonical implementations.

## Tool Entrypoints

```text
OpenAI Codex             -> AGENTS.md
Claude Code              -> CLAUDE.md -> @AGENTS.md (+ optional .claude runtime adapters)
GitHub Copilot           -> .github/copilot-instructions.md + .github/agents/*.agent.md + .github/prompts/*.prompt.md
Gemini                    -> GEMINI.md
Generic repo-aware agent -> AGENTS.md
```

See [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md) for details.

## Validation

Run:

```bash
python3 scripts/validate-agentdefaults.py
```

The canonical suite covers structure, schemas, manifest integrity, stack invariants, Markdown links, cross-tool entrypoints, principal engineering contracts, GitHub Actions contracts/routing, specialist DevOps documentation contracts, DevSecOps security contracts, codebase-maintenance/de-slop contracts, and bounded-completion control-plane regressions.

For GitHub Actions stack changes, the focused check is:

```bash
python3 scripts/validate-github-actions-stack.py
```

Do not report a validator as passed unless it actually ran successfully.
