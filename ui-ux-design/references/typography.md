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


---

## 🎥 Reference: YouTube Video (EcbgbKtOELY) (`EcbgbKtOELY`)

# Typography & Density Architecture

### Source: YouTube Video (EcbgbKtOELY)

### Concrete Rules & Mathematical Principles
- **Single Sans-Serif Rule**: Standardize on a single, clean sans-serif typeface (e.g., Inter, SF Pro, Geist) across the entire interface. Avoid multi-font complexity.
- **Display Tightening Formula (Headlines)**:
  - **Tracking / Letter-spacing**: Tighten large display text by `-2%` to `-3%` (`letter-spacing: -0.02em` to `-0.03em`).
  - **Leading / Line-height**: Compress large text line-height down to `110%`–`120%` (`line-height: 1.1` to `1.2`). This eliminates loose optical gaps.
- **Scale Ceilings by Context**:
  - **Websites & Landing Pages**: Cap size ramps at a maximum of 6 distinct font sizes; allow wide scale ranges (e.g., 14px body up to 64px+ hero).
  - **High-Density Dashboards / Productivity Apps**: Compress the entire font scale ceiling. Typography rarely exceeds `24px` to maintain strict spatial information density.

### Anti-Patterns
- **Font Multiplicity**: Mixing three or more typefaces across marketing and application chrome.
- **Default Heading Tracking**: Leaving headlines at `letter-spacing: 0` or positive tracking with loose line-heights (`1.4`+), creating fragmented, amateur headers.

### Implementation Specs
```css
/* Display Headline Preset */
.heading-display {
  font-family: -apple-system, BlinkMacSystemFont, "Inter", sans-serif;
  font-size: clamp(2rem, 5vw, 3.5rem);
  font-weight: 700;
  line-height: 1.15; /* 115% */
  letter-spacing: -0.025em; /* -2.5% optical compression */
}

/* High-Density Dashboard Typography Scale */
:root {
  --text-caption: 11px;
  --text-sm: 12px;
  --text-base: 13px;
  --text-md: 14px;
  --text-lg: 16px;
  --text-xl: 18px;
  --text-max-dashboard: 24px; /* Strict upper bound */
}
```
