# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Alter RepoConfig.repo to OneToOneField."""

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20251124_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repoconfig',
            name='repo',
            field=models.OneToOneField(
                on_delete=models.PROTECT,
                to='main.ghrepo',
            ),
        ),
    ]
