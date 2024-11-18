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

from typing import TypedDict, Protocol, final
from contextlib import suppress

import attrs
from github.Repository import Repository

from main.services.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class GhReviveConfig(ReviveConfig):

    _gh_repo: Repository
    _default_config: ReviveConfig

    def parse(self) -> ConfigDict:
        variants = ('.revive-bot.yaml', '.revive-bot.yml')
        # TODO
        repo_config: dict[str, str | int] = {}
        default_config = self._default_config.parse()
        for variant in variants:
            with suppress(UnknownObjectException):
                file = self._gh_repo.get_contents(variant)
                if isinstance(file, list):
                    # TODO
                    raise Exception
                # TODO
                repo_config = read_config(  # type: ignore[assignment]
                    file
                    .decoded_content
                    .decode('utf-8'),
                )
        return default_config | repo_config
