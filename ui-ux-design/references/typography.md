# 📘 Typography & Font Sizing Playbook

> Distilled rules, mathematical formulas, and scale constraints for text hierarchy.

---

## 🎥 Source: *Every UI/UX Concept Explained in Under 10 Minutes* (Kole Jain)

### 1. Concrete Mathematical Benchmarks
* **The "Pro Heading" Typography Formula:**
  * **Tracking / Letter-spacing:** **`-2%` to `-3%`** (`tracking-tight` or `-0.025em`).
  * **Line-height:** **`110%` to `120%`** (`leading-tight` or `leading-none`).
  * *Why:* Large display fonts default to loose spacing. Negative tracking tightens the visual rhythm, making headlines look crisp and editorial.
* **The Single-Font Rule:**
  * 99% of digital interfaces need only **ONE** high-quality sans-serif font family (Inter, Plus Jakarta Sans, SF Pro, Geist). Never mix 3+ fonts without brand justification.
* **Scale Constraints & Information Density:**
  * **Websites & Landing Pages:** Maximum **6 distinct font sizes** across the entire page.
  * **Dashboards & Tools:** Cap primary headers at $\le 24$px (`text-xl`) to maximize information density without awkward whitespace gaps.

### 2. Code Presets
```html
<!-- Large Pro Heading -->
<h1 class="text-3xl md:text-5xl font-extrabold tracking-[-0.03em] leading-[1.15] text-white">
  Editorial Headline
</h1>

<!-- Dashboard Dense Label -->
<div class="text-xs font-semibold text-slate-400 uppercase tracking-wider">
  Metric Name
</div>
```

### 3. Anti-Patterns
* ❌ Leaving large headers with default `letter-spacing: normal` (looks amateur and loose).
* ❌ Using 8+ different font sizes on a single screen.
