# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Issue creation strategies."""

from main.services.github_objs.new_issue import NewIssue

ISSUE_LABEL = 'revive-code-bot'


def apply_issue_strategy(
    new_issue: NewIssue,
    strategy: str,
    title: str,
    body: str,
) -> None:
    """Apply issue creation strategy.

    Args:
        new_issue: Issue abstraction.
        strategy: Strategy name ('create_always', 'update_or_create', 'create_after_close').
        title: Issue title.
        body: Issue body content.

    """
    if strategy == 'create_always':
        new_issue.create(title, body, [ISSUE_LABEL])
    elif strategy == 'update_or_create':
        open_issues = new_issue.find_issues(ISSUE_LABEL, 'open')
        matching = [issue for issue in open_issues if issue['title'] == title]
        if matching:
            new_issue.update_issue(matching[0]['number'], body)
        else:
            new_issue.create(title, body, [ISSUE_LABEL])
    elif strategy == 'create_after_close':
        open_issues = new_issue.find_issues(ISSUE_LABEL, 'open')
        matching = [issue for issue in open_issues if issue['title'] == title]
        if not matching:
            new_issue.create(title, body, [ISSUE_LABEL])
    else:
        new_issue.create(title, body, [ISSUE_LABEL])
