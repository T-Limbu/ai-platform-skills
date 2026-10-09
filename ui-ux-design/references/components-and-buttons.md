# 📘 Components & Buttons Playbook

> Button geometry, icon harmony, ghost buttons, and container ergonomics.

---

## 🎥 Source: *Every UI/UX Concept Explained in Under 10 Minutes* (Kole Jain)

### 1. Concrete Mathematical Benchmarks
* **The 2x Button Proportions Rule:**
  * Target Button Width $\approx 2\times$ Button Height (e.g. 40px height with 80px+ horizontal padding span).
* **Icon Box Alignment:**
  * Icon box dimensions must strictly match the accompanying text line-height (e.g., 24px line-height $\rightarrow$ 24px icon frame).
* **Ghost Buttons for Secondary CTAs:**
  * Borderless transparent buttons with subtle hover fills (`hover:bg-white/[0.08]`) next to a solid primary button.

### 2. Code Presets
```html
<!-- Primary & Secondary (Ghost) Button Pair -->
<div class="flex items-center space-x-3">
  <!-- Primary Button (2x ratio, tactile active state) -->
  <button class="px-5 py-2.5 rounded-xl font-bold text-xs bg-sky-500 hover:bg-sky-400 active:scale-[0.97] text-slate-950 transition shadow-lg shadow-sky-500/20">
    Confirm Action
  </button>
  
  <!-- Secondary Ghost Button -->
  <button class="px-4 py-2.5 rounded-xl font-semibold text-xs text-slate-300 hover:text-white hover:bg-white/[0.06] active:scale-[0.97] transition">
    Cancel
  </button>
</div>
```

### 3. Anti-Patterns
* ❌ Square, squat buttons with equal height and width for text actions.
* ❌ Icons floating unaligned with text line-height.
