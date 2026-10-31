---
name: cicd-deployment
description: Use when setting up or changing CI/CD, release workflows, render.yaml, SemVer tags or deployments, or when a deploy fails. Defines the 3-tier model (local dev, cloud qa from main by manual dispatch, gated prod with autoDeploy false and explicit owner sign-off), test gates and pinned Render deploys.
version: 1.1.0
---

# CI/CD and Production Deployment Standard

This skill defines the organization-wide CI/CD, version packaging, and deployment standard. **Every repository in the workspace (`ai-app-*` and `ai-platform-*`) must adhere to this architecture from Day 1.**

## When to use

- Scaffolding a repository or onboarding one to the release standard.
- Editing `render.yaml`, `.github/workflows/`, version tags or release packaging.
- Promoting a build to `qa` or `prod`, or diagnosing a failed deploy or health check.

Do not use for: general git branching and PR hygiene (use `git-ops`).

## Requirements

- Tools: `git`, `gh`, `curl`, and the project test runner (`npm`, `pytest`).
- Environment variables and CI secrets (names only): `RENDER_API_KEY`, `RENDER_SERVICE_ID`. Values come from the secret store or GitHub Actions secrets; never write them into files.

## Owner rules (apply to every step)

- A ticket the owner created or approved is the approval to code its Scope, push, land on `main` once the full suite and CI are green, and deploy to `qa`.
- Work outside a ticket's Scope, or without a ticket, needs the owner's explicit confirmation before any code change or push.
- Never push a release tag or deploy to `prod` without the owner's explicit approval, every time. No ticket, standing rule or other session's message grants it.
- Never put secrets in files, workflows, logs or examples.

## The 4 core pillars

### 1. The 3-Tier Environment Architecture on Day 1 (`render.yaml`)
Never wait until MVP completion to configure deployment. Every project adheres to the 3-tier `main`-centric lifecycle:

| Tier | Environment | Target & Branch | Promotion Trigger | Purpose & Configuration |
| :--- | :--- | :--- | :--- | :--- |
| **Dev** | `local` | Localhost (`localhost:<port>`) | Instant HMR | Fast workstation iteration, unit testing, local SQLite/IndexedDB, zero latency, zero cloud cost. |
| **QA** | `qa` (Cloud) | Render `*-qa.onrender.com` (`main` branch) | Controlled / Manual Dispatch | Cloud staging for non-prod end-to-end testing (`ai-platform-sentinel`), mobile dogfooding, WAN latency validation, test keys (`pk_test_*`), and mandatory in-app Black Box Flight Recorder (`flight-recorder` skill). |
| **Prod** | `prod` (Cloud) | Render `*.onrender.com` (`main` branch) | **`autoDeploy: false`** (explicit owner sign-off only) | Strict zero-downtime production. **NEVER trigger a `prod` deployment unless the owner explicitly asks to deploy to `prod`.** |

> **Mandatory governance gates:**
> - **Explicit prod sign-off:** Never push or trigger deployments to `prod` unless the owner explicitly requests a production deployment. Default all deliveries and verifications to `dev` / `qa`.
> - **Ticket or confirmation:** Code changes, pushes to `main` and `qa` deploys need an owner-approved ticket covering them, or the owner's explicit confirmation. Tag pushes trigger `prod`, so they follow the prod rule above.

> Drop-in template: [`references/render-blueprint-template.yaml`](./references/render-blueprint-template.yaml)

---

### 2. Mandatory Test Suite & PR Code Review Gate (`.github/workflows/test.yml`)
No code is released or promoted without automated verification:
- Runs automatically on every pull request targeting `main` or direct push to `dev`.
- Executes linters (`eslint`, `ruff`, etc.) and unit/integration test suites (`vitest`, `pytest`, `unittest`).
- **Automated PR Code Review Gate:** When a PR targets `main`, an automated code review job inspects git diffs, security boundaries, and regression safety. Bypassed for internal dev pushes; strictly enforced on PRs to `main`.
- **Strict Quality Gate:** Any failing test or rejected review halts execution and blocks merging.

---

### 3. Pinned Version Release & Deployment (`.github/workflows/release.yml`)
Production deployments are deterministic, immutable, and test-gated.

