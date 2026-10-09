# daisyUI 68 Components — Complete Master Catalog

Reference of all 68 official daisyUI components categorized by functional taxonomy, semantic utility, classes, and pairings.

---

## 1. Actions & Interactive Triggers

| Component | Base Class | Key Modifiers / Variants | Common Pairings |
|---|---|---|---|
| **Button** | `btn` | `btn-primary`, `btn-secondary`, `btn-accent`, `btn-neutral`, `btn-outline`, `btn-ghost`, `btn-link`, `btn-xs`, `btn-sm`, `btn-lg`, `btn-circle`, `btn-square`, `btn-wide`, `btn-block` | `loading`, `badge`, `dropdown` |
| **Dropdown** | `dropdown` | `dropdown-end`, `dropdown-top`, `dropdown-bottom`, `dropdown-left`, `dropdown-right`, `dropdown-hover`, `dropdown-open` | `btn`, `menu`, `card` |
| **Swap** | `swap` | `swap-rotate`, `swap-flip`, `swap-active` | `swap-on`, `swap-off`, `swap-indeterminate` (icons) |
| **Theme Controller** | `theme-controller` | Used on `input type="checkbox"`, `input type="radio"`, or `btn` with `value="[theme-name]"` | `toggle`, `swap`, `dropdown` |
| **FAB (Floating Action Button)** | `fab` | `fab-flower`, `fab-vertical` | Fixed position container, icons, tooltips |

---

## 2. Navigation & Wayfinding

| Component | Base Class | Key Modifiers / Variants | Common Pairings |
|---|---|---|---|
| **Navbar** | `navbar` | `navbar-start`, `navbar-center`, `navbar-end` | `dropdown`, `btn`, `avatar`, `indicator` |
| **Menu** | `menu` | `menu-horizontal`, `menu-vertical`, `menu-xs`, `menu-sm`, `menu-lg`, `menu-title` | `drawer`, `sidebar`, `dropdown` |
| **Megamenu** | `megamenu` | Popover horizontal navigation for enterprise layouts | `navbar`, `card`, `list` |
| **Drawer (Sidebar)** | `drawer` | `drawer-toggle`, `drawer-content`, `drawer-side`, `drawer-overlay`, `drawer-end` | `menu`, `navbar`, `stat` |
| **Dock (Bottom App Bar)** | `dock` | Stamped bottom navigation for mobile viewports | Icons, badges, active indicator |
| **Breadcrumbs** | `breadcrumbs` | `ul > li > a` auto slash separation | Page headers, docs navigation |
| **Tabs** | `tabs` | `tabs-box`, `tabs-border`, `tabs-lift`, `tab-active`, `tabs-xs/sm/lg` | Filter bars, view switchers |
| **Pagination** | `pagination` | Often built using `join > btn` or `btn-group` | Tables, catalog grids |
| **Steps** | `steps` | `steps-vertical`, `steps-horizontal`, `step-primary`, `step-success`, `step-neutral` | Onboarding flows, checkout steppers |
| **Link** | `link` | `link-primary`, `link-secondary`, `link-accent`, `link-neutral`, `link-hover` | Footers, card descriptions |

---

## 3. Data Display & Typography Containers

