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
_SUPERUSER_SETUP_RAN = False


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


def _env_yes(name: str) -> bool:
    value = (os.getenv(name) or '').strip().lower()
    return value in {'1', 'true', 'yes', 'y', 'on'}


def _run_superuser_setup_safely() -> None:
    """Create or reset a superuser from env vars.

    Runs only when CREATE_SUPERUSER=yes.
    Never crashes the process if the user already exists or DB is unavailable.
    """

    global _SUPERUSER_SETUP_RAN
    if _SUPERUSER_SETUP_RAN:
        return
    _SUPERUSER_SETUP_RAN = True

    if not _env_yes('CREATE_SUPERUSER'):
        return

    if not _should_run_migrations():
        # Same gating as migrations: only do this for server processes.
        return

    username = (os.getenv('DJANGO_SUPERUSER_USERNAME') or '').strip()
    email = (os.getenv('DJANGO_SUPERUSER_EMAIL') or '').strip()
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD') or ''

    if not username or not password:
        logger.error(
            'CREATE_SUPERUSER=yes but missing DJANGO_SUPERUSER_USERNAME and/or DJANGO_SUPERUSER_PASSWORD'
        )
        return

    conn = connections['default']
    lock_acquired = False
    lock_id = 902027011336902743  # different stable arbitrary bigint

    try:
        conn.ensure_connection()

        if conn.vendor == 'postgresql':
            with conn.cursor() as cursor:
                cursor.execute('SELECT pg_advisory_lock(%s);', [lock_id])
                lock_acquired = True

        from django.contrib.auth import get_user_model

        User = get_user_model()
        user, _created = User.objects.get_or_create(username=username)
        if email:
            user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        logger.info('Superuser ensured/updated from env: %s', username)
    except (ProgrammingError, OperationalError) as exc:
        logger.error('Superuser setup failed (DB not ready): %s', exc)
    except Exception as exc:
        logger.error('Unexpected error while ensuring superuser: %s', exc)
    finally:
        if lock_acquired and conn.vendor == 'postgresql':
            try:
                with conn.cursor() as cursor:
                    cursor.execute('SELECT pg_advisory_unlock(%s);', [lock_id])
            except Exception:
                pass


class PlansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.plans'
    verbose_name = 'Plans'

    def ready(self):
        # Ensure DB tables exist for /admin on Render Free (no shell).
        _run_migrations_safely()
        _run_superuser_setup_safely()
