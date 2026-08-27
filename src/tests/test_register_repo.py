# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final
from unittest.mock import patch

import attrs
import pytest
from django.conf import settings

from main.models import GhRepo, RepoConfig
from main.services.github_objs.gh_repo_installation import GhRepoInstallation

pytestmark = [pytest.mark.django_db]


@final
@attrs.define(frozen=True)
class FkContent:
    decoded_content: bytes


@final
@attrs.define(frozen=True)
class FkHook:
    config: dict[str, str]


@final
@attrs.define
class FkRepo:
    """Fake github repo for testing."""

    _hooks: list[FkHook]
    created_hooks_count: int = 0

    def create_hook(self, name: str, config: dict[str, str], events: list[str]) -> None:
        self.created_hooks_count += 1
        self._hooks.append(FkHook(config))

    def get_hooks(self) -> list[FkHook]:
        return list(self._hooks)

    def get_contents(self, name: str) -> FkContent:
        return FkContent(b'limit: 5')


@pytest.fixture
def fk_repo() -> FkRepo:
    return FkRepo([])


@pytest.fixture
def mock_scheduler(mock_http):
    mock_http.get(
        '{0}/api/v1/tasks'.format(settings.CRONIQ_DOMAIN),
        status_code=200,
        json={'results': []},
    )
    mock_http.post(
        '{0}/api/v1/tasks'.format(settings.CRONIQ_DOMAIN),
        status_code=200,
        json={'id': 'fake-task-id'},
    )
    return mock_http


def test_registers_repo_and_creates_webhook(fk_repo: FkRepo, mock_scheduler) -> None:
    with patch(
        'main.services.github_objs.gh_repo_installation.github_repo',
        return_value=fk_repo,
    ):
        GhRepoInstallation(
            [{'full_name': 'owner/repo'}],
            1,
        ).register()

    assert GhRepo.objects.filter(full_name='owner/repo').exists()
    assert RepoConfig.objects.filter(repo__full_name='owner/repo').exists()
    repo = GhRepo.objects.get(full_name='owner/repo')
    assert repo.has_webhook
    assert fk_repo.created_hooks_count == 1


def test_idempotent_register_no_duplicate_webhook(fk_repo: FkRepo, mock_scheduler) -> None:
    with patch(
        'main.services.github_objs.gh_repo_installation.github_repo',
        return_value=fk_repo,
    ):
        GhRepoInstallation(
            [{'full_name': 'owner/repo'}],
            1,
        ).register()
        GhRepoInstallation(
            [{'full_name': 'owner/repo'}],
            1,
        ).register()

    assert GhRepo.objects.filter(full_name='owner/repo').count() == 1
    assert RepoConfig.objects.filter(repo__full_name='owner/repo').count() == 1
    assert fk_repo.created_hooks_count == 1
