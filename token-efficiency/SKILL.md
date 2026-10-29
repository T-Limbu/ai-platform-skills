---
name: token-efficiency
description: Use when a session is burning tokens or context quickly, when a task will run long, or before starting a new task in an existing session. Lists practices that cut usage without lowering code quality, tells the agent when to proactively offer a fresh session, and sets the quality guards that efficiency must never trade away.
version: 1.2.3
---

# Token Efficiency Standard (No Quality Trade-offs)

Every turn re-reads the fixed instructions plus the whole conversation so far. Cost grows with session length, not just with work done. These practices reduce that cost while keeping the same checks, tests and review rigor.

## When to use

- A session feels expensive, slow or is nearing its context limit.
- Starting a new task in a session that already holds an unrelated one.
- Planning a long task that will read many files, pages or logs.

Do not use for: deciding what to build (use the delivery workflow skills) or for release configuration (use `cicd-deployment`).

## Requirements

- Ability to start a fresh session or clear context.
- Optional: a usage report for the session (group usage by tool type and note the largest tool outputs).

## 1. Session hygiene (largest saving)

- One task per session. When the topic changes (review, then feature, then deploy), start a new session.
- Before a handoff or archive, and at the end of any session that changed or learned something, run the end-of-session wrap-up in the `project-docs` skill: a dated `docs/PROGRESS.md` entry of at most 10 lines (rotated at 10 entries), new facts moved into their topic docs and `docs/INDEX.md`. Skip it only when the session changed and learned nothing.
- Write the handoff note so it points to that PROGRESS entry instead of repeating it.
- Start the next session from the handoff note and `docs/PROGRESS.md`, not from the old history.
- A handed-off ticket session works in its own git worktree (or the app's worktree option), never in a checkout another session is using: switching branches there moves files under the running session and leaves edits on the wrong branch.
- Do not keep a failed approach in context: after a dead end, summarise the learning in one line and move on.

## Proactive new-session prompt

The agent, not the user, watches for the point where a fresh session pays off, and offers it once at a natural boundary.

Offer a fresh session when ANY of these is true and the work is at a stopping point:

- The context is roughly half full, or the session has run about 40 turns (use the session's own usage indicator when one exists).
- A task just finished: committed, pushed, deployed or handed to the user.
- The user switches to an unrelated topic.
- A very large tool output (page dump, log, whole file) was just consumed and is no longer needed.

How to offer it:

- Put it at the end of a turn, never mid-edit, mid-test or mid-deploy, and never while a decision is pending.
- First record progress in `docs/PROGRESS.md` (section 1).
- Keep it to a few lines: why now (for example "context is large and this task is done"), a handoff that points to the `docs/PROGRESS.md` entry, and a yes/no choice to start the new session with that handoff.
- Ask at most once per boundary. If the user declines, continue and do not repeat until the next boundary.
- Never start the new session or discard context without the user's yes.

## 2. Trim the fixed overhead

- Enable only the skills a project needs (per-project manifest). Remove unused skills and integrations from the session.
- Keep instruction files short and link to details instead of inlining them.
- Prefer a short skill description that states when to use it; long descriptions are paid for on every turn.

## 3. Read narrowly

- Search first, then read only the matching line range. Do not read whole files to find one function.
- Never re-read a file already in context unless it changed.
- Skip generated, vendored and lock files unless the task is about them.
- For web pages and dashboards, fetch the single fact needed (a status code, one field, a filtered view). Use extracted text over screenshots for checking wording; zoom into a region instead of full-page captures.
- A single large page or log dump stays in context for every later turn, so avoid pulling one in "just in case".

## 4. Keep command output small

- Limit output (head, tail, count-only, filters) and scope searches to the relevant folder. Exclude dependency, build and vendored folders.
- Set timeouts on scans that could walk a large tree.
- Redirect long output to a file and read only the part that matters.

## 5. Fewer round trips

- Batch independent tool calls into one message. Batch browser steps into one call.
- Make several edits to one file in a single pass. Do not re-read a file just to confirm an edit that already reported success.
- Run the narrowest test first while iterating; run the full suites once before declaring done.

## 6. Match effort and process to the task

- Use the lowest reasoning effort that fits mechanical work (renames, config, formatting). Raise it for design, debugging and security-sensitive changes.
- Use a cheaper or faster model tier for read-only work (searching, summarising, listing) and keep the strongest tier for writing and reviewing code.
- Scale ceremony to size: a one-line fix does not need requirements elicitation or a retrospective; a feature does.

## Quality guards (never trade these away)

- Read the code you are about to change before changing it.
- Keep tests, the regression vault and the QA gate; efficiency never skips a verification step or claims a result that was not checked.
- Keep the approval gates: a ticket whose Scope covers the work, or the owner's confirmation, before code changes and pushes; the owner's explicit approval for every prod deploy; confirmation for anything else outward-facing.
- Keep secret scrubbing and safety rules in force.
- If a saving would reduce correctness, do not take it.

## Quick checklist

- [ ] New topic, new session, with a handoff note.
- [ ] Before a handoff or archive, added the `docs/PROGRESS.md` entry and updated topic docs and `docs/INDEX.md`.
- [ ] At a boundary (task done, topic switch, context about half full), offered a fresh session once.
- [ ] Only needed skills and integrations enabled.
- [ ] Reads are ranged; no repeated reads; no whole-page dumps.
- [ ] Commands limited, scoped and timed out.
- [ ] Independent calls batched.
- [ ] Effort and model tier matched to the task.
- [ ] Verification gates unchanged.

## Rules

- Savings come from less repeated context and less unneeded output, never from fewer checks.
- When unsure whether a saving is safe for quality, keep the check.

## Read next

| File | Read it when |
| -- | -- |
| `cicd-deployment` skill | Choosing which tests run at each release gate |
| `flight-recorder` skill | Diagnosing issues from compact logs instead of long transcripts |
| `project-docs` skill | Running the end-of-session wrap-up |

## Changelog

- 1.2.3 (2026-10-29): section 1: a handed-off ticket session works in its own git worktree, never in a checkout another session uses. From the Shuttle Feed retro.
- 1.2.2 (2026-10-29): the wrap-up detail moved to the `project-docs` skill; section 1 now points to it.
- 1.2.1 (2026-10-29): quality guard restated for the approval policy (ticket or confirmation for code and pushes; prod always needs the owner's explicit approval); `docs/PROGRESS.md` keeps the latest 10 entries, older ones move to `docs/progress/<year>.md`.
- 1.2.0 (2026-10-29): before a handoff or archive, record progress in `docs/PROGRESS.md` (dated entry, at most 10 lines), move new facts into topic docs and `docs/INDEX.md`, and point the handoff at that entry; added a checklist line.
- 1.1.0 (2026-10-25): added the proactive new-session prompt (triggers, how to offer, never mid-task).
- 1.0.0 (2026-10-25): initial version, from a measured long session where history re-reads and large page dumps dominated cost.
