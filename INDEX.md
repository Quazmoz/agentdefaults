# AgentDefaults Index

Fast lookup for agents, skills, prompts, and recommended stacks.

Use this file when an AI agent needs to quickly determine which defaults exist and how to compose them. Use `README.md` for the broader human-facing project overview.

## Quick Selection

| Need | Start With | Add Skills / Prompts |
|------|------------|----------------------|
| Work on Quinn's Kubernetes homelab | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-gitops-change-management.md`, `skills/kubernetes-homelab-troubleshooting.md`, `skills/context-budgeting-and-pruning.md`, `skills/token-output-budgeting.md` |
| Make any agent more concise | `agents/token-efficient-response-agent.md` | `skills/token-efficient-response-compression.md`, `skills/token-output-budgeting.md` |
| Manage context/tool/output token budgets across long tasks | `agents/token-economy-orchestrator.md` | `skills/context-budgeting-and-pruning.md`, `skills/token-output-budgeting.md`, `skills/token-efficiency-measurement.md` |
| Make a coding agent terse and senior-engineer focused | `agents/terse-technical-coding-agent.md` | `skills/context-budgeting-and-pruning.md`, `skills/token-output-budgeting.md` |
| Compress reusable prompts or memory files | `skills/prompt-and-memory-compression.md` | `prompts/token-efficiency/compress-memory-file.md`, `prompts/token-efficiency/agent-retrofit.md` |
| Measure token savings for common tasks | `skills/token-efficiency-measurement.md` | `prompts/token-efficiency/common-task-benchmark.md`, `prompts/token-efficiency/compare-models.md` |
| Research authenticated or automation-hostile sites with Comet | `agents/comet-authenticated-research-agent.md` | `skills/comet-authenticated-research.md`, `skills/comet-local-bridge-safety.md`, `skills/context-budgeting-and-pruning.md` |
| Improve classic SEO and AI search visibility | `agents/seo-ai-search-optimization-agent.md` | `skills/token-efficient-response-compression.md`, `skills/token-output-budgeting.md` |
| Design or review a local Comet bridge | `agents/comet-authenticated-research-agent.md` | `skills/comet-local-bridge-safety.md` |
| Diagnose Kubernetes homelab runtime issues | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-homelab-troubleshooting.md`, `skills/context-budgeting-and-pruning.md` |
| Add or modify Kubernetes GitOps manifests | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-gitops-change-management.md`, `skills/token-output-budgeting.md` |

## Agents

### Kubernetes Homelab Engineer

**Path:** `agents/kubernetes-homelab-engineer.md`

Use for Quinn's `Quazmoz/K8SHomelab` repo and similar production-style homelab Kubernetes environments.

Best for:

- Flux CD / GitOps workflows
- HelmRelease and Kustomize changes
- Kubernetes app deployment
- Homelab networking, storage, scheduling, and observability
- Calico, MetalLB, NGINX Ingress, WireGuard, SOPS/Age
- OpenWebUI, Phoenix, n8n, AWX, MCPO, Context Forge, and MCP infrastructure

Key guardrails:

- Preserve GitOps as source of truth.
- Never commit plaintext secrets.
- Respect Oracle/WireGuard node constraints.
- Treat the repo as public unless proven otherwise.
- Include validation and rollback for risky changes.

### Token-Efficient Response Agent

**Path:** `agents/token-efficient-response-agent.md`

Use as a behavior layer when responses should be concise, direct, and high-signal.

Best for:

- Reducing verbose agent output
- Expert technical Q&A
- Compact repo-work summaries
- Iterative coding workflows
- Prompt and handoff compression

Key guardrails:

- Brevity must not override safety, accuracy, citations, validation, or uncertainty.
- Do not claim commands or checks were run unless they actually were.
- Prefer the lowest sufficient verbosity.

### Token Economy Orchestrator

**Path:** `agents/token-economy-orchestrator.md`

Use when the agent must actively manage input, context, tool-result, and output tokens across long-running workflows.

Best for:

- Long agent sessions
- Multi-file repo tasks
- Context-window preservation
- Cost and latency reduction
- Benchmarkable prompt/agent optimization
- Model-agnostic concise behavior across hosted and local LLMs

Key guardrails:

- Compress language, not meaning.
- Preserve exact code, paths, commands, errors, citations, validation, risks, and user constraints.
- Do not reduce safety or correctness for token savings.
- Use compact handoffs before context gets noisy.

### Terse Technical Coding Agent

**Path:** `agents/terse-technical-coding-agent.md`

Use for senior-engineer coding workflows where the assistant should make focused changes and avoid excessive narration.

Best for:

- IDE coding agents
- Bug fixes and refactors
- PR review comments
- CI failure analysis
- Release-blocker triage
- Small-to-medium implementation tasks

Key guardrails:

- Keep diffs focused and reviewable.
- Preserve behavior unless asked to change it.
- Do not reformat unrelated code.
- Validation must be run or explicitly marked not run.
- Compact communication must not mean unreadable source code.

