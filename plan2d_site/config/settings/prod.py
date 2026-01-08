"""
Production settings for plan2d_site project.
"""
import os
from .base import *

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# Env compatibility: accept both Render-style names and legacy DJANGO_* names.
_secret_from_env = os.getenv('SECRET_KEY') or os.getenv('DJANGO_SECRET_KEY')
if not _secret_from_env:
    raise ImproperlyConfigured('SECRET_KEY environment variable is required in production')

SECRET_KEY = _secret_from_env

# Allow Render service domains (no wildcard "*" in ALLOWED_HOSTS)
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.onrender.com',
]

# Database (Render provides DATABASE_URL)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', ''),
        conn_max_age=600,
        ssl_require=True,
    )
}

if not DATABASES['default']:
    raise ImproperlyConfigured('DATABASE_URL environment variable is required in production')

# Static files (serve via WhiteNoise)
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
]

# HSTS settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')


