---
name: cicd-deployment
description: Standard release, CI/CD, and deployment blueprint across all projects. Enforces dual environments (dev continuous auto-deploy vs main locked down), tagged release packaging (SemVer v*), automated test gates, GitHub release artifacts, Render API pinned deploy, and summary reporting.
---

# 🚀 CI/CD & Production Deployment Standard

This skill defines the organization-wide CI/CD, version packaging, and deployment standard. **Every repository in the workspace (`ai-app-*` and `ai-platform-*`) must adhere to this architecture from Day 1.**

---

## 🏛️ The 4 Core Architectural Pillars

### 1. The 3-Tier Environment Architecture on Day 1 (`render.yaml`)
Never wait until MVP completion to configure deployment. Every project adheres to the 3-tier `main`-centric lifecycle:

| Tier | Environment | Target & Branch | Promotion Trigger | Purpose & Configuration |
| :--- | :--- | :--- | :--- | :--- |
| **Dev** | `local` | Localhost (`localhost:<port>`) | Instant HMR | Fast workstation iteration, unit testing, local SQLite/IndexedDB, zero latency, zero cloud cost. |
| **QA** | `qa` (Cloud) | Render `*-qa.onrender.com` (`main` branch) | Controlled / Manual Dispatch | Cloud staging for non-prod end-to-end testing (`ai-platform-sentinel`), mobile dogfooding, WAN latency validation, test keys (`pk_test_*`), and mandatory in-app Black Box Flight Recorder (`flight-recorder` skill). |
| **Prod** | `prod` (Cloud) | Render `*.onrender.com` (`main` branch) | **`autoDeploy: false`** (Explicit Stakeholder Sign-Off Only) | Strict zero-downtime production. **NEVER trigger a `prod` deployment unless the Stakeholder explicitly asks to deploy to `prod`.** |

> ⚠️ **Mandatory Governance Gates:**
> - **Explicit Prod Sign-Off:** Never push or trigger deployments to `prod` unless the Stakeholder explicitly requests a production deployment. Default all deliveries and verifications to `dev` / `qa`.
> - **Gemini Flash-Only Code Changes:** Only make code changes with **Gemini Flash**; never modify code using Opus, Gemini Pro, or Gemini 4.

> 📁 Drop-in template: [`references/render-blueprint-template.yaml`](./references/render-blueprint-template.yaml)

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
1. **SemVer Tag Push:** `git tag v1.0.0 && git push origin v1.0.0`
2. **GitHub Release:** Publishing an official release via the GitHub UI.
3. **Manual Rollback / Dispatch (`workflow_dispatch`):** Run with any previous `commit_sha` for instantaneous rollback.

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

> 📁 Centralized Reusable Actions: Available in [`T-Limbu/ai-platform-workflows`](https://github.com/T-Limbu/ai-platform-workflows) (`ci-test.yml` and `render-release.yml`).
> 📁 Drop-in template: [`references/release-workflow-template.yml`](./references/release-workflow-template.yml)

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

### 5. Render Fullstack Node/SPA Invariants & Self-Healing Standard

Field-tested rules derived from production container debugging on Render:

1. **`npm install` DevDependency Retention**:
   - Render sets `NODE_ENV=production` inside build containers. Under this variable, npm automatically prunes `devDependencies` unless `--include=dev` is supplied.
   - **Mandatory Blueprint Setting:**
     ```yaml
     buildCommand: npm install --include=dev && npm run build
     ```
   - **Package Hardening:** Elevate core build tools (`vite`, `vue-tsc`, `typescript`, `tailwindcss`, `daisyui`) into `dependencies` in `package.json` so builds never throw `Exit Code 127: Command Not Found`.

2. **Explicit Node Runtime Pinning**:
   - Modern tooling (Vite 6, TypeScript 5.6+) requires Node 20+.
   - Add `"engines": { "node": ">=20.0.0" }` in `package.json`.
   - Specify `NODE_VERSION: 20` under `envVars` in `render.yaml`.

3. **`0.0.0.0` Host Binding**:
   - Express servers must explicitly bind to `0.0.0.0` (`app.listen(PORT, '0.0.0.0')`). Binding to default `localhost` or IPv6 loopback causes Render's IPv4 reverse-proxy port scanner to fail, timing out the deployment after 120 seconds.

4. **Zero-Downtime Health Probes**:
   - Expose explicit `GET /health` and `GET /api/health` endpoints returning HTTP 200 JSON `{ status: 'ok' }`.
   - Implement an express fallback for `GET /` if `dist/index.html` static bundles are building or pending.

5. **Autonomous Self-Healing Loop via Render API**:
   - When a deploy fails or health check times out, use `RENDER_API_KEY` to query `https://api.render.com/v1/services/{id}/events`.
   - Diagnose exit codes (`nonZeroExit: 127` $\rightarrow$ missing build dependencies).
   - Patch service parameters via Render REST API (`PATCH /v1/services/{id}`) and trigger a fresh deploy with `clearCache: "clear"`.
   - Validate post-deploy health using `ai-platform-sentinel`.

---

## 👥 Autonomous Engineering Role Responsibilities

- **Architect:**
  - Evaluates project hosting needs during the Pre-Flight phase.
  - Automatically commits `render.yaml` and `.github/workflows/` blueprints (inheriting from `T-Limbu/ai-platform-workflows`) before engineering begins.
- **Engineer:**
  - Writes code and ensures unit tests pass locally (`dev`) and in CI.
  - Increments semantic versioning (`vX.Y.Z`) and generates tags upon milestone completion.
- **QA Engineer:**
  - Validates test pass rate in CI and runs `ai-platform-sentinel` end-to-end checks against `qa`.
  - Verifies build artifacts in `qa` before authorizing production release promotion.
- **Product Manager:**
  - Conducts black-box UAT on `qa` before signing off on the tagged production release.
