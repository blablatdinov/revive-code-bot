# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test issue creation strategies."""

import pytest

from main.services.github_objs.fk_new_issue import FkNewIssue
from main.services.github_objs.fk_open_issues import FkOpenIssues
from main.services.issue_strategies import apply_issue_strategy

pytestmark = [pytest.mark.django_db]

ISSUE_TITLE = 'Issue from revive-code-bot'
ISSUE_BODY = 'Stagnant files list'
ISSUE_LABEL = 'revive-code-bot'
OLD_BODY = 'old body'
STRATEGY_CREATE_ALWAYS = 'create_always'
STRATEGY_SKIP_IF_EXISTS = 'skip_if_exists'


def test_create_always_creates_new():
    new_issue = FkNewIssue.ctor()
    open_issues = FkOpenIssues(new_issue.issues, ISSUE_LABEL)
    apply_issue_strategy(new_issue, open_issues, STRATEGY_CREATE_ALWAYS, ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert ISSUE_LABEL in new_issue.issues[0]['labels']


def test_create_always_creates_duplicate():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, OLD_BODY, [ISSUE_LABEL])
    open_issues = FkOpenIssues(new_issue.issues, ISSUE_LABEL)
    apply_issue_strategy(new_issue, open_issues, STRATEGY_CREATE_ALWAYS, ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 2


def test_skip_if_exists_no_open_issue():
    new_issue = FkNewIssue.ctor()
    open_issues = FkOpenIssues(new_issue.issues, ISSUE_LABEL)
    apply_issue_strategy(new_issue, open_issues, STRATEGY_SKIP_IF_EXISTS, ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert ISSUE_LABEL in new_issue.issues[0]['labels']


def test_skip_if_exists_skips_when_open():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, OLD_BODY, [ISSUE_LABEL])
    open_issues = FkOpenIssues(new_issue.issues, ISSUE_LABEL)
    apply_issue_strategy(new_issue, open_issues, STRATEGY_SKIP_IF_EXISTS, ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert new_issue.issues[0]['body'] == OLD_BODY


def test_skip_if_exists_ignores_different_label():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, OLD_BODY, ['other-label'])
    open_issues = FkOpenIssues(new_issue.issues, ISSUE_LABEL)
    apply_issue_strategy(new_issue, open_issues, STRATEGY_SKIP_IF_EXISTS, ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 2


def test_unknown_strategy_defaults_to_create():
    new_issue = FkNewIssue.ctor()
    open_issues = FkOpenIssues(new_issue.issues, ISSUE_LABEL)
    apply_issue_strategy(new_issue, open_issues, 'unknown', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
