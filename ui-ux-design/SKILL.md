---
name: ui-ux-design
description: Use when designing, building or reviewing any web or mobile UI, including spacing, typography, color, dark mode, buttons, interaction states, overlays or battery-frugal background behavior. Holds the 12 UI/UX laws (4-point grid, dark-mode surface elevation, mandatory hover, active and disabled states) and a pre-done checklist.
version: 0.1.0
---

# 🎨 UI/UX Design System & Craft Standard

This skill codifies the core design fundamentals that separate amateur interfaces from world-class, production-ready product applications (inspired by Mobbin, Apple, Linear, and Stripe). **Every frontend component and screen built by the AI Data Squad must adhere to these laws.**

---

## 🏛️ The 12 Inviolable Laws of UI/UX Craft

### 1. Affordances & Signifiers (Zero Manuals Required)
* **Principle:** Users must instinctively understand what an interface does without reading instructions.
* **Containers create relationships:** Grouping items inside a border/card instantly signals they belong together; items outside are separate.
* **Visual clues:**
  * Active/selected containers must visibly distinguish themselves (e.g. solid border, subtle background tint, or accent pill).
  * Disabled items must have lowered opacity (`opacity-40` or grayed-out text) and `cursor-not-allowed` to signal they cannot be clicked.
  * Interactive elements require cursor pointers and hover/press feedback.

---

### 2. Visual Hierarchy & Contrast
* **Principle:** Raw data presented uniformly looks like a spreadsheet. Hierarchy guides the human eye through contrast.
* **The 4 Levers:**
  1. **Position:** Critical content lives at the top; secondary metadata (timestamps, IDs) lives at the bottom.
  2. **Size:** Primary titles must be noticeably larger than body copy.
  3. **Weight & Color:** Differentiating values (e.g. Price, Status Pill) should be right-aligned or highlighted with accent color.
  4. **Visual Shorthand:** Use connecting lines, progress dots, and icons to depict flow (e.g., origin $\rightarrow$ destination) instead of verbose text.

---

### 3. The 4-Point Grid & Whitespace
* **The 4-Point Spacing Rule:** All padding, margins, gaps, and heights must be clean multiples of 4:
  `4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`, `40px`, `48px`, `64px`.
  * *Why:* Cleanly divides in half across all device pixel densities ($1\times, 2\times, 3\times$).
* **Whitespace > Grid Stiffness:** Content needs breathing room. Rather than cramming elements against borders, let sections breathe with generous padding (`p-6` to `p-8`). Group tightly coupled items (label + input) with smaller gaps (`gap-1.5` to `gap-2`).

---

### 4. Typography & The "Pro Heading" Rules
* **Rule of One:** 99% of apps need exactly **ONE** high-quality sans-serif font family (Inter, Plus Jakarta Sans, SF Pro, Geist). Never mix 3+ fonts.
* **The Large Heading "Pro Hack":**
  * Tighten letter-spacing (tracking): `-0.02em` to `-0.03em` (`tracking-tight` or `tracking-tighter`).
  * Drop line-height: `110%` to `120%` (`leading-tight` or `leading-none`).
  * *Result:* Immediately eliminates amateur visual looseness and gives large text a crisp, premium editorial finish.
* **Scale Limits:**
  * Landing pages: Max 6 font sizes.
  * High-density dashboards & tools: Cap primary headers under `24px` (`text-xl` to `text-2xl`) to maintain information density.

---

### 5. Semantic Color Architecture
* **Rule of Primary:** Start with **ONE** primary brand color.
  * Lighten it for subtle surface backgrounds (`bg-brand-50` or `bg-brand-950/40`).
  * Darken/saturate it for readable accents and text badges.
* **Semantic Colors are for PURPOSE, not decoration:**
  * 🔵 **Blue / Slate:** Informational, neutral actions, structure.
  * 🟢 **Green:** Success, active states, verified completion.
  * 🟡 **Yellow / Amber:** Warnings, caution, temporary alerts.
  * 🔴 **Red:** Danger, destructive actions, validation errors.
* **Never use arbitrary rainbow colors** across components without semantic justification.

---

### 6. Dark Mode Engineering
* **No Drop Shadows for Elevation:** Drop shadows vanish against dark canvases. In dark mode, **elevation is created purely through surface lightness**:
  * Canvas Background: Deepest base (`#0B0E14` or `#0F172A`)
  * Level 1 (Cards, Panels): Slightly lighter (`#151D2A` or `#1E293B`)
  * Level 2 (Modals, Popovers, Dropdowns): Even lighter (`#1C2638` or `#334155`)
