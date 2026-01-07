from django.db import migrations, models


def move_unpublished_to_draft(apps, schema_editor):
    Plan = apps.get_model('plans', 'Plan')
    Plan.objects.filter(
        publish_status='unpublished',
        published_at__isnull=True,
        is_deleted=False
    ).update(publish_status='draft')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0005_add_gumroad_payment_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='publish_status',
            field=models.CharField(
                choices=[('draft', 'Draft'), ('unpublished', 'Unpublished'), ('published', 'Published')],
                db_index=True,
                default='draft',
                help_text='Controls whether the plan is publicly visible',
                max_length=20,
            ),
        ),
        migrations.RunPython(move_unpublished_to_draft, reverse_code=noop),
    ]
