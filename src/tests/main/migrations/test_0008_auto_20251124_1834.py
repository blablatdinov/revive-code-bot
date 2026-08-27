# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test that migration 0008 is a safe no-op.

The migration originally made external API calls to GitHub and Croniq.
It has been replaced with a no-op to keep deploys deterministic.
The sync logic now lives in the `sync_repo_configs` management command.
"""

import pytest

from main.models import GhRepo

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def old_state(migrator):
    migrator.apply_initial_migration(('main', '0007_alter_processtask_status'))


@pytest.mark.usefixtures('old_state', 'baker')
def test_migration_is_noop(migrator, baker):
    baker.make('main.GhRepo', _quantity=3)
    migrator.apply_tested_migration(('main', '0008_auto_20251124_1834'))
    assert GhRepo.objects.filter(repoconfig__isnull=True).count() == 3