| Component | Base Class | Key Modifiers / Variants | Common Pairings |
|---|---|---|---|
| **Card** | `card` | `card-body`, `card-title`, `card-actions`, `card-compact`, `card-side`, `image-full`, `bg-base-100/200/300`, `shadow-sm/md/xl` | Products, blogs, features, forms |
| **Stat** | `stat` | `stats` container (`stats-vertical`, `stats-horizontal`), `stat-title`, `stat-value`, `stat-desc`, `stat-figure` | KPI cards, dashboards, badges |
| **Table** | `table` | `table-zebra`, `table-pin-rows`, `table-pin-cols`, `table-xs/sm/lg` | Admin dashboards, order logs |
| **Badge** | `badge` | `badge-primary`, `badge-secondary`, `badge-accent`, `badge-neutral`, `badge-info`, `badge-success`, `badge-warning`, `badge-error`, `badge-outline`, `badge-xs/sm/lg` | Status tags, count indicators, pricing |
| **Avatar** | `avatar` | `avatar-group`, `avatar-online`, `avatar-offline`, `avatar-placeholder`, `rounded-full/xl` | Navbar user menus, social proof piles |
| **Timeline** | `timeline` | `timeline-vertical`, `timeline-horizontal`, `timeline-start`, `timeline-middle`, `timeline-end`, `timeline-compact` | Order status, history, roadmap |
| **Accordion** | `accordion` | Radio-driven mutual exclusivity container | FAQ sections, collapsible details |
| **Collapse** | `collapse` | `collapse-arrow`, `collapse-plus`, `collapse-open`, `collapse-close` | Help docs, expandable tables |
| **List** | `list` | `list-row`, `list-col-wrap`, `list-col-grow` | Activity feeds, settings rows |
| **Carousel** | `carousel` | `carousel-center`, `carousel-end`, `carousel-vertical`, `carousel-item` | Hero promos, photo galleries |
| **Countdown** | `countdown` | CSS variables `--value: X` driving transition counter | Sale timers, OTP resend cooldowns |
| **Diff** | `diff` | `diff-item-1`, `diff-item-2`, `diff-resizer` | Before/after image or code comparisons |
| **Divider** | `divider` | `divider-horizontal`, `divider-vertical`, `divider-primary`, `divider-start`, `divider-end` | Form splits, layout separation |
| **Kbd** | `kbd` | `kbd-xs`, `kbd-sm`, `kbd-md`, `kbd-lg` | Shortcut chips (`⌘K`, `Shift`) |
| **Status** | `status` | `status-primary`, `status-success`, `status-warning`, `status-error`, `status-info` | Real-time presence pings |
| **Text Rotate** | `text-rotate` | Animated rotating headlines (up to 6 lines, pause on hover) | Hero headlines, dynamic value props |
| **Hover 3D Card** | `hover-3d` | Perspective tilt & rotate wrapper following cursor | Bento grid cards, luxury showcases |
| **Hover Gallery** | `hover-gallery` | Multi-image container shifting visible slide on horizontal mouse move (up to 10 images) | E-commerce product cards, portfolios |
| **Aura** | `aura` | Dynamic border-glow wrapper | Featured CTA button, pricing card highlight |

---

## 4. Data Input & Form Controls

| Component | Base Class | Key Modifiers / Variants | Common Pairings |
|---|---|---|---|
| **Text Input** | `input` | `input-bordered`, `input-primary`, `input-secondary`, `input-ghost`, `input-xs/sm/lg` | `label`, `fieldset`, `validator` |
| **Textarea** | `textarea` | `textarea-bordered`, `textarea-primary`, `textarea-xs/sm/lg` | Contact forms, feedback cards |
| **Select** | `select` | `select-bordered`, `select-primary`, `select-xs/sm/lg` | Filter bars, sorting menus |
| **Checkbox** | `checkbox` | `checkbox-primary`, `checkbox-secondary`, `checkbox-accent`, `checkbox-success`, `checkbox-xs/sm/lg` | Data tables, terms agreements |
| **Radio** | `radio` | `radio-primary`, `radio-secondary`, `radio-accent`, `radio-xs/sm/lg` | Plan selectors, single-choice surveys |
| **Range Slider** | `range` | `range-primary`, `range-secondary`, `range-accent`, `range-xs/sm/lg` | Price filters, volume/progress controls |
| **Rating** | `rating` | `rating-half`, `rating-hidden`, `mask mask-star-2 bg-orange-400` | Review cards, social proof |
| **Toggle** | `toggle` | `toggle-primary`, `toggle-secondary`, `toggle-accent`, `toggle-success`, `toggle-xs/sm/lg` | Dark mode toggle, billing toggle |
| **File Input** | `file-input` | `file-input-bordered`, `file-input-primary`, `file-input-xs/sm/lg` | Image uploaders, document attachments |
| **OTP Input** | `otp` | 4-6 box numerical verification digits with auto-advance | 2FA verification, phone sign-in |
| **Filter** | `filter` | Radio chip group with automatic active selection & reset chip | Faceted catalog browsing, tags |
| **Fieldset** | `fieldset` | Semantic wrapper with `fieldset-legend` and `label` | Complex form groups, payment fields |
| **Label** | `label` | Semantic floating or attached field descriptor | Inputs, select boxes, file inputs |
| **Validator** | `validator` | Dynamic HTML5 validity color state reflection (`input:valid`, `input:invalid`) | Instant feedback sign-in/up forms |

