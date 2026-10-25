# 📘 Interaction States & Feedback Playbook

> The mandatory 4 interaction states, tactile motion feedback, and form inputs.

---

## 🎥 Source: *Every UI/UX Concept Explained in Under 10 Minutes* (Kole Jain)

### 1. Concrete Mathematical Benchmarks
* **The Mandatory 4 States Rule:**
  * Every interactive element must visibly implement:
    1. **`Default`**: Clean resting state.
    2. **`Hover`**: Visual elevation or brightness bump.
    3. **`Active / Pressed`**: Tactile feedback (e.g. `active:scale-[0.97]` or slight darkening).
    4. **`Disabled`**: `opacity-40`, `cursor-not-allowed`, grayed-out text.
    5. *(Bonus)* **`Loading`**: Spinner preserves exact button dimensions.
* **Form Inputs:**
  * Must feature an accessible focus ring (`focus:outline-none focus:border-sky-400 focus:ring-1 focus:ring-sky-400`).
  * Error state: Red border (`border-rose-500`) + specific explanatory microcopy below the input.

### 2. Code Presets
```html
<!-- Interactive Button with Full State Handling -->
<button class="px-4 py-2 rounded-xl text-xs font-bold bg-sky-500 hover:bg-sky-400 active:scale-[0.97] disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 transition-all duration-150">
  Submit Data
</button>

<!-- Form Input with Focus & Error Handling -->
<div class="space-y-1">
  <label class="block text-[11px] font-bold text-slate-400 uppercase">Email Address</label>
  <input type="email" class="w-full bg-slate-950/80 border border-white/[0.08] focus:border-sky-400 focus:ring-1 focus:ring-sky-400 rounded-xl px-3 py-2 text-xs text-white focus:outline-none transition">
</div>
```

### 3. Anti-Patterns
* ❌ Buttons that do not shrink or react when pressed (`active:scale` missing).
* ❌ Disabling a button without `cursor-not-allowed` or opacity change.
