---
name: mobile-pwa-audio
description: Architecture, diagnostic standards, and runtime invariants for building bulletproof mobile background audio players in PWAs (Chromium Android & WebKit iOS). Covers in-app flight recorders, ISO BMFF in-memory demuxing, Chromium background pause avoidance, and OS MediaSession lifecycle management.
---

# 🎵 Mobile Background Audio & PWA Media Playbook

This skill defines the organization-wide architecture and runtime invariants for building bulletproof, offline-first mobile background audio players in Progressive Web Apps (PWAs), particularly across Android Chromium (Chrome, Samsung Internet, Edge) and iOS WebKit (Safari).

---

## 🏛️ The 6 Core Engineering Pillars

```
+-----------------------------------------------------------------------------------+
|                        MOBILE BACKGROUND AUDIO ARCHITECTURE                       |
+-----------------------------------------------------------------------------------+
|  1. Flight Recorder First   |  2. Pure Native <audio> HAL  |  3. In-Memory Demux  |
|  In-app telemetry drawer    |  Bypass WebAudio on mobile;  |  Strip 'vide' trak;  |
|  Ring buffer + cloud sync   |  no microtask pause-fighting |  adjust 'stco' in-mem|
+-----------------------------+------------------------------+----------------------+
|  4. Strict ISO BMFF Parser  |  5. Non-Destructive Invariant|  6. MediaSession Sync|
|  moov->trak->mdia->hdlr     |  Never purge user libraries; |  OS lock screen ctrl;|
|  handler type at offset +12 |  transform dynamically       |  suppress DOM reflow |
+-----------------------------------------------------------------------------------+
```

---

### 1. The Telemetry-First Rule: In-App Flight Recorder on Day 1
**Never attempt to diagnose mobile audio lifecycle issues via desktop DevTools, USB debugging, or guesswork.**
- **Why desktop DevTools fails:** Desktop browsers do not throttle background execution, do not run Android Knox / battery optimization daemons, and do not simulate mobile audio focus contention.
- **Why USB debugging masks bugs:** Tethering an Android phone via ADB / USB cable actively keeps the device in `battery_charging` state, preventing aggressive OS deep-sleep power states from engaging.
- **The Mandatory Solution:**
  1. Implement an in-app **Black Box Flight Recorder** (`flightRecorder.ts`) that runs directly inside the client PWA.
  2. Maintain an in-memory ring buffer (100–200 events) and persist the last 50 events in `localStorage`.
  3. Hook all `<audio>` events (`play`, `playing`, `pause`, `waiting`, `stalled`, `ended`, `error`, `suspend`, `emptied`).
  4. Hook all Page Lifecycle events (`visibilitychange`, `freeze`, `resume`, `pagehide`, `pageshow`).
  5. Provide an unobtrusive in-app diagnostic drawer (`🐞 Logs`) with one-tap clipboard copy and remote cloud POST endpoint (e.g. to Oplox or telemetry API).

---

### 2. The Microtask Event-Listener Ban (Never Fight OS Pauses)
**Never call `elem.play()` inside `elem.addEventListener('pause')`.**
- **The Anti-Pattern:**
  ```ts
  // ❌ FATAL ANTI-PATTERN: Fights the Android Audio HAL
  elem.addEventListener('pause', () => {
    if (this.state.isPlaying && !this.userInitiatedPause) {
      queueMicrotask(() => elem.play());
    }
  });
  ```
- **The Failure Mechanism:**
  1. When screen locks, Android issues a transient pause to the audio hardware while transitioning output to the background audio sink.
  2. The microtask immediately calls `elem.play()`.
  3. The OS immediately pauses again, triggering another microtask.
  4. In live telemetry, this caused **40 pause/play oscillations within 150 milliseconds**, causing an audible ~0.5s stutter and exhausting the browser's transient user activation token.
  5. On the subsequent minimize, `elem.play()` is rejected with `NotAllowedError: play() failed because the user didn't interact with the document first`.
- **The Golden Rule:** Let the OS manage playback state transitions. Update internal state on `pause`, sync with `navigator.mediaSession.playbackState`, and only trigger `play()` upon explicit user action or foreground recovery.

---

### 3. Chromium's `has_video_` Background Pause Trap
**In Chromium for Android (`WebMediaPlayerImpl::OnFrameHidden`), if a media file has ANY video track (`has_video_ == true`), Chrome forcibly executes `Pause()` 3–12ms after screen lock.**
- **The Trap:**
  - Standard HTML5 `<audio>` elements are backed by the same `WebMediaPlayerImpl` engine in Chromium.
  - If an MP4 / M4A audio file was downloaded from YouTube, converted from MP4, or contains a placeholder/blank video track (`vide` atom in ISO BMFF), Chromium flags `has_video_ = true`.
  - Android Chrome assumes the user was watching a video and pauses it to conserve battery and CPU.
