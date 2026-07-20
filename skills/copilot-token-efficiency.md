# GitHub Copilot Token Efficiency Skill

## Purpose

Use this skill to reduce GitHub Copilot spend without losing output quality. It maps the model-agnostic token levers in this library onto how Copilot actually bills and works: usage-based **AI Credits**, model multipliers, free inline completions, scoped chat context, and the `.github` customization files.

Under usage-based billing, **tokens are money**: chat, edit, and agent requests are metered by input + output + cached tokens at each model's published rate. Cutting tokens cuts the bill directly.

Pair this with the canonical levers in [`skills/context-budgeting-and-pruning.md`](context-budgeting-and-pruning.md) (input), [`skills/token-output-budgeting.md`](token-output-budgeting.md) (output), and [`skills/token-efficiency-measurement.md`](token-efficiency-measurement.md) (proof).

## When To Use

Use when:

- A team or user wants to lower Copilot cost or stay inside an AI Credit / premium-request budget
- Setting up `.github/copilot-instructions.md`, `*.instructions.md`, or `*.prompt.md` for a repo
- Deciding which model to select for a task
- Chat/agent runs feel expensive, slow, or over-verbose
- Onboarding a team to cost-aware Copilot habits

Do not use to disable Copilot where it adds real value, or to push users onto an underpowered model for tasks that genuinely need a stronger one. Cheaper-but-wrong is the most expensive outcome.

## Billing Model (Verify Current Rates)

As of June 2026, Copilot bills paid plans with **usage-based AI Credits** (credits replaced the premium-request unit). Key facts that drive every tactic below:

- **Inline code completions and next-edit suggestions are free** on all paid plans — they do not consume credits.
- **Chat, edit (inline/multi-file), and agent requests consume credits**, priced by token usage (input + output + cached) at the selected model's rate.
- **Model rate varies by an order of magnitude** — a frugal model can cost ~10–20× less per token than a top-tier reasoning model for the same task.
- **Legacy plans** may still use premium-request multipliers: a base tier is included at 1×, and other models carry higher multipliers (legacy annual multipliers rose in June 2026). The same tactics apply; only the unit differs.
- **Copilot code review** consumes credits and GitHub Actions minutes — treat it as a deliberate spend, not an always-on default.

Exact prices, multipliers, and plan allowances change often. Confirm current values at GitHub's docs before quoting numbers: `https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing`.

## Inputs Needed

- Copilot plan and the AI Credit / premium-request budget, if known
- Task type: completion, quick Q&A, scoped edit, multi-file refactor, agent task, review
- Repo size and whether whole-workspace context is being attached
- Current model selection habit (manual vs auto)
- Whether `.github` customization files already exist

## Cost Levers, Ranked By Impact

Apply in order; the first two move the bill the most.

### 1. Choose the cheapest model that can do the task

Model selection is the dominant cost lever. Match model tier to task difficulty instead of defaulting to the strongest one.

| Task | Use |
|---|---|
| Autocomplete, boilerplate, obvious edits | Inline completions (free) — no chat request |
| Simple Q&A, rename, small fix, docstring, format | Frugal/fast tier (e.g. GPT-5 mini, Gemini Flash, Claude Haiku) |
| Most day-to-day chat, scoped edits, reviews | Standard tier (mid Sonnet / GPT-5 class) |
| Hard architecture, deep debugging, large refactors | High/reasoning tier — only when the task earns it |

- Prefer **auto model selection** when available; it routes by task and, on legacy plans, applies a multiplier discount.
- Do not run a top-tier reasoning model on a rename or a typo. That is the most common avoidable spend.

### 2. Scope the context (input tokens)

Input tokens are billed every request, and a long thread re-sends prior turns.

- Attach **specific files or symbols** (`#file`, `#selection`, `#sym`) instead of `@workspace` or whole folders when you already know where the code lives.
- Reserve `@workspace` / broad codebase search for genuine "where is this?" questions.
- **Start a new chat per task.** Long threads carry stale context forward into every priced request — the most overlooked cost in day-to-day use.
- Don't paste large logs, lockfiles, or generated output into chat; attach the few relevant lines. (See [`skills/context-budgeting-and-pruning.md`](context-budgeting-and-pruning.md).)

### 3. Pick the right mode

Cost rises left to right: **completions (free) → ask → edit → agent**.

- Use **inline completions** for code you can guide as you type — zero credits.
- Use **ask** for explanations and decisions.
- Use **edit** for a known, scoped change across known files.
- Use **agent** only for genuinely multi-step work. Agent loops re-send context and tools each turn and can quietly become the largest single cost. Give it a tight, well-scoped task; don't use it as a default chat.

