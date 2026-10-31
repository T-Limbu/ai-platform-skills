---
name: project-docs
description: Use when creating, updating or checking a repo's docs/ folder (INDEX, architecture, runbook, integrations, findings, decisions, PROGRESS), when a ticket needs a fact written down to link it, or at the end of a session that changed or learned something. Holds the docs convention, one template per doc type and a checker script.
version: 0.1.1
---

# Project Docs

Each repo keeps the knowledge that code and git can't show in `docs/`, with `docs/INDEX.md` as the entry point. Tickets and sessions link to these docs instead of re-deriving or copying them. This skill is the single source for that convention; `conventions/AGENTS.md` and `ticket-writing` point here.

## When to use

- A repo has no `docs/` yet, or its docs are stale, scattered or missing an INDEX.
- A finding, decision or integration fact needs writing down, often so a ticket can link it.
- The end of a session that changed or learned something (when it runs: `token-efficiency`, section 1).

Do not use for: code comments or API reference generated from code, or the hub's cross-project `knowledge/` (that has its own layout).

## Requirements

- The repo checked out, with git history.
- Python 3.9+ for `scripts/check_docs.py` (standard library only).

## Workflow: create `docs/` for a repo

1. **Read the code first.** Entry points, build and test commands, config and env var names, external services. Run the commands you will document.
2. **Write only what code and git can't show** (see Store / don't store). Start with these, each from its template:

| Doc | Template | Holds |
| -- | -- | -- |
| `docs/INDEX.md` | [references/templates/index.md](references/templates/index.md) | One line per doc: path, what, when to read, last verified |
| `docs/architecture.md` | [references/templates/architecture.md](references/templates/architecture.md) | Components, data flow, invariants, where things live |
| `docs/runbook.md` | [references/templates/runbook.md](references/templates/runbook.md) | Setup, run, test, deploy and recover, with expected results |
| `docs/integrations.md` | [references/templates/integrations.md](references/templates/integrations.md) | Contracts with other repos and services, and who owns each |
| `docs/findings/<date>-<topic>.md` | [references/templates/finding.md](references/templates/finding.md) | One verified finding: symptom, cause with `file:line`, impact |
| `docs/decisions/<date>-<topic>.md` | [references/templates/decision.md](references/templates/decision.md) | One decision: context, options, choice, consequences |
| `docs/PROGRESS.md` | [references/templates/progress.md](references/templates/progress.md) | Session log, newest first |

3. **Stamp each doc** with the commit you verified it against, and add its INDEX line.
4. **Link `docs/INDEX.md` from the repo's `AGENTS.md`.** Never auto-include docs into agent context; readers open what the INDEX says they need.
5. **Check** with `python <skills>/project-docs/scripts/check_docs.py <repo>` and fix every error.
6. Once the check exits 0, commit the docs in their own pull request (or with the code they describe), under a ticket or the owner's confirmation.

## Workflow: end-of-session wrap-up

Run it before a handoff or archive, and at the end of any session that changed or learned something (`token-efficiency` sets when). Skip it only when the session changed and learned nothing.

1. Add a dated entry at the top of `docs/PROGRESS.md`: goal, done (commits, tickets), decisions, open items, next step. At most 10 lines.
2. Rotate: keep the latest 10 entries. When adding the 11th, move the oldest to `docs/progress/<year>.md` (newest first) and list that file in `docs/INDEX.md`.
3. Move new facts into the topic doc they belong to (a finding or decision gets its own file). Refresh that doc's stamp and its INDEX line.
4. Run `check_docs.py`. Write the handoff note so it points to the PROGRESS entry instead of repeating it.

## Rules

- **Store / don't store.** Store: why things are the way they are, contracts, invariants, gotchas, verified findings, decisions, the commands that work. Don't store: what the code or `git log` already shows, transcripts, secrets or token values, machine paths, or guesses (mark "likely" with how to confirm).
- **Verified stamp.** Every topic doc carries `Verified against \`<sha>\`, <date>` near the top. Re-verify before trusting a doc whose named files changed a lot since that commit.
- **Owning repo.** A fact shared by repos lives in the repo that owns it (the provider of an API or contract); other repos link to it. Cross-project knowledge goes in the hub's `knowledge/`.
- **Commit only on a passing check.** Commit docs changes only when `check_docs.py` exits 0. Gate on the exit code, not on piped output: `cmd | tail && git commit` takes `tail`'s exit code and commits even when the check fails. Example: `python check_docs.py . && git commit …`.
- **Same pull request.** Update docs in the same pull request as the code they describe.
- **Bounded reading.** Tickets list their Context docs as `repo:path` with the verified commit, attached as GitHub links. Readers follow links one level at most.
- **Rotation.** `docs/PROGRESS.md` holds at most 10 entries of at most 10 lines; older entries live in `docs/progress/<year>.md`.
- **Short and current beats complete.** Delete a doc that is wrong and can't be fixed now, and say so in PROGRESS.

## Checker

[scripts/check_docs.py](scripts/check_docs.py) takes a repo root and checks: every doc is in the INDEX, relative links resolve, each topic doc has a stamp whose sha exists (warns when the named files moved more than 50 commits since), and PROGRESS stays within its limits. It prints errors and warnings separately, exits 1 on errors, and supports `--format github` for CI.

## Read next

| File | Read it when |
| -- | -- |
| [references/templates/index.md](references/templates/index.md) | Writing or fixing an INDEX |
| [references/templates/progress.md](references/templates/progress.md) | Writing the end-of-session entry |
| `ticket-writing` skill | Linking docs from a ticket |
| `token-efficiency` skill | Deciding when the wrap-up runs |

## Changelog

- 0.1.1 (2026-10-29): rule: commit docs only when `check_docs.py` exits 0, gated on the exit code rather than piped output.
- 0.1.0 (2026-10-29): first version. Docs convention moved here from `conventions/AGENTS.md` and `ticket-writing`; templates per doc type; end-of-session wrap-up with PROGRESS rotation; `check_docs.py`.
