# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Alter RepoConfig.repo to OneToOneField."""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_processtask_trigger_issue_id'),
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
