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

"""Service utils."""

import random
import tempfile
from pathlib import Path
from typing import TypedDict

import requests
from django.conf import settings
from django.template import Context, Template

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.exceptions import UnavailableRepoError
from main.models import GhRepo, RepoConfig, RepoStatusEnum
from main.services.github_objs.cloned_repo import ClonedRepo
from main.services.github_objs.github_client import github_repo
from main.services.github_objs.new_issue import NewIssue
from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.disk_revive_config import DiskReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig
from main.services.revive_config.merged_config import MergedConfig
from main.services.revive_config.pg_revive_config import PgReviveConfig
from main.services.revive_config.pg_updated_revive_config import PgUpdatedReviveConfig
from main.services.revive_config.revive_config import ConfigDict
from main.services.revive_config.safe_disk_revive_config import SafeDiskReviveConfig
from main.services.synchronize_touch_records import PgSynchronizeTouchRecords


def get_or_create_repo(repo_full_name: str, installation_id: int) -> GhRepo:
    """Get or create repository db record."""
    pg_repo = GhRepo.objects.filter(full_name=repo_full_name)
    if pg_repo.exists():
        return pg_repo.earliest('id')
    new_repo = GhRepo.objects.create(
        full_name=repo_full_name,
        installation_id=installation_id,
        has_webhook=True,
    )
    config = MergedConfig.ctor(
        GhReviveConfig(
            github_repo(installation_id, repo_full_name),
            DefaultReviveConfig(random),
        ),
    )
    RepoConfig.objects.create(
        repo=new_repo,
        cron_expression=config.parse()['cron'],
    )
    return new_repo


def update_config(repo_full_name: str) -> None:
    """Update config."""
    repo = GhRepo.objects.get(full_name=repo_full_name)
    pg_revive_config = PgReviveConfig(repo.id)
    gh_repo = github_repo(repo.installation_id, repo.full_name)
    try:
        config = PgUpdatedReviveConfig(
            repo.id,
            MergedConfig.ctor(
                pg_revive_config,
                GhReviveConfig(
                    gh_repo,
                    pg_revive_config,
                ),
            ),
        ).parse()
    except UnavailableRepoError:
        repo.status = RepoStatusEnum.inactive
        repo.save()
        return
    response = requests.put(
        '{0}/api/jobs'.format(settings.SCHEDULER_HOST),
        {
            'repo_id': repo.id,
            'cron_expression': config['cron'],
        },
        timeout=1,
    )
    response.raise_for_status()


class _Repository(TypedDict):

    default_branch: str
    ref: str


class _RequestForCheckBranchDefault(TypedDict):

    ref: str
    repository: _Repository


def is_default_branch(request_json: _RequestForCheckBranchDefault) -> bool:
    """Check repo branch is default."""
    actual = 'refs/heads/{0}'.format(request_json['repository']['default_branch'])
    default_branch = request_json['ref']
    return actual == default_branch


def process_repo(repo_id: int, cloned_repo: ClonedRepo, new_issue: NewIssue) -> None:
    """Processing repo."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        repo_path = cloned_repo.clone_to(Path(tmpdirname))
        pg_config = PgReviveConfig(repo_id)
        config = PgUpdatedReviveConfig(
            repo_id,
            MergedConfig.ctor(
                pg_config,
                SafeDiskReviveConfig(
                    DiskReviveConfig(repo_path),
                    pg_config,
                ),
            ),
        ).parse()
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(
                repo_path,
                define_files_for_search(repo_path, config),
            ),
            repo_path,
        )
    stripped_file_list: list[tuple[str, int]] = _sorted_file_list(repo_path, got)[:config['limit']]
    file_list: list[str] = [file for file, _ in stripped_file_list]
    new_issue.create(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '## Potentially Stagnant Files Identified\n'
            'This issue was automatically created by Revive Code Bot to highlight files that',
            "haven't been updated for a long time or may require review. Regular updates and reviews",
            'of such files help maintain the quality and relevance of the project codebase.',
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            '## Recommended Actions:',
            '1. Create separate issues for each file (referencing this issue for context).',
            '2. Review the listed files:',
            '  - Update or remove outdated files.',
            '  - Mark relevant files as reviewed in the checklist below.',
            '3. Once all files have been reviewed, close this issue.',
        ])).render(Context({
            'files': file_list,
        })),
    )
    PgSynchronizeTouchRecords().sync(
        file_list,
        repo_id,
    )


def define_files_for_search(repo_path: Path, config: ConfigDict) -> list[Path]:
    """Define files for search."""
    return [
        pth
        for pth in repo_path.glob(config['glob'] or '**/*')
        if '.git/' not in str(pth) and pth.is_file()  # TODO .github/workflows dir case
    ]


def _sorted_file_list(repo_path: Path, file_list: dict[Path, int]) -> list[tuple[str, int]]:
    return sorted(
        [
            (
                str(path).replace(
                    '{0}/'.format(repo_path),
                    '',
                ),
                points,
            )
            for path, points in file_list.items()
        ],
        key=lambda x: (x[1], str(x[0])),
        reverse=True,
    )
