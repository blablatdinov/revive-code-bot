# Generated by Django 5.1.3 on 2024-11-26 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_repoconfig_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='ghrepo',
            name='status',
            field=models.CharField(
                choices=[('active', 'Active'), ('inactive', 'Inactive')],
                default=1,
                max_length=16,
            ),
            preserve_default=False,
        ),
    ]
