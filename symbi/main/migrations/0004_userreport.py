# Generated by Django 4.2.6 on 2023-12-07 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("main", "0003_alter_socialuser_date_of_birth"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserReport",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "report_category",
                    models.IntegerField(
                        choices=[(1, "Post"), (2, "Comment"), (0, "No Category")],
                        default=0,
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "reporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {
                    ("reporter", "content_type", "object_id", "report_category")
                },
            },
        ),
    ]
