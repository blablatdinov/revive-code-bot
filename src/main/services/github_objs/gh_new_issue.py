# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""New issue in github."""

from typing import final, override

import attrs
from github.Repository import Repository

from main.services.github_objs.new_issue import NewIssue


@final
@attrs.define(frozen=True)
class GhNewIssue(NewIssue):
    """New issue in github."""

    _repo: Repository

    @override
    def create(self, title: str, content: str) -> None:
        """Creating issue."""
        self._repo.create_issue(title, content)
