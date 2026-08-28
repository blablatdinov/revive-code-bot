# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Open issues in github."""

from typing import final, override

import attrs
from github.Repository import Repository

from main.services.github_objs.open_issues import OpenIssues


@final
@attrs.define(frozen=True)
class GhOpenIssues(OpenIssues):
    """Open issues in github."""

    _repo: Repository
    _label: str

    @override
    def find(self) -> bool:
        """Return True if open issues with configured label exist."""
        issues = self._repo.get_issues(state='open', labels=[self._label])
        return bool(list(issues))
