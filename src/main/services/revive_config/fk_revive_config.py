# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive bot config from github."""

from typing import final, override

import attrs

from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class FkReviveConfig(ReviveConfig):
    """Fake revive config."""

    _origin: ConfigDict

    @override
    def parse(self) -> ConfigDict:
        """Return origin."""
        return self._origin
