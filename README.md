# 🧠 Squad Skills Hub

> **Centralized Git Repository & Catalog of Autonomous AI Squad Skills & Playbooks**
> Managed by the Autonomous AI Data Squad for cross-project engineering, testing, and deployment standards.

---

## 📚 Skill Catalog

| Skill Name | Purpose | Target Domains |
| :--- | :--- | :--- |
| [`cicd-deployment`](./cicd-deployment/SKILL.md) | Dual-environment release pipeline (`dev` auto-deploy vs `main` locked), SemVer tag releases, and Render pinned deployment. | DevOps, CI/CD, Releases |
| [`cicd-devops`](./cicd-devops/SKILL.md) | Hardened GitHub Actions automation, test gates, PR code reviews, and build verification blueprints. | GitHub Actions, Workflows |
| [`daisyui-design-vault`](./daisyui-design-vault/SKILL.md) | Synthesis and customization of production daisyUI v5 / Tailwind v4 layouts, components, and 35-theme switcher. | UI/UX, Themes, Prototypes |
| [`data-squad`](./data-squad/SKILL.md) | Multi-role autonomous AI squad orchestration (Product Manager, Architect, Engineer, QA). | Autonomous Orchestration |
| [`download-trending`](./download-trending/SKILL.md) | Autonomous UK Singles Top 100 scraping, background downloads, and local IndexedDB music syncing. | Media Extraction, Scraping |
| [`git-ops`](./git-ops/SKILL.md) | Multi-branch Git hygiene, pull request gatekeeping, squash-merge workflows, and remote sync procedures. | Version Control, GitOps |
| [`mobile-adb`](./mobile-adb/SKILL.md) | Mobile diagnostics, Android Debug Bridge (ADB), APK reverse engineering, and Web Bluetooth/device troubleshooting. | Mobile, Hardware, Bluetooth |
| [`ui-ux-design`](./ui-ux-design/SKILL.md) | Modern UI/UX guidelines: 4-point spacing grid, dark-mode surface elevation, typography scale, micro-interactions, and battery preservation. | Design Standards, Ergonomics |
| [`flight-recorder`](./flight-recorder/SKILL.md) | Mandatory in-app Black Box Flight Recorder for `qa` and mobile dogfooding builds. | QA, Mobile Diagnostics |
| [`mobile-pwa-audio`](./mobile-pwa-audio/SKILL.md) | Background audio invariants for mobile PWAs, including the in-memory video-track demuxer. | Mobile, Audio |
| [`token-efficiency`](./token-efficiency/SKILL.md) | Practices that cut session token use without lowering quality, and when to offer a fresh session. | Agent Workflow |
| [`vue-daisyui-standard`](./vue-daisyui-standard/SKILL.md) | Vue 3 + Tailwind + daisyUI project layout, conventions and mobile invariants. | Frontend Architecture |

---

## 🔄 Installing skills (this repo is the single source)

Edit skills here only. Agent runtimes read them from this folder; nothing is copied back.

### Claude Code: directory junctions

Link each skill folder instead of copying it, so edits here apply immediately:

```powershell
# User level (every repo)
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\git-ops" -Target "$PWD\git-ops"

# Project level (one repo): link into <repo>\.claude\skills\ and keep the links out of git
```

User level: `cicd-deployment`, `data-squad`, `flight-recorder`, `git-ops`, `mobile-adb`, `token-efficiency`. Project level: the UI skills in Vue repos, `mobile-pwa-audio` in the audio PWAs, `download-trending` in `ai-app-off-grid-audio` only. A running session reads skills at startup, so check new links in a fresh session.

### Antigravity: one-way copy

Antigravity loads skills from `~/.gemini/config/skills/`. Run `.\sync-to-local.ps1` to copy this repo there. Do not copy that folder back into the repo: it holds older, non-tool-neutral versions (the former `sync-from-local.ps1` was removed for that reason).

---

## 🏛️ Contributing a New Skill

1. Create a subfolder: `<skill-name>/` at the repo root
2. Create `SKILL.md` with required frontmatter:
   ```yaml
   ---
   name: my-new-skill
   description: Use when <situation>. One or two sentences on what the skill holds.
   version: 0.1.0
   ---
   ```
3. Add supporting files in `references/` or `scripts/` and link them from `SKILL.md`.
4. Run the linter (below), then commit. Push only when the owner asks.

---

## Linting skills

```bash
python scripts/lint_skills.py                 # PASS/WARN/FAIL per skill, file:line reasons
python scripts/lint_skills.py --format github # CI annotations
python -m unittest discover -s tests          # linter self-tests
```

Checks L1-L18 follow the tool-neutral SKILL.md standard. Exit code is 1 when any skill has a FAIL.
