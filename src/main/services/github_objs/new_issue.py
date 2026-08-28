# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""New issue."""

from typing import Protocol, TypedDict


class IssueInfo(TypedDict):
    """Info about existing issue."""

    number: int
    title: str
    state: str


class NewIssue(Protocol):
    """New issue."""

    def create(self, title: str, body: str, labels: list[str] | None = None) -> None:
        """Creating issue."""

    def find_issues(self, label: str, state: str) -> list[IssueInfo]:
        """Find issues by label and state."""

    def update_issue(self, issue_number: int, body: str) -> None:
        """Update existing issue body."""
