---
name: ticket-writing
description: Use when turning a review, bug report, plan or owner request into Linear tickets that another model or subagent will pick up in a fresh session, or when splitting or refining such tickets. Each ticket is a self-contained brief (context, objective, how to build, test and run end to end, quality bar, stop points, report-back format), so a reader with none of the original conversation can deliver durable work.
version: 0.3.3
---

# Ticket Writing

A ticket here is a **brief for a model that starts cold**: a subagent or a new session that has the repo and the Linear connector, but none of the conversation that produced the ticket. If the brief leaves something out, that model will guess. Write so it doesn't have to.

This is the Product Manager and Architect step of `data-squad`, written down so it can be handed off.

## When to use

- The owner asks for tickets, a backlog or a hand-off from a review, plan, bug report or list of findings.
- Work is about to be delegated to another session or subagent.
- A ticket is too big, vague or overlapping, and needs splitting or rewriting.

Do not use for: one-line fixes the owner wants done now (just do them), or tracking steps inside the current session.

## Requirements

- The Linear connector, with access to team `KSH` (team ID in `conventions/AGENTS.md`, section 4).
- Read access to the code, plus the repo's commands for running the app and its tests.

## Workflow

1. **Verify.** Read the `docs/INDEX.md` of every repo the work touches, and the docs it points to that are relevant. Re-read the code behind every finding and cite `file:line` (`~` for approximate). Write any new finding into the owning repo's `docs/` with the finding template from `project-docs` (with the owner's yes, as it's a repo change) so the ticket can link it. Run the commands the brief will tell the reader to run, so they're known to work. Anything unconfirmed is written as "likely", with how to confirm it.
2. **Check for existing tickets.**
   - Search the team by key words and file names, and list the project's open tickets. Read any that overlap.
   - A finding that's already covered becomes a link, not a new ticket.
   - Look for **gaps between tickets**: a planned change in one repo that silently breaks another app. That gap is a ticket of its own.
3. **Slice.** Follow the slicing rules below. Draft the titles and priorities first; for more than about 8 tickets, show the list to the owner before writing the bodies.
4. **Pilot, then write the rest.** For a batch, write one brief first (the most complex) and take it through the cold-read test in step 6 until the verdict is yes. Apply what it taught to the other briefs before writing them. First drafts usually fail: both pilot briefs (KSH-286, KSH-289) failed their first cold read on real defects.
5. **Write each brief** with [references/ticket-template.md](references/ticket-template.md). Fill the quality bar from [references/quality-bar.md](references/quality-bar.md): keep only the items that apply, and make each one specific to this ticket.
6. **Cold-read test.** Before creating, give a draft to a fresh-context reviewer (a subagent with no conversation history) and ask: "What would you need to ask before starting? What would you guess?" Fix the brief until the answer is "nothing", and repeat until the verdict is yes.
7. **Create and link.** Set the fields per the conventions below. Create blocking tickets first, so later tickets can name them.
8. **Report back** with a table of ticket links, project and priority, plus any overlap with existing tickets.
9. **Learn from each worked ticket.** Read the reader's "Brief gaps" in its report-back: what it had to ask or guess. A gap that recurs across tickets becomes a change to the template or quality bar (with the owner's yes, as it's a skill change).

## Slicing rules

- **One ticket = one repo = one branch = one pull request.** Cross-repo work becomes linked tickets, one per repo.
- **Sized for one session.** A model should be able to read the context, build, test and run it end to end within one session's budget. If the brief needs more than about 10 required changes, split it.
- **Decisions are separate.** If the work can't start until the owner chooses, write an `[Owner decision]` ticket (labels `Spike`, `Role: Architect`) and block the build ticket on it. A model must never have to make a product or security decision mid-build.
- **Owner-only actions** (secrets, prod sign-off, account changes) get an `[Owner]` ticket.
- **Group small items by theme and file**; keep security and data-loss items on their own.

## Field conventions

