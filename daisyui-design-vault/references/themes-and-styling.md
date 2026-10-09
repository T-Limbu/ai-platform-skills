# daisyUI Themes, Semantic Color Tokens & Anti-AI-Slop Styling

Complete rules for color semantics, theme switching, contrast hierarchies, and avoiding common AI generation traps.

---

## 1. The 35 Official daisyUI Themes

daisyUI provides 35 out-of-the-box themes toggled via `<html data-theme="[name]">`. Each theme automatically defines the complete CSS custom property set for semantic surfaces and text colors.

| Theme Category | Theme Names | Recommended Archetypes |
|---|---|---|
| **Clean / Modern Light** | `light`, `corporate`, `nord`, `winter`, `silk` | Enterprise SaaS, Admin Dashboards, Legal / B2B |
| **Sleek / High-Contrast Dark** | `dark`, `night`, `dim`, `black`, `abyss` | Developer Tools, SRE Dashboards, Web3 / Crypto |
| **Vibrant / Cyberpunk** | `cyberpunk`, `synthwave`, `acid`, `luxury` | Gaming, Web3, Creative Portfolios |
| **Warm / Earthy / Editorial** | `coffee`, `retro`, `autumn`, `forest`, `caramellatte` | Cafes, Publications, Blogs, Lifestyle E-commerce |
| **Playful / Pastel / Soft** | `cupcake`, `bumblebee`, `pastel`, `valentine`, `lemonade` | Social Apps, Creative Agencies, Wellness / Health |
| **Minimalist / Tech** | `lofi`, `wireframe`, `dracula`, `cmyk`, `sunset`, `aqua`, `fantasy`, `garden` | Prototyping, Technical Documentation, Utilities |

---

## 2. Semantic Color Rules (Zero Hardcoded Hex Codes)

### The Semantic Palette Hierarchy
Never use hardcoded Tailwind colors like `bg-blue-600` or `text-gray-900` when building with daisyUI. Always use daisyUI semantic variables:

1. **Brand Roles**:
   * `primary` / `primary-content`: Primary actions, core branding accents.
   * `secondary` / `secondary-content`: Supporting highlights, badges, complementary actions.
   * `accent` / `accent-content`: Eye-catching focal points, notification badges, hero highlights.
   * `neutral` / `neutral-content`: High-contrast framing, terminal blocks, footers, code mockups.
2. **Surface Elevations**:
   * `bg-base-100`: Canvas background (page level).
   * `bg-base-200`: Card surfaces, input backgrounds, sidebar panels.
   * `bg-base-300`: Borders, dividers, nested card highlights, table header rows.
   * `text-base-content`: Default readable text (automatically contrasts with base-100).
   * `text-base-content/60` or `/70`: Secondary muted captions and helper notes.
3. **Status Indicators**:
   * `info` / `info-content`: Informational alerts, system status.
   * `success` / `success-content`: Confirmations, positive growth percentages, checkmarks.
   * `warning` / `warning-content`: Cautionary alerts, pending reviews.
   * `error` / `error-content`: Destructive actions, validation errors, critical drops.

---

## 3. Anti-AI-Slop Design Guardrails

To prevent typical generative AI styling mistakes:

1. **Never Float Untethered Cards**:
   * AI mistake: Placing pure white cards on light gray backgrounds with huge blurred drop-shadows.
   * DaisyUI standard: Ground cards with subtle borders (`border border-base-200` or `border border-base-300/60`) and use `bg-base-100` on a `bg-base-200` canvas.
2. **Never Clutter Button Variants**:
   * AI mistake: Every button has a different loud gradient.
   * DaisyUI standard: Exactly **one** `btn-primary` per viewport section. Secondary actions must use `btn-outline` or `btn-ghost`.
3. **Respect 4-Point Spacing Rhythm**:
   * Use Tailwind's 4-point spacing scale (`p-4`, `p-6`, `p-8`, `p-12`, `gap-3`, `gap-6`, `space-y-4`). Avoid arbitrary pixels like `p-[17px]`.
4. **Use Tabular Typography for Metrics**:
   * Any metric numbers inside `stat-value` or `table` must use `font-mono tracking-tight` or bold numerals to prevent jitter on counter updates.
5. **Interactive Feedback Is Mandatory**:
   * Every clickable element must specify hover/active states (`hover:bg-primary-focus`, `active:scale-98`, `transition-all`).
