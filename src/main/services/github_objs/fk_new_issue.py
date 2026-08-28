# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fk issue storage."""

from typing import Self, TypedDict, final, override

import attrs

from main.services.github_objs.new_issue import IssueInfo, NewIssue


class _IssueDict(TypedDict):

    title: str
    body: str
    labels: list[str]
    number: int
    state: str


@final
@attrs.define
class FkNewIssue(NewIssue):
    """Fk issue storage."""

    issues: list[_IssueDict]

    @classmethod
    def ctor(cls) -> Self:
        """Ctor."""
        return cls([])

    @override
    def create(self, title: str, body: str, labels: list[str] | None = None) -> None:
        """Creating issue."""
        self.issues.append({
            'title': title,
            'body': body,
            'labels': labels or [],
            'number': len(self.issues) + 1,
            'state': 'open',
        })

    @override
    def find_issues(self, label: str, state: str) -> list[IssueInfo]:
        """Find issues by label and state."""
        return [
            IssueInfo({
                'number': issue['number'],
                'title': issue['title'],
                'state': issue['state'],
            })
            for issue in self.issues
            if label in issue['labels'] and issue['state'] == state
        ]

    @override
    def update_issue(self, issue_number: int, body: str) -> None:
        """Update existing issue body."""
        for issue in self.issues:
            if issue['number'] == issue_number:
                issue['body'] = body
                return
