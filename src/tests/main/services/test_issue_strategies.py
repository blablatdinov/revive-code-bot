# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Test issue creation strategies."""

import pytest

from main.services.github_objs.fk_new_issue import FkNewIssue
from main.services.issue_strategies import apply_issue_strategy

pytestmark = [pytest.mark.django_db]

ISSUE_TITLE = 'Issue from revive-code-bot'
ISSUE_BODY = 'Stagnant files list'
ISSUE_LABEL = 'revive-code-bot'


def test_create_always_creates_new_issue():
    new_issue = FkNewIssue.ctor()
    apply_issue_strategy(new_issue, 'create_always', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert new_issue.issues[0]['title'] == ISSUE_TITLE
    assert ISSUE_LABEL in new_issue.issues[0]['labels']


def test_create_always_creates_duplicate():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, 'old body', [ISSUE_LABEL])
    apply_issue_strategy(new_issue, 'create_always', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 2


def test_update_or_create_when_no_open_issue():
    new_issue = FkNewIssue.ctor()
    apply_issue_strategy(new_issue, 'update_or_create', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert ISSUE_LABEL in new_issue.issues[0]['labels']


def test_update_or_create_updates_existing():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, 'old body', [ISSUE_LABEL])
    apply_issue_strategy(new_issue, 'update_or_create', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert new_issue.issues[0]['body'] == ISSUE_BODY


def test_update_or_create_skips_closed_issue():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, 'old body', [ISSUE_LABEL])
    new_issue.issues[0]['state'] = 'closed'
    apply_issue_strategy(new_issue, 'update_or_create', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 2
    assert new_issue.issues[0]['body'] == 'old body'
    assert new_issue.issues[1]['body'] == ISSUE_BODY


def test_update_or_create_ignores_different_title():
    new_issue = FkNewIssue.ctor()
    new_issue.create('Different title', 'old body', [ISSUE_LABEL])
    apply_issue_strategy(new_issue, 'update_or_create', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 2


def test_create_after_close_no_previous():
    new_issue = FkNewIssue.ctor()
    apply_issue_strategy(new_issue, 'create_after_close', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert ISSUE_LABEL in new_issue.issues[0]['labels']


def test_create_after_close_after_previous_closed():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, 'old body', [ISSUE_LABEL])
    new_issue.issues[0]['state'] = 'closed'
    apply_issue_strategy(new_issue, 'create_after_close', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 2


def test_create_after_close_skips_when_open_exists():
    new_issue = FkNewIssue.ctor()
    new_issue.create(ISSUE_TITLE, 'old body', [ISSUE_LABEL])
    apply_issue_strategy(new_issue, 'create_after_close', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
    assert new_issue.issues[0]['body'] == 'old body'


def test_unknown_strategy_defaults_to_create():
    new_issue = FkNewIssue.ctor()
    apply_issue_strategy(new_issue, 'unknown', ISSUE_TITLE, ISSUE_BODY)
    assert len(new_issue.issues) == 1
