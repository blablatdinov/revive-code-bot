# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""GitHub issue comment."""

from typing import final, override

import attrs
from github.Repository import Repository

from main.services.github_objs.issue_comment import IssueComment


@final
@attrs.define(frozen=True)
class GhIssueComment(IssueComment):
    """GitHub issue comment."""

    _repo: Repository
    _issue_number: int
    _comment_text: str

    @override
    def publish(self) -> None:
        """Publish comment."""
        self._repo.get_issue(number=self._issue_number).create_comment(self._comment_text)
