# Branding & Presentation System - User Guide

## 🎯 Overview

The branding system allows administrators to manage all visual branding assets including logos and presentation slider images **without touching code**. Everything is controlled through the Django admin interface.

---

## 🖼️ Logo Management

### Available Logo Types

1. **Main Logo (Header)** - Displayed in the navigation bar on all pages
2. **Footer Logo** - Displayed in the footer (optional)
3. **Favicon** - Browser tab icon (optional)

### How to Upload/Change a Logo

1. **Access Admin Interface**
   - Go to: http://127.0.0.1:8000/admin/
   - Navigate to: **Branding & Presentation** → **Logos**

2. **Add New Logo**
   - Click "Add Logo" button
   - Select logo type (Main Logo, Footer Logo, or Favicon)
   - Upload image file (SVG, PNG, WEBP, JPG supported)
   - Enter alt text for accessibility
   - Set as "Active" (checked)
   - Click "Save"

3. **Replace Existing Logo**
   - Click on existing logo in list
   - Upload new image file
   - Click "Save"
   - Old logo is automatically replaced

4. **Remove Logo**
   - Uncheck "Active" to hide logo
   - Text fallback will appear instead
   - To restore: check "Active" again

### Logo Requirements

| Logo Type | Max Size | Recommended Dimensions | Formats |
|-----------|----------|------------------------|---------|
| Main Logo | 5MB | Width: 180px, Height: 40px | SVG, PNG, WEBP |
| Footer Logo | 5MB | Width: 200px, Height: 60px | SVG, PNG, WEBP |
| Favicon | 5MB | 512x512px or smaller | PNG, ICO |

### Important Rules

✅ **Only one active logo per type** - Setting a new logo as active automatically deactivates others
✅ **Instant reflection** - Logo changes appear immediately on all pages
✅ **Safe fallback** - If no logo is active, brand name text displays instead
✅ **Responsive** - Logos automatically scale for mobile devices

---

## 🎬 Presentation Slider Management

### What is the Presentation Slider?

A rotating image carousel displayed on the homepage to showcase key visuals, featured plans, or promotional content.

### How to Manage Slider Images

#### 1. Access Slider Admin

- Go to: **Branding & Presentation** → **Presentation Slider**
- View all slides with preview images and status indicators

#### 2. Add New Slide

- Click "Add Presentation Slide"
- Fill in details:
  - **Title**: Optional overlay text (e.g., "Featured Plans")
  - **Short Description**: Optional subtitle (max 500 chars)
  - **Image**: Upload slider image (JPG, PNG, WEBP)
  - **Link URL**: Optional destination when clicked
  - **Display Order**: Number (lower = appears first)
  - **Is Active**: Check to display on website
- Click "Save"

#### 3. Reorder Slides

**Method 1: Edit Display Order**
- In the slide list, change the number in "Display Order" column
- Click away to save
- Lower numbers appear first (e.g., 0, 1, 2, 3...)

**Method 2: Edit Individual Slide**
- Click on slide
- Change "Display Order" field
- Click "Save"

#### 4. Activate/Deactivate Slides

**Quick Method (Bulk Actions)**:
- Select slides using checkboxes
- Choose action from dropdown:
  - ✓ Activate selected slides
  - ⊘ Deactivate selected slides
- Click "Go"

**Individual Method**:
- Click on slide
- Check/uncheck "Is Active"
- Click "Save"

#### 5. Delete Slides

**Soft Delete (Recommended)**:
- Select slides
- Choose "🗑️ Soft delete selected slides"
- Slides are hidden but can be restored

**Restore Deleted Slides**:
- Select soft-deleted slides
- Choose "♻️ Restore deleted slides"
- Slides become available again

**Permanent Delete (Superuser Only)**:
- Click on slide → "Delete" button at bottom
- Confirm deletion
- ⚠️ This cannot be undone!

### Slider Image Requirements

