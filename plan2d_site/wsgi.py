"""WSGI config for Render/Gunicorn.

Entrypoint: gunicorn plan2d_site.wsgi:application
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan2d_site.settings")

application = get_wsgi_application()
