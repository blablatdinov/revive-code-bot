# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive bot config."""

from typing import Protocol, TypedDict


class ConfigDict(TypedDict):
    """Configuration structure."""

    limit: int
    cron: str
    glob: str


class ReviveConfig(Protocol):
    """Revive bot config."""

    def parse(self) -> ConfigDict:
        """Parsing."""
