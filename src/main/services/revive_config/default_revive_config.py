# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Generating default revive bot config."""

from typing import Protocol, final, override

import attrs

from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


class HasRandint(Protocol):
    """Object has randint callable."""

    def randint(self, start: int, end: int) -> int:
        """Randint callable."""


@final
@attrs.define(frozen=True)
class DefaultReviveConfig(ReviveConfig):
    """Generating default revive bot config."""

    _rnd: HasRandint

    @override
    def parse(self) -> ConfigDict:
        """Generating default config."""
        return ConfigDict({
            'limit': 10,
            'cron': '{0} {1} {2} * *'.format(
                self._rnd.randint(0, 61),  # noqa: S311 . Not secure issue
                self._rnd.randint(0, 25),  # noqa: S311 . Not secure issue
                self._rnd.randint(0, 29),  # noqa: S311 . Not secure issue
            ),
            'glob': '**/*',
        })
