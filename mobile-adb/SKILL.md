---
name: mobile-adb
description: Mobile device diagnostics, Android Debug Bridge (ADB) automation, APK reverse engineering, and Web Bluetooth/device troubleshooting. Includes field-tested procedures and hardened rules from learnings.
---

# Mobile Diagnostics & ADB Skill

This skill provides standardized procedures, automation commands, and rules for interacting with connected mobile devices (Android/Samsung), diagnosing apps, and reverse engineering device protocols.

---

## 🛠️ Tool Group: Mobile & Device Engineering

| Tool | Purpose | Key Commands |
| :--- | :--- | :--- |
| **`adb`** | Android Debug Bridge for device control, logs, intents, packages | `adb devices`, `adb shell`, `adb pull/push`, `adb logcat` |
| **`jadx` / `apktool`** | APK decompiler and Smali/Java code extractor | `jadx -d out base.apk`, `apktool d app.apk` |
| **`Chrome DevTools Remote`** | Inspect webviews and mobile Chrome tabs over USB | `adb forward tcp:9222 localabstract:chrome_devtools_remote` |
| **Package Manager (`pm`)** | Inspect and grant runtime permissions | `adb shell pm grant <pkg> <perm>`, `adb shell pm path <pkg>` |
| **Activity Manager (`am`)** | Launch intents, broadcast receivers, and cold-starts | `adb shell am start -a android.intent.action.VIEW -d <url>` |

---

## 📋 Common Operational Runbooks

### 1. Reliable Screen Capture (Windows PowerShell Safe)
**Problem**: Redirecting `adb exec-out screencap -p > file.png` in PowerShell encodes binary data as UTF-16LE, corrupting the image.
**Solution**:
```powershell
# Safe two-step binary pull:
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png ./screen.png
```

### 2. Cold-Launching Web Pages in Mobile Chrome
When Chrome has open dialogs, bookmarks, or background tabs that prevent new URL intents from foregrounding:
```powershell
# Force-stop and cold-launch directly to the target URL
adb shell am force-stop com.android.chrome
adb shell am start -a android.intent.action.VIEW -d "https://your-url.com" -n com.android.chrome/com.google.android.apps.chrome.Main
```

### 3. Granting Web Bluetooth & Device Permissions
```powershell
# Turn Bluetooth ON
adb shell svc bluetooth enable

# Grant location & nearby device scanning to Chrome
adb shell pm grant com.android.chrome android.permission.ACCESS_FINE_LOCATION
adb shell pm grant com.android.chrome android.permission.BLUETOOTH_SCAN
adb shell pm grant com.android.chrome android.permission.BLUETOOTH_CONNECT
```

---

## 📚 Rules from Learning (Field-Hardened Guidelines)

1. **Rule [Binary Screencap Redirection]**: NEVER use `>` or `Set-Content` in PowerShell to capture `adb exec-out screencap`. Always write to `/sdcard/` on the device and use `adb pull` to ensure clean binary PNGs.
2. **Rule [Samsung Internet vs Chrome]**: Samsung Galaxy devices route external web links to Samsung Internet by default, which blocks Web Bluetooth. Any Web Bluetooth app on Android MUST be directed to Google Chrome.
3. **Rule [Device Lock Detection]**: Check `adb shell dumpsys trust` for `deviceLocked=1`. If locked by biometric/PIN, `wm dismiss-keyguard` cannot bypass security; prompt the user to unlock with their fingerprint/PIN.
4. **Rule [Single-File Self-Contained Mobile PWAs]**: Mobile browsers on sport courts or weak cellular networks can fail or hang when loading multi-file ES module imports. Always bundle core protocol drivers and UI into a single self-contained file with an offline-first service worker or local persistence.
5. **Rule [Continuous Rule Update]**: Every time an adb command fails or a mobile OS quirk is unblocked, document it immediately as a new rule in this file.
