# Procedural Template Generation & Iterative Adjustment Engine

Rules and algorithms for procedurally generating balanced, responsive daisyUI templates from scratch, randomly, or guided by natural language Stakeholder descriptions.

---

## 1. The Archetype Synthesis Formula

When generating a template, determine:
1. **Archetype Persona**:
   * `saas_landing`: Growth-focused, social proof, bento grid, pricing toggle, conversion CTA.
   * `admin_dashboard`: Dense information architecture, drawer sidebar, KPI stats, charts, tables.
   * `online_store`: E-commerce catalog, faceted filters, hover-galleries, cart drawer, checkout modal.
   * `auth_portal`: Split-screen layout, social OAuth, form validation, 2FA/OTP inputs.
   * `dev_docs`: Three-column developer reference, code mockups, API tables, diff comparisons.
   * `mobile_showcase`: Centered phone mockup with active screen, feature callouts, app store badges.
   * `analytics_charts`: Multi-card KPI dashboard with radial progress gauges, trend tables, and sparklines.
   * `portfolio_blog`: Clean editorial grid with article cards, author avatars, tag filter chips.
2. **Theme Pairing**:
   * Select a theme fitting the tone (e.g. Web3/Tech -> `dark`, `abyss`, `synthwave`; Lifestyle/Eco -> `forest`, `cupcake`, `autumn`; Corporate -> `corporate`, `nord`).
3. **Component Palette**:
   * Pick 6-12 complementary daisyUI components from the 68 catalog.
   * Ensure balance: 1 Shell navigation, 1 Primary focal hero/display, 2 Content/Data modules, 1 Interactive control/feedback module, 1 Footer/Closing.

---

## 2. Prompt-Guided Adjustment Algorithm

When the Stakeholder asks to adjust or tweak an existing template:

| User Request | Action Taken by Agent / Generator |
|---|---|
| *"Make it darker / techy"* | Switch theme to `dark`, `night`, `abyss`, or `cyberpunk`. Add subtle glowing `aura` around primary CTA. |
| *"Add pricing options"* | Insert a 3-tier pricing card section with a monthly/annual `toggle` and `badge-primary` on the recommended plan. |
| *"Add customer reviews"* | Insert a testimonial carousel or 3-column card grid with `avatar` and `rating rating-sm`. |
| *"Make it an analytics dashboard instead"* | Replace hero with `stats` 4-column cluster, add `table table-zebra`, and insert `radial-progress` KPI cards. |
| *"Add 2FA or login"* | Integrate split-screen auth modal or dedicated OTP component section with `countdown`. |
| *"Show mobile view"* | Wrap content in `mockup-phone` with bottom `dock` navigation bar. |

---

## 3. Standalone HTML Contract

Every generated template must be self-contained and immediately renderable in any browser or iframe without complex build steps:
```html
<!DOCTYPE html>
<html lang="en" data-theme="[THEME_NAME]">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Template Title]</title>
  <!-- Tailwind CSS & daisyUI CDN -->
  <link href="https://cdn.jsdelivr.net/npm/daisyui@latest/dist/full.min.css" rel="stylesheet" type="text/css" />
  <script src="https://cdn.tailwindcss.com"></script>
  <!-- Fonts & Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
    code, pre, .font-mono { font-family: 'JetBrains Mono', monospace; }
  </style>
</head>
<body class="bg-base-100 text-base-content min-h-screen">
  <!-- Template Content -->
</body>
</html>
```
