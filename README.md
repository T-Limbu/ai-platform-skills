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

---

## 🔄 Two-Way Synchronization with Antigravity

Antigravity loads global custom skills from `~/.gemini/config/skills/`.

### Automated Sync Scripts

#### 1. Push repo changes to Antigravity (`push-to-antigravity.ps1`):
```powershell
.\sync-to-local.ps1
```
Copies all skills from this repository to `C:\Users\<User>\.gemini\config\skills\`.

#### 2. Pull runtime changes back to Git (`pull-from-antigravity.ps1`):
```powershell
.\sync-from-local.ps1
```
Pulls any new skills generated in the local agent configuration into this repository for git tracking.

---

## 🏛️ Contributing a New Skill

1. Create a subfolder: `skills/<skill-name>/`
2. Create `SKILL.md` with required frontmatter:
   ```yaml
   ---
   name: my-new-skill
   description: One-line concise description of what the skill does and when to invoke it.
   ---
   ```
3. Add supporting scripts or references in `scripts/` or `resources/`.
4. Run `git status`, commit, and push.
