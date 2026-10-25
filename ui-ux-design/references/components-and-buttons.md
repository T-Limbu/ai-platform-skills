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


---

## 🎥 Reference: YouTube Video (EcbgbKtOELY) (`EcbgbKtOELY`)

# Button Architecture & Icon Alignment

### Source: YouTube Video (EcbgbKtOELY)

### Concrete Rules & Mathematical Principles
- **The Line-Height Icon Sizing Rule**: Normalize icon dimensions precisely to the typography's `line-height` value. If body/button text uses a font size of `14px` with a line-height of `24px`, configure icon bounding boxes to exactly `24×24px`. This prevents vertical baseline jitter.
- **Button Aspect Padding Ratio ($2H = W$ Rule-of-Thumb)**:
  - Approximate horizontal padding by doubling vertical spatial dimensions (`padding: 10px 20px` or `padding: 12px 24px`), maintaining stable horizontal visual mass.
- **Ghost Button Mechanics**: Sidebar navigation elements and secondary actions are ghost buttons (background-free buttons that only reveal borders or fills upon hover/focus). Pair primary solid CTAs with ghost buttons for clean visual weighting.

### Anti-Patterns
- **Oversized Icon Clutter**: Using 32px icons beside 16px text without normalizing bounding boxes, creating top-heavy alignment.
- **Competing Dual Primaries**: Placing two solid-filled high-contrast buttons directly adjacent to each other.

### Implementation Specs
```css
/* Standard Button Token Base */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 40px;
  padding: 0 20px; /* 2:1 width-to-height distribution ratio */
  font-size: 14px;
  line-height: 20px;
  border-radius: 6px;
  transition: all 120ms ease-in-out;
}

.btn-icon {
  width: 20px;  /* Locked precisely to line-height */
  height: 20px;
  flex-shrink: 0;
}

.btn-ghost {
  background: transparent;
  color: var(--text-secondary);
}
.btn-ghost:hover {
  background: var(--surface-hover);
  color: var(--text-primary);
}
```
