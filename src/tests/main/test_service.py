# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test service utils."""

import tempfile
from pathlib import Path

import pytest
from django.conf import settings
from git import Repo

from main.service import define_files_for_search, process_repo
from main.services.github_objs.fk_cloned_repo import FkClonedRepo
from main.services.github_objs.fk_new_issue import FkNewIssue

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker):
    repo = baker.make('main.GhRepo')
    baker.make('main.RepoConfig', repo=repo)
    return repo


@pytest.fixture
def file_list() -> tuple[str, ...]:
    return (
        'CHANGELOG.md',
        'Dockerfile',
        'LICENSE',
        'README.md',
        'Taskfile.yml',
        'go.mod',
        'go.sum',
        'pyproject.toml',
        'renovate.json',
        'src/cmd/gotemir.go',
        'src/logic/cmprd_structures.go',
        'src/logic/compared_structures.go',
        'src/logic/config.go',
        'src/logic/directory.go',
        'src/logic/excluded_tests.go',
        'src/logic/file_name_variants.go',
        'src/logic/filter_out_from_config.go',
        'src/logic/fk_directory.go',
        'src/logic/fk_path.go',
        'src/logic/os_directory.go',
        'src/logic/path.go',
        'src/logic/source_file_name_variants.go',
        'src/logic/test_file_name_variants.go',
        'tests/it/test.py',
        'tests/unit/logic/cmprd_structures_test.go',
        'tests/unit/logic/excluded_tests_test.go',
        'tests/unit/logic/fk_path_test.go',
        'tests/unit/logic/os_directory_test.go',
        'tests/unit/logic/source_file_name_variants_test.go',
        'tests/unit/logic/test_file_name_variants_test.go',
        '.github/workflows/pr-check.yaml',
        '.github/workflows/release.yaml',
    )


@pytest.fixture
def tmp_dir(file_list):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pth = Path(tmpdirname)
        Repo.init(pth)
        (pth / 'src/cmd').mkdir(exist_ok=True, parents=True)
        (pth / 'src/logic').mkdir(exist_ok=True, parents=True)
        (pth / 'tests/it/').mkdir(exist_ok=True, parents=True)
        (pth / 'tests/unit/logic').mkdir(exist_ok=True, parents=True)
        (pth / '.github/workflows').mkdir(exist_ok=True, parents=True)
        for fl in file_list:
            (pth / fl).write_text('')
        yield pth


def test_process_repo_without_disk_config(gh_repo):
    new_issue = FkNewIssue.ctor()
    process_repo(
        gh_repo.id,
        FkClonedRepo(settings.BASE_DIR / 'tests/fixtures/repo-without-config.zip'),
        new_issue,
    )


def test_define_files(tmp_dir, file_list):
    got = define_files_for_search(
        tmp_dir,
        {'glob': '**/*'},
    )

    assert sorted(got) == sorted([tmp_dir / pth for pth in file_list])
    assert (tmp_dir / '.git/hooks/pre-commit.sample') not in got
    assert (tmp_dir / '.github/workflows/pr-check.yaml') in got
