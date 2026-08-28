# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fk open issues search."""

from typing import final, override

import attrs

from main.services.github_objs.fk_new_issue import _IssueDict
from main.services.github_objs.open_issues import OpenIssues


@final
@attrs.define(frozen=True)
class FkOpenIssues(OpenIssues):
    """Fk open issues search."""

    _issues: list[_IssueDict]
    _label: str

    @override
    def find(self) -> bool:
        """Return True if open issues with configured label exist."""
        return any(self._label in issue['labels'] for issue in self._issues)
