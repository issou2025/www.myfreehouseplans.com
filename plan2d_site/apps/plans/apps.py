from __future__ import annotations

import logging
import os
import sys

from django.apps import AppConfig
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError, ProgrammingError


logger = logging.getLogger('plans')


_MIGRATIONS_RAN = False


def _should_run_migrations() -> bool:
    """Return True only when running a server process.

    Avoid recursion when the current process is already a management command.
    """

    argv = " ".join(sys.argv).lower()
    management_markers = (
        "makemigrations",
        "migrate",
        "collectstatic",
        "createsuperuser",
        "shell",
        "dbshell",
        "test",
    )
    if any(marker in argv for marker in management_markers):
        return False

    # Only run for typical server entrypoints.
    server_markers = ("gunicorn", "uwsgi", "daphne", "runserver")
    if any(marker in argv for marker in server_markers):
        return True

    # On Render, gunicorn is typical; keep a conservative fallback.
    if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"):
        return True

    return False


def _run_migrations_safely() -> None:
    """Run migrations without ever crashing the process."""

    global _MIGRATIONS_RAN
    if _MIGRATIONS_RAN:
        return
    _MIGRATIONS_RAN = True

    if not _should_run_migrations():
        return

    conn = connections["default"]
    lock_acquired = False
    lock_id = 902027011336902742  # stable arbitrary bigint

    try:
        conn.ensure_connection()

        if conn.vendor == "postgresql":
            with conn.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_lock(%s);", [lock_id])
                lock_acquired = True

        call_command("migrate", interactive=False, verbosity=1)
        logger.info("Startup migrations completed")
    except (ProgrammingError, OperationalError) as exc:
        # Never crash admin/site if DB is temporarily unavailable.
        logger.error("Startup migrations failed: %s", exc)
    except Exception as exc:
        logger.error("Unexpected error while running startup migrations: %s", exc)
    finally:
        if lock_acquired and conn.vendor == "postgresql":
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_unlock(%s);", [lock_id])
            except Exception:
                pass


class PlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.plans'
    verbose_name = 'Plans'

    def ready(self):
        # Ensure DB tables exist for /admin on Render Free (no shell).
        _run_migrations_safely()
