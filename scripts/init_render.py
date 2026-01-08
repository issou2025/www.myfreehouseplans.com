from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def _env_yes(name: str) -> bool:
    value = (os.getenv(name) or "").strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _configure_django() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    project_root = repo_root / "plan2d_site"
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan2d_site.settings")


def _run_migrations() -> None:
    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=1)


def _ensure_superuser() -> None:
    """Delete + recreate the superuser when CREATE_SUPERUSER=yes."""

    if not _env_yes("CREATE_SUPERUSER"):
        return

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or ""

    if not username or not password:
        raise SystemExit(
            "CREATE_SUPERUSER=yes requires DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD"
        )

    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Requirement: delete existing superuser with same username (if exists), then recreate.
    User.objects.filter(username=username).delete()
    User.objects.create_superuser(username=username, email=email, password=password)


def main() -> int:
    _configure_django()

    import django
    from django.db.utils import OperationalError, ProgrammingError

    django.setup()

    # Migrations must succeed before Gunicorn serves /admin.
    retries = 5
    delay = 2.0
    for attempt in range(1, retries + 1):
        try:
            _run_migrations()
            break
        except (OperationalError, ProgrammingError) as exc:
            if attempt >= retries:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 30.0)

    # Superuser create/reset is optional and gated.
    _ensure_superuser()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
