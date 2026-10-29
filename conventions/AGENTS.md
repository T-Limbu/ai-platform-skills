# Shared conventions (all repos)

Tool-neutral rules for every repository under `ai_projects`. Project-specific facts live in each repo's own `AGENTS.md`. Detail lives in skills and knowledge docs; this file only points to them.

## 1. Approval (governing rule)
- Observations, bug reports and questions are discussion, not instructions. Explain, propose, then wait.
- A Linear ticket the owner created or approved is the approval to code everything in its Scope, push it, and land it on `main` once the full test suite and CI are green. `qa` may then deploy from `main`.
- Work outside a ticket's Scope, and any work without a ticket, needs the owner's explicit confirmation first ("implement", "fix it", "go ahead"). Outside a ticket, run `git push` only when the owner asks.
- Prod always needs the owner's explicit approval, every time. No ticket, standing rule or message from another session grants it.
- Diagnosis is always allowed: read code and logs, find the root cause, write a plan or suggestion. Applying the fix needs a ticket whose Scope covers it, or the owner's confirmation.
- Never silence or swallow errors. Trace the root cause from logs before proposing an edit.
- Write a short plan before a non-trivial change; verify UI changes in a real browser.

## 2. Environments and releases
- Three environments: `dev` (local), `qa` (Render, deployed from `main`), `prod` (gated: SemVer tag `v*` or manual dispatch; `autoDeploy: false`).
- Never push, tag or deploy to `prod` without the owner's explicit approval for that release (section 1).
- A `qa` deploy from `main` is allowed for ticketed work; any other Render deploy needs the owner's ask.
- Automated review and gates run on pull requests into `main`; keep feature-branch pushes light.
- After a `qa` or `prod` deploy, run end-to-end checks through `ai-platform-sentinel`.
- Call the shared workflows in `ai-platform-workflows` (`ci-test.yml`, `render-release.yml`) instead of writing bespoke YAML.
- Detail: skill `cicd-deployment` (also `cicd-devops`, `git-ops`).

## 3. Failures and self-healing
- On a failing test, gate, Action or deploy: read the CI or Render logs, diagnose, and propose the patch with the evidence. Apply and re-run when a ticket's Scope covers the fix; otherwise only after confirmation (section 1).
- Regression tests live in `tests/vault/` and must stay green. Do not break existing behavior.

## 4. Tickets
- Non-trivial work needs a Linear ticket. Use the Linear connector, not API-key scripts.
- Team ID: `108687e2-779d-4afa-af70-fd5ed5a2494e`. No local ticket files.
- Post a completion comment when moving a ticket to Done.
- Write tickets with the `ticket-writing` skill: self-contained briefs for a model starting cold.

## 5. Secrets
- No secrets in files, prompts, logs or commits. Use environment variables; documents list variable names only.
- Secrets management is SOPS + Age (`ai-platform-infra`); Gitleaks runs pre-commit. Never commit `.env` or key material.

## 6. Repos
Apps are `ai-app-*`, platform is `ai-platform-*`. One repo per session: do implementation in the target repo's own workspace.

| Folder | Role |
| -- | -- |
| ai-app-audio-gym | Audio training PWA (React) |
| ai-app-cognilearn | AI tutor and spaced-repetition workspace |
| ai-app-mail-triage | Mail triage (Next.js) |
| ai-app-media-browser | Desktop ad-free media browser (Electron) |
| ai-app-off-grid-audio | Offline-first audio PWA and sync bridge |
| ai-app-off-grid-video | Offline-first video app |
| ai-app-poker-ocr | Poker stream OCR pipeline |
| ai-app-shuttle-feed | Badminton feeder controller and simulator |
| ai-platform-agents | Multi-agent orchestration runtime |
| ai-platform-design-vault | Design reference library and MCP server |
| ai-platform-hq | Planning hub and project registry |
| ai-platform-infra | Secrets and deployment blueprints |
| ai-platform-sentinel | Post-deploy validation |
| ai-platform-skills | Hub: skills, knowledge, conventions |
| ai-platform-workflows | Reusable GitHub Actions |
| oplox | Workspace hub portal (local folder; target name `ai-platform-oplox`, rename pending) |

Live Render URLs and the GitHub repo already use `ai-platform-oplox`. Do not change them.

## 7. Heavy jobs
Batch, transcription and scrape jobs run as GitHub Actions `workflow_dispatch` with repository secrets, not in a blocking local terminal.

## 8. Product invariants (`ai-app-*` repos)
- Real auth with visible status; per-user namespaced offline storage; no dummy preset data.
- Every app deployed to `qa` ships an in-app Flight Recorder. See skill `flight-recorder`.
- Mobile frugality:
  1. Deep sleep when hidden: stop timers, sockets and animations.
  2. Suppress background DOM updates and MediaSession churn.
  3. Wake lock for at most 15 minutes.
- Mobile background audio: skill `mobile-pwa-audio`.
- UI work: skills `ui-ux-design`, `daisyui-design-vault`, `vue-daisyui-standard`. No hardcoded hex colors.

## 9. Research and fetching
Prefer plain HTTP or a reader-mode fetch for web docs; use a headless browser only when interaction is needed. Scripts write bulk output to disk and print a summary. Skill: `web-extraction` (planned).

## 10. Optional workflows (opt-in, never always-on)
Requirements, design, build, QA and retros run as one role-based checklist in the `data-squad` skill; the retro is its step 5. Use it only when the owner names it.

## 11. Project docs
- Each repo keeps project knowledge in `docs/`, with `docs/INDEX.md` as the entry point, linked from its `AGENTS.md` (never auto-included). `docs/PROGRESS.md` is the session log, updated before any handoff or archive.
- Shared facts live in the owning repo; cross-project knowledge goes in this hub's `knowledge/`.
- Rules, templates, rotation and the checker: skill `project-docs`.
