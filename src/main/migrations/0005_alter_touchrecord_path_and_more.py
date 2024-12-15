# Generated by Django 5.1.3 on 2024-12-15 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0004_ghrepo_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="touchrecord",
            name="path",
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterUniqueTogether(
            name="touchrecord",
            unique_together={("gh_repo", "path")},
        ),
    ]
