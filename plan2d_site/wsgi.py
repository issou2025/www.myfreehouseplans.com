"""WSGI config for Render/Gunicorn.

Render Free plan provides no shell access. To ensure database tables exist
before the app serves traffic, we run migrations programmatically on WSGI
startup.

Entrypoint: gunicorn plan2d_site.wsgi:application
"""

from __future__ import annotations

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan2d_site.settings")

from django.conf import settings
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from django.db import connections


def _run_startup_migrations() -> None:
	"""Run migrations once per process startup.

	Uses a Postgres advisory lock to avoid concurrent `migrate` executions
	when Gunicorn starts multiple workers.
	"""

	# Ensure Django settings are loaded
	if not settings.configured:  # pragma: no cover
		return

	conn = connections["default"]
	lock_acquired = False

	try:
		conn.ensure_connection()

		if conn.vendor == "postgresql":
			# Stable, app-specific bigint lock id.
			lock_id = 902027011336902742  # arbitrary constant
			with conn.cursor() as cursor:
				cursor.execute("SELECT pg_advisory_lock(%s);", [lock_id])
				lock_acquired = True

		# No interactive prompts, safe for CI/build/startup.
		call_command("migrate", interactive=False, verbosity=1)
	finally:
		if lock_acquired and conn.vendor == "postgresql":
			try:
				with conn.cursor() as cursor:
					cursor.execute("SELECT pg_advisory_unlock(%s);", [lock_id])
			except Exception:
				# If unlock fails, process exit will release the advisory lock.
				pass


_run_startup_migrations()

application = get_wsgi_application()
