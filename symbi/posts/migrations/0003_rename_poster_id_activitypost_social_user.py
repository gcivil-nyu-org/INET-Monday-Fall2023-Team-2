# Generated by Django 4.2.6 on 2023-10-22 19:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0002_alter_activitypost_poster_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="activitypost", old_name="poster_id", new_name="social_user",
        ),
    ]
