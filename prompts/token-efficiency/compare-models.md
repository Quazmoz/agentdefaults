# Compare Models for Token Efficiency Prompt

## Purpose

Use this prompt to compare how different models respond to the same token-efficiency instructions.

This helps verify that an agent default is flexible enough for frontier models, coding models, and smaller/local LLMs.

## Prompt

```text
You are evaluating model-agnostic token efficiency.

Goal:
Compare multiple models using the same baseline tasks and the same candidate token-efficiency prompt. Determine which models preserve quality while reducing tokens.

Models/runtimes:
1. <model A>
2. <model B>
3. <model C>

Candidate token-efficiency prompt:
<paste prompt>

Task set:
- Technical Q&A: explain a React re-render bug to an experienced developer.
- Debugging: diagnose expired JWTs sometimes being accepted.
- Code review: identify security issues from a short diff.
- DevOps: summarize a noisy CI/Docker failure and propose the fix.
- Handoff: compress a long task state into next-agent context.

Rules:
- Use identical task text for every model.
- Use deterministic settings where possible.
- Use the same tool policy for every model.
- Count input/output tokens using exact tokenizer when available; otherwise estimate as ceil(characters / 4).
- Score quality 1-5.
- Note failures specific to small/local models, such as over-compression, ambiguity, missed safety caveats, or instruction drift.

Report:

| Model | Avg Output Tokens | Avg Savings vs Baseline | Avg Quality | Main Regression | Decision |
|-------|-------------------|-------------------------|-------------|-----------------|----------|
| <model> | <count> | <pct> | <score> | <issue> | <adopt/revise/reject> |

Recommendation:
- Best default prompt: <prompt/version>
- Model-specific adjustment needed: <yes/no + details>
- Safe minimum verbosity mode: <mode>

Keep report compact. Do not include full raw outputs unless asked.
```

## Quality Bar

A useful comparison:

- Uses identical tasks and settings
- Separates token savings from quality
- Names model-specific regressions
- Does not overfit to one provider
- Produces a clear adoption decision
