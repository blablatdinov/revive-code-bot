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
from github.GithubException import GithubException

from main.exceptions import UnavailableRepoError
from main.models import GhRepo, ProcessTask, ProcessTaskStatusEnum, RepoStatusEnum
from main.service import process_repo
from main.services.github_objs.gh_cloned_repo import GhClonedRepo
from main.services.github_objs.gh_issue_comment import GhIssueComment
from main.services.github_objs.gh_new_issue import GhNewIssue
from main.services.github_objs.github_client import github_repo

logger = logging.getLogger(__name__)


def mark_failed(task: ProcessTask) -> None:
    """Mark a process task as failed with traceback."""
    task.status = ProcessTaskStatusEnum.failed
    task.updated_at = timezone.now()
    task.traceback = traceback.format_exc() or ''
    task.save()


def deactivate_repo(repo: GhRepo, task: ProcessTask) -> None:
    """Deactivate repo and mark task as failed."""
    repo.status = RepoStatusEnum.inactive
    repo.save()
    mark_failed(task)


def notify_trigger_issue(task: ProcessTask, repo: GhRepo) -> None:
    """Post a comment on the trigger issue after successful processing."""
    if task.trigger_issue_id:
        GhIssueComment(
            github_repo(repo.installation_id, repo.full_name),
            task.trigger_issue_id,
            'Issue created',
        ).publish()


def handle_github_exception(err: GithubException, repo: GhRepo, task: ProcessTask) -> bool:
    """Handle GithubException. Returns True if handled, False to re-raise."""
    if 'Issues has been disabled in this repository' not in str(err):
        return False
    logger.warning('Issues has been disabled in this repository')
    deactivate_repo(repo, task)
    return True


class Command(BaseCommand):
    """CLI command."""

    help = ''

    def handle(self, *args: list[str], **options: Any) -> None:  # noqa: ANN401
        """Entrypoint."""
        while True:
            try:  # noqa: PLW0717
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
                try:  # noqa: PLW0717
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
                    notify_trigger_issue(process_task_record, repo)
                except GithubException as err:
                    if not handle_github_exception(err, repo, process_task_record):
                        raise
                except UnavailableRepoError:
                    logger.exception('Issues has been disabled in this repository')
                    deactivate_repo(repo, process_task_record)
                except Exception:
                    logger.exception('Fail process repo. Traceback: %s', traceback.format_exc())
                    mark_failed(process_task_record)
            except OperationalError:
                logger.exception('Django OperationalError. Traceback: %s\n\nSleep 5 seconds...', traceback.format_exc())
                close_old_connections()
                sleep(5)
