# 📘 Depth, Shadows & Overlays Playbook

> Ambient shadows, image overlay gradients, progressive blur, and glassmorphism.

---

## 🎥 Source: *Every UI/UX Concept Explained in Under 10 Minutes* (Kole Jain)

### 1. Concrete Mathematical Benchmarks
* **Softness over Opacity (The Shadow Law):**
  * *"If the shadow is the first thing you notice on a card, it is set too strong."*
  * Lower opacity (`opacity-5` to `opacity-15`), increase blur radius (`blur-md` to `blur-2xl`).
* **Image Overlay Gradients:**
  * Never place text directly over raw images or slap an opaque black rectangle over them.
  * Use a smooth linear gradient: `bg-gradient-to-t from-slate-950 via-slate-950/70 to-transparent`.
* **Progressive Backdrop Blur:**
  * Add modern backdrop blur (`backdrop-blur-md` or `backdrop-blur-xl`) behind modals and floating headers for an authentic glass aesthetic.

### 2. Code Presets
```html
<!-- Progressive Gradient Overlay for Image Readability -->
<div class="relative overflow-hidden rounded-2xl">
  <img src="preview.jpg" class="w-full h-64 object-cover" />
  <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/60 to-transparent backdrop-blur-[2px] flex items-end p-6">
    <h3 class="text-white font-bold text-lg">Crisp Readable Text</h3>
  </div>
</div>

<!-- Ambient Elevated Card -->
<div class="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-[0_10px_30px_-10px_rgba(0,0,0,0.15)] border border-slate-100 dark:border-white/[0.08]">
  Card Content
</div>
```

### 3. Anti-Patterns
* ❌ Using harsh black solid boxes over images.
* ❌ Dark, muddy drop shadows with zero blur spread.
