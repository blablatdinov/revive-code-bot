# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Merged Config."""

from collections.abc import Iterable
from typing import final

import attrs

from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class MergedConfig(ReviveConfig):
    """Merged Config."""

    _origins: Iterable[ReviveConfig]

    @classmethod
    def ctor(cls, *origins: ReviveConfig) -> ReviveConfig:
        """Ctor."""
        return cls(origins)

    def parse(self) -> ConfigDict:
        """Merge configs."""
        result_config = ConfigDict({'limit': 0, 'cron': '', 'glob': ''})
        for config in self._origins:
            result_config |= config.parse()
        return result_config
