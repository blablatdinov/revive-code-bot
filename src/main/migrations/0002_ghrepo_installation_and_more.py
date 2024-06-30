# Generated by Django 5.0.6 on 2024-06-29 22:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ghrepo',
            name='installation',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='main.ghinstallation'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ghinstallation',
            name='installation_id',
            field=models.BigIntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='ghrepo',
            name='full_name',
            field=models.CharField(max_length=512, unique=True),
        ),
    ]
