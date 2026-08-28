# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Issue creation strategies."""

from main.services.github_objs.new_issue import NewIssue
from main.services.github_objs.open_issues import OpenIssues

ISSUE_LABEL = 'revive-code-bot'

STRATEGY_CREATE_ALWAYS = 'create_always'
STRATEGY_SKIP_IF_EXISTS = 'skip_if_exists'


def apply_issue_strategy(
    new_issue: NewIssue,
    open_issues: OpenIssues,
    strategy: str,
    title: str,
    body: str,
) -> None:
    """Apply issue creation strategy.

    Args:
        new_issue: Issue creation object.
        open_issues: Open issues search object.
        strategy: Strategy name ('create_always' or 'skip_if_exists').
        title: Issue title.
        body: Issue body content.

    """
    if strategy == STRATEGY_SKIP_IF_EXISTS and open_issues.find():
        return
    new_issue.create(title, body, [ISSUE_LABEL])
