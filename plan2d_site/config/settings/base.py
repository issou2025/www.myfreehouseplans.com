"""
Django base settings for plan2d_site project.
SEO-first architecture for a 2D house plans website.
"""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def _env_bool(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_csv(name: str, default=None):
    raw = os.getenv(name)
    if raw is None:
        return default if default is not None else []
    return [item.strip() for item in raw.split(',') if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY') or os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_bool('DEBUG', default=False)

ALLOWED_HOSTS = _env_csv('ALLOWED_HOSTS', default=[])

if not SECRET_KEY:
    # Allow a safe dev fallback; production settings should always inject a real secret.
    if DEBUG:
        SECRET_KEY = 'django-insecure-development-only'
    else:
        raise ImproperlyConfigured('SECRET_KEY environment variable is required when DEBUG is False')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    
    # Local apps
    'apps.core',
    'apps.plans',
    'apps.seo',
    'apps.orders',
    'apps.analytics',
    'apps.notifications',
    'apps.branding',  # Logo & presentation slider management
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # Language detection
    'django.middleware.common.CommonMiddleware',
    'apps.analytics.middleware.VisitTrackingMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',  # i18n context
                'apps.core.context_processors.brand',  # Brand + domain context
                'apps.branding.context_processors.branding_context',  # Site logos
                'apps.branding.context_processors.slider_context',  # Presentation slider
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/stable/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/stable/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/stable/topics/i18n/

LANGUAGE_CODE = 'en'  # Default language

LANGUAGES = [
    ('en', 'English'),
    ('fr', 'Français'),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/stable/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/stable/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration
# For development: console backend (prints to terminal)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ----------------------------
# Brand + SEO (FreeHousePlan)
# ----------------------------
BRAND_NAME = os.getenv('BRAND_NAME', 'FreeHousePlan')
BRAND_DOMAIN = os.getenv('BRAND_DOMAIN', 'www.myfreehouseplans.com')
BRAND_TAGLINE = os.getenv(
    'BRAND_TAGLINE',
    "Free house plans. Upgrade when you're ready to build.",
)

# Public-facing base URL used for canonical URLs and branding.
# Keep this as your production domain (even during local dev).
SITE_BASE_URL = os.getenv('SITE_BASE_URL', f"https://{BRAND_DOMAIN}").rstrip('/')

# Backwards compatibility (some code/docs reference SITE_URL)
SITE_URL = os.getenv('SITE_URL', SITE_BASE_URL)

SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@myfreehouseplans.com')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', f"{BRAND_DOMAIN} <noreply@myfreehouseplans.com>")

# Admin Contact Information
ADMIN_EMAIL = 'entreprise2rc@gmail.com'
ADMIN_WHATSAPP = '+22796380877'

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Allowed file types for contact form
CONTACT_ALLOWED_FILE_TYPES = ['pdf', 'jpg', 'jpeg', 'png', 'zip']

# ----------------------------
# Privacy-respecting analytics
# ----------------------------
# Stores only: URL path, country code (ISO), device type, timestamp.
# Never stores IP addresses or personal identifiers.
ANALYTICS_ENABLED = True
ANALYTICS_THROTTLE_SECONDS = 60

# Optional GeoIP2 support:
# If you download a GeoLite2 Country database (mmdb), set GEOIP_PATH to the folder path.
# Example: GEOIP_PATH = BASE_DIR / 'geoip'

# ----------------------------
# Logging Configuration
# ----------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '{levelname}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'app.log',
            'formatter': 'verbose',
        },
        'notifications_file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'notifications.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'notifications': {
            'handlers': ['console', 'notifications_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'orders': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