---

## 5. Mockups & Framing Elements

| Component | Base Class | Structure / Features | Common Pairings |
|---|---|---|---|
| **Mockup Browser** | `mockup-browser` | Top URL bar, navigation dots, responsive preview frame | Hero sections, SaaS application previews |
| **Mockup Window** | `mockup-window` | Mac OS title bar with 3 colored window control dots | Feature cards, desktop software showcases |
| **Mockup Phone** | `mockup-phone` | Realistic mobile device bezel with camera notch & speaker | Mobile app landing pages, responsive previews |
| **Mockup Code** | `mockup-code` | Terminal editor shell with `data-prefix="$"` prompt lines | Developer docs, API installation blocks |

---

## 6. Feedback, Overlays & Layout Utilities

| Component | Base Class | Key Modifiers / Variants | Common Pairings |
|---|---|---|---|
| **Alert** | `alert` | `alert-info`, `alert-success`, `alert-warning`, `alert-error`, `alert-vertical` | Top banners, form status messages |
| **Toast** | `toast` | `toast-top`, `toast-bottom`, `toast-start`, `toast-center`, `toast-end` | Floating notifications container |
| **Modal** | `modal` | `modal-box`, `modal-action`, `modal-backdrop`, `modal-top/bottom/middle` | Detail views, deletion confirms, checkout |
| **Tooltip** | `tooltip` | `tooltip-top`, `tooltip-bottom`, `tooltip-left`, `tooltip-right`, `tooltip-primary` | Action buttons, table status icons |
| **Indicator** | `indicator` | `indicator-item`, `indicator-top/bottom`, `indicator-start/end` | Notification badge over avatar/cart |
| **Loading** | `loading` | `loading-spinner`, `loading-dots`, `loading-ring`, `loading-ball`, `loading-bars`, `loading-infinity`, `loading-xs/sm/lg` | Async buttons, data fetch skeletons |
| **Skeleton** | `skeleton` | Animated shimmer loading placeholder | Lazy-loaded cards, metric blocks |
| **Radial Progress** | `radial-progress` | Circular percentage dial using `--value: X; --size: Y; --thickness: Z;` | Battery/storage meters, KPI scores |
| **Progress** | `progress` | `progress-primary`, `progress-secondary`, `progress-success`, `progress-error` | Linear loading bars, step completion |
| **Hero** | `hero` | `hero-content`, `hero-overlay`, `min-h-screen` | Top-of-page value proposition |
| **Footer** | `footer` | `footer-center`, `footer-horizontal`, `footer-title` | Page closing, multi-column site directory |
| **Join** | `join` | `join-horizontal`, `join-vertical`, `join-item` | Clustered inputs with buttons, segmented tabs |
| **Stack** | `stack` | Visually stacks layered cards with 3D offset depth | Card decks, photo stacks |
| **Mask** | `mask` | `mask-squircle`, `mask-heart`, `mask-hexagon`, `mask-decagon`, `mask-star-2` | Avatars, custom image cropping |
| **Chat Bubble** | `chat` | `chat-start`, `chat-end`, `chat-image`, `chat-header`, `chat-bubble`, `chat-footer` | Messaging apps, support widgets, AI dialogs |
