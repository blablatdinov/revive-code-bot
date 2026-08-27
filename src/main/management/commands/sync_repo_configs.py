# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Sync repo configs and Croniq tasks for repos without config."""

import logging
import random
from typing import Any

from django.core.management.base import BaseCommand

from main.exceptions import UnavailableRepoError
from main.models import GhRepo, RepoConfig, RepoStatusEnum
from main.services.croniq_task import CroniqTask
from main.services.github_objs.github_client import github_repo
from main.services.revive_config.default_revive_config import DefaultReviveConfig
from main.services.revive_config.gh_revive_config import GhReviveConfig
from main.services.revive_config.merged_config import MergedConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """CLI command."""

    help = 'Sync repo configs and Croniq tasks for repos without a RepoConfig'

    def handle(self, *args: list[str], **options: Any) -> None:  # noqa: ANN401
        """Entrypoint."""
        for repo_db_record in GhRepo.objects.filter(repoconfig__isnull=True):
            try:
                gh_repo = github_repo(repo_db_record.installation_id, repo_db_record.full_name)
            except UnavailableRepoError:
                logger.warning('Repo %s unavailable, marking inactive', repo_db_record.full_name)
                repo_db_record.status = RepoStatusEnum.inactive
                repo_db_record.save()
                continue
            config = MergedConfig.ctor(
                GhReviveConfig(
                    gh_repo,
                    DefaultReviveConfig(random.Random()),  # noqa: S311
                ),
            )
            parsed_config = config.parse()
            RepoConfig.objects.create(
                repo=repo_db_record,
                cron_expression=parsed_config['cron'],
            )
            CroniqTask(repo_db_record.id).apply(
                parsed_config['cron'],
            )
            self.stdout.write('Synced config for {0}'.format(repo_db_record.full_name))
