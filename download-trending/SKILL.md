---
name: download-trending
description: Autonomous workflow to download and update trending songs (Official UK Singles Top 100) into the Off-Grid Audio local library. Automatically verifies/starts local backend and frontend servers, drives the PWA to queue and download tracks to IndexedDB, monitors background downloads, and reports a library audit summary. Trigger whenever the user says "download", "download trending", "update trending", "sync trending", or "fetch trending".
---

# 🎵 Autonomous Trending Songs Sync Skill

This skill automates the complete end-to-end process of updating and caching the **Official UK Singles Chart Top 100** into local IndexedDB storage for offline playback.

Whenever the user prompts:
- *"download"*
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
