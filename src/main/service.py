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
import random
import tempfile
import zipfile
from contextlib import suppress
from pathlib import Path
from typing import Protocol, TypedDict, final

import attrs
import yaml
from django.conf import settings
from django.template import Context, Template
from git import Repo
from github import Auth, Github, Repository
from github.GithubException import UnknownObjectException

from main.algorithms import files_sorted_by_last_changes, files_sorted_by_last_changes_from_db
from main.models import GhRepo, RepoConfig, TouchRecord
from cron_validator import CronValidator


class ConfigDict(TypedDict):
    """Configuration structure."""

    limit: int
    cron: str
    glob: str


def pygithub_client(installation_id: int) -> Github:
    """Pygithub client."""
    auth = Auth.AppAuth(
        874924,
        Path(settings.BASE_DIR / 'revive-code-bot.2024-04-11.private-key.pem').read_text(encoding='utf-8'),
    )
    return Github(auth=auth.get_installation_auth(installation_id))


def read_config(config: str) -> ConfigDict:
    """Read config from yaml files."""
    parsed_config: ConfigDict = yaml.safe_load(config)
    if not CronValidator.parse(parsed_config['cron']):
        # TODO: custom exception
        # TODO: notify repository owner
        raise ValueError('Cron expression: "{0}" has invalid format'.format(parsed_config['cron']))
    return 


def generate_default_config():
    """Generating default config."""
    return ConfigDict({
        'limit': 10,
        'cron': '{0} {1} {2} * *'.format(
            random.randint(0, 61),  # noqa: S311 . Not secure issue
            random.randint(0, 25),  # noqa: S311 . Not secure issue
            random.randint(0, 29),  # noqa: S311 . Not secure issue
        ),
        'glob': '**/*',
    })


def config_or_default(repo_path: Path) -> ConfigDict:
    """Read or default config."""
    config_file = list(repo_path.glob('.revive-bot.*'))
    if config_file:
        return read_config(next(iter(config_file)).read_text())
    return generate_default_config()


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


class ClonedRepo(Protocol):
    """Cloned git repository."""

    def clone_to(self, path: Path) -> Path:
        """Run cloning."""


class NewIssue(Protocol):
    """New issue."""

    def create(self, title: str, content: str) -> None:
        """Creating issue."""


@final
@attrs.define(frozen=True)
class GhNewIssue(NewIssue):
    """New issue in github."""

    _repo: Repository

    def create(self, title: str, content: str) -> None:
        """Creating issue."""
        self._repo.create_issue(title, content)


@final
class FkNewIssue(Protocol):
    """Fk issue storage."""

    issues: list

    def __init__(self) -> None:
        """Ctor."""
        self.issues = []

    def create(self, title: str, content: str) -> None:
        """Creating issue."""
        self.issues.append({
            'title': title,
            'content': content,
        })


@final
@attrs.define(frozen=True)
class FkClonedRepo(ClonedRepo):
    """Fk git repo."""

    _zipped_repo: Path

    def clone_to(self, path: Path):
        """Unzipping repo from archieve."""
        with zipfile.ZipFile(self._zipped_repo, 'r') as zip_ref:
            zip_ref.extractall(path)
        return path


@final
@attrs.define(frozen=True)
class GhClonedRepo(ClonedRepo):
    """Git repo from github."""

    _gh_repo: GhRepo

    def clone_to(self, path: Path) -> Path:
        """Cloning from github."""
        gh = pygithub_client(self._gh_repo.installation_id)
        repo = gh.get_repo(self._gh_repo.full_name)
        gh.close()
        Repo.clone_from(repo.clone_url, path)
        return path


def process_repo(repo_id: int, cloned_repo: ClonedRepo, new_issue: NewIssue):
    """Processing repo."""
    repo_config = RepoConfig.objects.get(repo_id=repo_id)
    with tempfile.TemporaryDirectory() as tmpdirname:
        repo_path = cloned_repo.clone_to(Path(tmpdirname))
        files_for_search = list(repo_config.glob or '**/*')
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


@final
class RegisteredRepoFromGithub(TypedDict):
    """Github webhook needed fields."""

    full_name: str


def register_repo(repos: list[RegisteredRepoFromGithub], installation_id: int, gh: Github):
    """Registering new repositories."""
    for repo in repos:
        repo_db_record = GhRepo.objects.create(
            full_name=repo['full_name'],
            installation_id=installation_id,
            has_webhook=False,
        )
        gh_repo = gh.get_repo(repo['full_name'])
        gh_repo.create_hook(
            'web',
            {
                'url': 'https://www.rehttp.net/p/https%3A%2F%2Frevive-code-bot.ilaletdinov.ru%2Fhook%2Fgithub',
                'content_type': 'json',
            },
            ['issues', 'issue_comment', 'push'],
        )
        config = _read_config_from_repo(gh_repo)
        RepoConfig.objects.create(repo=repo_db_record, cron_expression=config['cron'])


def _read_config_from_repo(gh_repo: Repository):
    # TODO write tests
    # TODO invalid cron in .revive-bot.yaml case
    # TODO merge fields from repo config and default config
    #  Example of repo config:
    #  ```yaml
    #  cron: 9 16 * * *
    #  ```
    #  for this case configs must be merged. Result config:
    #  ```yaml
    #  limit: 10  # noqa: ERA001. It's yaml
    #  cron: 9 16 * * *
    #  glob: **/*
    #  ```
    variants = ('.revive-bot.yaml', '.revive-bot.yml')
    for variant in variants:
        with suppress(UnknownObjectException):
            return read_config(
                gh_repo
                .get_contents(variant)
                .decoded_content
                .decode('utf-8'),
            )
    return generate_default_config()
