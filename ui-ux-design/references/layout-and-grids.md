# 📘 Layout, Grids & Spacing Playbook

> Mathematical spacing systems, whitespace harmony, and responsive layouts.

---

## 🎥 Source: *Every UI/UX Concept Explained in Under 10 Minutes* (Kole Jain)

### 1. Concrete Mathematical Benchmarks
* **The 4-Point Grid Rule:**
  * All padding, margins, gaps, and heights must be clean multiples of 4:
    `4px`, `8px`, `12px`, `16px`, `20px`, `24px`, `32px`, `48px`, `64px`.
  * *Why:* Allows mathematical halving across all screen resolutions and retina densities ($1\times, 2\times, 3\times$).
* **Whitespace > Grid Rigidity:**
  * Content needs breathing room. Rather than rigidly snapping every hero section to a 12-column grid, use generous section padding (`p-6` to `p-8`) and tightly coupled gaps (`gap-1.5` to `gap-2`).
* **Responsive Column Conventions:**
  * Desktop: 12 columns
  * Tablet: 8 columns
  * Mobile: 4 columns

### 2. Code Presets
```html
<!-- Harmonized 4pt Section Container -->
<section class="max-w-7xl mx-auto px-6 py-8 space-y-6">
  <div class="flex items-center gap-4">
    <!-- Items separated by 16px (multiple of 4) -->
  </div>
</section>
```

### 3. Anti-Patterns
* ❌ Using odd pixel values (`13px`, `17px`, `23px`) that break responsive scaling.
* ❌ Cramming elements against borders without breathing room.
