# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive config stored in postgres."""

from typing import final, override

import attrs

from main.models import RepoConfig
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class PgReviveConfig(ReviveConfig):
    """Revive config stored in postgres."""

    _repo_id: int

    @override
    def parse(self) -> ConfigDict:
        """Fetch config from DB."""
        cfg = RepoConfig.objects.get(repo_id=self._repo_id)
        return ConfigDict({
            'limit': 10,
            'cron': cfg.cron_expression,
            'glob': cfg.files_glob,
        })
