# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive config stored in postgres."""

from typing import final, override

import attrs

from main.models import RepoConfig
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class PgUpdatedReviveConfig(ReviveConfig):
    """Update config in DB."""

    _repo_id: int
    _actual: ReviveConfig

    @override
    def parse(self) -> ConfigDict:
        """Fetch and save in DB."""
        cfg = RepoConfig.objects.get(repo_id=self._repo_id)
        origin = self._actual.parse()
        cfg.cron_expression = origin['cron']
        cfg.files_glob = origin['glob']
        cfg.save()
        return origin
