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

from types import ModuleType
from django.test.client import Client

import pytest
from django.conf import settings

from main.models import GhRepo

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def repo(baker: ModuleType) -> GhRepo:
    return baker.make('main.GhRepo')  # type: ignore [no-any-return]


@pytest.mark.integration
def test(anon: Client, repo: GhRepo) -> None:
    response = anon.post(
        '/process-repo/{0}'.format(repo.id),
        headers={
            'Authentication': 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN),
        },
    )

    assert response.status_code == 200