| Field | Rule |
| -- | -- |
| Team | `KSH` |
| Project | The project of the repo that changes. |
| Title | `<App>: <problem or outcome>`, specific and in plain words, under about 100 characters. Renaming a ticket changes its Linear git branch name, so after any title change, update the branch name inside the brief. |
| Labels | One role (`Role: Engineer` or `Role: Architect`) plus one type (`Bug`, `Feature`, `Improvement`, `Spike`). |
| Priority | **Urgent**: security exposure, data loss or a hardware safety problem, live now. **High**: wrong behaviour users hit, or a blocker. **Medium**: quality, performance, maintainability. **Low**: housekeeping. |
| Relations | `blockedBy` for hard order (including the repo's regression-baseline ticket, if any); `relatedTo` for overlap. Duplicates only with the owner's yes. |
| Status | `Backlog`. |

## Rules

- **Self-contained.** Restate every fact the reader needs. A linked ticket gets a one-line summary of what matters from it, not just its id. Never write "as discussed", "see above" or "the usual way".
- **Project docs, linked not copied.** A ticket lists the docs it depends on under Context docs, as `repo:path` plus the verified commit, attached as GitHub links so a session without that repo can read them. Where docs live and who owns a fact: `project-docs`.
- **Bounded reading.** The reader opens the listed docs and follows their links **one level** at most, never crawling other repos' `docs/`. If something is missing, it stops and comments on the ticket.
- **Provenance.** Every brief starts with "Written against: `repo@commit`, date". The reader runs `git log <commit>..HEAD -- <scoped files>` first and re-verifies any `file:line` that moved before trusting it.
- **Short form for small changes.** One or two files with no cross-repo or data impact: Objective, Context (with `file:line`), Change, Tests, Acceptance, Stop/Report. Anything bigger, or touching stored data, auth, secrets or deploy order, uses the full form (template Variants).
- **Test data has a source.** The brief says where test accounts, fixture tokens and seed data come from: the project's seed or fixture files, never real credentials. If none exist, creating them is part of the ticket.
- **Objective before steps.** State the outcome and why it matters, so the reader can make sound small choices the brief didn't foresee.
- **Exact commands.** Give the real commands to set up, run the app, run the tests and check end to end, and the expected result of each.
- **Every brief has** Must not break, Tests to write, an end-to-end check, Given-When-Then acceptance criteria, stop points and a report-back format.
- **Stop points are explicit.** An owner-created or owner-approved ticket is the approval for its Scope: the reader commits on the ticket's branch, pushes, lands it on `main` once the full test suite and CI are green, lets `qa` deploy and runs the post-deploy checks. It never deploys to prod, which always needs the owner's explicit approval. It stops and comments on the ticket when anything in the brief turns out wrong or work outside Scope is needed.
- **Status flow.** The reader moves the ticket to In Progress on starting (and posts the Baseline comment), to In Review when the pull request opens, and to Done after landing on `main` and passing the `qa` checks, with the report-back as the completion comment.
- **Prod approval request.** After `qa`, if prod is wanted, the reader posts a comment titled "Prod approval needed" (what's on `qa`, the evidence, the risk, the rollback) and stops.
- Creating tickets publishes them, so create them only when the owner asks. Editing or commenting on other existing tickets needs the owner's yes each time; the reader updates its own ticket as the status flow says.
- Name files, functions and env var names; never machine paths, token values or secrets.
- No local ticket files. On Done, post a completion comment saying what shipped and what was verified.

## Read next

| File | Read it when |
| -- | -- |
| [references/ticket-template.md](references/ticket-template.md) | Writing a ticket body |
| [references/quality-bar.md](references/quality-bar.md) | Filling the quality bar section |
| `data-squad` skill | The tickets feed a squad delivery |
| `git-ops` skill | Starting work on a ticket |
| `project-docs` skill | Writing or linking a repo's docs |

## Changelog

- 0.3.3 (2026-10-29): Title convention: renaming a ticket changes its Linear branch name, so update the branch name in the brief after any title change.
- 0.3.2 (2026-10-29): new workflow step: pilot one brief through the cold-read test until it passes, then apply its lessons to the rest of the batch. From the Shuttle Feed retro: both pilot drafts (KSH-286, KSH-289) failed their first cold read.
- 0.3.1 (2026-10-29): the docs convention detail moved to the `project-docs` skill; this skill now points to it.
- 0.3.0 (2026-10-29): short form for small tickets; "Written against" provenance with a `git log` re-check; Linear status flow; "Prod approval needed" comment; test data source; feedback loop from the reader's brief gaps. Pilot feedback (KSH-286): CI and `qa` deploy checks, inputs touched, shared-code load order, storage re-validation, catching unblocked hosts in tests, repeated cold reads.
- 0.2.0 (2026-10-29): approval policy. The ticket approves its Scope through landing on `main` after green CI and the `qa` deploy and its checks; the reader stops before prod, which always needs the owner's explicit approval.
- 0.1.0 (2026-10-29): first version. Tickets are briefs for a cold-start model; adds the quality bar and the cold-read test. Distilled from the Oplox security backlog (KSH-246 to KSH-257) and the Shuttle Feed review (KSH-285 to KSH-295).
