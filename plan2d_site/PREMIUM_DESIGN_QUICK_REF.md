# Premium Design System - Quick Reference

## 🎨 Color Palette

```css
/* Primary Colors */
--premium-primary: #1E3A8A         /* Deep professional blue */
--premium-primary-dark: #1E293B    /* Nearly black blue */
--premium-primary-light: #3B82F6   /* Lighter blue */

/* Accent */
--premium-accent: #059669           /* Professional green */
--premium-accent-dark: #047857      /* Darker green */

/* Neutrals (Gray Scale) */
--premium-neutral-50: #FAFAFA       /* Off-white */
--premium-neutral-100: #F5F5F5      /* Very light gray */
--premium-neutral-200: #E5E5E5      /* Light gray */
--premium-neutral-500: #737373      /* Medium gray */
--premium-neutral-900: #171717      /* Almost black */

/* Text */
--premium-text-primary: #171717     /* Main text */
--premium-text-secondary: #525252   /* Secondary text */
--premium-text-tertiary: #737373    /* Tertiary text */
```

---

## 📝 Typography

### Font Families
```css
--premium-font-heading: 'Space Grotesk'  /* Modern, architectural */
--premium-font-body: 'Inter'             /* Professional, readable */
```

### Heading Classes
```html
<h1 class="premium-h1">48px desktop / 32px mobile</h1>
<h2 class="premium-h2">36px desktop / 28px mobile</h2>
<h3 class="premium-h3">30px desktop / 24px mobile</h3>
<h4 class="premium-h4">24px desktop / 20px mobile</h4>
```

### Text Utilities
```html
<p class="premium-text">Default body text (16px)</p>
<p class="premium-text-sm">Small text (14px)</p>
<p class="premium-text-lg">Large text (18px)</p>
<p class="premium-text-primary">Primary color text</p>
<p class="premium-text-secondary">Secondary color text</p>
```

---

## 🔘 Buttons

