from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("plans", "0008_planreferencesequence"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="ifc_available",
            field=models.BooleanField(
                default=False,
                help_text="Toggle on when an open IFC file is available for this plan.",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="gumroad_ifc_url",
            field=models.URLField(
                blank=True,
                help_text="Gumroad checkout link for the IFC file. Payments remain on Gumroad.",
                max_length=500,
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="ifc_version",
            field=models.CharField(
                blank=True,
                help_text="IFC version or schema (e.g., IFC2x3, IFC4).",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="ifc_notes",
            field=models.TextField(
                blank=True,
                help_text="Optional context describing what is included in the IFC export.",
            ),
        ),
    ]
