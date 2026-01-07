# Pack Delivery System: ZIP Structure & Gumroad Integration

## Overview
Pack 2 (Standard) and Pack 3 (Pro BIM) are delivered as ZIP archives hosted on Gumroad. Each ZIP contains both Metric and Imperial versions of all deliverables in separate folders.

## ZIP Structure

### Pack 2 (Standard Build Set)
```
PACK2-Standard-{plan_reference}.zip
├─ metric/
│   ├─ full-set.pdf
│   ├─ schedules.xlsx (optional)
│   └─ notes.txt (optional)
└─ imperial/
    ├─ full-set-imperial.pdf
    ├─ schedules-ft.xlsx (optional)
    └─ notes.txt (optional)
```

### Pack 3 (Pro BIM)
```
PACK3-Pro-{plan_reference}.zip
├─ metric/
│   ├─ editable.rvt
│   ├─ coordination.ifc
│   ├─ dwg/
│   │   ├─ floor-plans.dwg
│   │   └─ elevations.dwg
│   └─ README.txt
└─ imperial/
    ├─ editable-imperial.rvt
    ├─ coordination-imperial.ifc
    ├─ dwg/
    │   ├─ floor-plans-ft.dwg
    │   └─ elevations-ft.dwg
    └─ README.txt
```

## Naming Convention
- **Pack 2:** `PACK2-Standard-{plan_reference}.zip`
- **Pack 3:** `PACK3-Pro-{plan_reference}.zip`
- **Plan reference:** Use the auto-generated reference from Django (e.g., `FHP-2026-0007`)

## Folder Requirements
1. **Mandatory folders:** `/metric/` and `/imperial/` at root level
2. **No root files:** All content must be inside one of these folders
3. **Consistent structure:** Both folders should mirror each other in file structure
4. **Non-empty:** Both folders must contain at least one file

## Gumroad Integration Workflow

### 1. Prepare ZIP Files
1. Gather all metric and imperial files for the pack
2. Organize into `/metric/` and `/imperial/` folders locally
3. Create ZIP using naming convention
4. Run validation script:
   ```bash
   python tools/validate_pack_zip.py PACK2-Standard-FHP-2026-0007.zip
   ```

### 2. Upload to Gumroad
1. Log into Gumroad dashboard
2. Create new product or edit existing one
3. Navigate to "Content" section
4. Upload the ZIP file
5. Set product name, price, and description
6. Copy the Gumroad product URL or ID

### 3. Configure in Django Admin
1. Open the Plan in Django Admin
2. Navigate to Pack 2 or Pack 3 fieldset
3. Paste Gumroad ZIP checkout URL in the appropriate field:
    - Pack 2: `pack_2_gumroad_zip_url`
    - Pack 3: `pack_3_gumroad_zip_url`
4. Save the plan

### 4. Update Existing ZIPs
To update a ZIP without changing URLs:
1. Prepare new ZIP with same filename
2. Upload to same Gumroad product (replaces old file)
3. Click "Save" in Gumroad
4. Buyers immediately get new version
5. No Django changes needed

## Validation Script
The `validate_pack_zip.py` script ensures ZIP structure compliance:

```bash
# Validate Pack 2 ZIP
python tools/validate_pack_zip.py PACK2-Standard-FHP-2026-0007.zip

# Validate Pack 3 ZIP
python tools/validate_pack_zip.py PACK3-Pro-FHP-2026-0007.zip
```

### What It Checks
- ✓ Correct naming convention
- ✓ `/metric/` and `/imperial/` folders exist
- ✓ Both folders are non-empty
- ✓ No files outside required folders
- ✓ ZIP is valid and not corrupted

## Admin Fields

### Pack 2 ZIP URL (`pack_2_gumroad_zip_url`)
- **Location:** Plan admin → Pack 2 · Standard Build Set
- **Purpose:** Store the single Gumroad checkout URL delivering the ZIP (Metric + Imperial PDFs)
- **Format:** Full HTTPS URL to a Gumroad product
- **Help text:** Reminds admins that the ZIP must already contain both unit folders

### Pack 3 ZIP URL (`pack_3_gumroad_zip_url`)
- **Location:** Plan admin → Pack 3 · Pro BIM — IFC
- **Purpose:** Store the single Gumroad checkout URL delivering the Pro BIM ZIP (Metric + Imperial Revit/IFC/DWG)
- **Format:** Full HTTPS URL to a Gumroad product
- **Help text:** Notes that the ZIP must bundle every premium asset for both unit systems

## Buyer Experience
1. Customer visits plan page
2. Clicks "Buy" button for Pack 2 or Pack 3
3. Redirected to Gumroad checkout
4. Completes payment
5. Receives email with download link
6. Downloads ZIP containing both metric and imperial files
7. Extracts and uses preferred unit system

## Backend Impact
- **No frontend changes:** Existing templates and CTAs unchanged
- **No delivery logic:** Gumroad handles all file hosting and delivery
- **No storage overhead:** ZIPs hosted on Gumroad, not Django
- **Backward compatible:** Existing URL fields and toggles remain functional

## Quality Checklist
Before uploading any ZIP:
- [ ] Correct filename format used
- [ ] `/metric/` folder exists and contains files
- [ ] `/imperial/` folder exists and contains files
- [ ] No files in ZIP root
- [ ] Validation script passes
- [ ] File sizes reasonable (< 500MB recommended)
- [ ] Gumroad product configured with correct price
- [ ] Django admin reference field updated

## Future Scaling
To add Pack 4 or beyond:
1. Add new `pack4_zip_gumroad_reference` field to Plan model
2. Update admin fieldsets to include new field
3. Follow same ZIP structure: `/metric/` + `/imperial/`
4. Use naming: `PACK4-{Name}-{reference}.zip`
5. Run validation script before upload

## Support & Troubleshooting

### ZIP won't upload to Gumroad
- Check file size (Gumroad has limits)
- Ensure ZIP is valid (test extraction locally)
- Try renaming to remove special characters

### Buyer reports missing files
- Re-run validation script on original ZIP
- Check Gumroad product shows correct file
- Verify both folders are populated

### Need to update just one unit system
- Create new ZIP with both folders (requirement)
- Update the unchanged folder with same files
- Upload to replace existing Gumroad file

---

**Last Updated:** January 2026  
**Validation Script:** `tools/validate_pack_zip.py`  
**Model Fields:** `pack_2_gumroad_zip_url`, `pack_3_gumroad_zip_url`
