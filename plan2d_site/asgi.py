"""ASGI config for completeness.

Render deployment uses WSGI/Gunicorn, but we keep ASGI correct and importable.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan2d_site.settings")

application = get_asgi_application()
