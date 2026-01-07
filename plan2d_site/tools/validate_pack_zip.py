#!/usr/bin/env python3
"""
ZIP Structure Validator for Pack 2 and Pack 3 Deliverables

Usage:
    python validate_pack_zip.py PACK2-Standard-FHP-2026-0007.zip
    python validate_pack_zip.py PACK3-Pro-FHP-2026-0007.zip

Validates that:
- ZIP contains /metric/ and /imperial/ folders
- Both folders are non-empty
- Naming convention is correct
- No files exist outside the required folders
"""

import sys
import zipfile
from pathlib import Path


def validate_pack_zip(zip_path: str) -> tuple[bool, list[str]]:
    """
    Validate ZIP structure for Pack 2 or Pack 3 delivery.
    
    Returns:
        (is_valid, error_messages)
    """
    errors = []
    zip_file = Path(zip_path)
    
    if not zip_file.exists():
        return False, [f"File not found: {zip_path}"]
    
    if not zip_file.suffix.lower() == '.zip':
        return False, [f"Not a ZIP file: {zip_path}"]
    
    # Extract pack type and reference from filename
    filename = zip_file.stem
    if not (filename.startswith('PACK2-Standard-') or filename.startswith('PACK3-Pro-')):
        errors.append(f"Invalid naming convention. Expected: PACK2-Standard-{{ref}}.zip or PACK3-Pro-{{ref}}.zip")
    
    try:
        with zipfile.ZipFile(zip_file, 'r') as zf:
            all_names = zf.namelist()
            
            # Check for required folders
            has_metric = any(name.startswith('metric/') for name in all_names)
            has_imperial = any(name.startswith('imperial/') for name in all_names)
            
            if not has_metric:
                errors.append("Missing required /metric/ folder")
            if not has_imperial:
                errors.append("Missing required /imperial/ folder")
            
            # Check for files outside metric/imperial folders
            root_files = [n for n in all_names if '/' not in n or (not n.startswith('metric/') and not n.startswith('imperial/'))]
            if root_files:
                errors.append(f"Files outside /metric/ and /imperial/ folders: {root_files}")
            
            # Check that folders are non-empty
            metric_files = [n for n in all_names if n.startswith('metric/') and n != 'metric/']
            imperial_files = [n for n in all_names if n.startswith('imperial/') and n != 'imperial/']
            
            if has_metric and not metric_files:
                errors.append("/metric/ folder is empty")
            if has_imperial and not imperial_files:
                errors.append("/imperial/ folder is empty")
            
            # Report structure
            if not errors:
                print(f"✓ Valid ZIP structure for {filename}")
                print(f"  /metric/ contains {len(metric_files)} file(s)")
                print(f"  /imperial/ contains {len(imperial_files)} file(s)")
                return True, []
    
    except zipfile.BadZipFile:
        return False, ["Corrupted or invalid ZIP file"]
    except Exception as e:
        return False, [f"Error reading ZIP: {str(e)}"]
    
    return False, errors


def main():
    if len(sys.argv) != 2:
        print("Usage: python validate_pack_zip.py <path-to-zip>")
        sys.exit(1)
    
    zip_path = sys.argv[1]
    is_valid, errors = validate_pack_zip(zip_path)
    
    if is_valid:
        print("\n✓ ZIP validation passed")
        sys.exit(0)
    else:
        print("\n✗ ZIP validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == '__main__':
    main()
