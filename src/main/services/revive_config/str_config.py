# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Config from string."""

from typing import final, override

import attrs
import yaml
from cron_validator import CronValidator  # type: ignore [import-untyped]

from main.exceptions import InvalidaCronError, InvalidConfigError
from main.services.revive_config.revive_config import ConfigDict, ReviveConfig


@final
@attrs.define(frozen=True)
class StrReviveConfig(ReviveConfig):
    """Config from string."""

    _config: str

    @override
    def parse(self) -> ConfigDict:
        """Parse config."""
        parsed_config: ConfigDict | None = yaml.safe_load(self._config)
        if not parsed_config:
            raise InvalidConfigError
        if parsed_config.get('cron'):
            # TODO: notify repository owner
            try:
                CronValidator.parse(parsed_config['cron'])
            except ValueError as err:
                msg = 'Cron expression: "{0}" has invalid format'.format(parsed_config['cron'])
                raise InvalidaCronError(msg) from err
        return parsed_config
