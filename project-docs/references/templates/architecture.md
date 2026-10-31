# Template: docs/architecture.md

Copy below the line. Aim for one screen. Name files and functions; leave out what reading the code makes obvious.

---

# Architecture

Verified against `abc1234`, 2026-10-29.

## What it is

One paragraph: what the app or service does, for whom, and its stack.

## Components

| Part | Lives in | Responsibility |
| -- | -- | -- |
| UI | `src/App.vue` | ... |
| Sync | `src/sync.ts` | ... |

## Data flow

The main flows, step by step, with `file:line` for each step. Add a diagram only when it explains more than text.

## Invariants

Rules that must stay true, each checkable. Example: "Storage keys are namespaced per user (`src/store.ts:~40`)."

## Gotchas

Non-obvious behaviour that has bitten someone, with the reason.
