# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive bot config from file."""

from typing import final, override

import attrs

from main.exceptions import ConfigFileNotFoundError
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class SafeDiskReviveConfig(ReviveConfig):
    """Handle exception for DiskReviveConfig."""

    _origin: ReviveConfig
    _analog: ReviveConfig

    @override
    def parse(self) -> ConfigDict:
        """Parsing file from file."""
        try:
            return self._origin.parse()
        except ConfigFileNotFoundError:
            return self._analog.parse()
