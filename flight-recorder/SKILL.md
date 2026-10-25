---
name: flight-recorder
description: Architecture, specification, and drop-in blueprint for the mandatory in-app Black Box Flight Recorder & Diagnostic Drawer required on all QA and staging services. Provides local ring buffering, localStorage persistence, OS lifecycle interception, unhandled error catching, 1-tap clipboard export, and remote cloud telemetry streaming.
---

# 🐞 In-App Black Box Flight Recorder Standard (Mandatory QA Feature)

**Organization Invariant:** Every client-facing application, PWA, or frontend service deployed to a **QA environment** (`qa`, staging, or local mobile dogfooding) must include the in-app **Black Box Flight Recorder** (`flightRecorder.ts`).

---

## 🏛️ Why This Standard Exists
1. **The Mobile DevTools Blind Spot:** Desktop DevTools cannot reproduce Android Knox, iOS WebKit background memory caps, or battery optimization throttling.
2. **USB Debugging Masking:** USB cable connections keep mobile devices in `battery_charging` state, preventing aggressive OS deep-sleep bugs from triggering.
3. **Instant Stakeholder Diagnosis:** Allows the Stakeholder or QA testers to test on physical hardware (phones, tablets, BLE machines) and send exact millisecond diagnostic logs to the squad in one tap without tethering or opening remote debuggers.

---

## 📋 The 5 Architectural Requirements

```
+-----------------------------------------------------------------------------------+
|                        BLACK BOX FLIGHT RECORDER ARCHITECTURE                     |
+-----------------------------------------------------------------------------------+
|  1. Ring Buffer + LocalStore | 2. Lifecycle Interception  | 3. Domain Event Hooks |
|  150 memory items, 60 saved  | window.onerror, pagehide,  | Audio, WebSockets, BLE|
|  survives crashes & reloads  | freeze, visibilitychange   | Downloads, Sync state |
+------------------------------+----------------------------+-----------------------+
|  4. Floating Diagnostic UI   | 5. Remote Cloud Telemetry                          |
|  Unobtrusive pill (🐞 Logs)  | 1-tap send to Oplox (/api/apps/<appId>/telemetry)   |
|  Filter tabs, 1-tap copy     | Zero DevTools needed on physical devices           |
+-----------------------------------------------------------------------------------+
```

### 1. In-Memory Ring Buffer & Persistence
* Ring buffer capped at **150 entries** in memory to prevent memory bloat.
* Latest **60 entries** mirrored to `localStorage` under `offgrid_flight_recorder_logs` (or `<appId>_flight_recorder_logs`) so logs survive browser crashes, tab discards, and cold reloads.
* Formatted timestamp with millisecond precision: `HH:mm:ss.SSS`.

### 2. Automatic Lifecycle & Error Interception
Must auto-intercept on initialization:
* `window.addEventListener('error')` $\rightarrow$ Logs unhandled script errors with stack traces.
* `window.addEventListener('unhandledrejection')` $\rightarrow$ Logs unhandled Promise rejections.
* `document.addEventListener('visibilitychange')` $\rightarrow$ Logs tab hidden/visible transitions with `navigator.userActivation` state.
* `window.addEventListener('freeze')` and `window.addEventListener('resume')` $\rightarrow$ Logs Chromium lifecycle freeze events.
* `window.addEventListener('pagehide')` and `window.addEventListener('pageshow')` $\rightarrow$ Logs navigation and BFCache transitions.

### 3. Domain Event Hooks
Domain engines must call `recordFlightLog(category, level, message, data)`:
* **Audio Services:** Hook native `<audio>` events (`play`, `pause`, `waiting`, `stalled`, `ended`, `error`).
* **Downloaders / Pipelines:** Log batch starts, worker milestones, retries, and completions.
* **BLE / Hardware Services:** Log connect, disconnect, MTU negotiation, characteristic writes, and packet timeouts.
* **Sync / Auth:** Log token renewals, Firestore sync batches, and connection drops.

### 4. Floating Diagnostic Drawer UI
* An unobtrusive floating button placed in the corner: `🐞 Logs (42)`.
* Tapping opens a sleek, dark-mode slide-over / modal drawer:
  * Badge counter showing total entries.
  * Category filter buttons (`ALL`, `AUDIO`, `LIFECYCLE`, `DOWNLOAD`, `ERROR`, etc.).
  * **"📋 Copy Logs"**: copies all logs formatted as clean text to clipboard (`navigator.clipboard.writeText`).
  * **"☁️ Send to Cloud"**: POSTs the log buffer to Oplox telemetry or app backend.
  * **"🗑️ Clear"**: wipes in-memory buffer and `localStorage`.

### 5. Remote Cloud Telemetry Ingestion
Dispatches payloads to:
```ts
const endpoints = [
  'https://ai-platform-oplox-prod.onrender.com/api/apps/<appId>/telemetry',
  '/api/telemetry/report'
];
```
This enables autonomous squad agents (`root_cause_diagnostician`, `qa_engineer`) to inspect live phone logs remotely via `https://ai-platform-oplox-prod.onrender.com/api/apps/<appId>/logs` without interrupting the Stakeholder.

---

## 🛠️ Drop-In Implementation Blueprint

```ts
export interface FlightLogEntry {
  id: number;
  time: string; // HH:mm:ss.SSS
  category: string;
  level: 'info' | 'warn' | 'error';
  message: string;
  data?: any;
}

const STORAGE_KEY = 'app_flight_recorder_logs';
const MAX_BUFFER = 150;
const MAX_PERSISTED = 60;

let ringBuffer: FlightLogEntry[] = [];
let logIdCounter = 0;

export function recordFlightLog(
  category: string,
  level: 'info' | 'warn' | 'error',
  message: string,
  data?: any
): FlightLogEntry {
  const now = new Date();
  const pad = (n: number, d = 2) => String(n).padStart(d, '0');
  const time = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}.${pad(now.getMilliseconds(), 3)}`;

  const entry: FlightLogEntry = {
    id: ++logIdCounter,
    time,
    category,
    level,
    message,
    ...(data !== undefined ? { data } : {})
  };

  ringBuffer.push(entry);
  if (ringBuffer.length > MAX_BUFFER) ringBuffer.shift();

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(ringBuffer.slice(-MAX_PERSISTED)));
  } catch {}

  return entry;
}
```

---

## 📋 QA Environment Verification Gate
Before QA sign-off on any release candidate:
- [ ] Flight recorder is initialized on application mount.
- [ ] Floating toggle button (`🐞 Logs`) renders and is accessible on mobile screens.
- [ ] Tapping "Copy Logs" copies clean formatted text.
- [ ] Tapping "Send to Cloud" returns `✓ Sent!` and reaches remote telemetry store.
- [ ] Unhandled errors and page visibility state changes appear immediately in the log list.
