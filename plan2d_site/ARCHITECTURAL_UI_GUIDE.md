# Architectural UI/UX Design Guide
## Professional House Plan Presentation System

**Last Updated:** January 2, 2026  
**Purpose:** Maintain professional, clean, and architecturally credible plan presentations

---

## 🎯 Core Design Principles

### 1. Beauty from Order, Not Decoration
- Plans are centered with proper margins
- Visual hierarchy is immediately clear
- Every element serves a purpose
- Clean presentation without visual clutter

### 2. Architectural Credibility
- High contrast between background and lines
- Clear line weights (walls thicker than furniture)
- Consistent graphic style across all plans
- Professional architectural document appearance

### 3. Mobile-First Excellence
- Plans are zoomable on all devices
- Text remains readable when zoomed
- No horizontal overflow
- Plans remain centered on small screens

---

## 📐 Layout Organization Rules

### Plan Cards (Grid View)
```css
.plan-dossier-card {
  /* Clean white container */
  /* 1px border with subtle shadow */
  /* Hover effect: lift and highlight */
  /* Mobile-first: full width → grid on larger screens */
}
```

**Visual Hierarchy:**
1. Plan image (centered, light background)
2. Reference code & category (top metadata)
3. Plan title (prominent, clickable)
4. Architectural specs (4-column grid)
5. Brief excerpt
6. CTAs (optional)

### Plan Detail Page
**Layout Structure:**
- Header: Breadcrumb + Title + Metadata
- Main: 8-column content area
  - Primary plan preview (centered, max 640px height)
  - Zoom toolbar (clean, right-aligned)
  - Gallery grid (responsive 2→3→4 columns)
  - Architect's notes (collapsible on mobile)
- Sidebar: 4-column info area
  - Architectural summary
  - Free vs Paid comparison
  - Use cases
  - Contact CTA

---

## 🎨 Visual Styling System

### Colors for Plans
```css
--plan-background: #FAFBFC;  /* Very light neutral */
--plan-border: #E2E8F0;       /* Soft gray */
--plan-hover: #3B82F6;        /* Primary blue */
```

### Typography
- **Reference Code:** Uppercase, bold, 700 weight
- **Plan Title:** 1.25rem (xl), 700 weight
- **Specs:** 0.75rem labels (xs), 1.125rem values (lg)
- **Categories:** Uppercase, 600 weight, letter-spacing

### Spacing
- **Card padding:** 1.25rem (space-5)
- **Image padding:** 1.5rem (space-6)
- **Grid gaps:** 0.75rem mobile → 1rem desktop

---

## 🖼️ Plan Image Presentation

### Main Plan Preview
```html
<div class="plan-preview">
  <img src="..." 
       style="padding: 2rem 1.5rem; 
              max-height: 640px;
              object-fit: contain;
              object-position: center;
              background: #FAFBFC;">
</div>
```

