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

import datetime
from types import ModuleType

import pytest

from main.models import TouchRecord, GhRepo
from time_machine import TimeMachineFixture
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
