# AgentDefaults Index

## Purpose

Provide a compact human-readable routing and navigation layer for AgentDefaults while `agentdefaults.manifest.json` remains the authoritative machine-readable featured-stack registry.

## Fast Start

| Need | Start with |
|---|---|
| Choose among the principal engineering agents | [`ENGINEERING_AGENTS_INDEX.md`](ENGINEERING_AGENTS_INDEX.md) |
| Use OpenAI Codex | [`docs/quickstarts/codex.md`](docs/quickstarts/codex.md) |
| Use Claude Code | [`docs/quickstarts/claude.md`](docs/quickstarts/claude.md) |
| Use GitHub Copilot custom agents | [`.github/agents/`](.github/agents/) |
| Use Gemini / Gemini CLI | [`GEMINI.md`](GEMINI.md) |
| Use a generic repository-aware agent | [`AGENTS.md`](AGENTS.md) |
| See all tool mappings | [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md) |
| Validate the repository | [`scripts/validate-agentdefaults.py`](scripts/validate-agentdefaults.py) + [`scripts/validate-cross-tool-routing.py`](scripts/validate-cross-tool-routing.py) |

## Principal Engineering Routing

| Scope | Canonical agent | Skill | Quickstart | Copilot adapter |
|---|---|---|---|---|
| DevOps/platform | [`agents/principal-devops-engineer.md`](agents/principal-devops-engineer.md) | [`skills/production-devops-engineering.md`](skills/production-devops-engineering.md) | [`docs/quickstarts/principal-devops-engineer.md`](docs/quickstarts/principal-devops-engineer.md) | [`.github/agents/principal-devops-engineer.agent.md`](.github/agents/principal-devops-engineer.agent.md) |
| AI engineering | [`agents/principal-ai-engineer.md`](agents/principal-ai-engineer.md) | [`skills/production-ai-engineering.md`](skills/production-ai-engineering.md) | [`docs/quickstarts/principal-ai-engineer.md`](docs/quickstarts/principal-ai-engineer.md) | [`.github/agents/principal-ai-engineer.agent.md`](.github/agents/principal-ai-engineer.agent.md) |
| Materially cross-domain AI + DevOps | [`agents/principal-ai-devops-engineer.md`](agents/principal-ai-devops-engineer.md) | [`skills/production-ai-devops-engineering.md`](skills/production-ai-devops-engineering.md) | [`docs/quickstarts/principal-ai-devops-engineer.md`](docs/quickstarts/principal-ai-devops-engineer.md) | [`.github/agents/principal-ai-devops-engineer.agent.md`](.github/agents/principal-ai-devops-engineer.agent.md) |

Use the smallest correct owner. Infrastructure hosting an AI workload is still DevOps-only unless AI application behavior also requires material change.

## Specialist Engineering Routes

| Need | Start with |
|---|---|
| Design, build, or audit another AI agent | [`docs/quickstarts/agent-builder.md`](docs/quickstarts/agent-builder.md) |
| Choose or challenge an automation platform | [`AUTOMATION_PLATFORM_INDEX.md`](AUTOMATION_PLATFORM_INDEX.md) |

## Other Featured Stacks

| Need | Start with |
|---|---|
| Google Play growth / ASO | [`docs/quickstarts/google-play-growth.md`](docs/quickstarts/google-play-growth.md) |
| Palmier Pro MCP video editing | [`docs/quickstarts/palmierpro-mcp.md`](docs/quickstarts/palmierpro-mcp.md) |
| App-market browser research | [`docs/quickstarts/app-market-research.md`](docs/quickstarts/app-market-research.md) |
| Community app-idea validation | [`docs/quickstarts/community-app-validation.md`](docs/quickstarts/community-app-validation.md) |
| Token economy | [`agents/token-economy-orchestrator.md`](agents/token-economy-orchestrator.md) |
| Wear OS development | [`WEAROS_DEVELOPMENT_INDEX.md`](WEAROS_DEVELOPMENT_INDEX.md) |
| Wear OS Play Store release | [`WEAROS_INDEX.md`](WEAROS_INDEX.md) |
| US-Europe travel preparation | [`TRAVEL_INDEX.md`](TRAVEL_INDEX.md) |

## Featured Stack Registry

The authoritative stack composition is [`agentdefaults.manifest.json`](agentdefaults.manifest.json). It currently registers:

- Agent Architect and Builder
- Principal AI and DevOps Engineering
- Principal DevOps Engineering
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
schemas/  machine-readable workflow contracts
```

Tool-specific entrypoints and wrappers route to these files; they are not separate canonical implementations.

## Tool Entrypoints

```text
OpenAI Codex             -> AGENTS.md
Claude Code              -> CLAUDE.md -> @AGENTS.md
GitHub Copilot           -> .github/copilot-instructions.md + .github/agents/*.agent.md
Gemini                    -> GEMINI.md
Generic repo-aware agent -> AGENTS.md
```

See [`docs/tool-integration-guide.md`](docs/tool-integration-guide.md) for details.

## Validation

Run:

```bash
python3 scripts/validate-agentdefaults.py
python3 scripts/validate-cross-tool-routing.py
```

The first covers existing structure, schemas, manifest integrity, stack invariants, and Markdown links. The second covers cross-tool entrypoints, engineering routing, Claude import wiring, quickstarts, manifest engineering-stack registration, and principal Copilot wrapper mappings.

Do not report either validator as passed unless it actually ran successfully.
