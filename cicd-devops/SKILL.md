---
name: cicd-devops
description: Continuous Integration & Continuous Delivery (CI/CD) pipelines, automated testing gates, GitHub Actions automation, build verifications, and deployment workflows. Includes reusable blueprints and hardened rules from learnings.
---

# CI/CD & DevOps Automation Skill

This skill provides modular patterns, workflow blueprints, tool suites, and field-tested rules for building resilient CI/CD pipelines.

---

## 🛠️ Tool Group: CI/CD & Automation Suite

| Category | Recommended Tools | Purpose & Capabilities |
| :--- | :--- | :--- |
| **Pipeline Runner** | **GitHub Actions** (`.github/workflows/`), GitLab CI | Event-driven automation on `push`, `pull_request`, `workflow_dispatch` |
| **Local Workflow Runner**| **`act`** (Nephrolepis / Nektos) | Run GitHub Actions locally inside Docker containers without pushing commits |
| **Test Runners** | **`pytest`**, **`jest`**, **`vitest`** | Automated unit, regression, and integration test execution |
| **Linters & Formatters** | **`ruff`**, **`flake8`**, **`eslint`**, **`prettier`** | Static analysis, code styling, syntax error detection before building |
| **Release & Packaging** | **`gh release`**, **`semantic-release`** | Automated changelog generation, GitHub Releases, and artifact publishing |

---

## 🚀 Reusable Workflow Blueprints

### 1. Zero-Friction Test & Quality Gate (`.github/workflows/test.yml`)
Runs tests on every pull request and push to `main`:

```yaml
name: Test Suite & Quality Gate

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt || true
          pip install pytest

      - name: Run Test Suite
        run: pytest -v --tb=short
```

### 2. Automated Static Web Deployment (`.github/workflows/deploy.yml`)
Auto-builds and publishes static PWAs or frontends to GitHub Pages:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload Artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

---

## 📚 Rules from Learning (Field-Hardened Guidelines)

1. **Rule [Quality Gate First]**: Never allow deployment workflows to trigger without an upstream test step passing. A failed unit test must abort deployment instantly.
2. **Rule [Action Version Pinning]**: Always pin GitHub Actions to major versions (e.g. `@v4`, `@v5`) or immutable commit SHAs. Avoid `@master` or `@main` which introduce sudden breaking changes.
3. **Rule [Least Privilege Tokens]**: Declare explicit `permissions` blocks at the job level rather than inheriting broad default write tokens.
4. **Rule [Idempotency & Concurrency]**: Set concurrency groups (`cancel-in-progress: true` for PR builds, `false` for production deployments) to prevent race conditions during rapid commits.
5. **Rule [Local Pre-Flight Verification]**: Before creating or modifying workflow YAML files, validate syntax locally or check that referenced shell commands exist in the runner environment.
6. **Rule [Learning Feedback Loop]**: When a CI/CD job fails due to an environment mismatch, secret leak, or runner incompatibility, record the root cause and guardrail in this section.
