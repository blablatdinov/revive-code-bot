# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Webhook management helpers."""

from http import HTTPStatus
from typing import final

import attrs
from github import GithubException
from github.Repository import Repository

from main.models import GhRepo

_WEBHOOK_URL = 'https://www.rehttp.net/p/https://revive-code-bot.ilaletdinov.ru/hook/github'


def _hook_already_exists(gh_repo: Repository, url: str) -> bool:
    """Check if a webhook with the given URL already exists on the repo."""
    return any(
        hook.config.get('url') == url
        for hook in gh_repo.get_hooks()
    )


@final
@attrs.define(frozen=True)
class WebhookCreation:
    """Manage webhook creation with idempotency."""

    _gh_repo: Repository

    def create_if_needed(self, repo_db_record: GhRepo) -> None:
        """Create webhook only if it does not already exist."""
        if repo_db_record.has_webhook:
            return
        if _hook_already_exists(self._gh_repo, _WEBHOOK_URL):
            repo_db_record.has_webhook = True
            repo_db_record.save(update_fields=['has_webhook'])
            return
        try:
            self._gh_repo.create_hook(
                'web',
                {
                    'url': _WEBHOOK_URL,
                    'content_type': 'json',
                },
                ['issues', 'issue_comment', 'push'],
            )
        except GithubException as exc:
            if exc.status != HTTPStatus.UNPROCESSABLE_ENTITY:
                raise
        repo_db_record.has_webhook = True
        repo_db_record.save(update_fields=['has_webhook'])
