# Template: docs/runbook.md

Copy below the line. Every command is one you ran, with what it prints when it works. Env vars by name only.

---

# Runbook

Verified against `abc1234`, 2026-10-29.

## Setup

* `<install command>` → expected result
* Env vars (names only): `API_URL`, `APP_ID`. Values come from the secret store.

## Run

* `<run command>` → `<url or how to open it>`

## Test

* Unit and vault: `<command>` → expected baseline (for example "132 passed")
* End to end: `<command or manual steps>`
* Test data: where seed and fixture data live.

## Deploy

* `qa`: how it deploys from `main`, and the post-deploy check.
* `prod`: the release path. Always needs the owner's explicit approval.

## Recover

Known failures, how to spot each (log line or symptom), and the fix or rollback.
