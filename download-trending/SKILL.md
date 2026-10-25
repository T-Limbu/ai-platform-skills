---
name: download-trending
description: Use when asked to download, update, sync or fetch trending songs (the Official UK Singles Top 100) into the Off-Grid Audio library, in the ai-app-off-grid-audio repo only. Starts the local backend and frontend if needed, runs the headless sync script and reports a library audit. Not for other downloads.
version: 0.1.0
---

# 🎵 Autonomous Trending Songs Sync Skill

This skill automates the complete end-to-end process of updating and caching the **Official UK Singles Chart Top 100** into local IndexedDB storage for offline playback.

Whenever the user prompts:
- *"download trending"*
- *"update trending songs"*
- *"sync trending"*
- *"fetch trending"*

Execute this exact runbook:

---

## 📋 Operational Runbook

### Step 1: Health Check & Server Auto-Boot
Check if the local backend and frontend dev servers are active:
- Backend: `http://localhost:3000/api/health`
- Frontend: `http://localhost:5173/`

If either service is down:
1. Start Backend: Run `npm run dev` inside `backend/` with `IsDaemon: true`.
2. Start Frontend: Run `npm run dev` inside `frontend/` with `IsDaemon: true`.
3. Wait 3 seconds for port binding.

---

### Step 2: Trigger Autonomous Headless Sync
Execute the automated sync runner:
```powershell
# From the frontend directory:
npm run sync:trending
```
*(Optionally append `--limit <number>` if the user requested a specific subset, e.g. `node scripts/sync-trending.mjs --limit 20`)*

The script will:
1. Launch Chromium with persistent profile (`.browser-data`).
2. Load the PWA, navigate to Search $\rightarrow$ Trending.
3. Fetch the latest Official UK Top 100.
4. Trigger the background queueing pipeline.
5. Poll Dexie `db.downloadQueue` and `db.tracks` until all songs have downloaded raw audio Blobs (> 20KB).
6. Emit real-time progress logs and output a final audit summary.

---

### Step 3: Emit Status Report to the Stakeholder
Once the script completes, present a structured summary:
- **Total Trending Songs Synced**
- **Existing vs. Newly Added Tracks**
- **Verified Offline Blobs**
- **Current Offline Library Total**
