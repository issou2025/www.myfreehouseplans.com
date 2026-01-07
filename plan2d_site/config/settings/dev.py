"""
Development settings for plan2d_site project.
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development-specific apps
INSTALLED_APPS += [
    # Add dev-only apps here if needed
]

# Database override for development (optional)
# DATABASES['default']['NAME'] = BASE_DIR / 'db_dev.sqlite3'

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security settings relaxed for development
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
