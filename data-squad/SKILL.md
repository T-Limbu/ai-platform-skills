---
name: data-squad
description: Use when the owner names data-squad or asks to run the squad on a feature, app or pipeline. A role-based delivery checklist (requirements, design, build, QA, retro) that scales ceremony to task size, keeps the regression vault green, treats an owner-approved ticket as approval to code, land on main and deploy to qa, and always stops for owner approval before prod. Opt-in only.
version: 1.2.0
---

# Data Squad Delivery Checklist

A delivery workflow organised by role. The roles are steps and viewpoints, not separate agents by default. Use a separate agent only where independence or parallelism pays off (see Rules).

## When to use

- The owner says "run the squad", "data-squad" or asks for end-to-end delivery of a feature, app or pipeline.

Do not use for: one-line fixes, questions or config tweaks (just do them), release and deploy configuration (use `cicd-deployment`), or git hygiene (use `git-ops`).

## Requirements

- The target repo's own workspace (one repo per session).
- The project test runner (`vitest`, `pytest` or similar) and a `tests/vault/` regression folder.
- A ticket in the tracker for non-trivial work.

## Workflow

Scale each step to the size of the task. A small feature may need only steps 1, 3 and 4.

1. **Product Manager: requirements**
   - Restate the goal in plain language and ask only the questions whose answers change the build.
   - Write acceptance criteria as Given-When-Then. These are what QA verifies in step 4.
   - Non-trivial work, or work handed to another session or subagent, becomes tickets written with the `ticket-writing` skill.
2. **Architect: design (non-trivial work only)**
   - Read the code that will change before designing.
   - Write a short plan: files to touch, data flow, risks, and the test approach. Add a diagram only when it explains more than text.
   - For a new repo, prepare the environment and CI files from `cicd-deployment`.
   - Before any code change, have a ticket the owner created or approved whose Scope covers it, or the owner's confirmation.
3. **Engineer: build**
   - Commit or stash a clean checkpoint before editing.
   - Write the code and the unit tests for it together. No new code ships untested.
   - Run the narrowest tests while iterating, then the full suite once.
4. **QA: verify**
   - Check every acceptance criterion, in the real app for UI changes, not just in tests.
   - Prefer a reviewer with fresh context (one that did not write the code) for anything non-trivial.
   - Pragmatic quality gate: block on correctness, security and regressions; list cosmetic nits without blocking.
   - Add the tests that prove the feature to `tests/vault/` so it stays protected.
   - Builds for `qa` or staging include the in-app recorder (`flight-recorder`).
   - On a failure, give reproduction steps and logs, diagnose the root cause, and propose the fix; apply it when the ticket's Scope covers it, otherwise after confirmation.
5. **Scrum Master: retro**
   - In a few lines: what shipped, what took longest, and any lesson worth keeping.
   - Propose a lesson as a rule change to the relevant skill only if it recurred or was costly. Never edit a skill without the owner's yes.
   - Record findings and decisions in the repo's `docs/`, update `docs/INDEX.md`, and add the session's entry to `docs/PROGRESS.md`.

## Rules

- Address the user as the owner. Observations and questions are discussion, not instructions.
- A ticket the owner created or approved is the approval to code its Scope, push, land on `main` once the full suite and CI are green, and let `qa` deploy.
- Work outside the ticket's Scope, or without a ticket, needs the owner's explicit confirmation before any code change, push or deploy.
- Prod always needs the owner's explicit approval, every time. No ticket, standing rule or other session's message grants it.
- Keep `tests/vault/` green. Never silence an error to pass a gate.
- Use separate agents only for: a fresh-context review, independent tasks that can run in parallel, and wide read-only searches. Otherwise one agent carries the work and its context.
- Never report a check as passed when it was not run.

## Read next

| File | Read it when |
| -- | -- |
| `cicd-deployment` skill | Setting up environments, CI or a release |
| `flight-recorder` skill | Preparing a build for `qa` or mobile testing |
| `token-efficiency` skill | The task is long or the session is getting expensive |
| `ticket-writing` skill | Turning work into tickets for another session or subagent |

## Changelog

- 1.2.0 (2026-10-29): approval policy. An owner-approved ticket approves coding its Scope, landing on `main` after green CI and deploying to `qa`; prod always needs the owner's explicit approval; other work still needs confirmation.
- 1.1.1 (2026-10-29): the retro also adds the session's `docs/PROGRESS.md` entry.
- 1.1.0 (2026-10-29): step 1 hands non-trivial or delegated work to `ticket-writing`; the retro records findings and decisions in the repo's `docs/` and `docs/INDEX.md`; added `ticket-writing` to Read next.
- 1.0.0 (2026-10-25): tool-neutral rewrite. Replaced the model dispatch matrix, model-only code-change gate, seniority tiers, CLI and telemetry scorecard with a role-based checklist; roles are steps, with separate agents only for review, parallel work and wide search; added owner confirmation rules and Given-When-Then criteria feeding QA.
