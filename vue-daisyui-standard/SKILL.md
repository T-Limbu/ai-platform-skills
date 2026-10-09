---
name: vue-daisyui-standard
description: Standard architectural blueprint, convention rules, and scaffolding template for Vue 3 + Tailwind CSS + daisyUI web applications across squad projects. Use whenever initializing, refactoring, or building Vue 3 frontends.
---

# 🎨 Vue 3 + daisyUI Standard Architectural Blueprint

> **Standard conventions, project layout, state patterns, and mobile invariants for all Autonomous AI Data Squad Vue 3 web applications.**

---

## 🏛️ Standard Technology Stack

| Layer | Standard Selection | Rationale |
| :--- | :--- | :--- |
| **Framework** | **Vue 3** (`<script setup lang="ts">`) | Modern composition API, reactive primitives (`ref`, `computed`), type-safe tooling. |
| **Build Tool** | **Vite** (`@vitejs/plugin-vue`) | Sub-second HMR, optimized ES modules, instant dev server. |
| **UI Framework** | **daisyUI v5 / Tailwind CSS v4** | Semantic theme variables (`bg-base-100`, `text-primary`), zero-runtime CSS, built-in dark mode. |
| **Typography** | **JetBrains Mono** or **Inter** | Clean monospace engineering aesthetic with high-contrast legibility. |
| **Icons** | **Lucide Vue Next** (`lucide-vue-next`) | Lightweight, tree-shakeable SVG icon collection. |
| **Testing** | **Vitest** + **@vue/test-utils** | Blazing-fast unit and component test runner matching Vite configuration. |

---

## 📁 Standard Directory Structure

Every Vue 3 repository created or maintained by the squad must follow this layout:

```
├── .github/workflows/
│   ├── ci-cd.yml             # Dual-environment release pipeline (dev auto -> main gated)
│   └── pr-review.yml         # Automated PR hygiene checks
├── public/
│   └── favicon.svg           # Scalable monochrome SVG favicon
├── src/
│   ├── assets/               # Static assets & styles
│   │   └── main.css          # Tailwind / daisyUI entrypoint & JetBrains Mono font imports
│   ├── components/           # Modular, single-responsibility components
│   │   ├── navigation/       # Header, WaffleMenu, Dock
│   │   ├── command/          # CommandPalette (Cmd+K)
│   │   ├── ui/               # Reusable primitives (Buttons, Modals, Toasts)
│   │   └── apps/             # Domain-specific cards and widgets
│   ├── composables/          # Reusable reactive logic & lifecycle hooks
│   │   ├── useTheme.ts       # 35-theme switcher & system theme sync
│   │   ├── useCommandMenu.ts # Cmd+K shortcut listener & state
│   │   └── useDeepSleep.ts   # Mobile visibilitychange battery preservation hook
│   ├── types/                # TypeScript interface definitions
│   │   └── index.ts
│   ├── App.vue               # Root application shell
│   └── main.ts               # Application entrypoint
├── tests/
│   ├── vault/                # Regression tests (Zero Breakage Guarantee)
│   └── unit/                 # Component and logic unit tests
├── index.html                # HTML entrypoint with data-theme="dark"
├── package.json              # Standard scripts (dev, build, preview, test)
├── tsconfig.json             # Strict TypeScript configuration
└── vite.config.ts            # Vite config with alias '@' -> './src'
```

---

## 🛡️ Squad Operating Standards & Invariants

### 1. Mobile Battery & Background Resource Safety
Whenever rendering in a browser or mobile webview:
```ts
// src/composables/useDeepSleep.ts
import { onMounted, onUnmounted } from 'vue';

export function useDeepSleep(onSleep: () => void, onWake: () => void) {
  const handleVisibilityChange = () => {
    if (document.visibilityState === 'hidden') {
      onSleep();
    } else {
      onWake();
    }
  };

  onMounted(() => document.addEventListener('visibilitychange', handleVisibilityChange));
  onUnmounted(() => document.removeEventListener('visibilitychange', handleVisibilityChange));
}
```
* Halt high-frequency intervals and DOM animations when `document.visibilityState === 'hidden'`.
* Never acquire wake-locks without an automatic timeout release (max 15 mins).

### 2. Google Workspace 9-Dot Waffle Navigation
All squad applications must either:
* Mount the embeddable standalone `<WaffleMenu />` component, or
* Load the zero-dependency `squad-nav.js` script to allow instant 1-click jumps between all ecosystem apps (*Court Commander, Audio Gym, Off-Grid Audio, Off-Grid Video, Mail Triage*).

### 3. DaisyUI Semantic Token Convention
* **Never** use hardcoded arbitrary colors (e.g. `bg-[#121212]`) when a semantic daisyUI token exists (`bg-base-100`, `bg-base-200`, `bg-base-300`).
* Use `text-base-content`, `border-base-content/10`, and semantic state classes (`text-primary`, `badge-success`, `badge-warning`).
