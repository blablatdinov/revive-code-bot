# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

import re

import pytest

from main.exceptions import InvalidaCronError
from main.services.revive_config.str_config import StrReviveConfig


def test() -> None:
    got = StrReviveConfig('\n'.join([
        'limit: 10',
    ])).parse()

    # TODO: StrReviveConfig.parse return not valid ConfigDict
    assert got == {'limit': 10}  # type: ignore [comparison-overlap]


def test_invalid_cron() -> None:
    cron_expr = '*/61 * * * *'
    with pytest.raises(
        InvalidaCronError,
        match=re.escape('Cron expression: "{0}" has invalid format'.format(cron_expr)),
    ):
        StrReviveConfig('\n'.join([
            "cron: '{0}'".format(cron_expr),
        ])).parse()
