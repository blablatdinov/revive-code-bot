# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import pytest

from main.services.github_objs.gh_cloned_repo import GhClonedRepo

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker):
    return baker.make('main.GhRepo', full_name='blablatdinov/iman-game-bot', installation_id=52326552)


def test(gh_repo, tmp_path):
    GhClonedRepo(
        gh_repo,
    ).clone_to(tmp_path)

    assert (tmp_path / 'config' / 'settings.py').exists()
