Set up Ponytail for this repository:

https://github.com/DietrichGebert/ponytail

Requirements:

1. Inspect the repository’s existing agent configuration first:
   - AGENTS.md
   - CLAUDE.md
   - .github/copilot-instructions.md
   - .claude/
   - .codex/
   - any existing graft configuration or hooks

2. Make the setup repository-local wherever possible. Do not modify:
   - ~/.claude
   - ~/.codex
   - ~/.copilot
   - global shell profiles
   - global package configuration
   - unrelated repositories

3. Support:
   - Claude Code
   - Codex
   - GitHub Copilot Chat and Copilot CLI

4. Preserve existing agent integrations, especially graft. Do not overwrite or merge lifecycle hooks blindly. Keep Ponytail hooks separate from existing graft hooks unless the host requires an explicit compatible merge.

5. Use Ponytail’s official repository-local adapter patterns:
   - Add only the Ponytail guidance needed to the existing AGENTS.md.
   - Add or update CLAUDE.md as a small bridge to AGENTS.md if appropriate.
   - Add or merge .github/copilot-instructions.md for Copilot.
   - Add Codex-specific repository configuration only if this Codex version supports it.
   - Do not copy Ponytail’s entire AGENTS.md over the repository’s instructions.

6. If native Claude or Codex plugin installation is user-global rather than repository-local, do not install it automatically. Prefer the repository-local instruction adapter and document the optional native commands separately.

7. Keep Ponytail’s guidance complementary to the repository’s existing rules:
   - Do not weaken security, validation, accessibility, error handling, or data-loss protection.
   - Do not remove repository-specific workflows.
   - Do not add unnecessary dependencies, scripts, hooks, or abstractions.
   - Do not change application source code.

8. Add a short documentation file such as docs/AGENT_TOOLING.md only if the repository has an appropriate documentation location. Explain:
   - which files were added or changed;
   - that the setup is repository-local;
   - how graft and Ponytail coexist;
   - which native plugin commands are optional and user-scoped.

9. Before editing, inspect the Ponytail README and portability documentation for the current installation format. Do not rely on guessed command names.

10. Validate the result:
   - parse any changed JSON/TOML/YAML;
   - run the repository’s relevant configuration or lint checks;
   - run git diff --check;
   - verify existing graft configuration still works;
   - report any host-specific limitation honestly.

Make the smallest coherent change, preserve unrelated user changes, do not commit, and summarize the files changed and validation performed.