#### Trigger Vectors:
1. **SemVer tag push (`v*`):** `git tag v1.0.0 && git push origin v1.0.0` (deploys `prod`: push only with the owner's explicit approval for this release).
2. **GitHub Release:** Publishing an official release via the GitHub UI.
3. **Manual rollback / dispatch (`workflow_dispatch`):** Run with any previous `commit_sha` for instantaneous rollback.

#### Release Execution Pipeline:
1. **Ref Resolution:** Checks out the exact release tag or pinned commit SHA.
2. **Test Gatekeeper:** Executes project test runner (`npm test` / `pytest`). Deployment terminates immediately if tests fail.
3. **Production Build:** Compiles production assets (`npm run build` / Docker build).
4. **Dist Packaging:** Zips the build output into `project-${VERSION}.zip` and archives it in GitHub Actions.
5. **Release Attachment:** Attaches the zip package to the GitHub Release using `softprops/action-gh-release@v2`.
6. **Pinned Render API Trigger:** Dispatches a deployment payload directly to Render's REST API:
   ```bash
   curl -fsSL -X POST "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \
     -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}" \
     -H "Content-Type: application/json" \
     -d '{"commitId": "'"$TARGET_COMMIT"'", "clearCache": "'"$CLEAR_CACHE"'"}'
   ```
7. **Audit Report:** Emits a rich markdown summary into `$GITHUB_STEP_SUMMARY`.

> Centralized Reusable Actions: Available in [`T-Limbu/ai-platform-workflows`](https://github.com/T-Limbu/ai-platform-workflows) (`ci-test.yml` and `render-release.yml`).
> Drop-in template: [`references/release-workflow-template.yml`](./references/release-workflow-template.yml)

---

### 4. Day 1 Project Setup Checklist

When scaffolding a new repository or onboarding an existing project to this standard:

1. **Repository Secrets (GitHub Settings $\rightarrow$ Secrets and Variables $\rightarrow$ Actions):**
   - `RENDER_API_KEY`: API token generated from Render Account Settings.
   - `RENDER_SERVICE_ID`: The unique service ID (e.g., `srv-d8tous6q1p3s73aq5ln0`) found in the Render service URL.
2. **Infrastructure as Code:**
   - Copy `references/render-blueprint-template.yaml` to `render.yaml` at repo root.
   - Set up the two services in Render using the Blueprint sync.
3. **Workflows:**
   - Place `release-workflow-template.yml` into `.github/workflows/release.yml`.
   - Ensure `.github/workflows/test.yml` runs on PRs and pushes to `main`.
4. **Branch Protection:**
   - Protect `main` branch to require pull request reviews and passing test gates.

---

### 5. Render Node/SPA invariants and failure diagnosis

Field-tested build and runtime rules (devDependency retention, Node pinning, `0.0.0.0` binding, health probes) and the read-only deploy-failure diagnosis procedure live in [references/render-node-invariants.md](references/render-node-invariants.md). Diagnosing is read-only: propose fixes and ask the owner before patching a service or redeploying.

## Role responsibilities

- **Architect:**
  - Evaluates project hosting needs during the Pre-Flight phase.
  - Prepares `render.yaml` and `.github/workflows/` blueprints (inheriting from `T-Limbu/ai-platform-workflows`) before engineering begins, and commits them under a ticket that covers them or once the owner confirms.
- **Engineer:**
  - Writes code and ensures unit tests pass locally (`dev`) and in CI.
  - Proposes semantic version bumps (`vX.Y.Z`) and creates tags at milestones; pushing a tag deploys `prod` and needs the owner's explicit approval every time.
- **QA Engineer:**
  - Validates test pass rate in CI and runs `ai-platform-sentinel` end-to-end checks against `qa`.
  - Verifies build artifacts in `qa` before authorizing production release promotion.
- **Product Manager:**
  - Conducts black-box UAT on `qa` before the owner signs off on the tagged production release.

## Read next

| File | Read it when |
| -- | -- |
| [references/render-node-invariants.md](references/render-node-invariants.md) | A Render build, boot or health check fails, or a Node/SPA service is being configured |
| [references/render-blueprint-template.yaml](references/render-blueprint-template.yaml) | Creating `render.yaml` for a new project |
| [references/release-workflow-template.yml](references/release-workflow-template.yml) | Creating `.github/workflows/release.yml` |
| `flight-recorder` skill | Preparing a build for `qa` (mandatory in-app recorder) |

## Changelog

- 1.1.0 (2026-10-29): approval policy. An owner-approved ticket approves coding its Scope, pushing, landing on `main` after green CI and deploying to `qa`; release tags and `prod` always need the owner's explicit approval.
- 1.0.0 (2026-10-25): tool-neutral rewrite. Description rewritten to the 3-tier model; removed the model-specific code-change rule and the autonomous self-healing loop (now propose-and-confirm); added owner rules; standard sections added.
