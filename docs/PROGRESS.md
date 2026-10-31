# Progress

## 2026-10-30 to 31 repo-wide review, backlog, PR #2

* **Goal:** review all 16 repos in ai_projects, plan how to scale this hub, turn both into Linear tickets, and record the owner's decisions.
* **Done:** tickets KSH-297 to KSH-340 written with `ticket-writing` (pilot KSH-298 passed a cold read; the rest self-checked). Owner decisions recorded as Linear comments; KSH-299 and KSH-302 Done. Branch pushed as PR T-Limbu/ai-platform-skills#2; commits `a879b37` (token-efficiency 1.3.0) and `b8e2960` (CI: `PYTHONDONTWRITEBYTECODE` so tests don't leave `__pycache__` for lint L11). CI green.
* **Decisions:** KSH-302: ship the hub as a `squad` plugin for local Claude sessions and use claude.ai account skills for cloud sessions (plugins don't load there). KSH-223 shrinks to the non-Claude targets.
* **Open:** owner merges PR #2 and rotates the Linear key (KSH-297); answers on KSH-306, KSH-320, the KSH-311 force-push and KSH-335 (who carries it out). A coordinator session runs the backlog in waves.
* **Next:** after the merge, KSH-304 packages the hub as the plugin.

## 2026-10-29 ticket-writing, approval policy, project-docs

* **Goal:** add the `ticket-writing` skill; then, as the owner asked, the PROGRESS rule, the ticket approval policy and a `project-docs` skill.
* **Done:** branch `feat/ticket-writing-skill`, commits `bf46418`, `2f7fb9e`, `cab6654`, `3c92c68`, `0a5bc9d`, plus this retro. Lint 0 FAIL; 56 tests pass. Not pushed.
* **Decisions:** `decisions/2026-10-29-ticket-approval-policy.md`.
* **Lessons:** `findings/2026-10-29-hub-session-retro.md` (applied to `git-ops` and `data-squad`).
* **Open:** owner answers on the approval-policy questions and on `check_docs` stamp wording ("Reviewed at"); align the workspace `CLAUDE.md`, session-start hook and Linear "Change Safety Protocol" with the policy.
* **Open:** linter crashes on Windows when a skill with emoji changes (workaround `PYTHONUTF8=1`; fix in the retro finding). User-level junctions for `ticket-writing` and `project-docs`; push and pull request (consider splitting `cab6654` into its own pull request).
* **Next:** owner reviews the branch, then `git push origin feat/ticket-writing-skill` and open the pull request.
