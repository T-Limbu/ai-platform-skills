# Progress

## 2026-10-29 ticket-writing, approval policy, project-docs

* **Goal:** add the `ticket-writing` skill; then, as the owner asked, the PROGRESS rule, the ticket approval policy and a `project-docs` skill.
* **Done:** branch `feat/ticket-writing-skill`, commits `bf46418`, `2f7fb9e`, `cab6654`, `3c92c68`, `0a5bc9d`, plus this retro. Lint 0 FAIL; 56 tests pass. Not pushed.
* **Decisions:** `decisions/2026-10-29-ticket-approval-policy.md`.
* **Lessons:** `findings/2026-10-29-hub-session-retro.md` (applied to `git-ops` and `data-squad`).
* **Open:** owner answers on the approval-policy questions and on `check_docs` stamp wording ("Reviewed at"); align the workspace `CLAUDE.md`, session-start hook and Linear "Change Safety Protocol" with the policy.
* **Open:** linter crashes on Windows when a skill with emoji changes (workaround `PYTHONUTF8=1`; fix in the retro finding). User-level junctions for `ticket-writing` and `project-docs`; push and pull request (consider splitting `cab6654` into its own pull request).
* **Next:** owner reviews the branch, then `git push origin feat/ticket-writing-skill` and open the pull request.