* **Subtle Borders:** Never use stark white lines. Use low-opacity borders: `border-white/[0.08]` or `border-slate-800`.
* **Desaturate Badges:** High-saturation neon chips cause eye fatigue. Lower saturation and brightness on badge backgrounds, keeping text crisp.
* **Tinting over Void Black:** Avoid flat `#000000`. Use deep rich slate, zinc, or midnight navy tints.

---

### 7. Soft Shadows & Ambient Depth (Light Mode)
* **Softness over Opacity:** Harsh dark shadows look amateur. Dial down opacity (`opacity-5` to `opacity-15`) and dial up blur radius (`blur-md` to `blur-2xl`).
* **Elevation Hierarchy:** Flat cards require minimal subtle shadows; floating dropdowns and modals need deeper ambient spread.
* **The Shadow Law:** *"If the shadow is the first thing you notice on a card, it is set too strong."*

---

### 8. Button & Icon Ergonomics
* **The 2x Button Ratio:** A well-proportioned button generally has **width $\approx 2\times$ height** (e.g. 40px height with 80px+ horizontal padding span).
* **Ghost Buttons:** Use borderless transparent buttons with subtle hover fills (`hover:bg-white/10`) for secondary actions next to a solid primary CTA.
* **Icon Harmony:** Match icon frame dimensions to the font line-height (e.g. 16px font $\rightarrow$ 16-20px icon; 24px heading $\rightarrow$ 24px icon).

---

### 9. The Mandatory 4 Interaction States
Every interactive element **must** implement these 4 visual states:
1. **`Default`**: Clean, resting state.
2. **`Hover`**: Visual elevation, brightness bump, or subtle border tint.
3. **`Active / Pressed`**: Tactile feedback (e.g. `scale-[0.98]`, slight darkening).
4. **`Disabled`**: Lower opacity (`opacity-40`), grayed text, `pointer-events-none`.
5. *(Bonus) `Loading`*: Spinner replaces text, preserving exact button dimensions.
* **Inputs:** Must feature an accessible `focus-visible:ring-2 ring-brand-500` ring, plus red borders and microcopy for errors.

---

### 10. Purposeful Micro-Interactions
* **Feedback with Delight:** Confirm user actions with motion.
  * Copying text? Animate a toast badge sliding up (`translate-y-0 opacity-100`).
  * Toggling a switch? Smooth spring transition (`transition-all duration-200 ease-out`).
  * Hovering a gallery card? Subtle zoom (`scale-[1.02]`) and border glow.

---

### 11. Overlays & Progressive Blur
* **Never slap opaque black rectangles over hero images.**
* **The Gradient Rule:** Use a linear gradient (`bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent`) so images fade smoothly into readable text.
* **Modern Polish:** Add backdrop blur (`backdrop-blur-md` or `backdrop-blur-xl`) behind modals and floating navbars for an authentic high-end glassmorphic feel.

---

### 12. Mobile Ergonomics & Battery Frugality
* **Principle:** A beautiful UI that burns 20% battery in 15 minutes in a background mobile browser tab is a defective UI. Premium craft includes energy efficiency.
* **The 4 Rules of Battery Frugality:**
  1. **Listen to Visibility:** Always attach `document.addEventListener('visibilitychange', ...)` to suspend polling, canvas/GPU animations, and non-essential WebSockets when the tab is hidden.
  2. **Zero DOM Thrash in Background:** When playing background audio or running background jobs, stop updating on-screen UI components (progress bars, counters, canvas visualizers). Rely solely on the native OS Media Session API.
  3. **Auto-Expiring Wake Locks:** Never hold `navigator.wakeLock` without a strict timeout (maximum 15m safety timer). Always catch and handle wake lock release events gracefully.
  4. **Smooth Foreground Resumption:** When returning to the foreground, trigger a single idempotent state reconciliation sync rather than a flood of stacked queued events.

---

## 🛠️ Quick Implementation Checklist for Developers

Before marking any UI code "Done", verify:
- [ ] Are headings tightened with negative tracking (`-0.02em`) and tight leading?
- [ ] Does spacing strictly obey the 4-point scale (4, 8, 12, 16, 24, 32px)?
- [ ] In dark mode, is elevation indicated by lighter surface fills rather than black shadows?
- [ ] Does every button have Hover, Active (`scale-98`), and Disabled states?
- [ ] Are input focus rings distinct and accessible?
- [ ] Is image text readable via progressive gradients rather than muddy overlays?
- [ ] Does mobile UI respect visibility states, pausing background timers and unneeded DOM reflows?
