# 📘 Color & Dark Mode Engineering Playbook

> Surface elevation scales, palette ramps, semantic purpose, and dark mode mechanics.

---

## 🎥 Source: *Every UI/UX Concept Explained in Under 10 Minutes* (Kole Jain)

### 1. Concrete Mathematical Benchmarks
* **The Dark Mode Surface Elevation Hierarchy (Zero Drop Shadows):**
  * Drop shadows do not render against dark backgrounds. Elevation is achieved purely through **surface lightness increments**:
    * **Canvas Background:** Deepest base (`#090D14` / `#0B0E14`)
    * **Level 1 (Cards, Panels):** Slightly lighter (`#111827` / `#151D2A`)
    * **Level 2 (Modals, Popovers, Dropdowns):** Even lighter (`#162032` / `#1C2638`)
* **Subtle Low-Opacity Borders:**
  * Use `border-white/[0.08]` or `border-slate-800`. Never use stark white lines.
* **Semantic Color Architecture (Purpose over Decoration):**
  * **Blue / Slate:** Informational, neutral actions, structural pills.
  * **Green:** Success, verified completion, active states.
  * **Yellow / Amber:** Warnings, caution, temporary alerts.
  * **Red:** Danger, destructive actions, validation errors.
* **Badge Saturation Guard:**
  * Lower saturation on dark mode chip fills to prevent eye vibration; keep text high-contrast and legible.

### 2. Code Presets
```html
<!-- Base Obsidian Canvas -->
<body class="bg-[#090D14] text-slate-100 min-h-screen">
  <!-- Level 1 Card -->
  <div class="bg-[#111827] border border-white/[0.08] rounded-2xl p-6">
    <!-- Level 2 Modal -->
    <div class="bg-[#162032] border border-white/[0.12] rounded-xl p-4"></div>
  </div>
</body>
```

### 3. Anti-Patterns
* ❌ Adding heavy dark drop shadows to cards in dark mode (invisible against dark backgrounds).
* ❌ Using pure `#000000` void black without rich tinting (deep slate/navy).
* ❌ Using bright neon solid fills for small badges.
