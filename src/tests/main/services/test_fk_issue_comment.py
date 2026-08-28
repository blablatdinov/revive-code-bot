# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test fake issue comment."""

from main.services.github_objs.fk_issue_comment import FkIssueComment


def test_publish_appends_to_published():
    comment = FkIssueComment.ctor()
    comment.publish()
    comment.publish()
    assert len(comment._published) == 2  # noqa: SLF001
