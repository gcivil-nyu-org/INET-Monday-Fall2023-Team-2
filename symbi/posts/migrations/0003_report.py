# Generated by Django 4.2.6 on 2023-12-07 17:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("posts", "0002_alter_comment_taggedusers"),
    ]

    operations = [
        migrations.CreateModel(
            name="Report",
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
                ("reported_object_id", models.PositiveIntegerField()),
                ("report_count", models.IntegerField(default=1)),
                (
                    "report_category",
                    models.IntegerField(choices=[(1, "post"), (2, "comment")]),
                ),
                (
                    "reason",
                    models.IntegerField(
                        choices=[
                            (1, "hate_speech_or_symbols"),
                            (2, "abuse_and_harassment"),
                            (3, "violence_or_dangerous_organizations"),
                            (4, "privacy"),
                            (5, "spam"),
                            (6, "sensitive_or_disturbing_media"),
                            (7, "scams_or_fraud"),
                            (8, "false_information"),
                        ]
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                (
                    "reporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
