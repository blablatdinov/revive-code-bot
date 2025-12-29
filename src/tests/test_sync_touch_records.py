# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import datetime
from types import ModuleType

import pytest
from time_machine import TimeMachineFixture

from main.models import GhRepo, TouchRecord
from main.services.synchronize_touch_records import PgSynchronizeTouchRecords

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def gh_repo(baker: ModuleType) -> GhRepo:
    return baker.make('main.GhRepo')  # type: ignore [no-any-return]


@pytest.fixture
def exist_touch_record(baker: ModuleType, gh_repo: GhRepo) -> TouchRecord:
    return baker.make(  # type: ignore [no-any-return]
        'main.TouchRecord',
        path='b.py',
        gh_repo=gh_repo,
        date=datetime.date(2020, 1, 1),
    )


@pytest.mark.usefixtures('exist_touch_record')
def test(gh_repo: GhRepo, time_machine: TimeMachineFixture) -> None:
    time_machine.move_to('2024-07-04')
    PgSynchronizeTouchRecords().sync(['a.py', 'b.py'], gh_repo.id)

    assert list(TouchRecord.objects.values('path', 'date')) == [
        {'path': 'b.py', 'date': datetime.date(2024, 7, 4)},
        {'path': 'a.py', 'date': datetime.date(2024, 7, 4)},
    ]
