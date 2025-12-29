# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import random
from typing import Self, final

import attrs
import pytest

from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig

pytestmark = [pytest.mark.django_db]


@final
@attrs.define(frozen=True)
class FkContent:

    decoded_content: bytes

    @classmethod
    def str_ctor(cls, str_input: str) -> Self:
        return cls(str_input.encode('utf-8'))


@final
@attrs.define(frozen=True)
class FkRepo:

    _origin: str

    def get_contents(self, filepath: str) -> FkContent:
        return FkContent.str_ctor(self._origin)


def test() -> None:
    got = GhReviveConfig(
        # Too hard create Protocol for github.Repository.Repository
        FkRepo(  # type: ignore [arg-type]
            '\n'.join([
                'cron: 3 4 * * *',
            ]),
        ),
        DefaultReviveConfig(random.Random(0)),  # noqa: S311 . Not secure issue
    ).parse()

    assert got == {'cron': '3 4 * * *', 'glob': '**/*', 'limit': 10}
