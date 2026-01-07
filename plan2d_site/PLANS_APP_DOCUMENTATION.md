# Plans App - Models & Admin Documentation

## Overview

The Plans app manages the core business logic for the house plans catalog, including categories, plans, and associated images.

## Models

### 1. Category

Organizes plans into logical groups (e.g., Modern, Traditional, Bungalow).

**Fields:**
- `name`: Category display name (unique)
- `slug`: URL-friendly identifier (auto-generated)
- `description`: Optional category description
- `display_order`: Controls display order (lower numbers first)
- `is_active`: Toggle visibility
- `created_at`, `updated_at`: Timestamps

**Methods:**
- Auto-generates slug from name on save

### 2. Plan

Core model representing a construction-ready 2D floor plan.

**Basic Information:**
- `title`: Display name (200 chars)
- `slug`: Auto-generated URL identifier
- `reference`: Internal reference code (e.g., PL-2024-001) - unique
- `category`: Foreign key to Category
- `plan_type`: Choice field (residential, commercial, mixed, other)

**Specifications:**
- `bedrooms`: Number of bedrooms (integer)
- `bathrooms`: Number of bathrooms (decimal for half baths)
- `total_area_sqm`: Total area in square meters
- `total_area_sqft`: Auto-calculated from sqm (read-only)

**Content:**
- `description`: Public-facing description
- `engineer_notes`: Internal notes (not visible to customers)

**Files:**
- `free_plan_file`: Preview plan without dimensions (PDF)
- `paid_plan_file`: Full plan with dimensions (PDF)

**Pricing:**
- `price`: Price in USD (decimal)

**Status:**
- `is_published`: Toggle public visibility
- `featured`: Mark as featured
- `views_count`: Track views (auto-incremented)
- `downloads_count`: Track downloads (auto-incremented)

**Methods:**
- Auto-generates slug from title
- Auto-calculates square feet from square meters
- `has_free_plan` property: Check if free plan exists
- `has_paid_plan` property: Check if paid plan exists

**Indexes:**
- slug (for fast lookups)
- is_published + created_at (for published plan queries)
- category + is_published (for category filtering)

### 3. PlanImage

Images associated with plans (floor plans, elevations, renders, etc.).

**Fields:**
- `plan`: Foreign key to Plan
- `image`: ImageField uploaded to plans/images/
- `image_type`: Choice field (floor_plan, elevation, section, 3d_render, photo, other)
- `caption`: Optional image caption
- `display_order`: Controls display order
- `is_primary`: Mark as main thumbnail
- `created_at`: Timestamp

**Methods:**
- Auto-removes primary flag from other images when marking new primary

## Django Admin Configuration

### Category Admin

**List View:**
- Displays: name, slug, plan count, display order, active status, updated date
- Filters: is_active, created_at
- Search: name, description
- Ordering: display_order, name

**Form:**
- Auto-generates slug from name (prepopulated field)
- Grouped fieldsets for clarity

### Plan Admin

**List View:**
- Displays: reference, title, category, bedrooms, bathrooms, area, price, status badge, files status, updated date
- Filters: published status, featured, category, plan type, bedrooms, created date
- Search: title, reference, description, engineer notes
- 25 items per page
- Date hierarchy navigation

**Custom Display Columns:**
- `total_area_display`: Shows both m² and ft²
- `status_badge`: Visual badge (Draft, Published, Featured)
- `files_status`: Shows which files are uploaded (icons)

**Form Organization:**
Grouped into logical fieldsets:
1. **Basic Information**: title, slug, reference, category, plan type
2. **Specifications**: bedrooms, bathrooms, areas
3. **Content**: description, engineer notes
4. **Files**: free/paid plan files
5. **Pricing & Publishing**: price, published status, featured
6. **Statistics**: views, downloads, timestamps (collapsed, read-only)

**Features:**
- Slug auto-populated from title
- Inline image management (add images without leaving plan page)
- Read-only calculated fields (sqft, stats)
- Bulk actions: publish, unpublish, mark as featured

### PlanImage Admin

**List View:**
- Displays: plan, image type, caption, primary status, display order, preview
- Filters: image type, is_primary, created date
- Search: plan title, plan reference, caption
- Editable: display_order (can be changed directly in list)

**Features:**
- Image preview in list view (50px height thumbnail)
- Can be managed inline within Plan admin

## Usage Guide for Engineers

### Adding a New Plan

1. **Navigate to Plans → Plans → Add Plan**

2. **Basic Information:**
   - Enter a descriptive title (slug auto-generates)
   - Create unique reference code (e.g., PL-2026-001)
   - Select category
   - Choose plan type

3. **Specifications:**
   - Enter bedrooms and bathrooms
   - Enter total area in m² (square feet calculates automatically)

4. **Content:**
   - Write public description
   - Add internal engineer notes if needed

5. **Files:**
   - Upload free preview PDF (without dimensions)
   - Upload paid full PDF (with dimensions)

6. **Pricing:**
   - Set price in USD

7. **Publishing:**
   - Check "Is published" when ready to go live
   - Check "Featured" for homepage/featured sections

8. **Images:**
   - Add images using the inline form at bottom
   - Mark one as primary for thumbnails
   - Set display order for image gallery

### Managing Categories

1. **Navigate to Plans → Categories**
2. Set display order (lower numbers appear first)
3. Categories protect their plans (can't delete if plans exist)

### Bulk Operations

Select multiple plans in list view:
- **Publish selected plans**: Make multiple plans live
- **Unpublish selected plans**: Remove from public view
- **Mark as featured**: Feature and publish simultaneously

### Tips for Efficient Workflow

1. **Use Filters**: Filter by publication status, category, bedrooms
2. **Search**: Search by reference code or keywords
3. **Date Hierarchy**: Navigate plans by creation date
4. **Inline Images**: Add all images while creating the plan
5. **Engineer Notes**: Use for internal documentation

## File Upload Structure

```
media/
├── plans/
│   ├── free/
│   │   └── 2026/
│   │       └── 01/
│   │           └── plan_files.pdf
│   ├── paid/
│   │   └── 2026/
│   │       └── 01/
│   │           └── plan_files.pdf
│   └── images/
│       └── 2026/
│           └── 01/
│               └── image_files.jpg
```

Files are automatically organized by year and month.

## Database Relationships

```
Category (1) ─────< (many) Plan (1) ─────< (many) PlanImage
```

- One Category has many Plans
- One Plan has many PlanImages
- Plans are protected (can't delete category if plans exist)
- Deleting a plan cascades to delete its images

## Admin Access

**URL:** http://127.0.0.1:8000/admin/

**Test Credentials:**
- Username: `admin`
- Password: `admin123`

**Change in production!**

## Next Steps

1. ✅ Models created and migrated
2. ✅ Admin interface configured
3. ⏳ Create frontend views for displaying plans
4. ⏳ Implement payment integration
5. ⏳ Add download tracking
6. ⏳ Create SEO features
