# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Cloned repo."""

from pathlib import Path
from typing import Protocol


class ClonedRepo(Protocol):
    """Cloned git repository."""

    def clone_to(self, path: Path) -> Path:
        """Run cloning."""
