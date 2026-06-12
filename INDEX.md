# AgentDefaults Index

Fast lookup for agents, skills, and recommended stacks.

Use this file when an AI agent needs to quickly determine which defaults exist and how to compose them. Use `README.md` for the broader human-facing project overview.

## Quick Selection

| Need | Start With | Add Skills |
|------|------------|------------|
| Work on Quinn's Kubernetes homelab | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-gitops-change-management.md`, `skills/kubernetes-homelab-troubleshooting.md`, `skills/token-efficient-response-compression.md` |
| Make any agent more concise | `agents/token-efficient-response-agent.md` | `skills/token-efficient-response-compression.md` |
| Research authenticated or automation-hostile sites with Comet | `agents/comet-authenticated-research-agent.md` | `skills/comet-authenticated-research.md`, `skills/comet-local-bridge-safety.md`, `skills/token-efficient-response-compression.md` |
| Improve classic SEO and AI search visibility | `agents/seo-ai-search-optimization-agent.md` | `skills/token-efficient-response-compression.md` |
| Design or review a local Comet bridge | `agents/comet-authenticated-research-agent.md` | `skills/comet-local-bridge-safety.md` |
| Diagnose Kubernetes homelab runtime issues | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-homelab-troubleshooting.md` |
| Add or modify Kubernetes GitOps manifests | `agents/kubernetes-homelab-engineer.md` | `skills/kubernetes-gitops-change-management.md` |

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

## Recommended Stacks

### Kubernetes Homelab Work

```text
Base agent:
  agents/kubernetes-homelab-engineer.md

Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/kubernetes-gitops-change-management.md
  skills/kubernetes-homelab-troubleshooting.md
  skills/token-efficient-response-compression.md
```

### Comet Authenticated Research

```text
Base agent:
  agents/comet-authenticated-research-agent.md

Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/comet-authenticated-research.md
  skills/comet-local-bridge-safety.md
  skills/token-efficient-response-compression.md
```

### SEO and AI Search Optimization

```text
Base agent:
  agents/seo-ai-search-optimization-agent.md

Behavior layer:
  agents/token-efficient-response-agent.md

Optional for private dashboards:
  agents/comet-authenticated-research-agent.md

Useful inputs:
  target URL, business goal, conversion action, analytics/Search Console data, app listing, GitHub repo, YouTube/Product Hunt URLs, competitors, target market
```

### Concise General Technical Agent

```text
Behavior layer:
  agents/token-efficient-response-agent.md

Skills:
  skills/token-efficient-response-compression.md
```

## Selection Rules

1. Choose **one domain agent** first.
2. Add `agents/token-efficient-response-agent.md` when concise behavior is desired.
3. Add only the skills needed for the task.
4. Prefer narrow skills over copying every file into context.
5. For repo work, inspect relevant files before making changes.
6. For authenticated browsing, keep credentials and session secrets out of agent context.
7. For risky infrastructure work, include validation and rollback.
8. For SEO and AI-search work, inspect the actual page, repo, listing, or analytics data before making specific claims when tools are available.

## Maintenance Rules

When adding a new default:

1. Add the file under `agents/`, `skills/`, `prompts/`, or `instructions/`.
2. Add it to `README.md` if it should be visible to humans.
3. Add it to this `INDEX.md` if agents should discover and compose it.
4. Include purpose, when-to-use, inputs, expected output, quality bar, and notes.
5. Keep copy-paste prompt blocks self-contained.

## Status

Current index includes:

- 4 agents
- 5 skills

Future index sections should add prompts, instructions, and examples as they are created.
