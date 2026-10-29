# Ticket template (brief for a cold-start model)

Copy the body below into the ticket description. Every section is required unless marked optional. Short is fine; missing isn't.

```markdown
**Read first:** [Change Safety Protocol](https://linear.app/kshitij-limbu/document/change-safety-protocol-read-before-starting-any-ticket-8baf630fa1c9). **Blocked by** KSH-NNN (one line: what it delivers that this needs).

## Objective

One or two sentences: the outcome when this is done, and why it matters to users or the owner.

## Context docs

Read these before starting, in order, and nothing else from other repos. Each is `repo:path`, with the commit it was verified at; the same docs are also attached as GitHub links.

* `this-repo:docs/architecture.md` (abc1234): why to read it, in a few words.
* `other-repo:docs/findings/2026-10-29-topic.md` (def5678): what this ticket depends on from it.

## Context

What the reader needs to know and can't get from this ticket's code alone. Summarise what matters from the Context docs; don't just link them.

* **System:** what the app is, its stack, and where this code sits.
  Example: "Static Vue 3 page `index.html`; syncs to the Oplox hub API; talks to the feeder over Web Bluetooth."
* **How it works today:** the relevant flow, step by step, with `file:line` for each step.
* **What's wrong or missing:** each fact with `file:line`. Lead with the consequence, then the mechanism. Mark anything unconfirmed as "likely", with how to confirm it.
* **Related work:** each linked ticket with one line on what it changes that affects this one.
* **Terms:** any name that isn't obvious (app ids, legacy names, hardware terms).

## Scope

* **In:** the files and behaviour this ticket changes.
* **Out (non-goals):** nearby things not to touch, and the ticket that owns each.

## Required changes

1. Numbered, concrete changes: what, not keystrokes.
2. Exact values, limits, defaults, names and formats.
3. What must stay unchanged (ids, routes, response shapes, storage keys).

## Quality bar

Only the items from the quality-bar reference that apply, each made specific.
Example: "Durability: deletes survive a failed request; set the pending-sync flag and retry on `online`."

## Environment and commands

* Setup: `<install command>`
* Run the app: `<command>` → `<url or how to open it>`
* Unit and vault tests: `<command>` → expected baseline (for example "132 passed")
* End to end: `<command or manual steps>`
* External services: how they're mocked or blocked in tests (never hit real ones).

## Build plan

1. **Baseline:** run the tests on a clean branch; record the counts.
2. **Pin current behaviour:** add tests for any Must not break item that has no test yet.
3. **Failing tests first:** write tests that reproduce the bug or prove the new rule, and confirm they fail.
4. **Change:** the smallest change that passes them, matching the surrounding style.
5. **Full suite, then end to end:** run the full suite, then the end-to-end check below.

## Must not break

* Existing behaviour that has to keep working, each item checkable.

## Tests to write

* One bullet per test: setup, action, expected result.
* Location (usually `tests/vault/`), plus any CI file that needs the new test added.

## End-to-end check

The real-app check after the tests pass: what to open, what to do, what to see. Say what evidence to capture (command output, screenshot, flight-recorder log).

## Acceptance criteria

* **Given** a starting state, **when** an action happens, **then** an observable result.

## Stop points

* Commit on the ticket's branch (its Linear branch name). Don't push, merge or deploy until the owner says so.
* Stop and comment on this ticket if:
  * the baseline is red
  * a fact in Context turns out wrong
  * a file outside Scope needs to change
  * a product or security choice comes up that this brief doesn't settle

## Report back

Post as a ticket comment:

* what changed and why, and the files touched
* tests: baseline vs after counts, and the new tests with proof they failed first
* end-to-end evidence
* anything not verified, and follow-ups found (not fixed)
* docs updated: which `docs/` files changed in this pull request, and the new `INDEX.md` lines

## Deployment (optional)

Order or timing constraints, for example "deploy to qa in the same window as KSH-NNN".

## Rollback (optional, for risky or data-touching changes)

Revert the pull request, or the migration rollback steps.
```

## Variants

**`[Owner decision]`** keeps Objective and Context, then replaces the build sections with:

- **Options:** two or three, each with its trade-off. Mark one "(recommended)".
- **Decide:** the exact questions to answer.
- **Unblocks:** the tickets waiting on this decision.

**`[Owner]` action:** the steps the owner performs, and the check that proves each one is done.

**`[Epic]`:** the objective, the ordered child tickets and the definition of done for the set. No implementation detail.

## Checklist before creating

- [ ] Could a model with only the repo and this ticket start without asking a question? (Cold-read test passed.)
- [ ] Every `file:line` was checked against current code, and every command was run.
- [ ] Linked tickets are summarised in a line, not just named.
- [ ] Context docs exist on `main` at the listed commits, and are attached as links.
- [ ] One repo, one pull request, sized for one session.
- [ ] Quality bar items are specific to this ticket, not generic.
- [ ] No secrets, token values or machine paths.
