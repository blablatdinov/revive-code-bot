# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""New issue in github."""

from typing import final, override

import attrs
from github.Repository import Repository

from main.services.github_objs.new_issue import IssueInfo, NewIssue


@final
@attrs.define(frozen=True)
class GhNewIssue(NewIssue):
    """New issue in github."""

    _repo: Repository

    @override
    def create(self, title: str, body: str, labels: list[str] | None = None) -> None:
        """Creating issue."""
        self._repo.create_issue(title, body, labels=labels or [])

    @override
    def find_issues(self, label: str, state: str) -> list[IssueInfo]:
        """Find issues by label and state."""
        return [
            IssueInfo({
                'number': issue.number,
                'title': issue.title,
                'state': issue.state,
            })
            for issue in self._repo.get_issues(state=state, labels=[label])
        ]

    @override
    def update_issue(self, issue_number: int, body: str) -> None:
        """Update existing issue body."""
        issue = self._repo.get_issue(issue_number)
        issue.edit(body=body)
