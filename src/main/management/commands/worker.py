# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
