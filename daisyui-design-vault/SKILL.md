---
name: daisyui-design-vault
description: Use when building or changing UI with daisyUI v5 or v4 or Tailwind CSS, creating a dashboard, landing page, store, auth or docs layout, choosing or switching daisyUI themes, or refining an existing daisyUI layout. Holds the 68-component catalog, blueprints of the official daisyUI store templates, theme tokens and anti-slop rules.
version: 0.1.0
---

# 🎨 daisyUI Design Vault Skill

The definitive knowledge base, layout synthesis engine, and visual design reference for **daisyUI v5 / v4** within the Antigravity AI Data Squad.

Grounds coding agents in real-world, shipped design systems from the **official daisyUI Store** (`daisyui.com/store/`) and provides instant access to all **68 official components**, semantic color rules, and procedural layout generation.

---

## 🏛️ When to Use This Skill

* Whenever designing, generating, or modifying web/mobile interfaces using **daisyUI** or **Tailwind CSS**.
* Whenever asked to create a new UI template, landing page, dashboard, e-commerce store, auth flow, or documentation layout.
* Whenever asked to **randomly generate** an interface based on best design practices.
* Whenever the Stakeholder asks to **adjust, refine, or tweak** an existing UI layout via prompt instructions.
* Whenever exporting interactive UI templates with screenshot snapshots into **Design Vault**.

---

## 📚 Essential References

| Topic | Reference Document | Key Content |
|---|---|---|
| **All 68 Components** | [references/components-68-catalog.md](./references/components-68-catalog.md) | Full taxonomy (Actions, Navigation, Display, Inputs, Mockups, Feedback) with classes & modifiers. |
| **Store Blueprints** | [references/store-templates-blueprints.md](./references/store-templates-blueprints.md) | Architectural breakdowns of Nexus Dashboard, Scalo, Auth, Store, Docs, Mobile Landing, Charts. |
| **Themes & Tokens** | [references/themes-and-styling.md](./references/themes-and-styling.md) | 35 themes, semantic color roles (`primary`, `base-100/200/300`), anti-AI-slop rules. |
| **Generation Engine** | [references/procedural-generation-engine.md](./references/procedural-generation-engine.md) | Algorithms for procedural random template generation and prompt-guided mutations. |

---

## 🧭 Core Archetypes & Composition Rules

### 1. Admin & Operations Dashboard (`Nexus` archetype)
* **Shell**: Persistent sidebar `<div class="drawer lg:drawer-open">` + sticky top `<div class="navbar">` with global search `<kbd>⌘K</kbd>` and theme dropdown.
* **Metrics**: 4-column cluster using `<div class="stats">` with `<div class="stat-figure radial-progress">`, bold tabular numerals, and percentage badges.
* **Data Layer**: High-density `<table class="table table-zebra table-pin-rows">` with row checkboxes, user avatars, and status badges.

### 2. SaaS Marketing & Conversion (`Scalo` archetype)
* **Hero**: Dynamic pill badge (`badge-primary badge-outline`), high-contrast title, dual CTAs, trust avatar pile + star rating, framed in a `mockup-browser` or `mockup-window`.
* **Social Proof**: Grayscale client logo cloud.
* **Features**: Asymmetrical Bento Grid with `card bg-base-200/60` and `hover-3d`.
* **Pricing**: Monthly/Annual `toggle` with 3-tier card layout; middle card highlighted with `border-primary` and `aura`.
* **FAQ**: Clean `<div class="join join-vertical">` with `<div class="collapse collapse-plus join-item">`.

### 3. E-Commerce Storefront (`Online Store` archetype)
* **Catalog**: 4-column responsive grid featuring `card bg-base-100 card-compact`.
* **Product Detail**: `<div class="hover-gallery">` for instant multi-angle previews without reloading.
* **Faceted Filters**: Price range slider using `range range-primary`, brand checkboxes, and size filter chips.
* **Cart**: Slide-out drawer or modal with stepper controls (`join` with `-`, count, `+`).

### 4. Authentication Suite (`Auth 2.0` archetype)
* **Layout**: Split-screen canvas with brand visual art on left and centered auth card on right.
* **Inputs**: Modern `fieldset` containers with `fieldset-legend`, floating labels, and HTML5 `validator`.
* **2FA**: Dedicated 6-digit `otp` boxes with countdown resend timer.

### 5. Developer Documentation (`Docs` archetype)
* **Layout**: 3-column desktop layout (Left `menu` hierarchy, Center `prose` article, Right table-of-contents).
* **Code Sandbox**: High-density `<div class="mockup-code">` with terminal prompt styling.
* **Diff Viewer**: Visual side-by-side `<div class="diff">` proving migrations or feature differences.

---

## 🎨 Theme Matrix (35 Built-in Themes)

Apply via `<html data-theme="[name]">`:

* **Clean / Modern Light**: `light`, `corporate`, `nord`, `winter`, `silk`
* **High-Contrast Dark**: `dark`, `night`, `dim`, `black`, `abyss`
* **Vibrant / Cyberpunk**: `cyberpunk`, `synthwave`, `acid`, `luxury`
* **Warm / Earthy**: `coffee`, `retro`, `autumn`, `forest`, `caramellatte`
* **Playful / Pastel**: `cupcake`, `bumblebee`, `pastel`, `valentine`, `lemonade`
* **Minimalist / Tech**: `lofi`, `wireframe`, `dracula`, `cmyk`, `sunset`, `aqua`, `fantasy`, `garden`

---

## 🛡️ Anti-AI-Slop Golden Rules

1. **Strictly Zero Hardcoded Colors**: Always use semantic tokens (`bg-primary`, `text-primary-content`, `bg-base-100`, `bg-base-200`, `border-base-300`). Never hardcode hex codes or raw Tailwind palettes (`bg-blue-600`).
2. **Ground All Elevated Surfaces**: Use subtle borders (`border border-base-200` or `border border-base-300/60`) on cards and dialogs.
3. **Single Primary Action per Viewport**: Do not compete for visual attention; exactly one `btn-primary` per section.
4. **Interactive States Mandatory**: All buttons, cards, and links must have explicit hover and active micro-interactions.
5. **Tabular Numerals**: Wrap numbers in `font-mono tracking-tight` inside stats, meters, and tables.

---

## ⚡ Interactive Studio & Generation Workflow

When generating or tweaking templates:
1. Synthesize the clean, standalone HTML document using the standard template envelope.
2. Ensure responsive viewports (`desktop`, `tablet`, `mobile`).
3. If inside Design Vault, utilize the interactive studio at `/studio` (or `/daisyui-studio`) or call the generator API (`/api/daisyui/generate`) to preview live and snapshot screens into the Design Vault reference gallery!

---

## 🌐 Autonomous "Inspire & Synthesize" Pipeline

Pass any target URL (e.g. `linear.app`, `stripe.com`, `spotify.com`) or design description:
1. **Intake & Crawl**: Playwright crawls the URL, captures high-res snapshots, and Pillow extracts the dominant color palette into `color_palette`.
2. **Palette & Mood Extraction**: Automatically maps dominant luminance and chroma into the best-fitting daisyUI theme (`dark`, `synthwave`, `forest`, `luxury`, `light`).
3. **Archetype Inference**: Inters domain and keywords into layout blueprints (e.g., developer issue tracker -> Admin Dashboard with pinned tables and `kbd`; e-commerce -> Online Store with `hover-gallery` and `range` filters).
4. **Synthesis & Vault Archiving**: Generates the complete, zero-slop, responsive HTML template and links it to the original inspiration screenshot in Design Vault!

