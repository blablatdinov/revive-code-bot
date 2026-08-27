# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Github repository installation."""

import random
from typing import Protocol, final, override

import attrs
from django.db import transaction

from main.models import GhRepo, RepoConfig
from main.services.croniq_task import CroniqTask
from main.services.github_objs.github_client import github_repo
from main.services.github_objs.repo_installation import RegisteredRepoFromGithub
from main.services.github_objs.webhook_manager import WebhookManager
from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig
from main.services.revive_config.merged_config import MergedConfig


class RepoInstallation(Protocol):
    """Repository installation."""

    def register(self) -> None:
        """Registering new repositories."""


@final
@attrs.define(frozen=True)
class GhRepoInstallation(RepoInstallation):
    """Github repository installation."""

    _repos: list[RegisteredRepoFromGithub]
    _installation_id: int

    @override
    def register(self) -> None:
        """Registering new repositories."""
        for repo in self._repos:
            with transaction.atomic():
                repo_db_record, _ = GhRepo.objects.get_or_create(
                    full_name=repo['full_name'],
                    defaults={
                        'installation_id': self._installation_id,
                        'has_webhook': False,
                    },
                )
                gh_repo = github_repo(self._installation_id, repo['full_name'])
                WebhookManager(gh_repo).create_if_needed(repo_db_record)
                config = MergedConfig.ctor(
                    GhReviveConfig(
                        gh_repo,
                        DefaultReviveConfig(random.Random()),  # noqa: S311
                    ),
                )
                parsed = config.parse()
                RepoConfig.objects.get_or_create(
                    repo=repo_db_record,
                    defaults={
                        'cron_expression': parsed['cron'],
                        'files_glob': parsed['glob'],
                    },
                )
                CroniqTask(repo_db_record.id).apply(
                    parsed['cron'],
                )
