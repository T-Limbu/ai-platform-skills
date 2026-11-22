# Assumptions ledger, pass log and final plan

Templates for the three things the loop maintains. Keep them in the conversation, or in a scratch file while working. They go into the repo only as part of the final plan or a `docs/findings/` entry, with the owner's yes.

## Assumptions ledger

One row per claim the plan depends on. Add rows as passes uncover new claims. Never delete a row: mark it `false` and say what replaced it.

| # | Claim | Status | Source and date | Plan impact if false |
| -- | -- | -- | -- | -- |
| A1 | CI failures block the merge | false | Git host branch-protection API: 403, "upgrade plan" (2026-11-22) | Put the hard stop in the deploy workflow instead |
| A2 | qa deploys from `main` | false | Hosting API: qa service branch is `dev` (2026-11-22) | Fix the service setting before relying on qa |
| A3 | Commit SHA is available at build time | verified | Hosting docs, default env vars page, URL (2026-11-22) | none |
| A4 | Seeded songs play while signed out | unverified | To confirm: run the smoke check locally against a seeded guest database | Smoke test needs a test account |

Status is one of `verified` (has a source), `false` (a source contradicts it) or `unverified` (written "to confirm", with how).

## Pass log

One entry per pass, newest last. Shown to the owner after each pass.

```
Pass N: <lens>
Checked: <sources opened for the first time this pass>
Findings:
  - [critical|high|medium|nit] <finding>, source <file:line, URL or API output>
Plan changes: <added, removed or reordered steps>
Ledger: <rows added or changed>
Stop rule: <met or not, and why>
```

## Final plan

```
# Plan: <goal>

Goal and constraints: <one paragraph, owner's constraints quoted>

Ground truth (verified, with sources):
- <fact>, <source>, <date>

Phase 0..N: <steps, each small enough for one pull request; dependencies named>

Open decisions: <question, options, recommendation>

Findings outside the plan (tracked, not fixed here):
- <risk>, <why it matters>, <suggested owner or ticket>

How it runs: <order, approvals needed, what stays manual>
Review history: <passes run, and what each changed, one line each>
```
