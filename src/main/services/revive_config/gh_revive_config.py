# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive bot config from github."""

from contextlib import suppress
from http import HTTPStatus
from typing import final, override

import attrs
from github.GithubException import GithubException, UnknownObjectException
from github.Repository import Repository

from main.exceptions import UnexpectedGhFileContentError
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig
from main.services.revive_config.str_config import StrReviveConfig


@final
@attrs.define(frozen=True)
class GhReviveConfig(ReviveConfig):
    """Revive bot config from github."""

    _gh_repo: Repository
    _default_config: ReviveConfig

    @override
    def parse(self) -> ConfigDict:
        """Read from github."""
        variants = ('.revive-code-bot.yaml', '.revive-code-bot.yml')
        config = self._default_config.parse()
        for variant in variants:
            with suppress(UnknownObjectException):
                try:
                    file = self._gh_repo.get_contents(variant)
                except GithubException as err:
                    if err.status == HTTPStatus.NOT_FOUND:
                        continue
                    return config
                if isinstance(file, list):
                    raise UnexpectedGhFileContentError
                config |= StrReviveConfig(
                    file
                    .decoded_content
                    .decode('utf-8'),
                ).parse()
        return config
