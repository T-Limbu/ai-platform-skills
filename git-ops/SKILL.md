---
name: git-ops
description: Use when committing, branching, merging, rebasing, syncing branches such as main and gh-pages, recovering lost commits or stashes, or running GitHub CLI tasks (pull requests, Actions, secrets). Holds field-tested git and gh procedures and the safety rules for pushes and force-pushes.
version: 0.2.2
---

# Git-Ops & Version Control Skill

This skill provides standardized procedures, command sequences, and field-tested rules for version control management across local repositories and remote GitHub hosts.

---

## 🛠️ Tool Group: Git & GitHub CLI

| Tool | Primary Purpose | Common Invocations |
| :--- | :--- | :--- |
| **`git`** | Local VCS tracking, branch management, staging, diffing | `git status`, `git add`, `git commit`, `git merge`, `git log` |
| **`gh`** (GitHub CLI) | Pull requests, repo creation, secret management, Actions inspection | `gh pr create`, `gh repo view`, `gh run list`, `gh secret set` |
| **`git diff`** | Verifying staged and unstaged working tree changes | `git diff --staged`, `git diff HEAD~1` |
| **`git reflog`** | Time-machine recovery for lost commits, detached HEADs | `git reflog`, `git reset --hard HEAD@{n}` |

---

## 📋 Standard Multi-Branch Workflows

### 1. Dual-Branch Sync (`main` & `gh-pages`)
When maintaining a project where `main` contains source code and `gh-pages` serves live web content:

```powershell
# 1. Commit changes on working branch
git add .
git commit -m "feat(scope): concise description"

# 2. Push to current branch
git push origin gh-pages

# 3. Synchronize with main cleanly
git checkout main
git merge gh-pages --ff-only  # fast-forward if linear
# If fast-forward is not possible:
# git merge gh-pages -m "merge: sync gh-pages into main"
git push origin main

# 4. Return to active branch
git checkout gh-pages
```

### 2. Feature Branch Lifecycle
```powershell
# Create & switch to feature branch
git checkout -b feature/short-name

# Work, test, commit atomically
git commit -m "feat: implement specific capability"

# Rebase on latest main before merging
git fetch origin
git rebase origin/main

# Merge into main and clean up
git checkout main
git merge --no-ff feature/short-name -m "merge: feature/short-name"
git branch -d feature/short-name
```

---

## 🛡️ Emergency Recovery & Safety Playbook

| Scenario | Safe Recovery Command |
| :--- | :--- |
| **Undo last commit (keep changes staged)** | `git reset --soft HEAD~1` |
| **Undo last commit (keep changes unstaged)** | `git reset HEAD~1` |
| **Discard all uncommitted local modifications** | `git restore .` (or `git reset --hard HEAD`) |
| **Recover accidentally deleted branch or commit** | 1. Find hash in `git reflog`<br>2. Run `git checkout -b recovered-branch <commit-hash>` |
| **Stash work in progress with description** | `git stash save "WIP: description of work"` |
| **List and restore stashes** | `git stash list` $\rightarrow$ `git stash pop stash@{0}` |

---

## 📚 Rules from Learning (Field-Hardened Guidelines)

These rules were learned from real production debugging and must always be followed:

1. **Rule [Pre-Commit Check]**: Always run `git status` before `git add .` to avoid accidentally staging untracked temporary files, binary dumps, or sensitive API keys.
2. **Rule [Windows CRLF/LF Hygiene]**: On Windows workstations, git may report CRLF replacement warnings. Ensure repository contains `.gitattributes` or set `git config core.autocrlf true` (or `false` for raw Unix files) so diffs remain clean across OS boundaries.
3. **Rule [Branch Verification]**: Never execute `git push` without verifying the active branch (`git branch --show-current`). Always explicitly specify the remote and branch target (e.g. `git push origin main`), never bare `git push`.
4. **Rule [Never Force Push on Shared Branches]**: Avoid `git push --force` on `main`, `master`, or `gh-pages`. Use `--force-with-lease` only when resolving rebases on personal feature branches.
5. **Rule [Self-Documenting Learnings]**: Whenever a tricky git collision, detached HEAD, or remote divergence is resolved in a session, append the root cause and solution to this "Rules from Learning" section.
6. **Rule [One Topic per Branch]**: When a request changes topic mid-branch (for example a policy change arriving on a docs-skill branch), start a new branch from `main` for it, so each pull request reviews one thing.
7. **Rule [One Commit per Command]**: Make each commit in its own shell call and check it with `git show --stat HEAD` before the next. Chaining several `git apply` / `git commit` steps with `&&` and heredocs in one call once produced one mixed commit instead of three. Recovery: `git reset <base>` keeps the working tree; then redo the commits one by one.
8. **Rule [Split Overlapping Work with the Index]**: When later work touches the same files as earlier uncommitted work, stage the earlier part, keep the later part in the working tree, and save one patch per part. Check the patches apply in order on a scratch index (`GIT_INDEX_FILE=<tmp> git read-tree HEAD`, then `git apply --cached`) before relying on them.
9. **Rule [One Worktree per Session]**: Each ticket session works in its own git worktree (`git worktree add ../<repo>-<ticket> -b <branch> main`, or the app's worktree option), never in a checkout another session is using. A ticket session once switched branches in a shared checkout and left uncommitted edits under a running session.
10. **Rule [Check for Junctions Before Deleting]**: On Windows, check `(Get-Item <dir>).LinkType` before deleting a folder. Skill folders in app repos can be junctions to the hub, and deleting one recursively deletes the hub's files. Remove a junction with `cmd /c rmdir <dir>`, which removes only the link.
11. **Rule [PowerShell 5.1 and gh Bodies]**: Write PR and issue bodies to a file and pass `--body-file <file>`. Windows PowerShell 5.1 splits a quoted multi-line `--body` string into several arguments.

## Changelog

- 0.2.2 (2026-10-31): rules 10-11 (check for junctions before deleting; `--body-file` in PowerShell 5.1), from the repo-wide review retro.
- 0.2.1 (2026-10-29): rule 9, one worktree per session, from the Shuttle Feed retro.
- 0.2.0 (2026-10-29): rules 6-8 from the hub session retro (one topic per branch, one commit per command, splitting overlapping work with the index).
