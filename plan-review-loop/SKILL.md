---
name: plan-review-loop
description: Use when a non-trivial plan (CI/CD or release process, test strategy, migration, architecture, security or multi-repo change) needs its gaps found before it becomes tickets or code, or when the owner asks to review a plan again, find issues or list gaps. Runs repeated review passes, each against a new kind of evidence (repo, platform docs, live config, dependencies, failure paths), keeps an assumptions ledger, and stops on a defined rule.
version: 0.1.0
---

# Plan Review Loop

A plan is a set of claims about the world: "CI runs these tests", "this check blocks the merge", "qa deploys from `main`". Most plans fail because one of those claims is false, not because the steps are badly written. This skill tests the claims in passes. **Each pass checks a new kind of evidence.** Re-reading the plan is not a pass.

This is the Architect step of `data-squad` made repeatable for plans that carry risk. When the plan is settled, the `ticket-writing` skill turns it into tickets.

## When to use

- Before a plan with more than a few steps, or any prod, data, auth or deploy impact, becomes tickets or code.
- When the owner asks to "review the plan again", "find the gaps", "where are the issues" or "do a final pass".

Do not use for: one-file changes (just plan and do them), reviewing a code diff (use a code review), or polishing ticket wording (`ticket-writing`).

## Requirements

- Read access to the code, CI and deploy config, and the repo's docs.
- Read-only access to the live services the plan depends on (hosting API or dashboard, Git host API, issue tracker). Reviewing never changes a live service; any change needs the owner's yes.
- A way to run one review with fresh context: a subagent or new session with no conversation history.

## Workflow

1. **Frame.** Write down the goal, the owner's constraints (for example "PR checks under 5 minutes", "prod always needs my approval") and the non-goals. Ask only the questions whose answers change the plan.
2. **Audit what exists before proposing.** List what is already there and where it runs: tests per suite, which run in CI, which never run, what checks a deploy. The gaps usually show up here, not in new ideas.
3. **Draft v1** of the plan, in phases, smallest safe step first.
4. **Start the assumptions ledger** ([references/assumption-ledger.md](references/assumption-ledger.md)). List every claim the plan depends on, each marked `verified`, `false` or `unverified`, with its source and date.
5. **Run review passes.** Each pass opens a new kind of evidence ([references/review-lenses.md](references/review-lenses.md)). The default order:
   1. **Repo:** code, config, workflows. Does the plan match what is actually in the repo?
   2. **Platform:** plan or tier limits, hosting behaviour, from current docs, not memory.
   3. **Live config:** read the live services' settings and compare them with the repo's config files. A config file in the repo is a claim about production, not proof of it.
   4. **Flow:** order and dependencies between steps, other repos and apps affected, shared resources (data, accounts, quotas).
   5. **Failure and bypass:** what happens if a step fails, races, is skipped, is overridden, or someone takes a manual path around the gate.
   6. **Final, critical and high only,** by a fresh-context reviewer where possible.

   Change the order when the plan calls for it. The one fixed rule is that every pass opens a source no earlier pass used.
6. **After each pass,** update the plan, the ledger and the pass log. Show the owner what changed (findings by severity, then the plan changes), not the whole plan again unless asked.
7. **Stop** when a pass opens a new source and produces no critical or high finding and no structural change, or after the final pass. Say plainly that returns are diminishing, and recommend starting the first phase. Don't go past about 5 passes unless the owner asks.
8. **Hand off.** The final plan has:
   - a Ground truth section (verified facts and their sources)
   - the phases
   - the open decisions
   - **findings outside the plan**: risks the plan doesn't fix, tracked rather than dropped

   When the owner asks for tickets, use `ticket-writing`. Findings worth keeping go into the repo's `docs/findings/` (`project-docs` skill, with the owner's yes).

## Severity

| Level | Meaning |
| -- | -- |
| Critical | Following the plan would cause data loss, a security exposure or a prod outage, or its main safety mechanism doesn't work at all. |
| High | A step silently does nothing, a gate can be bypassed, or a false assumption changes the plan's structure. |
| Medium | A missing detail that would surface during the build anyway. |
| Nit | Wording or style. |

## Rules

- **Verify, don't recall.** Every platform fact gets a source (doc URL, API output, `file:line`) and a date. A fact that can't be checked yet is written "to confirm", with how to confirm it.
- **Live config beats config files.** Read the real settings from the service. Repo files and dashboards drift apart, and the drift is where the worst findings hide.
- **Design around controls that actually stop things.** Check which gates can really block (plan-tier limits, manual deploy buttons, override paths) before relying on one. Put the hard stop where it can't be bypassed.
- **At least one pass with fresh context** for any plan with more than about 5 steps, or with prod or data impact. The author shares the plan's blind spots.
- **Track findings outside the plan.** A risk the plan doesn't fix is listed and tracked, not dropped.
- **Report honestly.** Say when a pass found nothing. Never mark an assumption verified without its source.
- **Read-only.** Reviewing never edits code, settings or tickets. Record the owner's decisions and don't reopen them.

## Read next

| File | Read it when |
| -- | -- |
| [references/review-lenses.md](references/review-lenses.md) | Choosing what each pass checks, and which sources to read |
| [references/assumption-ledger.md](references/assumption-ledger.md) | Starting the ledger, the pass log or the final plan |
| [references/worked-example.md](references/worked-example.md) | Seeing what each pass found in a real CI and deploy safety plan |
| `ticket-writing` skill | Turning the final plan into tickets |
| `data-squad` skill | The plan belongs to a squad delivery |
| `cicd-deployment` skill | The plan touches CI, releases or deploys |
| `project-docs` skill | Recording findings and decisions in a repo's `docs/` |

## Changelog

- 0.1.0 (2026-11-22): first version. Distilled from the Off-Grid Audio regression-safety plan (epic KSH-354): five passes, each against a new kind of evidence, found that merges couldn't be blocked, that Render builds the app itself, that qa and prod share one Firebase project, and, from the live config only, that the qa service tracked a stale branch and that the Render dashboard skipped every gate.
