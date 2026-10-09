---
name: cicd-deployment
description: Standard release, CI/CD, and deployment blueprint across all projects. Enforces dual environments (dev continuous auto-deploy vs main locked down), tagged release packaging (SemVer v*), automated test gates, GitHub release artifacts, Render API pinned deploy, and summary reporting.
---

# 🚀 CI/CD & Production Deployment Standard

This skill defines the organization-wide CI/CD, version packaging, and deployment standard. **Every repository in the workspace and Data Squad pipeline must adhere to this architecture from Day 1.**

---

## 🏛️ The 4 Core Architectural Pillars

### 1. Dual Environments on Day 1 (`render.yaml`)
Never wait until MVP completion to configure deployment. Every project maintains two distinct environments:

| Environment | Branch | Auto-Deploy | Purpose |
| :--- | :--- | :--- | :--- |
| **Development (`dev`)** | `dev` | **`true`** | Rapid dogfooding, automated smoke testing, and QA validation. |
| **Production (`prod`)** | `main` | **`false`** | Strict zero-downtime production. **Never auto-deploys directly on push.** |

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

## 👥 Data Squad Role Responsibilities

- **Junior Architect:**
  - Evaluates project hosting needs during the Pre-Flight phase.
  - Automatically commits `render.yaml` and `.github/workflows/` blueprints before engineering begins.
- **Junior Engineer:**
  - Writes code and ensures unit tests pass locally and in CI.
  - Increments semantic versioning (`vX.Y.Z`) and generates tags upon milestone completion.
- **Junior QA Engineer:**
  - Validates test pass rate in CI.
  - Verifies build artifacts in `dev` before authorising production release promotion.
- **Junior Product Manager:**
  - Conducts black-box UAT on `dev` before signing off on the tagged production release.