- **The Solution:** Strip the video track so `WebMediaPlayerImpl::HasVideo()` returns `false`.

---

### 4. The Non-Destructive In-Memory Demuxer Standard
**Never delete local or cloud user files to fix container formatting. Fix the container in-memory at load time.**
- **The Anti-Pattern:** Auto-purging tracks from IndexedDB / local storage when a video track is detected, hoping the client will re-download a pure audio stream.
  - *Why it fails:* Mobile users may be offline, outside local Wi-Fi, or without access to a backend scraping server. Auto-purging deletes the user's music library and leaves them stranded with broken playback.
- **The In-Memory Demuxer Standard:**
  - Intercept the `Blob` in `resolveAudioBlobUrl()` before calling `URL.createObjectURL()`.
  - If an embedded video track is detected, pass the `ArrayBuffer` to an in-memory MP4 demuxer (`stripVideoTrackFromMp4`).
  - Drop the `vide` `trak` box, update the parent `moov` box header, and decrement all subsequent `stco` (chunk offset) values by the size of the removed box.
  - Execution time: **~1ms in pure WebAssembly / JavaScript** for a 10MB audio file. Zero disk I/O, zero network calls, zero data loss.

---

### 5. Structural ISO BMFF Atom Parsing vs. Naive String Scanning
**Never scan binary buffers with naive byte searches (e.g. searching for `0x76, 0x69, 0x64, 0x65`).**
- **The False-Positive Trap:**
  - Searching for the 4-byte sequence `'vide'` (`0x76, 0x69, 0x64, 0x65`) in the first 256KB matches titles, metadata, comments, and URLs containing words like "video" or "Official Music Video".
  - This marks 100% pure audio files as corrupt.
- **The Standard ISO/IEC 14496-12 Parser:**
  - A track is a video track IF AND ONLY IF `'vide'` appears as the `handler_type` inside a `hdlr` box:
    - 4 bytes: Box size
    - 4 bytes: Box type (`'hdlr'`: `0x68, 0x64, 0x6C, 0x72`)
    - 4 bytes: Version and flags
    - 4 bytes: Pre-defined (reserved)
    - 4 bytes: Handler type (`'vide'` for video, `'soun'` for sound).
  - Therefore, verify that `'vide'` appears strictly at offset `+12` from the `'hdlr'` box identifier:
    ```ts
    export async function hasEmbeddedVideoTrack(blob: Blob): Promise<boolean> {
      try {
        const scanBuffer = await blob.slice(0, Math.min(blob.size, 262144)).arrayBuffer();
        const u8 = new Uint8Array(scanBuffer);
        for (let i = 0; i <= u8.length - 16; i++) {
          if (u8[i] === 0x68 && u8[i + 1] === 0x64 && u8[i + 2] === 0x6C && u8[i + 3] === 0x72) {
            if (
              u8[i + 12] === 0x76 && // 'v'
              u8[i + 13] === 0x69 && // 'i'
              u8[i + 14] === 0x64 && // 'd'
              u8[i + 15] === 0x65    // 'e'
            ) {
              return true;
            }
          }
        }
      } catch {}
      return false;
    }
    ```

---

### 6. Native `<audio>` Direct Hardware Output vs. Web Audio API on Mobile
**On mobile devices, route native `<audio>` directly to hardware output. Do NOT pipe through `AudioContext.createMediaElementSource()`.**
- **The Trap:** When an `<audio>` element is connected to a Web Audio `AudioContext` graph, mobile operating systems treat the audio graph as an active web application resource. When the browser tab is hidden or minimized, the operating system suspends the `AudioContext` to conserve CPU, which immediately starves and halts the native `<audio>` element.
- **The Standard:**
  - Use `AudioContext` solely on desktop where advanced visualizers, equalizers, and non-suspended background graphs are supported.
  - On mobile (`navigator.userAgent` matching mobile/tablet or `navigator.maxTouchPoints > 1`), bypass `createMediaElementSource()` entirely and let `<audio>` stream directly to the OS media session.

---

## 🛠️ Code Implementation: The Reference In-Memory Demuxer

