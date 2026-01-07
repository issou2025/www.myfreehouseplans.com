#!/usr/bin/env python
"""
Compile translation files (.po to .mo) using Django's built-in compiler.
This script works without requiring gettext to be installed on Windows.
"""
import os
import sys
from pathlib import Path

# Add the project to the path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
import django
django.setup()

from django.core.management import call_command

# Compile messages
try:
    call_command('compilemessages', verbosity=2)
    print("\n✓ Translation files compiled successfully!")
except Exception as e:
    print(f"\n✗ Error compiling messages: {e}")
    print("\nNote: If gettext is not installed, you may need to install it.")
    print("For Windows, you can download from: https://mlocati.github.io/articles/gettext-iconv-windows.html")
