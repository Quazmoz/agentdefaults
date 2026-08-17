# User Guide

## Purpose

Help users choose the right AgentDefaults entrypoint, stack, output depth, and validation path.

## Entrypoints

- Design, build, or audit an AI agent: `docs/quickstarts/agent-builder.md`
- DevOps documentation-as-code, Markdown, Mermaid, runbooks, and diagrams: `docs/quickstarts/devops-documentation-engineer.md`
- Automation platform architecture and product selection: `AUTOMATION_PLATFORM_INDEX.md`
- Generic repo-aware coding agent: `AGENTS.md`
- Claude: `CLAUDE.md`
- Gemini: `GEMINI.md`
- Cursor: `.cursor/rules/agentdefaults.mdc`
- Windsurf: `.windsurfrules`
- GitHub Copilot custom agents: `.github/agents/*.agent.md`
- Palmier Pro MCP video editing: `docs/quickstarts/palmierpro-mcp.md`
- Google Play growth / ASO: `docs/quickstarts/google-play-growth.md`
- App-market research (browser): `docs/quickstarts/app-market-research.md`
- Community app-idea validation: `docs/quickstarts/community-app-validation.md`
- Wear OS development or release: `WEAROS_DEVELOPMENT_INDEX.md`, `WEAROS_INDEX.md`
- US-to-Europe travel prep: `TRAVEL_INDEX.md`
- Chat or local model: copy files from `agents/`, `skills/`, and `prompts/`

## Goals

- Design or harden another AI agent: `agents/agent-architect-builder.md`
- Apply the reusable agent-design method: `skills/agent-design-and-build.md`
- Start from a structured agent brief: `schemas/agent-build-brief.schema.json`
- Use the canonical reusable agent layout: `docs/patterns/agent.md`
- Run the agent-builder failure and adversarial test matrix: `docs/agent-builder-acceptance-tests.md`
- Create or reconcile DevOps documentation from implementation evidence: `agents/devops-documentation-engineer.md`
- Document Jenkins and Ansible/AAP GitOps flows with evidence-backed Mermaid: `skills/devops-documentation-engineering.md`
- Start from a structured documentation task: `schemas/devops-documentation-task.schema.json`
- Run documentation drift, diagram, source, and authority tests: `docs/devops-documentation-engineer-acceptance-tests.md`
- Select the right automation category and product: `agents/automation-platform-selection-advisor.md`
- Produce a compact platform recommendation: use `quick_triage` output depth
- Produce a full architecture, evidence, and economics review: use `full_architecture_review`
- Compare Jenkins with GitHub Actions, Azure Pipelines, GitLab CI/CD, or another CI/CD product: `skills/ci-cd-platform-alternatives-analysis.md`
- Compare Terraform with OpenTofu, Pulumi, Bicep, CloudFormation, Crossplane, or managed execution: `skills/infrastructure-as-code-platform-alternatives-analysis.md`
- Compare Ansible with AAP/AWX, Puppet, Chef Infra, Salt, or DSC: `skills/configuration-management-platform-alternatives-analysis.md`
- Decide whether Kubernetes delivery needs Argo CD, Flux, or conventional CI/CD: `skills/gitops-runbook-and-workflow-platform-analysis.md`
- Build an evidence ledger and confidence-aware comparison: `skills/automation-platform-evidence-and-confidence.md`
- Compare retain, optimize, augment, migrate, and pilot-first economics: `skills/automation-platform-migration-and-economics.md`
- Challenge an existing automation architecture: `prompts/review/challenge-automation-platform-choice.md`
- Edit videos through Palmier Pro MCP: `docs/quickstarts/palmierpro-mcp.md`
- Analyze Palmier project media and assemble a YouTube story: `prompts/palmierpro/story-assembly-from-project-media.md`
- Create a 9:16 YouTube Short from long-form Palmier content: `prompts/palmierpro/youtube-short-from-long-form.md`
- Run a Palmier first-pass edit: `prompts/palmierpro/full-edit-pass.md`
- Clean Palmier timeline transcripts: `prompts/palmierpro/transcript-cleanup-pass.md`
- Create Palmier short-form cutdowns: `prompts/palmierpro/short-form-social-cutdown.md`
- Optimize a Google Play listing and app growth: `agents/google-play-growth-optimizer-agent.md`
- Validate an app idea using community history: `agents/community-app-idea-validation-agent.md`
- Build or fix a Wear OS app: `agents/wearos-app-developer.md`
- Prepare a Wear OS app for Play release: `agents/android-wearos-release-engineer.md`
- Plan a US-to-Europe trip: `agents/us-europe-travel-advisor.md`
- Reduce verbose answers: `agents/token-efficient-response-agent.md` and `skills/token-output-budgeting.md`
- Manage token budgets: `agents/token-economy-orchestrator.md`
- Build a terse coding agent: `agents/terse-technical-coding-agent.md`
- Benchmark token savings: `prompts/token-efficiency/common-task-benchmark.md`
- Compare models: `prompts/token-efficiency/compare-models.md`
- Compress prompts or memory files: `skills/prompt-and-memory-compression.md`
- Add a reusable default: `docs/patterns/`