### Primary Button
```html
<a href="#" class="premium-btn-primary">Main Action</a>
<button class="premium-btn-primary premium-btn-lg">Large Primary</button>
```
- **Color**: Deep blue (#1E3A8A)
- **Usage**: Main CTAs, important actions
- **Hover**: Lifts up, darker blue

### Secondary Button
```html
<a href="#" class="premium-btn-secondary">Secondary Action</a>
<button class="btn-outline-primary">Alternative</button>
```
- **Color**: Outlined blue
- **Usage**: Alternative actions
- **Hover**: Fills with blue

### Accent Button
```html
<a href="#" class="premium-btn-accent">Buy Now</a>
<button class="btn-success">Purchase</button>
```
- **Color**: Professional green (#059669)
- **Usage**: Success actions, purchases
- **Hover**: Darker green

### Button Sizes
```html
<button class="premium-btn-primary premium-btn-sm">Small (40px)</button>
<button class="premium-btn-primary">Default (48px)</button>
<button class="premium-btn-primary premium-btn-lg">Large (56px)</button>
```

---

## 📦 Cards

### Basic Card
```html
<div class="premium-card">
  <h3 class="premium-card-title">Card Title</h3>
  <p class="premium-card-text">Card content goes here.</p>
</div>
```
- **Background**: White
- **Border**: Light gray (1px)
- **Shadow**: Very subtle
- **Radius**: 12px
- **Hover**: Subtle lift

### Plan Card
```html
<div class="premium-plan-card">
  <div class="premium-plan-image">
    <img src="..." alt="Plan">
  </div>
  <div class="premium-plan-content">
    <h3 class="premium-plan-title">Plan Name</h3>
    <div class="premium-plan-specs">
      <div class="premium-plan-spec">
        <span class="premium-plan-spec-label">BEDROOMS</span>
        <span class="premium-plan-spec-value">3</span>
      </div>
      <!-- More specs -->
    </div>
    <div class="premium-plan-actions">
      <button class="premium-btn-primary">View Plan</button>
    </div>
  </div>
</div>
```

---

## 📐 Layout & Grid

### Section Structure
```html
<section class="premium-section">
  <div class="container">
    <div class="premium-section-header">
      <h2 class="premium-section-title">Section Title</h2>
      <p class="premium-section-subtitle">Description</p>
    </div>
    <div class="premium-grid premium-grid-3">
      <!-- Grid items -->
    </div>
  </div>
</section>
```

### Grid Options
```html
<div class="premium-grid premium-grid-2">2 columns (desktop)</div>
<div class="premium-grid premium-grid-3">3 columns (desktop)</div>
<div class="premium-grid premium-grid-4">4 columns (desktop)</div>
```
- **Mobile**: Always 1 column
- **Tablet**: 2 columns for grid-3 and grid-4
- **Desktop**: As specified

### Hero Section
```html
<section class="premium-hero">
  <div class="premium-hero-content">
    <h1 class="premium-hero-title">Hero Title</h1>
    <p class="premium-hero-subtitle">Subtitle text</p>
    <div class="premium-hero-actions">
      <a href="#" class="premium-btn-primary">Primary</a>
      <a href="#" class="premium-btn-secondary">Secondary</a>
    </div>
  </div>
</section>
```

---

## 📝 Forms

### Form Group
```html
<div class="premium-form-group">
  <label class="premium-form-label">Label</label>
  <input type="text" class="premium-form-input" placeholder="Enter text">
  <p class="premium-form-help">Helper text</p>
</div>

<div class="premium-form-group">
  <label class="premium-form-label">Message</label>
  <textarea class="premium-form-textarea"></textarea>
</div>

<button type="submit" class="premium-btn-primary">Submit</button>
```

### Form Input Features
- **Min Height**: 48px
- **Font Size**: 16px (prevents iOS zoom)
- **Border**: 2px solid gray
- **Focus**: Blue border + subtle shadow
- **Full Width**: Automatic on mobile

---

## 🏷️ Badges & Tags

```html
<span class="premium-badge">Default Badge</span>
<span class="premium-badge premium-badge-primary">Primary Badge</span>
<span class="premium-badge premium-badge-accent">Accent Badge</span>
```

---

## 📏 Spacing Utilities

### Margin
```html
<div class="premium-mt-sm">margin-top: 8px</div>
<div class="premium-mt-md">margin-top: 16px</div>
<div class="premium-mt-lg">margin-top: 24px</div>
<div class="premium-mt-xl">margin-top: 32px</div>
<div class="premium-mt-2xl">margin-top: 48px</div>

<!-- Same for mb (bottom), ml (left), mr (right) -->
```

### Padding
```html
<div class="premium-p-sm">padding: 8px</div>
<div class="premium-p-md">padding: 16px</div>
<div class="premium-p-lg">padding: 24px</div>
<div class="premium-p-xl">padding: 32px</div>
<div class="premium-p-2xl">padding: 48px</div>
```

### Gap (Flexbox/Grid)
```html
<div class="premium-flex premium-gap-sm">gap: 8px</div>
<div class="premium-flex premium-gap-md">gap: 16px</div>
<div class="premium-flex premium-gap-lg">gap: 24px</div>
```

---

## 🎯 Display Utilities

### Flexbox
```html
<div class="premium-flex">display: flex</div>
<div class="premium-flex premium-flex-col">flex-direction: column</div>
<div class="premium-flex premium-items-center">align-items: center</div>
<div class="premium-flex premium-justify-center">justify-content: center</div>
<div class="premium-flex premium-justify-between">justify-content: space-between</div>
```

### Text Alignment
```html
<div class="premium-text-left">Left aligned</div>
<div class="premium-text-center">Center aligned</div>
<div class="premium-text-right">Right aligned</div>
```

---

## 🖼️ Borders & Shadows

### Borders
```html
<div class="premium-border">1px solid border</div>
<div class="premium-border-top">Top border only</div>
<div class="premium-border-bottom">Bottom border only</div>
<div class="premium-rounded">8px border radius</div>
<div class="premium-rounded-lg">12px border radius</div>
```

### Shadows
```html
<div class="premium-shadow-sm">Light shadow</div>
<div class="premium-shadow-md">Medium shadow</div>
<div class="premium-shadow-lg">Large shadow</div>
```

---

## 🎨 Background Colors

```html
<div class="premium-bg-white">White background</div>
<div class="premium-bg-gray">Light gray background</div>
<div class="premium-bg-primary">Blue background (white text)</div>
```

---

## 🧭 Navigation

```html
<nav class="navbar premium-navbar">
  <div class="container">
    <a class="navbar-brand premium-navbar-brand" href="#">Brand</a>
    <ul class="navbar-nav">
      <li class="nav-item">
        <a class="nav-link premium-nav-link" href="#">Link</a>
      </li>
      <li class="nav-item">
        <a class="nav-link premium-nav-link active" href="#">Active</a>
      </li>
    </ul>
  </div>
</nav>
```

---

## 🦶 Footer

```html
<footer class="premium-footer">
  <div class="container">
    <div class="premium-footer-content">
      <div class="premium-footer-section">
        <h5 class="premium-footer-title">Section</h5>
        <a href="#" class="premium-footer-link">Link</a>
      </div>
    </div>
    <div class="premium-footer-bottom">
      <p>© 2026 Your Company</p>
    </div>
  </div>
</footer>
```

---

## ⚡ Quick Migration Guide

### Replace These Classes:

```html
<!-- OLD → NEW -->
<section class="hero"> → <section class="premium-hero">
<div class="card"> → <div class="premium-card">
<h2 class="section-title"> → <h2 class="premium-section-title">
<div class="feature-grid"> → <div class="premium-grid premium-grid-3">
```

### Buttons Auto-Apply Premium Styling:
```html
<!-- These already get premium styling automatically -->
<button class="btn-primary">Already premium!</button>
<button class="btn-secondary">Already premium!</button>
<button class="btn-success">Already premium!</button>
```

### Cards Auto-Apply Premium Styling:
```html
<!-- Existing .card class gets premium styling -->
<div class="card">Already premium!</div>
```

---

## 💡 Best Practices

### ✅ DO
- Use premium color variables
- Apply consistent spacing (8px/16px/24px)
- Use grid-based layouts
- Keep shadows subtle
- Maintain typography hierarchy
- Test on mobile (320px minimum)

### ❌ DON'T
- Don't mix color systems
- Don't use inconsistent spacing
- Don't add heavy shadows
- Don't use decorative fonts
- Don't overcomplicate layouts
- Don't forget mobile testing

---

## 📱 Mobile Considerations

### Automatic Behaviors:
- Buttons become full-width on mobile
- Grids collapse to single column
- Typography scales down appropriately
- Touch targets minimum 48px
- Hero actions stack vertically

### Mobile-Specific Classes:
```html
<!-- These work everywhere, optimized for mobile -->
<button class="premium-btn-primary">Full width on mobile</button>
<div class="premium-grid premium-grid-3">Single column on mobile</div>
```

---

## 🚀 Getting Started

### Step 1: Verify CSS is Loaded
```html
<!-- Check this is in your base.html -->
<link rel="stylesheet" href="{% static 'css/premium-design-system.css' %}">
```

### Step 2: Start with Hero
```html
<section class="premium-hero">
  <div class="premium-hero-content">
    <h1 class="premium-hero-title">Your Title</h1>
    <p class="premium-hero-subtitle">Your subtitle</p>
    <div class="premium-hero-actions">
      <a href="#" class="premium-btn-primary">Get Started</a>
    </div>
  </div>
</section>
```

### Step 3: Add Sections
```html
<section class="premium-section">
  <div class="container">
    <div class="premium-section-header">
      <h2 class="premium-section-title">Section Title</h2>
    </div>
    <div class="premium-grid premium-grid-3">
      <div class="premium-card">Card 1</div>
      <div class="premium-card">Card 2</div>
      <div class="premium-card">Card 3</div>
    </div>
  </div>
</section>
```

### Step 4: Test Responsiveness
- Open DevTools (F12)
- Toggle Device Mode (Ctrl+Shift+M)
- Test at 320px, 375px, 768px, 1024px
- Verify touch targets and readability

---

## 📊 Cheat Sheet

| Component | Class | Notes |
|-----------|-------|-------|
| Hero | `.premium-hero` | Gradient background, centered |
| Section | `.premium-section` | 64px padding (32px mobile) |
| Card | `.premium-card` | White bg, subtle shadow |
| Button (Primary) | `.premium-btn-primary` | Blue, filled |
| Button (Secondary) | `.premium-btn-secondary` | Blue, outlined |
| Grid 3-col | `.premium-grid-3` | 3 cols → 2 → 1 |
| Plan Card | `.premium-plan-card` | Architectural style |
| Form Input | `.premium-form-input` | 48px height, 16px font |
| Badge | `.premium-badge` | Small, uppercase label |
| Footer | `.premium-footer` | Dark background |

---

**Pro Tip**: Most existing classes (`.btn-primary`, `.card`) automatically receive premium styling. Just add the CSS file and see the transformation!

**Version**: 1.0  
**Last Updated**: January 3, 2026
