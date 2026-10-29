# Template: docs/integrations.md

Copy below the line. One section per external contract. If another repo owns the contract, write one line and link to its doc instead of copying it.

---

# Integrations

Verified against `abc1234`, 2026-10-29.

## <Service or repo name>

* **Owner:** this repo, or `other-repo:docs/integrations.md` (link, don't copy).
* **Contract:** endpoint, message or file format, with the fields that matter and their types.
* **Auth:** the mechanism and env var names; never values.
* **Called from:** `file:line`.
* **Failure behaviour:** timeouts, retries, offline handling.
* **Change rule:** what must stay compatible, and which repos break if it changes.
