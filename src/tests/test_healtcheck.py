# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test healthcheck."""

import pytest
from django.test.client import Client

pytestmark = [pytest.mark.django_db]


def test(anon: Client) -> None:
    """Test health check endpoint."""
    got = anon.get('/health-check/')

    assert got.status_code == 200
    assert got.content == b'{"app": "ok"}'
