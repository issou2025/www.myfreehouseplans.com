from django.db import models


class Visit(models.Model):
    class DeviceType(models.TextChoices):
        MOBILE = "mobile", "Mobile"
        DESKTOP = "desktop", "Desktop"

    url = models.CharField(max_length=500, db_index=True)
    country_code = models.CharField(max_length=2, default="UN", db_index=True)
    device_type = models.CharField(
        max_length=10,
        choices=DeviceType.choices,
        default=DeviceType.DESKTOP,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["country_code", "created_at"]),
            models.Index(fields=["url", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.country_code} {self.device_type} {self.url}"
