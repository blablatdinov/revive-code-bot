# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fk issue storage."""

from typing import Self, TypedDict, final, override

import attrs

from main.services.github_objs.new_issue import NewIssue


class _IssueDict(TypedDict):

    title: str
    content: str


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
    def create(self, title: str, content: str) -> None:
        """Creating issue."""
        self.issues.append({
            'title': title,
            'content': content,
        })
