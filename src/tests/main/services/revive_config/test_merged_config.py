# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
