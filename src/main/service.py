# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""Service utils."""

import datetime
import tempfile
from pathlib import Path
from typing import TypedDict

import yaml
from django.conf import settings
from django.template import Context, Template
from git import Repo
from github import Auth, Github

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.models import GhRepo, TouchRecord


class ConfigDict(TypedDict):
    """Configuration structure."""

    limit: int


def pygithub_client(installation_id: int) -> Github:
    """Pygithub client."""
    auth = Auth.AppAuth(
        874924,
        Path(settings.BASE_DIR / 'revive-code-bot.2024-04-11.private-key.pem').read_text(encoding='utf-8'),
    )
    return Github(auth=auth.get_installation_auth(installation_id))


def read_config(config: str) -> ConfigDict:
    """Read config from yaml files."""
    return yaml.safe_load(config)


def config_or_default(repo_path: Path) -> ConfigDict:
    """Read or default config."""
    config_file = repo_path.glob('.revive-bot.*')
    if config_file:
        return read_config(next(iter(config_file)).read_text())
    return ConfigDict({
        'limit': 10,
    })


def sync_touch_records():
    pass


def process_repo(repo_id: int):
    """Processing repo."""
    gh_repo = GhRepo.objects.get(id=repo_id)
    gh = pygithub_client(gh_repo.installation_id)
    repo = gh.get_repo(gh_repo.full_name)
    gh.close()
    with tempfile.TemporaryDirectory() as tmpdirname:
        Repo.clone_from(repo.clone_url, tmpdirname)
        repo_path = Path(tmpdirname)
        files_for_search = list(repo_path.glob('**/*.py'))
        config = config_or_default(repo_path)
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(repo_path, files_for_search),
            tmpdirname,
        )
    stripped_file_list = sorted(
        [
            (
                str(path).replace(
                    '{0}/'.format(tmpdirname),
                    '',
                ),
                points,
            )
            for path, points in got.items()
        ],
        key=lambda x: (x[1], str(x[0])),
        reverse=True,
    )[:config['limit']]
    repo.create_issue(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            'Expected actions:\n'
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
        ])).render(Context({
            'files': [
                file
                for file, _ in stripped_file_list
            ],
        })),
    )
    exists_touched_records = TouchRecord.objects.filter(gh_repo=gh_repo).values_list('path', flat=True)
    for_create = [
        file
        for file, _ in stripped_file_list
        if file in exists_touched_records
    ]
    TouchRecord.objects.bulk_create([
        TouchRecord(
            gh_repo_id=repo_id,
            path=file,
            date=datetime.datetime.now(tz=datetime.UTC).date(),
        )
        for file in for_create
    ])
    for_update = [
        file
        for file, _ in stripped_file_list
        if file in exists_touched_records
    ]
    for file_updated in for_update:
        tr = TouchRecord.objects.get(gh_repo=gh_repo, file=file_updated)
        tr.date = datetime.datetime.now(tz=datetime.UTC).date()
        tr.save()
