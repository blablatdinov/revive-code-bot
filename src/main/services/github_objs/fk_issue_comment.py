# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake issue comment."""

from typing import Self, final, override

import attrs

from main.services.github_objs.issue_comment import IssueComment


@final
@attrs.define
class FkIssueComment(IssueComment):
    """Fake issue comment."""

    published: list[str]

    @classmethod
    def ctor(cls) -> Self:
        """Ctor."""
        return cls([])

    @override
    def publish(self) -> None:
        """Publish comment."""
        self.published.append('published')
