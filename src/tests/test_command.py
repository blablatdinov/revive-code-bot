# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from collections.abc import Generator
from operator import attrgetter
from types import ModuleType

import pytest
from django.core.management import call_command

from main.models import GhRepo, RepoConfig
from main.services.github_objs.github_client import github_repo

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker: ModuleType) -> Generator[GhRepo, None, None]:
    yield baker.make(
        'main.GhRepo',
        full_name='blablatdinov/iman-game-bot',
        installation_id=52326552,
    )
    repo = github_repo(52326552, 'blablatdinov/iman-game-bot')
    for issue in repo.get_issues():
        if issue.title == 'Issue from revive-code-bot':
            issue.edit(state='closed')


@pytest.fixture
def repo_config(baker: ModuleType, gh_repo: GhRepo) -> RepoConfig:
    return baker.make(  # type: ignore [no-any-return]
        'main.RepoConfig',
        repo=gh_repo,
    )


@pytest.mark.integration
@pytest.mark.usefixtures('repo_config')
def test(gh_repo: GhRepo) -> None:
    call_command('process_repos')

    assert next(iter(sorted(
        # TODO search issues
        [],
        key=attrgetter('created_at'),
        reverse=True,
    ))).body == '\n'.join([
        '- [ ] `manage.py`',
        '- [ ] `game/views.py`',
        '- [ ] `game/migrations/__init__.py`',
        '- [ ] `game/apps.py`',
        '- [ ] `game/__init__.py`',
        '',
        '',
        'Expected actions:',
        '1. Create new issues with reference to this issue',
        '2. Clean files must be marked in checklist',
        '3. Close issue',
    ])
