# Safe Git sync for agent-managed local checkouts

## When to use

Use this for repositories edited both by local IDE/AI tools and remote GitHub agents. It avoids repeating Android Studio/JetBrains "Patch Conflict" dialogs during Project Update while preserving local edits. It is a Git workflow problem, not an Android build problem.

## Identify the conflict

In Android Studio's three-way Patch Conflict UI:

- **Your uncommitted changes** are edits in the local working tree.
- **Changes from remote** are newer commits Git is trying to integrate.
- **Result** is the proposed merged file.

Never click **Accept Right** or **Accept Left** across the board without checking whether the opposite side contains unique changes. **Accept Right** is reasonable only for a file whose local changes are known to be superseded by the remote. **Apply Changes** completes the chosen resolution.

If a dialog is already open, either resolve each conflict after reviewing the sides, or abort and use the terminal procedure below. Aborting does not intentionally erase committed Git history, but check `git status` before further operations.

## Inspect and preserve first

Run inside the affected repository, with no ongoing merge/rebase before starting a new one:

```bash
git status --short --branch
git diff HEAD -- docs/ARCHITECTURE.md
git log --oneline --decorate -5
git fetch origin
git log --oneline --left-right HEAD...origin/main
```

If you have **valuable local edits**, create a local topic branch for them rather than editing or committing directly on `main`. A new branch preserves your working tree, but the work still needs a deliberate commit before changing branches:

```bash
git switch -c work/local-changes
# Review your staged files, avoid secrets/build outputs, then commit intentional changes.
git add <specific-files>
git commit -m "Preserve local work"
git switch main
git merge --ff-only origin/main
```

Review the topic branch and cherry-pick or PR only the changes still needed. A branch switch can be blocked by unrelated local/untracked files: resolve those explicitly, never force-reset blindly.

If the local edits are **obsolete**, back up the file's full tracked diff before discarding it:

```bash
mkdir -p "$HOME/git-conflict-backups"
git diff HEAD -- docs/ARCHITECTURE.md > "$HOME/git-conflict-backups/architecture-local.patch"
# Check patch contents and size. Do not run the next command unless those local edits can be discarded.
git restore --source=HEAD --staged --worktree -- docs/ARCHITECTURE.md
git merge --ff-only origin/main
```

Do not copy private secrets into backup patches or commit them. `git restore` permanently replaces the named file's working-tree/index changes; preserve valuable content first. If other files remain dirty, merge may still refuse; that is intentional.

A stash is an option for short-lived work, but avoid automatically applying it after the pull: `git stash pop` or Android Studio's unshelve can produce exactly the same content conflict. Inspect `git stash list` and `git stash show -p` first and apply selectively.

## Default workflow to prevent recurrence

1. Treat local `main` as a synchronization branch. Remote agents publish through topic branches and reviewed PRs, rather than competing with local uncommitted changes on `main`.
2. Do local feature work in `work/... ` branches or separate Git worktrees. Commit deliberate work before updating `main`.
3. Pull only when the local main checkout has a clean working tree. Use `git fetch origin` followed by `git merge --ff-only origin/main`. If fast-forward is impossible, inspect divergence instead of generating a merge commit automatically.
4. In agent workflows, change stable architecture/agent instructions only when the invariant or structural design actually changes. Avoid routine date/version/status churn in these high-contention files; use release/status documents for volatile release details instead.
5. For competing local and remote agents, establish single-writer ownership for the overlapping file or coordinate with a PR. Git merge configuration cannot infer which side contains the correct product contract.
6. Never use blanket `.gitattributes merge=ours`, `merge=union`, `git reset --hard`, `git clean -fd`, `skip-worktree`, or `.gitignore` on an already-tracked canonical document as a workaround; these can lose or conceal changes.

Optional safety default for new merges:

```bash
git config --global pull.ff only
```

This stops accidental pull-time merge commits; it does **not** magically reconcile dirty worktrees.

## Batch-update only clean `main` repositories (macOS Bash)

The following intentionally **skips** modified or non-main repositories, and never stashes, resets, discards, switches branches, commits, or pushes:

```bash
for git_dir in "$HOME"/AndroidStudioProjects/*/.git; do
  [ -d "$git_dir" ] || continue
  repo="${git_dir%/.git}"
  (
    cd "$repo" || exit 1
    branch=$(git branch --show-current)
    if [ "$branch" != "main" ] || [ -n "$(git status --porcelain)" ]; then
      printf 'SKIP (branch=%s or dirty): %s\n' "$branch" "$repo"
      exit 0
    fi
    if ! git remote get-url origin >/dev/null 2>&1; then
      printf 'SKIP (no origin): %s\n' "$repo"
      exit 0
    fi
    printf 'SYNC: %s\n' "$repo"
    git fetch origin && git merge --ff-only origin/main ||
      printf 'REVIEW required (diverged or fetch failure): %s\n' "$repo"
  )
done
```

Run it in Terminal, not while Android Studio has an active merge/rebase or an editor writing tracked files. A repository skipped for local changes is a successful safety outcome, not a sync failure. This command does not address nested repositories, custom default branches, or in-progress operations.

## Verification

In each updated repository:

```bash
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
```

For clean main repositories, both SHAs should match after a successful fast-forward. Do not interpret a clean Git state as Android build, test, or production-release qualification.
