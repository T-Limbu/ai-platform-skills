# Worked example: Off-Grid Audio regression safety (2026-11-22)

The owner asked how to stop new changes breaking existing features, without running every test on every deploy. The plan went through four review passes and a final critical-only pass before becoming Linear tickets (epic KSH-354, tickets KSH-355 to KSH-364).

## Starting point

- Frontend unit tests in CI, about 113.
- A Playwright e2e suite, a backend suite, a Firestore/Storage rules suite and a `tests/vault/` regression folder.
- Static sites on Render for qa and prod. A deploy workflow dispatched by hand.

v1 of the plan: affected-only tests on PRs, a test pyramid, run e2e in CI, a qa smoke test, gate prod on it.

## What each pass found

| Pass | Evidence opened | Findings | Severity | Plan change |
|---|---|---|---|---|
| Audit | Workflows, scripts, test folders | Tests ran 4 times per change; e2e, backend, rules and vault suites never ran in CI; e2e couldn't start (Playwright waited on port 5173, Vite served 8080); nothing checked qa after a deploy | High | Phase 0: make CI honest before adding anything |
| 1 Platform | Git host API, Render `render.yaml`, reusable workflow | Branch protection returned 403 on the free private plan, so **merges can't be blocked**; Render builds the app itself, so CI's artifact never ships; Layout Check failed because Playwright doesn't support the new runner OS | Critical, high | The deploy workflow becomes the only hard stop; the qa smoke test and prod gate move up to Phase 1 |
| 2 Platform docs and code | Render docs (fetched), `firebase.ts`, `backendUrl.ts`, Node pins | No Node pin anywhere; **qa and prod share one Firebase project**; the backend is local-only, so downloads can't be smoke-tested on qa | High | The smoke test stays signed out; Node pinned; separate Firebase project tracked as an owner decision |
| 3 Flow and failure | The plan's own gates, workflow files | Firestore rules untested; Phase 1 blocked by the runner bug; no `concurrency:` (overlapping deploys could record a result against the wrong commit); no emergency override; no `data-testid`s | High, medium | Rules tests added; dependencies made explicit; concurrency, override and test ids added |
| Final, critical only | **Live Render settings via API** | qa service tracked `dev`, 49 commits behind `main`, and wasn't in the Blueprint, so `render.yaml` edits did nothing; the **Render dashboard's Manual Deploy skips every gate**, so tests must stay in Render's build | High, high | Fix the live settings first; keep tests in the build script; rule: deploy only through the workflow |

The stop rule was met at the final pass: no further structural change, and the third pass had already mostly added detail.

## Lessons

- **The worst findings came from live config, not from the repo.** `render.yaml` said `main`; the service said `dev`. Read the service.
- **"Can this gate actually block?" changed the whole design.** Once merges couldn't be blocked, the safety net had to live in the deploy workflow.
- **Each pass found something because it opened a new source.** Passes that only re-read the plan would have found nothing.
- **Findings outside the plan were kept** as tickets (shared Firebase project, phone-only audio checks, the cross-app sign-in path) instead of disappearing.
- **Weakness of this run:** every pass was done by the plan's author. A fresh-context reviewer on the final pass would have been stronger.