| Requirement | Specification |
|-------------|---------------|
| **Max File Size** | 10MB |
| **Min Width** | 800px (recommended: 1920px) |
| **Aspect Ratio** | 16:9 recommended for best display |
| **Formats** | JPG, PNG, WEBP |
| **Max Displayed** | 10 slides at once |

### Slider Behavior

- **Auto-rotation**: Changes every 5 seconds
- **Manual control**: Arrows and dots for navigation
- **Pause on hover**: Desktop only
- **Touch swipe**: Mobile-friendly
- **Keyboard navigation**: Arrow keys work
- **Performance**: Lazy-loading for images after first slide

---

## 🎨 Admin Interface Features

### Logo Admin List View

- 🏠 **Icon indicators** for logo type
- **Preview thumbnail** in list
- **Status badge** (Active/Inactive)
- **Upload date** and uploader tracking

### Slider Admin List View

- **Order number** (#0, #1, #2...)
- **Image preview** thumbnail
- **Title** with fallback for untitled slides
- **Status badges**:
  - ✓ ACTIVE (green)
  - ⊘ INACTIVE (gray)
  - 🗑️ DELETED (red)
- **Creation date** tracking

### Edit View Features

- **Large image preview** - See current logo/slide
- **Upload history** - Who uploaded and when
- **Validation** - Automatic file type/size checking
- **Audit trail** - All changes logged

---

## 📋 Common Workflows

### Workflow 1: Brand Redesign (Change Logo)

1. Go to **Branding & Presentation** → **Logos**
2. Click on "Main Logo (Header)"
3. Upload new logo file
4. Verify preview looks correct
5. Click "Save"
6. Refresh website to see new logo

**Result**: New logo appears on all pages immediately

---

### Workflow 2: Create Homepage Slider

1. Go to **Branding & Presentation** → **Presentation Slider**
2. Click "Add Presentation Slide" (repeat for each slide)
3. For each slide:
   - Upload high-quality image (1920x1080px recommended)
   - Add descriptive title
   - Set display order (0, 1, 2, 3...)
   - Check "Is Active"
   - Save
4. Visit homepage to see slider

**Result**: Beautiful rotating slider on homepage

---

### Workflow 3: Temporarily Hide Slider

1. Go to **Presentation Slider** admin
2. Select all slides (checkbox at top)
3. Choose "⊘ Deactivate selected slides"
4. Click "Go"

**Result**: Slider disappears from homepage (but slides remain in database)

**To restore**: Repeat with "✓ Activate selected slides"

---

### Workflow 4: Seasonal Promotion Slider

**December: Add holiday slides**
1. Create 3-5 slides with promotional images
2. Set display order 0-4
3. Activate all

**January: Switch back to regular slides**
1. Select holiday slides
2. Soft delete them
3. Select regular slides
4. Restore them

**Result**: Easy seasonal content switching without losing slides

---

## 🔒 Security & Permissions

### File Validation

- **Server-side checks** prevent malicious uploads
- **File type restrictions** (images only)
- **Size limits** enforced automatically
- **Image integrity** verified on upload

### Permission Levels

| Action | Staff | Superuser |
|--------|-------|-----------|
| View logos/slides | ✓ | ✓ |
| Add/edit logos/slides | ✓ | ✓ |
| Soft delete slides | ✓ | ✓ |
| Hard delete (permanent) | ✗ | ✓ only |

### Audit Logging

All changes are logged:
- Who uploaded/modified
- When the change occurred
- What was changed

Check logs at: `logs/django.log` (search for `[branding]`)

---

## 🚨 Troubleshooting

### Logo Not Appearing

**Symptom**: Uploaded logo but still seeing text brand name

**Solutions**:
1. Check "Is Active" is checked on logo
2. Verify logo uploaded successfully (see preview in admin)
3. Clear browser cache (Ctrl+Shift+R)
4. Check image file is valid (not corrupted)

---

### Slider Not Showing

**Symptom**: Homepage has no slider

**Solutions**:
1. Verify at least one slide is Active
2. Check slides aren't soft-deleted
3. Clear browser cache
4. Check image files uploaded successfully

---

### Upload Failed

**Symptom**: "Validation error" when uploading

**Common Causes**:
- File too large (>5MB for logos, >10MB for slides)
- Wrong file format
- Image dimensions too small (slides need min 800px width)
- Corrupted image file

**Solutions**:
- Resize/compress image
- Convert to supported format (PNG, JPG, WEBP)
- Try different image file

---

### Slider Order Wrong

**Symptom**: Slides appear in unexpected order

**Solution**:
- Check "Display Order" numbers
- Lower numbers appear first (0, 1, 2, 3...)
- Duplicate numbers may cause unpredictable ordering

---

## 💡 Best Practices

### Logo Guidelines

✅ **DO**:
- Use SVG for scalability
- Keep logos simple and clear
- Use transparent backgrounds (PNG)
- Test on both light and dark backgrounds
- Maintain consistent branding

✗ **DON'T**:
- Use overly complex logos
- Upload logos with too much text
- Use low-resolution images
- Forget to set alt text (accessibility)

### Slider Guidelines

✅ **DO**:
- Use high-quality images (1920x1080px)
- Keep text overlays short and readable
- Use 3-7 slides (optimal range)
- Test on mobile devices
- Use consistent image styles/colors
- Compress images before upload

✗ **DON'T**:
- Upload 50+ slides (performance issues)
- Use images with busy backgrounds
- Put critical text in images (use title field)
- Forget to set display order
- Use portrait images (use landscape 16:9)

### Content Strategy

**Homepage Slider Ideas**:
- Featured house plans
- Seasonal promotions
- Customer testimonials
- Building process showcase
- Before/after comparisons

**Optimal Slider Count**: 3-5 slides
- Too few: Looks empty
- Too many: Users won't see all

---

## 📱 Mobile Responsiveness

### Automatic Adaptations

**Logos**:
- Scale to fit mobile screens
- Max height maintained proportionally

**Slider**:
- Height adjusts: 400px (desktop) → 300px (tablet) → 250px (mobile)
- Touch swipe gestures enabled
- Buttons sized for finger taps
- Text overlays resize automatically

---

## 🎓 Quick Reference

### Admin URLs

- **Logo Management**: `/admin/branding/logo/`
- **Slider Management**: `/admin/branding/presentationslider/`

### Keyboard Shortcuts (Slider)

- `←` Left Arrow: Previous slide
- `→` Right Arrow: Next slide
- `Spacebar`: Pause/resume (when focused)

### File Paths (for reference)

- Logos stored in: `media/branding/logos/`
- Slider images in: `media/presentation/slider/`

---

## ✅ Testing Checklist

After making branding changes:

- [ ] Check homepage on desktop
- [ ] Check homepage on mobile
- [ ] Test slider navigation (arrows, dots)
- [ ] Verify logo appears in header
- [ ] Verify logo appears in footer
- [ ] Check favicon in browser tab
- [ ] Test slider touch swipe on mobile
- [ ] Verify images load quickly
- [ ] Check text overlays are readable
- [ ] Confirm links work (if added)

---

## 🆘 Support

If you encounter issues not covered in this guide:

1. Check Django admin logs: `/admin/`
2. Review server logs: `logs/django.log`
3. Verify database migrations applied: `python manage.py migrate branding`
4. Clear browser cache completely
5. Test in incognito/private browsing mode

---

## 📊 Summary

**Branding System Features**:
- ✅ Admin-controlled logos (main, footer, favicon)
- ✅ Presentation slider with ordering
- ✅ No code changes required
- ✅ Instant updates across site
- ✅ Full audit trail
- ✅ Mobile-responsive
- ✅ Secure file validation
- ✅ Soft delete protection

**Everything is managed through**: `/admin/branding/`

No developer needed for visual updates! 🎉
