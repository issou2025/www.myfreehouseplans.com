import os

from django.contrib.auth import get_user_model


User = get_user_model()


def main() -> None:
    """Create or update a superuser from env vars.

    This script is kept for local convenience, but it must never hardcode
    credentials (to avoid leaking passwords in git).
    """

    username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "admin").strip()
    email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or ""

    if not password:
        raise SystemExit("DJANGO_SUPERUSER_PASSWORD is required")

    user, _ = User.objects.get_or_create(username=username)
    if email:
        user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.set_password(password)
    user.save()
    print(f"✅ Superuser ensured: {user.username}")


if __name__ == "__main__":
    main()