```ts
/**
 * In-memory MP4/M4A video track stripper.
 * Drops the 'vide' trak box and adjusts 'stco' chunk offsets in-place.
 */
export function stripVideoTrackFromMp4(buffer: ArrayBuffer): ArrayBuffer {
  const u8 = new Uint8Array(buffer);
  const view = new DataView(buffer);

  let moovOffset = -1;
  let moovSize = 0;
  let pos = 0;

  while (pos <= buffer.byteLength - 8) {
    const size = view.getUint32(pos);
    if (size < 8 || pos + size > buffer.byteLength) break;
    const type = String.fromCharCode(u8[pos + 4], u8[pos + 5], u8[pos + 6], u8[pos + 7]);
    if (type === 'moov') {
      moovOffset = pos;
      moovSize = size;
      break;
    }
    pos += size;
  }

  if (moovOffset === -1) return buffer;

  let moovPos = moovOffset + 8;
  const moovEnd = moovOffset + moovSize;
  const retainedChildren: { offset: number; size: number }[] = [];
  let videoTrakSize = 0;

  while (moovPos <= moovEnd - 8) {
    const childSize = view.getUint32(moovPos);
    if (childSize < 8 || moovPos + childSize > moovEnd) break;
    const childType = String.fromCharCode(u8[moovPos + 4], u8[moovPos + 5], u8[moovPos + 6], u8[moovPos + 7]);

    let isVideoTrak = false;
    if (childType === 'trak') {
      for (let i = moovPos; i <= moovPos + childSize - 16; i++) {
        if (u8[i] === 0x68 && u8[i + 1] === 0x64 && u8[i + 2] === 0x6C && u8[i + 3] === 0x72) {
          if (u8[i + 12] === 0x76 && u8[i + 13] === 0x69 && u8[i + 14] === 0x64 && u8[i + 15] === 0x65) {
            isVideoTrak = true;
            break;
          }
        }
      }
    }

    if (isVideoTrak) {
      videoTrakSize += childSize;
    } else {
      retainedChildren.push({ offset: moovPos, size: childSize });
    }
    moovPos += childSize;
  }

  if (videoTrakSize === 0) return buffer; // Pure audio already

  const newSize = buffer.byteLength - videoTrakSize;
  const newBuf = new Uint8Array(newSize);
  const newView = new DataView(newBuf.buffer);

  // 1. Copy everything before moov
  newBuf.set(u8.subarray(0, moovOffset), 0);

  // 2. Write new moov box header
  const newMoovSize = moovSize - videoTrakSize;
  newView.setUint32(moovOffset, newMoovSize);
  newBuf.set(u8.subarray(moovOffset + 4, moovOffset + 8), moovOffset + 4);

  // 3. Copy retained moov children, adjusting stco chunk offsets
  let writePos = moovOffset + 8;
  for (const child of retainedChildren) {
    const childBytes = u8.slice(child.offset, child.offset + child.size);
    const childView = new DataView(childBytes.buffer);
    for (let i = 0; i <= childBytes.length - 8; i++) {
      const type = String.fromCharCode(childBytes[i + 4], childBytes[i + 5], childBytes[i + 6], childBytes[i + 7]);
      if (type === 'stco') {
        const count = childView.getUint32(i + 12);
        for (let j = 0; j < count; j++) {
          const offPos = i + 16 + j * 4;
          if (offPos + 4 <= childBytes.length) {
            const oldOff = childView.getUint32(offPos);
            if (oldOff > moovOffset) {
              childView.setUint32(offPos, oldOff - videoTrakSize);
            }
          }
        }
      }
    }
    newBuf.set(childBytes, writePos);
    writePos += child.size;
  }

  // 4. Copy trailing payload (mdat, etc.)
  newBuf.set(u8.subarray(moovEnd), writePos);

  return newBuf.buffer;
}
```

---

## 📋 Checklist for Any Mobile PWA Audio Implementation

- [ ] **Flight Recorder:** Installed before testing on physical devices (`flightRecorder.ts`).
- [ ] **Audio Output:** Native `<audio>` streams directly to hardware on mobile; WebAudio is restricted to desktop.
- [ ] **No Microtask Pause Loops:** Zero `elem.play()` invocations inside `onpause` listeners.
- [ ] **Container Sanitation:** ISO BMFF atom parser checks for `hdlr -> vide`; `stripVideoTrackFromMp4` runs in-memory before `URL.createObjectURL()`.
- [ ] **MediaSession Integration:** Lock screen metadata and action handlers (`play`, `pause`, `previoustrack`, `nexttrack`, `seekto`) populated.
- [ ] **Background Reflow Suppression:** DOM updates and visualizers frozen when `document.visibilityState === 'hidden'`.
- [ ] **Wake Lock Safety:** Screen wake lock acquired only during foreground viewing; released during background playback or on 15-minute timeout.
- [ ] **Non-Destructive Guarantee:** Never delete user audio files or drop DB records to handle codec/container quirks.
