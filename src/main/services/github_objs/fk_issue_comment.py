# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Fake issue comment."""

from typing import Self, final, override

import attrs

from main.services.github_objs.issue_comment import IssueComment


@final
@attrs.define
# This fake class for tests
class FkIssueComment(IssueComment):  # noqa: PEO200
    """Fake issue comment."""

    published: list[str]  # noqa: PEO300

    @classmethod
    def ctor(cls) -> Self:
        """Ctor."""
        return cls([])  # noqa: PEO102

    @override
    def publish(self) -> None:
        """Publish comment."""
        self.published.append('published')