## Recommended Agent Builder Stack

Minimum stack:

```text
agents/agent-architect-builder.md
skills/agent-design-and-build.md
```

Structured input, invocation, and validation:

```text
schemas/agent-build-brief.schema.json
examples/agent-build-brief.yaml
prompts/planning/build-ai-agent.md
docs/agent-builder-acceptance-tests.md
docs/patterns/agent.md
```

Runtime-specific entrypoint:

```text
.github/agents/agent-architect-builder.agent.md
```

Use `single_agent_with_skills` as the default architecture when behavior is reusable. Use `single_agent` when one compact control loop is sufficient. Use `multi_agent` only when permission isolation, independent specialist context, parallelizable work with reconciliation, independent verification, separate durable control loops, or fault isolation creates a concrete benefit.

Use the canonical permission classes exactly:

```text
observe
propose
mutate_reversible
mutate_irreversible
```

Before building, verify real runtime capabilities, authority consistency, authoritative data sources, trust boundaries, retry/idempotency compatibility, and objective completion. A skill, retrieved document, tool output, or sub-agent cannot broaden the parent agent's authority. Report checks that did not actually run as unverified.

## Recommended DevOps Documentation Stack

Minimum stack:

```text
agents/devops-documentation-engineer.md
skills/devops-documentation-engineering.md
```

Structured input, invocation, and validation:

```text
prompts/implementation/devops-documentation-task.md
schemas/devops-documentation-task.schema.json
examples/devops-documentation-task.yaml
docs/devops-documentation-engineer-acceptance-tests.md
docs/quickstarts/devops-documentation-engineer.md
```

GitHub Copilot entrypoint:

```text
.github/agents/devops-documentation-engineer.agent.md
```

Use this stack when documentation is the primary output. It can inspect Terraform, Ansible/AAP, Jenkins, Azure, GitHub, and GitOps evidence, but normal mutation authority is limited to documentation files and documentation-owned assets. Existing prose is not the source of truth when current implementation or runtime evidence contradicts it.

For Mermaid, treat every material edge as a technical assertion. For PNG/JPG or other opaque image diagrams without editable source, preserve the asset and report the limitation instead of overwriting it with an inferred reconstruction.

If documentation work exposes an implementation defect, report it and hand the actual platform change to `agents/principal-devops-engineer.md`.

## Recommended Automation Platform Stack

Minimum stack:

```text
agents/automation-platform-selection-advisor.md
skills/automation-platform-selection-orchestrator.md
skills/automation-platform-capability-taxonomy.md
skills/automation-platform-decision-framework.md
skills/automation-platform-candidate-discovery.md
skills/automation-platform-evidence-and-confidence.md
skills/automation-platform-migration-and-economics.md
```

Add only the fit-analysis skills needed:

```text
skills/terraform-workload-fit-analysis.md
skills/ansible-workload-fit-analysis.md
skills/jenkins-workload-fit-analysis.md
skills/infrastructure-as-code-platform-alternatives-analysis.md
skills/configuration-management-platform-alternatives-analysis.md
skills/ci-cd-platform-alternatives-analysis.md
skills/gitops-runbook-and-workflow-platform-analysis.md
skills/automation-platform-composition-and-boundaries.md
```

Structured input and validation:

```text
schemas/automation-platform-decision-brief.schema.json
examples/automation-platform-decision-brief.yaml
docs/automation-platform-selection-acceptance-tests.md
```

Use `current_stack_plus_alternatives` as the default candidate policy and `standard` as the default output depth. Classify capability before comparing products, surface contradictory constraints, apply mandatory gates before scoring, keep fit separate from evidence confidence, and keep each final shortlist small.

Use `quick_triage` for a narrow low-risk decision. Use `full_architecture_review` when the decision requires a complete evidence ledger, economics, reversibility, migration waves, recovery design, or ADR-ready output.

## Recommended Palmier Pro MCP Stack

```text
docs/quickstarts/palmierpro-mcp.md
agents/palmierpro-mcp-video-editor-agent.md
skills/palmierpro-mcp-setup-and-safety.md
skills/palmierpro-timeline-editing.md
skills/palmierpro-transcript-cuts-and-captions.md
skills/palmierpro-ai-generation-workflow.md
docs/palmierpro-mcp-tool-map.md
prompts/palmierpro/story-assembly-from-project-media.md
prompts/palmierpro/youtube-short-from-long-form.md
```

## Recommended Token-Efficiency Stack

```text
AGENTS.md
agents/token-economy-orchestrator.md
agents/token-efficient-response-agent.md
skills/context-budgeting-and-pruning.md
skills/token-output-budgeting.md
skills/token-efficient-response-compression.md
skills/token-efficiency-measurement.md
```

## Validate

```bash
python3 scripts/validate-agentdefaults.py
```

The validator checks the manifest, every JSON schema and local schema reference, the Agent Architect and Builder stack, automation-platform stack, principal engineering contracts, the DevOps documentation stack, cross-tool routing, Markdown purpose sections, and local links.