### 4. Cut output verbosity (output tokens)

Output tokens are billed too. A standing "be concise" instruction trims every future response.

- Put concise-output rules in `.github/copilot-instructions.md` (see template below).
- Ask for diffs/patches over full-file rewrites; ask for the change, not a narrated essay.
- See [`skills/token-output-budgeting.md`](token-output-budgeting.md) for response modes.

### 5. Reuse instead of re-typing (the `.github` customization layer)

These files load automatically and standardize behavior, so you stop paying to re-establish context and conventions in every thread.

- **`.github/copilot-instructions.md`** — repo-wide standing instructions (style, conventions, "be concise"). Applies to every request.
- **`.github/instructions/*.instructions.md`** — path-specific rules via an `applyTo` glob in frontmatter (e.g. `applyTo: "**/*.test.*"`). Multiple matching files **stack** (union, no override), so keep each one small and targeted.
- **`.github/prompts/*.prompt.md`** — reusable prompts for recurring tasks (review checklist, scaffolding, migration). Invoke instead of retyping a long prompt every time.

### 6. Make code review deliberate

Automated Copilot code review spends credits and Actions minutes per run. Scope it to meaningful PRs/paths rather than every push.

## Drop-In `copilot-instructions.md`

Copy into `.github/copilot-instructions.md` in any repo. See [`examples/copilot-token-efficiency.md`](../examples/copilot-token-efficiency.md) for the full recipe with `*.instructions.md` and `*.prompt.md` samples.

```markdown
# Copilot Instructions

## Response style
- Lead with the answer, change, or recommendation. No preamble or filler.
- Prefer diffs/patches over full-file rewrites. Show only changed regions.
- Use `Done / Changed / Validate` for completed work and `Cause → Fix → Check` for debugging.
- Be terse for an expert audience; expand only when asked.

## Context
- Edit only the files relevant to the task; do not restate unchanged code.
- Ask before pulling in broad workspace context for a narrow change.

## Accuracy
- Preserve exact paths, commands, errors, and identifiers.
- Mark unverified work as `Not verified`. Do not invent results, files, or APIs.
```

## What Not To Compromise

Saving credits never justifies losing correctness or safety. Keep:

- Exact paths, commands, errors, identifiers, and versions
- Security warnings and material risks
- Validation status (`Not verified` when true)
- The actual answer

Priority order when these conflict with cost: safety → correctness → user instructions → required validation/citations → token/credit reduction.

## Measurement

Prove savings instead of assuming them:

- Track AI Credit / premium-request consumption in GitHub billing (org-level cost centers and budgets on Business/Enterprise) before and after adopting these habits.
- For prompt/model A-B comparisons, use [`skills/token-efficiency-measurement.md`](token-efficiency-measurement.md): compare baseline vs candidate on the same task, score quality 1–5 separately, and adopt only if quality holds.
- Watch the lead indicators: fewer agent runs for scoped work, lower share of high-tier-model requests, shorter threads.

## Expected Output

When asked to apply this skill, produce one of: a tailored `.github` customization file set, a ranked list of where a user/team is overspending with the specific fix, or a model-selection recommendation for a given task — each tied to the lever it pulls.

## Quality Bar

A successful application:

- Names the dominant lever for the situation (usually model choice or context scope)
- Gives concrete, Copilot-native actions (model, mode, `#`-reference, or `.github` file), not generic advice
- Preserves correctness, safety, and validation
- Is measurable against AI Credit / premium-request usage
- Does not push users onto an underpowered model for work that needs more

## Copy-Paste Skill Prompt

```text
Apply GitHub Copilot token efficiency. Treat tokens as money: chat, edit, and agent requests bill input + output + cached tokens at the selected model's rate; inline completions are free.

Optimize in this order: (1) pick the cheapest model that can do the task and prefer auto-selection; (2) scope context with specific files/#-references instead of @workspace, and start a fresh chat per task; (3) use the cheapest sufficient mode — completions, then ask, then edit, then agent; (4) cut output verbosity via concise standing instructions; (5) reuse .github/copilot-instructions.md, *.instructions.md (applyTo globs, which stack), and *.prompt.md instead of re-typing context; (6) make automated code review deliberate.

Never trade away correctness, safety, exact identifiers, or validation status to save credits. When asked, return a tailored .github customization set, a ranked overspend list with fixes, or a model-selection recommendation — each tied to its lever. Verify current prices/multipliers at GitHub's billing docs before quoting numbers.
```
