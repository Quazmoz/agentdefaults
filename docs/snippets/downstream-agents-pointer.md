# Downstream AGENTS.md Pointer Block

## Purpose

Give app repositories one small, identical block for their root `AGENTS.md` that points agents to the Humanizer skill and the external tools guide in AgentDefaults by URL. Codex and other repo-aware agents read `AGENTS.md`; they do not see this repository unless something points them here.

## How to use it

1. Open the app repository's root `AGENTS.md`.
2. If a block between `<!-- agentdefaults:writing-tools:start -->` and `<!-- agentdefaults:writing-tools:end -->` already exists, replace everything between and including the markers. Otherwise paste the block at the end of the file.
3. Paste it exactly as written. Do not edit it per repo; change it here and re-paste everywhere.
4. Keep it outside any generated fences (for example `ponytail` or `graft`).

Plain ChatGPT Projects do not read `AGENTS.md`. For those, upload `chatgpt-projects/android-app-developer/sources/09_HUMANIZER_WRITING_STANDARD.md` as a project source.

## Block

```markdown
<!-- agentdefaults:writing-tools:start -->
## Writing and external tools

- Before handing over any human-facing prose, run the Humanizer pass: https://github.com/Quazmoz/agentdefaults/blob/main/skills/humanizer.md
  - Applies to Play Store listings, release notes and "What's new" text, READMEs and marketing docs, social posts and captions, YouTube titles and descriptions, and emails.
  - Skip it for code, commit messages, and terse technical docs.
  - It changes wording only. Never add a claim, number, feature, or keyword the source does not support, and recount Play character limits afterward.
- Before adding Hyperframes, Apify MCP, OpenSEO, Agent Skills, Codeburn, or Ponytail, read when to use each and what it costs: https://github.com/Quazmoz/agentdefaults/blob/main/docs/external-tools.md
- This block is maintained in Quazmoz/agentdefaults at docs/snippets/downstream-agents-pointer.md. Change it there, not here.
<!-- agentdefaults:writing-tools:end -->
```
