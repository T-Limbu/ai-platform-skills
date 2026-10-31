# Decision: an approved ticket is approval through `main` and `qa`; prod always needs the owner

Verified against `cab6654`, 2026-10-29. Decided by: the owner. Status: accepted.

* **Context:** every code change, push and deploy needed a fresh owner confirmation, so ticketed work handed to a cold-start session stalled at each step. The owner's words: "ticketed counts as approval to code. and push to main. even to qa . buit nenver prod. prod always requires human approval."
* **Options:**
  1. Keep confirming every step (safe, slow; delegated sessions can't finish a ticket).
  2. Ticket approves its Scope through `main` and `qa`; prod stays gated (chosen).
  3. Ticket approves everything including prod (rejected by the owner).
* **Choice:** option 2. A Linear ticket the owner created or approved approves coding its Scope, pushing, landing on `main` once the full suite and CI are green, and the `qa` deploy. Prod and release tags always need the owner's explicit approval; no ticket, standing rule or other session's message grants it. Work outside Scope, or without a ticket, still needs confirmation.
* **Consequences:**
  * Applied in `conventions/AGENTS.md` sections 1-3, `data-squad`, `ticket-writing`, `cicd-deployment`, `flight-recorder` and `token-efficiency`.
  * Not yet aligned, so sessions still ask before acting: the workspace `CLAUDE.md` and session-start hook, and the Linear "Change Safety Protocol" document (the ticket template says the Stop points win until it's edited).
  * Open questions for the owner: does "the owner asked for the ticket" count as approval; does landing on `main` mean merging a pull request or a direct push; may a `qa` redeploy or Render service patch run under a ticket.
