# 📘 Visual Hierarchy And Signifiers Playbook



---

## 🎥 Reference: YouTube Video (EcbgbKtOELY) (`EcbgbKtOELY`)

# Visual Hierarchy & Affordance Signifiers

### Source: YouTube Video (EcbgbKtOELY)

### Concrete Rules & Mathematical Principles
- **Container Boundary Affinity**: Enclosing related items within an explicit bounding surface or border automatically signals semantic grouping (Law of Common Region). In a set of $N$ items, wrapping $k$ items creates an immediate parent-child cluster without textual explanation.
- **The Contrast Triad (Size, Position, Color)**:
  - **Size**: Primary focal items must dominate typographic scale (e.g., entity titles in bold text at ≥20px) compared to secondary metadata (e.g., timestamp/date at ≤14px regular).
  - **Position**: Place the highest cognitive priority content at the top-left (for LTR systems). Anchor secondary anchor metrics (such as financial transactions or item cost) at the top-right aligned axis.
  - **Color**: Semantic chromatic accents (e.g., `#0066FF` for price or active link) pull fixation vectors away from monochromatic body text.
- **Implicit Vector Signification**: Use directional icons (e.g., origin point $\rightarrow$ arrow $\rightarrow$ destination point) and horizontal line dividers to signify transit or state change over explicit text labels like "From: / To:".
- **Affordance Signaling via Text Attenuation**: Inactive items require text opacity reduction (typically 40–50% opacity or disabled grey tones) to intuitively communicate non-interactivity.

### Anti-Patterns
- **Spreadsheet UI Syndrome**: Flattening card metadata into equal-weight rows with identical font size, weight, and color, stripping visual landmarks.
- **Instructional Crutches**: Adding instructional helper text for behaviors that standard affordances (selected states, containers, press feedback) should convey intrinsically.

### Implementation Specs
```css
/* Top-Right Semantic Price Anchor */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.card-title {
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--text-primary);
}
.card-price {
  font-size: 1rem;
  font-weight: 600;
  color: var(--brand-accent);
  text-align: right;
}

/* Inactive / Disabled Affordance */
.interactive-item[aria-disabled="true"] {
  opacity: 0.45;
  pointer-events: none;
  cursor: not-allowed;
}
```
