# Generated by Django 5.0.6 on 2024-06-29 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_ghinstallation_table_alter_ghrepo_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ghrepo',
            old_name='installation',
            new_name='gh_installation',
        ),
    ]