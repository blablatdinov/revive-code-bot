# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fk git repo."""

import zipfile
from pathlib import Path
from typing import final, override

import attrs

from main.services.github_objs.cloned_repo import ClonedRepo


@final
@attrs.define(frozen=True)
class FkClonedRepo(ClonedRepo):
    """Fk git repo."""

    _zipped_repo: Path

    @override
    def clone_to(self, path: Path) -> Path:
        """Unzipping repo from archieve."""
        with zipfile.ZipFile(self._zipped_repo, 'r') as zip_ref:
            zip_ref.extractall(path)
        return path
