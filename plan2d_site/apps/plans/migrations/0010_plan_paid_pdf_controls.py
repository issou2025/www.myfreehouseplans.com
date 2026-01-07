from django.db import migrations, models
from django.db.models import F


def copy_gumroad_urls(apps, schema_editor):
    Plan = apps.get_model('plans', 'Plan')
    Plan.objects.exclude(gumroad_url='').update(gumroad_paid_pdf_url=F('gumroad_url'))


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("plans", "0009_plan_ifc_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="plan",
            name="paid_pdf_available",
            field=models.BooleanField(
                default=True,
                help_text="Toggle off to hide the dimensioned paid PDF while keeping the free preview available.",
            ),
        ),
        migrations.AddField(
            model_name="plan",
            name="gumroad_paid_pdf_url",
            field=models.URLField(
                blank=True,
                help_text="Optional Gumroad link dedicated to the paid PDF checkout.",
                max_length=500,
            ),
        ),
        migrations.RunPython(copy_gumroad_urls, noop),
    ]
