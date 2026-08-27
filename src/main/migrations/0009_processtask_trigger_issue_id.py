# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20251124_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='processtask',
            name='trigger_issue_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
