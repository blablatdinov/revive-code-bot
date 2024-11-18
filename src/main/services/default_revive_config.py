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

import random
from typing import TypedDict, Protocol, final

import attrs
from github.Repository import Repository

from main.services.revive_config import ConfigDict


@final
@attrs.define(frozen=True)
class DefaultReviveConfig(Protocol):

    _rnd: random.Random

    def parse(self) -> ConfigDict:
        return ConfigDict({
            'limit': 10,
            'cron': '{0} {1} {2} * *'.format(
                self._rnd.randint(0, 61),  # noqa: S311 . Not secure issue
                self._rnd.randint(0, 25),  # noqa: S311 . Not secure issue
                self._rnd.randint(0, 29),  # noqa: S311 . Not secure issue
            ),
            'glob': '**/*',
        })