### Comet Authenticated Research Agent

**Path:** `agents/comet-authenticated-research-agent.md`

Use when research requires Comet running locally as a visible browser, especially for authenticated or automation-hostile pages.

Best for:

- Authenticated website research
- Human-in-the-loop login, MFA, SSO, CAPTCHA, or approval flows
- JavaScript-heavy dashboards and portals
- Pages that block or degrade headless automation
- Browser-only verification where Comet adds value

Key guardrails:

- Never ask for passwords, MFA codes, cookies, tokens, session storage, local storage, request headers, or private keys.
- User must authenticate directly in Comet.
- Use the least invasive page context available.
- Require confirmation before account-mutating actions.
- Treat Comet summaries as research aids, not source-of-truth.

### SEO and AI Search Optimization Agent

**Path:** `agents/seo-ai-search-optimization-agent.md`

Use for practical search visibility work across classic SEO, Google AI search features, answer engines, app/product launches, GitHub projects, YouTube videos, Product Hunt pages, and consultant/product landing pages.

Best for:

- Website SEO audits
- AI-search readiness reviews
- Consultant site and portfolio optimization
- Android / Wear OS app landing page optimization
- Google Play listing and website alignment
- GitHub README discoverability
- YouTube and Product Hunt launch discoverability
- Content gap analysis and topic planning
- Metadata, schema, internal link, sitemap, robots.txt, and measurement fixes
- Turning product features into high-intent landing pages and content briefs

Key guardrails:

- Treat AI SEO, AEO, and GEO as extensions of durable SEO fundamentals, not hacks.
- Do not promise rankings, AI Overview inclusion, or answer-engine citations.
- Do not recommend keyword stuffing, fake reviews, fake mentions, fake backlinks, doorway pages, cloaking, or scaled low-value AI content.
- Do not add structured data for content that is not visible to users.
- Tie recommendations to business outcomes and measurement.

## Skills

### Token-Efficient Response Compression

**Path:** `skills/token-efficient-response-compression.md`

Use to compress verbose agent output without losing correctness.

Covers:

- Direct answers
- Decisions
- Work summaries
- Reviews
- Debugging
- Prompts
- Agent handoffs

### Context Budgeting and Pruning

**Path:** `skills/context-budgeting-and-pruning.md`

Use to reduce input/context token usage before the agent answers or changes code.

Covers:

- Smallest-relevant-context selection
- Context source ranking
- Context ledgers
- Large-input summarization
- Duplicate/superseded context pruning
- Compact handoff creation

### Token Output Budgeting

**Path:** `skills/token-output-budgeting.md`

Use to control output verbosity with explicit modes and final cut passes.

Covers:

- Micro, compact, work-summary, review, handoff, and deep modes
- `Cause → Fix → Check`
- `Issue → Impact → Fix`
- `Path — change`
- `Done → Changed → Validate`
- Exact technical identifier preservation

### Prompt and Memory Compression

**Path:** `skills/prompt-and-memory-compression.md`

Use to rewrite reusable prompts, memory files, and instruction files into smaller recurring context.

Covers:

- Behavior-preserving compression
- Exact preservation of code, commands, paths, schemas, and safety rules
- Deduplication and normalization
- Approximate token savings reports
- Human-review risk notes

### Token Efficiency Measurement

**Path:** `skills/token-efficiency-measurement.md`

Use to verify whether concise prompts improve token usage without degrading quality.

Covers:

- Baseline vs candidate comparison
- Input/output/tool token tracking
- 1-5 quality scoring
- Savings formulas
- Pass/fail criteria
- Safety-critical regression checks

### Kubernetes GitOps Change Management

**Path:** `skills/kubernetes-gitops-change-management.md`

Use for safe Kubernetes repo changes.

Covers:

- Kustomize inclusion
- HelmRelease and manifest review
- Secret safety
- Storage and scheduling guardrails
- Ingress and MetalLB safety
- Validation and rollback

### Kubernetes Homelab Troubleshooting

**Path:** `skills/kubernetes-homelab-troubleshooting.md`

Use for diagnosing Kubernetes homelab failures.

Covers:

- Flux errors
- Pod scheduling and image failures
- DNS and CoreDNS
- Ingress failures
- MetalLB issues
- Calico and VXLAN
- WireGuard and Oracle node problems
- Local PV/PVC binding issues

### Comet Authenticated Research

**Path:** `skills/comet-authenticated-research.md`

Use for human-in-the-loop authenticated research through Comet.

Covers:

- Safe login flow
- Account/workspace confirmation
- Minimal page context collection
- Verification of material claims
- Separation of account-specific and general findings
- Stop-points before mutating actions

### Comet Local Bridge Safety

**Path:** `skills/comet-local-bridge-safety.md`

Use when building or reviewing a bridge between an agent and local Comet.

Covers:

- Narrow command surfaces
- Local-only binding
- Session-secret denial
- User confirmation for mutations
- Prompt-injection resistance
- Bridge threat modeling
- Safe logging and redaction

## Prompts

### Common Task Token Efficiency Benchmark

**Path:** `prompts/token-efficiency/common-task-benchmark.md`

Use to benchmark baseline vs token-efficient prompts across common engineering tasks.

Covers:

- Shared task set
- Equal test conditions
- Output and net savings calculations
- Quality scoring
- Adopt/revise/reject decision

### Token Efficiency Agent Retrofit

**Path:** `prompts/token-efficiency/agent-retrofit.md`

Use to add token-efficiency behavior to an existing agent or prompt while preserving its original role.

Covers:

- Context budgeting additions
- Tool economy additions
- Output budgeting additions
- Behavior-critical preservation
- Change notes and benchmark recommendation

### Compress Memory or Instruction File

**Path:** `prompts/token-efficiency/compress-memory-file.md`

Use to compress reusable memory or instruction files for lower recurring input-token cost.

Covers:

- Exact preservation rules
- Deduplication
- Compact directive rewriting
- Approximate savings report
- Human-review notes

### Compare Models for Token Efficiency

**Path:** `prompts/token-efficiency/compare-models.md`

Use to compare whether the same token-efficiency prompt works across different models and runtimes.

Covers:

- Identical task comparison
- Model-specific regressions
- Output savings and quality table
- Recommended default prompt/mode

## Recommended Stacks

### Token Economy Stack

```text
Behavior layers:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficient-response-compression.md
  skills/token-efficiency-measurement.md

Prompts:
  prompts/token-efficiency/common-task-benchmark.md
```

### Terse Coding Work

```text
Base / behavior layer:
  agents/terse-technical-coding-agent.md

Skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficient-response-compression.md

Optional measurement:
  skills/token-efficiency-measurement.md
  prompts/token-efficiency/common-task-benchmark.md
```

### Prompt / Memory Compression

```text
Skills:
  skills/prompt-and-memory-compression.md
  skills/token-efficiency-measurement.md

Prompts:
  prompts/token-efficiency/compress-memory-file.md
  prompts/token-efficiency/agent-retrofit.md
  prompts/token-efficiency/compare-models.md
```

### Kubernetes Homelab Work

```text
Base agent:
  agents/kubernetes-homelab-engineer.md

Behavior layer:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Skills:
  skills/kubernetes-gitops-change-management.md
  skills/kubernetes-homelab-troubleshooting.md
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
```

### Comet Authenticated Research

```text
Base agent:
  agents/comet-authenticated-research-agent.md

Behavior layer:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Skills:
  skills/comet-authenticated-research.md
  skills/comet-local-bridge-safety.md
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
```

### SEO and AI Search Optimization

```text
Base agent:
  agents/seo-ai-search-optimization-agent.md

Behavior layer:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Optional for private dashboards:
  agents/comet-authenticated-research-agent.md

Useful inputs:
  target URL, business goal, conversion action, analytics/Search Console data, app listing, GitHub repo, YouTube/Product Hunt URLs, competitors, target market
```

### Concise General Technical Agent

```text
Behavior layer:
  agents/token-economy-orchestrator.md
  agents/token-efficient-response-agent.md

Skills:
  skills/context-budgeting-and-pruning.md
  skills/token-output-budgeting.md
  skills/token-efficient-response-compression.md
```

## Selection Rules

1. Choose **one domain agent** first.
2. Add `agents/token-economy-orchestrator.md` for long-running work where context/tool/output budgets matter.
3. Add `agents/token-efficient-response-agent.md` when concise behavior is desired.
4. Add `agents/terse-technical-coding-agent.md` for coding sessions that need senior, low-narration behavior.
5. Add only the skills needed for the task.
6. Prefer narrow skills over copying every file into context.
7. For repo work, inspect relevant files before making changes.
8. For authenticated browsing, keep credentials and session secrets out of agent context.
9. For risky infrastructure work, include validation and rollback.
10. For SEO and AI-search work, inspect the actual page, repo, listing, or analytics data before making specific claims when tools are available.
11. For token-efficiency claims, use `skills/token-efficiency-measurement.md` or `prompts/token-efficiency/common-task-benchmark.md`.

## Maintenance Rules

When adding a new default:

1. Add the file under `agents/`, `skills/`, `prompts/`, or `instructions/`.
2. Add it to `README.md` if it should be visible to humans.
3. Add it to this `INDEX.md` if agents should discover and compose it.
4. Include purpose, when-to-use, inputs, expected output, quality bar, and notes.
5. Keep copy-paste prompt blocks self-contained.
6. For token-efficiency defaults, include measurement or evaluation guidance.

## Status

Current index includes:

- 6 agents
- 9 skills
- 4 token-efficiency prompts

Future index sections should add instructions and examples as they are created.
