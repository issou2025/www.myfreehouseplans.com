#!/usr/bin/env python
"""
Test i18n implementation - verify translations work correctly.
"""
import os
import sys
from pathlib import Path

# Setup Django
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

import django
django.setup()

from django.utils.translation import activate, gettext, get_language
from django.conf import settings

print("=" * 60)
print("Django i18n Configuration Test")
print("=" * 60)

# Test 1: Check settings
print("\n1. Settings Configuration:")
print(f"   - Default language: {settings.LANGUAGE_CODE}")
print(f"   - Supported languages: {settings.LANGUAGES}")
print(f"   - USE_I18N: {settings.USE_I18N}")
print(f"   - Locale paths: {settings.LOCALE_PATHS}")

# Test 2: Check current language
print(f"\n2. Current Language: {get_language()}")

# Test 3: Test English translations
print("\n3. English Translations:")
activate('en')
test_strings = [
    "Home",
    "Plans",
    "About",
    "Contact",
    "Browse Plans",
]
for s in test_strings:
    translated = gettext(s)
    print(f"   - '{s}' -> '{translated}'")

# Test 4: Test French translations
print("\n4. French Translations:")
activate('fr')
for s in test_strings:
    translated = gettext(s)
    status = "✓" if translated != s else "✗"
    print(f"   {status} '{s}' -> '{translated}'")

# Test 5: Check .mo file exists
print("\n5. Translation Files:")
for lang_code, lang_name in settings.LANGUAGES:
    mo_file = project_root / 'locale' / lang_code / 'LC_MESSAGES' / 'django.mo'
    if mo_file.exists():
        size = mo_file.stat().st_size
        print(f"   ✓ {lang_name} ({lang_code}): {mo_file.name} ({size} bytes)")
    else:
        print(f"   ✗ {lang_name} ({lang_code}): File not found")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
