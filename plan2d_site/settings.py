"""Canonical settings module for Render/Gunicorn.

This project historically used `config.settings.dev` / `config.settings.prod`.
Render and Gunicorn in this deployment expect `plan2d_site.settings`.

We keep existing settings packages intact and import the appropriate one.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None


REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = REPO_ROOT / "plan2d_site"

# Load local environment variables from repo-root .env (if present).
# Render provides env vars directly; .env is not required in production.
if load_dotenv is not None:
    load_dotenv(REPO_ROOT / ".env")

# Ensure legacy layout (apps/, config/, templates/, static/) is importable
# when running from the repository root (Render/Gunicorn).
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _select_settings_module() -> str:
    # Explicit override wins
    env = (os.getenv("DJANGO_ENV") or "").strip().lower()
    if env in {"dev", "development"}:
        return "config.settings.dev"
    if env in {"prod", "production"}:
        return "config.settings.prod"

    # Render commonly sets RENDER/RENDER_SERVICE_ID.
    if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"):
        return "config.settings.prod"

    # Local default: dev, so commands work without requiring DATABASE_URL/SECRET_KEY.
    return "config.settings.dev"


_selected = _select_settings_module()

if _selected == "config.settings.prod":
    from config.settings.prod import *  # noqa: F403
else:
    from config.settings.dev import *  # noqa: F403

# Enforce canonical entrypoints (required by deployment spec)
ROOT_URLCONF = "plan2d_site.urls"
WSGI_APPLICATION = "plan2d_site.wsgi.application"
ASGI_APPLICATION = "plan2d_site.asgi.application"
