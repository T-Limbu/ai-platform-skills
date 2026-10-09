---
name: git-ops
description: Comprehensive Git operations, multi-branch synchronization, GitHub automation, repository health, and version control workflows. Includes field-tested procedures and hardened rules from learnings.
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
