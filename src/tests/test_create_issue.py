# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test create issue."""

import datetime
from types import ModuleType

import pytest
from django.conf import settings

from main.models import GhRepo, TouchRecord
from main.service import process_repo
from main.services.github_objs.fk_cloned_repo import FkClonedRepo
from main.services.github_objs.fk_new_issue import FkNewIssue

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker: ModuleType) -> GhRepo:
    repo = baker.make(
        'main.GhRepo',
        full_name='blablatdinov/iman-game-bot',
        installation_id=52326552,
    )
    baker.make('main.RepoConfig', repo=repo, files_glob='**/*')
    return repo  # type: ignore [no-any-return]


@pytest.fixture
def _exist_touch_records(baker: ModuleType, gh_repo: GhRepo) -> None:
    files = [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
    ]
    baker.make(
        'main.TouchRecord',
        gh_repo=gh_repo,
        path=(f for f in files),
        date=datetime.datetime.now(tz=datetime.UTC).date(),
    )


@pytest.mark.integration
def test(gh_repo: GhRepo) -> None:
    new_issue = FkNewIssue.ctor()
    process_repo(
        gh_repo.id,
        FkClonedRepo(settings.BASE_DIR / 'tests/fixtures/iman-game-bot.zip'),
        new_issue,
    )
    today = datetime.datetime.now(tz=datetime.UTC).date()

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 5
    assert new_issue.issues[0] == {
        'title': 'Issue from revive-code-bot',
        'content': '\n'.join([
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
        ]),
    }


@pytest.mark.integration
@pytest.mark.usefixtures('_exist_touch_records')
def test_double_process(gh_repo: GhRepo) -> None:
    new_issue = FkNewIssue.ctor()
    process_repo(
        gh_repo.id,
        FkClonedRepo(settings.BASE_DIR / 'tests/fixtures/iman-game-bot.zip'),
        new_issue,
    )
    today = datetime.datetime.now(tz=datetime.UTC).date()

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'manage.py',
        'game/views.py',
        'game/migrations/__init__.py',
        'game/apps.py',
        'game/__init__.py',
        'config/wsgi.py',
        'config/asgi.py',
        'bot_init/urls.py',
        'bot_init/migrations/__init__.py',
        'bot_init/migrations/0001_initial.py',
    ]
    assert new_issue.issues[0] == {
        'title': 'Issue from revive-code-bot',
        'content': '\n'.join([
            '- [ ] `config/wsgi.py`',
            '- [ ] `config/asgi.py`',
            '- [ ] `bot_init/urls.py`',
            '- [ ] `bot_init/migrations/__init__.py`',
            '- [ ] `bot_init/migrations/0001_initial.py`',
            '',
            '',
            'Expected actions:',
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
        ]),
    }
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 10
