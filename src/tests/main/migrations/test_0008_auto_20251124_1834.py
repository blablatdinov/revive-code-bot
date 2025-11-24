# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import itertools
import random
import re
from functools import partial
from pathlib import Path

import pytest
from django.conf import settings

from main.models import GhRepo

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def empty_revive_config(mock_http):
    mock_http.register_uri(
        'POST',
        re.compile(r'https://api.github.com:443/app/installations/\d+/access_tokens'),
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_app_access_tokens_response.json').read_text(encoding='utf-8'),
    )
    mock_http.register_uri(
        'GET',
        re.compile(r'https://api.github.com:443/repos/\w+/\w+'),
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_repos_response.json').read_text(encoding='utf-8'),
    )
    mock_http.get(
        'https://api.github.com:443/repos/blablatdinov/gotemir',
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_repos_response.json').read_text(encoding='utf-8'),
    )
    mock_http.post(
        'https://api.github.com:443/repos/blablatdinov/gotemir/hooks',
        text=Path(settings.BASE_DIR / 'tests/fixtures/gh_hooks_response.json').read_text(encoding='utf-8'),
    )
    mock_http.register_uri(
        'GET',
        re.compile(r'https://api.github.com:443/repos/blablatdinov/gotemir/contents/.revive-code-bot.*'),
        status_code=404,
        text='\n'.join([
            '{',
            '  "message": "Not Found",',
            '  "documentation_url": "https://docs.github.com/rest/repos/contents#get-repository-content",',
            '  "status": "404"',
            '}',
        ]),
    )


@pytest.fixture
def mock_scheduler(mock_http):
    mock_http.register_uri(
        'GET',
        re.compile(r'{0}/api/v1/tasks\?name=repo_\d+'.format(settings.CRONIQ_DOMAIN)),
        json={'results': []},
    )
    mock_http.post(
        f'{settings.CRONIQ_DOMAIN}/api/v1/tasks',
        status_code=200,
        json={'id': 'fake-task-id'},
        headers={'Authorization': f'Basic {settings.CRONIQ_API_KEY}'},
    )
    return mock_http


@pytest.fixture
def old_state(migrator):
    migrator.apply_initial_migration(('main', '0007_alter_processtask_status'))


@pytest.fixture
def repos_with_cfg(baker):
    repos = baker.make(
        'main.GhRepo',
        _quantity=10,
        # Not secure issue
        installation_id=partial(random.randrange, 1000, 2000),  # noqa: S311
        full_name=lambda: f'blablatdinov/repo_{random.randrange(1000, 2000)}',  # noqa: S311
    )
    baker.make('main.RepoConfig', repo=itertools.cycle(repos))
    return repos


@pytest.fixture
def repo_without_cfg(baker):
    return baker.make('main.GhRepo', full_name='blablatdinov/gotemir', installation_id=52326552)


@pytest.mark.usefixtures('empty_revive_config', 'mock_scheduler', 'old_state', 'repos_with_cfg', 'repo_without_cfg')
def test(migrator, baker):
    migrator.apply_tested_migration(('main', '0008_auto_20251124_1834'))
    assert not GhRepo.objects.filter(repoconfig__isnull=True)
