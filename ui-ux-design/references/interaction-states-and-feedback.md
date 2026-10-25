# 📘 Interaction States And Feedback Playbook



---

## 🎥 Reference: YouTube Video (EcbgbKtOELY) (`EcbgbKtOELY`)

# Comprehensive Interaction States & Micro-Interactions

### Source: YouTube Video (EcbgbKtOELY)

### Concrete Rules & Mathematical Principles
- **The 4-to-5 State Interactive Mandate**: Every interactive component must handle distinct visual conditions:
  1. **Default**: Baseline rest state.
  2. **Hover**: Cursor proximity indicator (luminance shift).
  3. **Active / Pressed**: Tactile inset or scale translation (`transform: scale(0.98)`).
  4. **Disabled**: Reduced opacity, pointer-events severed.
  5. **Loading**: Replaces label with progress indicator or spinner.
- **Form Input State Matrix**:
  - **Focus**: Distinct highlight ring (usually primary accent tint with an outer glow).
  - **Error**: Semantic red outer border accompanied by descriptive messaging.
  - **Warning**: Semantic yellow/amber styling for non-fatal configuration issues.
- **Action Confirmation Micro-Interactions**: Direct manipulation requires physical confirmation beyond generic states. Secondary tasks like "Copy to Clipboard" must transition into immediate visual feedback (e.g., an animated checkmark, tooltips, or sliding chips) confirming execution.

### Anti-Patterns
- **The Static Dead-End**: Leaving buttons without hover, pressed, or disabled styles.
- **Silent Clipboard / Action Triggers**: Firing an asynchronous event without an immediate visual confirmation state.
- **Error Signaling Exclusively by Color**: Relying solely on red borders without textual error descriptions or persistent visual cues.

### Implementation Specs
```css
/* Focus-visible ring standard */
.interactive-control:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px var(--bg-surface), 0 0 0 4px var(--brand-accent);
}

/* Micro-Interaction Animation for Inline Confirmations */
@keyframes slideUpFadeIn {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.copy-toast-chip {
  animation: slideUpFadeIn 150ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
```
