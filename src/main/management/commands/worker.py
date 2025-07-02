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

import json
import logging
import traceback
from contextlib import closing
from time import sleep
from typing import Any

import pika
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import close_old_connections
from django.db.utils import OperationalError
from django.db import connection
from django.utils import timezone
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from main.models import ProcessTask, ProcessTaskStatusEnum
from main.service import process_repo
from main.services.github_objs.gh_cloned_repo import GhClonedRepo
from main.services.github_objs.gh_new_issue import GhNewIssue
from main.services.github_objs.github_client import github_repo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """CLI command."""

    help = ''

    def _callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: bytes) -> None:
        logger.info('Message %s received, handling...', body)
        data = json.loads(body.decode('utf-8'))
        process_task_record = ProcessTask.objects.get(id=data['data']['process_task_id'])
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
        except Exception:  # noqa: BLE001
            logger.exception('Fail process repo. Traceback: %s', traceback.format_exc())
            process_task_record.status = ProcessTaskStatusEnum.failed
            process_task_record.updated_at = timezone.now()
            process_task_record.traceback = traceback.format_exc() or ''
            process_task_record.save()
        if method.delivery_tag is not None:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            logger.warning('Received message with None delivery_tag')

    # "Any" annotation taken from
    # https://github.com/typeddjango/django-stubs/blob/c7df64/django-stubs/core/management/commands/check.pyi#L6
    def handle(self, *args: list[str], **options: Any) -> None:  # noqa: ANN401
        """Entrypoint."""
        while True:
            try:
                if connection.connection and not connection.is_usable():
                    connection.close()
                with closing(
                    pika.BlockingConnection(pika.ConnectionParameters(
                        virtual_host=settings.RABBITMQ_VHOST,
                        host=settings.RABBITMQ_HOST,
                        port=settings.RABBITMQ_PORT,
                        credentials=pika.PlainCredentials(
                            settings.RABBITMQ_USER,
                            settings.RABBITMQ_PASS,
                        ),
                    )),
                ) as rq_connection:
                    channel = rq_connection.channel()
                    queue_name = settings.REPO_PROCESS_ORDER_QUEUE_NAME
                    channel.queue_declare(queue=queue_name, durable=True)
                    channel.basic_qos(prefetch_count=1)
                    channel.basic_consume(queue=queue_name, on_message_callback=self._callback)
                    logger.info('Starting consuming...')
                    try:
                        channel.start_consuming()
                    except KeyboardInterrupt:
                        logger.info('Stopped by user')
                        channel.stop_consuming()
                        break
            except OperationalError:
                logger.exception('Django OperationalError. Traceback: %s\n\nSleep 5 seconds...', traceback.format_exc())
                close_old_connections()
                sleep(5)
