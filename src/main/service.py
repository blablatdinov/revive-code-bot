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

from django.conf import settings
from django.template import Context, Template
from github import Auth, Github

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.models import RepoConfig, TouchRecord


def pygithub_client(installation_id: int) -> Github:
    """Pygithub client."""
    auth = Auth.AppAuth(
        874924,
        Path(settings.BASE_DIR / 'revive-code-bot.private-key.pem').read_text(encoding='utf-8'),
    )
    return Github(auth=auth.get_installation_auth(installation_id))


def sync_touch_records(files: list[str], repo_id: int) -> None:
    """Synching touch records."""
    exists_touch_records = TouchRecord.objects.filter(gh_repo_id=repo_id)
    for tr in exists_touch_records:
        if tr.path in files:
            tr.date = datetime.datetime.now(tz=datetime.UTC).date()
            tr.save()
    for file in files:
        if not TouchRecord.objects.filter(gh_repo_id=repo_id, path=file).exists():
            TouchRecord.objects.create(
                gh_repo_id=repo_id,
                path=file,
                date=datetime.datetime.now(tz=datetime.UTC).date(),
            )


def process_repo(repo_id: int, cloned_repo: ClonedRepo, new_issue: NewIssue):
    """Processing repo."""
    repo_config = RepoConfig.objects.get(repo_id=repo_id)
    with tempfile.TemporaryDirectory() as tmpdirname:
        repo_path = cloned_repo.clone_to(Path(tmpdirname))
        files_for_search = [
            x
            for x in repo_path.glob(repo_config.files_glob or '**/*')
            if '.git' not in str(x)
        ]
        config = config_or_default(repo_path)
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(repo_path, files_for_search),
            repo_path,
        )
    stripped_file_list = sorted(
        [
            (
                str(path).replace(
                    '{0}/'.format(repo_path),
                    '',
                ),
                points,
            )
            for path, points in got.items()
        ],
        key=lambda x: (x[1], str(x[0])),
        reverse=True,
    )[:config['limit']]
    stripped_file_list = [file for file, _ in stripped_file_list]
    new_issue.create(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            'Expected actions:\n'
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
        ])).render(Context({
            'files': stripped_file_list,
        })),
    )
    sync_touch_records(
        stripped_file_list,
        repo_id,
    )
