import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Create or update a Django superuser from environment variables. "
        "Safe for Render Free (no shell)."
    )

    def handle(self, *args, **options):
        username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "admin").strip()
        email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "").strip()
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or ""

        if not username:
            self.stdout.write(self.style.WARNING("No username provided; skipping admin creation."))
            return

        # Do not hardcode or print passwords. If not provided, do nothing.
        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_PASSWORD not set; skipping admin creation/update."
                )
            )
            return

        User = get_user_model()

        user, created = User.objects.get_or_create(username=username)
        changed = False

        if email and getattr(user, "email", None) != email:
            user.email = email
            changed = True

        if not user.is_staff:
            user.is_staff = True
            changed = True

        if not user.is_superuser:
            user.is_superuser = True
            changed = True

        # Always set password from env (allows rotation)
        user.set_password(password)
        changed = True

        if created or changed:
            user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser created: {username}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser ensured/updated: {username}"))
