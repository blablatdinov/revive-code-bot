# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake issue comment."""

from typing import Self, final, override

import attrs

from main.services.github_objs.issue_comment import IssueComment


@final
@attrs.define(frozen=True)
class FkIssueComment(IssueComment):
    """Fake issue comment."""

    _published: list[str] = attrs.field(factory=list)

    @classmethod
    def ctor(cls) -> Self:
        """Ctor."""
        return cls()

    @override
    def publish(self) -> None:
        """Publish comment."""
        self._published.append('published')
