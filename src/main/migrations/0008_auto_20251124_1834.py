# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""No-op migration replacing external API calls.

Originally this migration fetched repo configs from GitHub and created
tasks in Croniq. External calls in migrations are non-deterministic and
can block deploys when external services are unavailable. The sync logic
has been moved to `sync_repo_configs` management command.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_alter_processtask_status'),
    ]

    operations = []
