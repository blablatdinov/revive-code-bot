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

import tempfile
from pathlib import Path

from django.template import Context, Template

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.models import RepoConfig
from main.services.github_objs.cloned_repo import ClonedRepo
from main.services.github_objs.new_issue import NewIssue
from main.services.revive_config.disk_revive_config import DiskReviveConfig
from main.services.revive_config.merged_config import MergedConfig
from main.services.revive_config.pg_revive_config import PgReviveConfig
from main.services.revive_config.pg_updated_revive_config import PgUpdatedReviveConfig
from main.services.synchronize_touch_records import PgSynchronizeTouchRecords


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
        config = PgUpdatedReviveConfig(
            repo_id,
            MergedConfig.ctor(
                PgReviveConfig(repo_id),
                DiskReviveConfig(repo_path),
            ),
        ).parse()
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(repo_path, files_for_search),
            repo_path,
        )
    stripped_file_list: list[tuple[str, int]] = sorted(
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
    file_list: list[str] = [file for file, _ in stripped_file_list]
    new_issue.create(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            'Expected actions:\n'
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
        ])).render(Context({
            'files': file_list,
        })),
    )
    PgSynchronizeTouchRecords().sync(
        file_list,
        repo_id,
    )
