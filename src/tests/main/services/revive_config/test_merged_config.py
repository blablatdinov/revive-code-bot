# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

from main.services.revive_config.fk_revive_config import FkReviveConfig
from main.services.revive_config.merged_config import MergedConfig
from main.services.revive_config.revive_config import ConfigDict


def test() -> None:
    got = MergedConfig.ctor(
        FkReviveConfig(ConfigDict({
            'cron': '* * * * *',
            'limit': 20,
            'glob': '**/*.js',
        })),
        FkReviveConfig(ConfigDict({
            'cron': '1 1 1 1 1',
            'limit': 10,
            'glob': '**/*.py',
        })),
    ).parse()

    assert got == {
        'cron': '1 1 1 1 1',
        'glob': '**/*.py',
        'limit': 10,
    }
