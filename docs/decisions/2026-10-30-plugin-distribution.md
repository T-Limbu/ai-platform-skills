# Decision: distribute the hub as a Claude Code plugin

Verified against `9b222e4`, 2026-10-31. Decided by: the owner (KSH-302, 2026-10-30); packaged in KSH-304. Status: accepted.

## Decision

- Local Claude sessions get the skills from one plugin, `squad`, in the marketplace `t-limbu` (install id `squad@t-limbu`). Source: GitHub `T-Limbu/ai-platform-skills`.
- One plugin `version` in `.claude-plugin/plugin.json`, with a matching `v<version>` tag on `main`, starting at `0.1.0`. Per-skill versions stay as they are.
- `"skills": ["./"]` points the plugin at the repo root, so the 14 skill folders stay the only copy. No `skills/` folder, no symlinks.
- Rename to `squad:<name>` only in Claude-only places (workspace `CLAUDE.md`, the SessionStart hook, the README install steps). SKILL.md bodies and `conventions/AGENTS.md` keep bare names because Gemini reads them too.
- Cloud sessions don't load plugins; they use claude.ai account skills (KSH-224). Antigravity keeps `sync-to-local.ps1`.

## Guard

Lint L19 fails when a SKILL.md or `references/*.md` names a skill (`` `name` skill `` or `skill `name` ``) that has no folder, or uses a `plugin:` prefix that differs from `plugin.json` `name`.

## Notes

- `git merge-base --is-ancestor <branch tip> origin/main` is false after a squash merge. To check that a squash-merged branch landed, compare trees: `git diff <branch tip> origin/main` is empty.
- `claude plugin validate .` passes with two warnings: no plugin icon, no marketplace description. Neither blocks install.
