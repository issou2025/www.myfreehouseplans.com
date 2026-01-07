# 🚀 Mobile-First Quick Reference

## ⚡ Quick Access

### Server
```bash
# Start server
cd "c:\Users\issoufou abdou\Desktop\DOSSIERS CLIENTS\site-web\plan2d_site"
python manage.py runserver

# Access site
http://127.0.0.1:8000/
```

### Documentation
- **📘 Complete Guide:** `MOBILE_FIRST_COMPLETE.md`
- **🧪 Testing Guide:** `MOBILE_TESTING_GUIDE.md`
- **📊 Summary:** `MOBILE_TRANSFORMATION_SUMMARY.md`
- **✅ Checklist:** `MOBILE_CHECKLIST.md`
- **🔄 Comparison:** `BEFORE_AFTER_COMPARISON.md`

---

## 📏 Key Numbers to Remember

### Typography
- **Body text:** 16px minimum (1rem)
- **H1 mobile:** 28px (1.75rem)
- **H1 desktop:** 48px (3rem)
- **Line height:** 1.7

### Touch Targets
- **Minimum:** 44x44px
- **Recommended:** 48x48px
- **Buttons:** 48px height
- **Links:** 44px height
- **Form inputs:** 48px height

### Breakpoints
- **Mobile:** 0-767px (default, no media query)
- **Tablet:** 768px+ (`@media (min-width: 768px)`)
- **Desktop:** 1024px+ (`@media (min-width: 1024px)`)

---

## 🎨 CSS Pattern

```css
/* ✅ CORRECT: Mobile-first */
.element {
  /* Mobile styles (default) */
  font-size: 1rem;
  padding: 1rem;
  width: 100%;
}

@media (min-width: 768px) {
  .element {
    /* Tablet: scale up */
    font-size: 1.25rem;
    width: 50%;
  }
}

@media (min-width: 1024px) {
  .element {
    /* Desktop: scale up more */
    font-size: 1.5rem;
    width: 33.333%;
  }
}
```

```css
/* ❌ WRONG: Desktop-first */
.element {
  font-size: 1.5rem; /* Desktop default */
}

@media (max-width: 768px) {
  .element {
    font-size: 1rem; /* Scale down */
  }
}
```

---

## 🖼️ Image Pattern

```html
<!-- ✅ Hero image (above fold): eager -->
<img src="hero.jpg" 
     alt="Descriptive text"
     loading="eager"
     decoding="async">

<!-- ✅ Gallery images (below fold): lazy -->
<img src="gallery.jpg" 
     alt="Descriptive text"
     loading="lazy"
     decoding="async">
```

---

## 👆 Touch Target Pattern

```css
/* ✅ Buttons */
.btn {
  min-height: 48px;
  min-width: 48px;
  padding: 16px 24px;
}

/* ✅ Links */
a {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
}

/* ✅ Form inputs */
.form-control {
  min-height: 48px;
  font-size: 16px; /* Prevents iOS zoom */
}
```

---

## 🖱️ Hover Detection

```css
/* No hover on mobile (default) */
.button {
  background: blue;
}

/* Hover only on desktop (mouse) */
@media (hover: hover) and (pointer: fine) {
  .button:hover {
    background: darkblue;
    transform: translateY(-2px);
  }
}
```

---

## 📱 Testing Shortcuts

### Chrome DevTools
1. `F12` - Open DevTools
2. `Ctrl+Shift+M` - Toggle device toolbar
3. Select device or custom width
4. Test away!

### Common Test Sizes
- **iPhone SE:** 375px
- **Galaxy S8:** 360px
- **iPad:** 768px
- **Desktop:** 1280px

### Network Throttling
- DevTools → Network tab
- Select **Slow 3G**
- Reload page

---

## ✅ Quick Checklist

Before deploying, verify:
- [ ] All text 16px minimum
- [ ] All buttons 48px height
- [ ] All links 44px height
- [ ] Forms don't zoom on iOS
- [ ] No horizontal scrolling
- [ ] Images lazy load
- [ ] Mobile nav works
- [ ] Tested on 375px width

---

## 🔧 Common Fixes

### Horizontal Scroll
```css
/* Add to body */
body {
  overflow-x: hidden;
  width: 100%;
}

/* Check images */
img {
  max-width: 100%;
  height: auto;
}
```

### Small Text
```css
/* Ensure minimum 16px */
body {
  font-size: 16px;
}

p, span, div {
  font-size: 1rem; /* 16px */
}
```

### iOS Form Zoom
```css
/* Use 16px font minimum */
input, textarea, select {
  font-size: 16px;
}
```

### Small Touch Targets
```css
/* Add minimum heights */
button, a, .clickable {
  min-height: 44px;
  min-width: 44px;
}
```

---

## 📚 Key Files

### CSS
- `static/css/main.css` - Mobile-first styles

### Templates
- `templates/base.html` - Base template
- `apps/plans/templates/plans/plan_list.html` - Plans list
- `apps/plans/templates/plans/plan_detail.html` - Plan detail
- `apps/core/templates/core/home.html` - Homepage

---

## 🎯 Quick Commands

### Django
```bash
# Run server
python manage.py runserver

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static
python manage.py collectstatic
```

---

## 💡 Pro Tips

1. **Always test on mobile first**
   - Use Chrome DevTools mobile view
   - Test on 375px width
   - Verify touch targets

2. **Use min-width media queries**
   - Start with mobile styles
   - Add tablet styles at 768px
   - Add desktop styles at 1024px

3. **Optimize images**
   - Use lazy loading
   - Add loading="lazy"
   - Add decoding="async"

4. **Make touch targets big**
   - Minimum 44px
   - Recommended 48px
   - More is better

5. **Test on slow networks**
   - Use Slow 3G throttling
   - Verify progressive loading
   - Check performance

---

## 🆘 Help

### Something broken?
1. Check browser console (`F12` → Console)
2. Verify server is running
3. Clear cache (`Ctrl+Shift+Delete`)
4. Hard reload (`Ctrl+Shift+R`)

### Need more info?
- Read `MOBILE_FIRST_COMPLETE.md`
- Follow `MOBILE_TESTING_GUIDE.md`
- Check `BEFORE_AFTER_COMPARISON.md`

---

## 🎉 Success Indicators

✅ Text readable without zoom
✅ Buttons easy to tap
✅ No horizontal scrolling
✅ Fast loading on mobile
✅ Forms don't trigger zoom
✅ Navigation works smoothly
✅ Images load progressively
✅ Lighthouse score 85+

---

**Quick Reference:** Keep this file handy!
**Status:** ✅ Mobile-First Complete
**Server:** http://127.0.0.1:8000/
