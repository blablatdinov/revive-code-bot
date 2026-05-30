# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Worker for read process repo."""

import logging
import traceback
from time import sleep
from typing import Any

from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.db.utils import OperationalError
from django.utils import timezone

from main.models import ProcessTask, ProcessTaskStatusEnum
from main.service import process_repo
from main.services.github_objs.gh_cloned_repo import GhClonedRepo
from main.services.github_objs.gh_issue_comment import GhIssueComment
from main.services.github_objs.gh_new_issue import GhNewIssue
from main.services.github_objs.github_client import github_repo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """CLI command."""

    help = ''

    def handle(self, *args: list[str], **options: Any) -> None:  # noqa: ANN401
        """Entrypoint."""
        while True:
            try:
                process_task_record = (
                    ProcessTask.objects
                    .filter(status=ProcessTaskStatusEnum.pending)
                    .order_by('created_at')
                    .first()
                )
                if not process_task_record:
                    sleep(2)
                    continue
                repo = process_task_record.repo
                try:
                    process_task_record.status = ProcessTaskStatusEnum.in_process
                    process_task_record.traceback = ''
                    process_task_record.updated_at = timezone.now()
                    process_task_record.save()
                    process_repo(
                        repo.id,
                        GhClonedRepo(repo),
                        GhNewIssue(github_repo(repo.installation_id, repo.full_name)),
                    )
                    logger.info('Repository %s processed', repo)
                    process_task_record.status = ProcessTaskStatusEnum.success
                    process_task_record.updated_at = timezone.now()
                    process_task_record.traceback = ''
                    process_task_record.save()
                    if process_task_record.trigger_issue_id:
                        GhIssueComment(
                            repo,
                            data['data']['trigger_issue_id'],
                            # TODO: tag comment author
                            # TODO: send link to new issue
                            'Issue created',
                        ).publish()
                except Exception:
                    logger.exception('Fail process repo. Traceback: %s', traceback.format_exc())
                    process_task_record.status = ProcessTaskStatusEnum.failed
                    process_task_record.updated_at = timezone.now()
                    process_task_record.traceback = traceback.format_exc() or ''
                    process_task_record.save()
            except OperationalError:
                logger.exception('Django OperationalError. Traceback: %s\n\nSleep 5 seconds...', traceback.format_exc())
                close_old_connections()
                sleep(5)
