# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fixtures for tests."""

from types import ModuleType

import pytest
import requests_mock
from django.test import Client


@pytest.fixture
def anon() -> Client:
    return Client()


@pytest.fixture
def baker() -> ModuleType:
    from model_bakery import baker as _baker  # noqa: PLC0415 . Conflict with fixture name
    return _baker


@pytest.fixture
def mock_http():
    with requests_mock.Mocker() as http_mocker:
        yield http_mocker
