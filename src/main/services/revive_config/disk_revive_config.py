# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive bot config from file."""

from pathlib import Path
from typing import final, override

import attrs

from main.exceptions import ConfigFileNotFoundError
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig
from main.services.revive_config.str_config import StrReviveConfig


@final
@attrs.define(frozen=True)
class DiskReviveConfig(ReviveConfig):
    """Revive bot config from file."""

    _repo_path: Path

    @override
    def parse(self) -> ConfigDict:
        """Parsing file from file."""
        config_file = list(self._repo_path.glob('.revive-code-bot.*'))
        if not config_file:
            raise ConfigFileNotFoundError
        return StrReviveConfig(next(iter(config_file)).read_text()).parse()
