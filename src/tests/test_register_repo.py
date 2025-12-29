# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from typing import final

import attrs
import pytest
from django.conf import settings

from main.services.github_objs.gh_repo_installation import GhRepoInstallation

pytestmark = [pytest.mark.django_db]


@final
@attrs.define(frozen=True)
class FkContent:

    decoded_content: bytes


@final
@attrs.define(frozen=True)
class FkRepo:

    def create_hook(self, name: str, config: dict[str, str], events: list[str]) -> None:
        pass

    def get_contents(self, name: str) -> FkContent:
        return FkContent(b'limit: 5')


@final
@attrs.define(frozen=True)
class FkGh:

    def get_repo(self, full_name: str) -> FkRepo:
        return FkRepo()


@pytest.fixture
def mock_scheduler(mock_http):
    mock_http.post(
        f'{settings.CRONIQ_DOMAIN}/api/v1/tasks',
        status_code=200,
        json={'id': 'fake-task-id'},
        headers={'Authorization': f'Basic {settings.CRONIQ_API_KEY}'},
    )
    return mock_http


# TODO: create asserts
@pytest.mark.skip
@pytest.mark.usefixtures('mock_scheduler')
def test() -> None:
    GhRepoInstallation(
        [{'full_name': 'owner_name/repo_name'}],
        1,
    ).register()
