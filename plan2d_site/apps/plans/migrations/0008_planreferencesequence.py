from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0007_plan_gumroad_revit_url_plan_revit_available_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanReferenceSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(unique=True)),
                ('last_number', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Plan Reference Sequence',
                'verbose_name_plural': 'Plan Reference Sequences',
            },
        ),
    ]