**Rules:**
- Always centered with generous padding
- Light neutral background (#FAFBFC)
- High contrast rendering (crisp-edges)
- Maximum height: 640px desktop, 480px mobile
- Cursor: zoom-in on hover

### Gallery Images
```css
.plan-gallery-grid {
  /* Responsive: 2 → 3 → 4 columns */
  /* Gap: 0.75rem */
}

.plan-gallery-item {
  /* Border, rounded corners */
  /* Hover: lift + highlight border */
  /* Image: 160px height, cover fit */
}
```

### Mobile Zoom
- Pinch-to-zoom hint on mobile
- Modal viewer with instructions
- Touch-friendly close button

---

## 🆓 Free vs Paid Visual Distinction

### Free Version
```css
.plan-version--free {
  background: linear-gradient(135deg, #FAFBFC, #F1F5F9);
  /* Badge: "FREE" in green */
}
```

**Features Shown:**
- ✓ Functional layout visible
- ✓ Room zoning readable
- ✓ Circulation logic clear
- ✗ No dimensions included
- ⚠️ Watermarked for preview

### Paid Version (Build-Ready)
```css
.plan-version--paid {
  background: linear-gradient(135deg, #EBF5FF, #DBEAFE);
  border-color: var(--color-primary-light);
  /* Badge: "BUILD-READY" in blue */
}
```

**Features Shown:**
- ✓ All dimensions included
- ✓ Wall thicknesses specified
- ✓ Door & window sizes
- ✓ Construction-ready details
- ✓ No watermarks

---

## 📊 Architectural Specifications

### Spec Grid
```html
<div class="plan-dossier-specs">
  <div class="plan-dossier-spec">
    <span>Label</span>
    <strong>Value</strong>
  </div>
  <!-- Repeat for: Bedrooms, Bathrooms, Area, Floors -->
</div>
```

**Mobile:** 2 columns  
**Tablet+:** 4 columns  
**Hover:** Subtle lift + shadow

### Displayed Information
1. **Primary:**
   - Bedrooms (integer)
   - Bathrooms (decimal, e.g., 2.5)
   - Total Area (m² and ft²)
   - Floors (integer or "—")

2. **Secondary:**
   - Suggested plot size
   - Roof type
   - Wall system
   - Climate suitability
   - Plot type
   - Budget level
   - Target user

---

## 📱 Mobile Optimization

### Touch Targets
- Minimum 44px × 44px for all clickable elements
- Gallery items: 160px height on mobile
- Buttons: Full width on mobile, inline on desktop

### Readability
- Font size: Minimum 16px (1rem) for body text
- Plan images: Zoomable via modal
- Specs: 2-column grid on mobile

### Performance
- Lazy loading for gallery images
- `loading="lazy"` attribute
- `decoding="async"` attribute
- Image optimization via CDN

### Navigation
- Sticky navigation (6rem scroll offset)
- Breadcrumbs collapse on mobile
- Collapsible sections (accordion style)

---

## 🧹 Cleanup & Maintenance

### Remove Duplicates
```css
.plan-duplicate {
  opacity: 0.3;
  pointer-events: none;
}
.plan-duplicate::after {
  content: 'DEPRECATED';
  /* Red overlay badge */
}
```

### Quality Standards
- ❌ Remove low-resolution plan images
- ❌ Remove outdated annotations
- ❌ Remove unnecessary symbols
- ✅ Maintain consistent line weights
- ✅ Ensure high contrast
- ✅ Use consistent scale across plans

### File Organization
```
media/plans/
├── images/          # Primary plan images
├── free/            # Free watermarked versions
└── paid/            # Build-ready dimensioned versions
```

---

## ✅ Visual Consistency Checklist

When adding or updating plans, verify:

- [ ] Plan is centered with proper margins
- [ ] Background is light neutral (#FAFBFC)
- [ ] Image has high contrast rendering
- [ ] Line weights are consistent
- [ ] Text labels are readable
- [ ] No visual clutter or noise
- [ ] Dimensions are clear (paid version)
- [ ] Watermark is discreet (free version)
- [ ] Same scale feeling across similar plans
- [ ] Hover states work correctly
- [ ] Mobile zoom functions properly
- [ ] Gallery grid displays correctly
- [ ] All metadata is filled in
- [ ] No duplicate images

---

## 🎯 Expected Results

### User Experience
- Plans look organized and professional
- Visual presentation feels clean and modern
- Users understand layouts instantly
- Plans resemble professional architectural documents
- Mobile experience is seamless

### Technical Quality
- Fast loading times
- Responsive across all devices
- Accessible (WCAG AA compliant)
- SEO optimized
- Print-friendly

### Business Impact
- Increased trust and credibility
- Higher conversion rates
- Lower bounce rates
- More plan downloads
- Positive user feedback

---

## 📚 CSS Classes Reference

### Plan Cards
- `.plan-dossier-card` - Main card container
- `.plan-dossier-thumb` - Image container
- `.plan-dossier-body` - Content area
- `.plan-dossier-meta` - Reference + category
- `.plan-dossier-title` - Plan name
- `.plan-dossier-specs` - Specs grid
- `.plan-dossier-spec` - Individual spec
- `.plan-dossier-excerpt` - Description
- `.plan-dossier-ctas` - Action buttons

### Plan Detail
- `.plan-preview` - Main plan viewer
- `.plan-preview__toolbar` - Zoom controls
- `.dossier-section` - Content block
- `.dossier-section__header` - Block title
- `.dossier-section__body` - Block content
- `.plan-versions` - Free/paid grid
- `.plan-version--free` - Free version card
- `.plan-version--paid` - Paid version card

### Gallery
- `.plan-gallery-grid` - Gallery container
- `.plan-gallery-item` - Gallery thumbnail
- `.plan-gallery-label` - Image type label
- `.pinch-zoom-hint` - Mobile instruction
- `.modal-img` - Modal viewer image

---

## 🔧 Customization Variables

```css
/* Adjust these in main.css if needed */
--plan-thumb-height: 280px;      /* Card thumbnail height */
--plan-preview-max: 640px;       /* Detail page max height */
--plan-gallery-item: 160px;      /* Gallery thumbnail height */
--plan-padding: 1.5rem;          /* Image padding */
--plan-border-radius: 0.75rem;   /* Corner radius */
```

---

## 🚀 Future Enhancements

### Planned Features
1. Advanced zoom controls (pan, rotate)
2. Side-by-side plan comparison
3. Room-by-room dimension overlay
4. Printable PDF generation
5. Interactive floor plan explorer
6. 3D model integration
7. AR preview mode
8. Virtual tour integration

### Accessibility Improvements
- Screen reader optimization
- Keyboard navigation
- High contrast mode
- Text-to-speech support
- Multilingual captions

---

## 📞 Support & Questions

For architectural UI questions or suggestions:
- Review this guide first
- Check existing plan examples
- Test on multiple devices
- Maintain consistency with examples
- Document any new patterns

**Remember:** Beauty comes from order, not decoration. Keep it clean, keep it professional, keep it architectural.
