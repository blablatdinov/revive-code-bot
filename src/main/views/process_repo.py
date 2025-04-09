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

"""HTTP controller for process repo."""

import datetime
import json
import logging
import traceback
import uuid
from contextlib import closing

import pika
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from pika.exchange_type import ExchangeType

from main.models import GhRepo, ProcessTask, ProcessTaskStatusEnum

logger = logging.getLogger(__name__)


def publish_event(event_data: dict) -> None:
    """Publishing event in rabbitmq."""
    try:
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
        ) as connection:
            exchange_name = 'ordered_repos'
            channel = connection.channel()
            channel.exchange_declare(exchange=exchange_name, exchange_type=ExchangeType.direct, durable=True)
            channel.basic_publish(
                exchange=exchange_name,
                body=json.dumps(event_data),
                routing_key='ordered_repos',
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json',
                ),
            )
            logger.info('Message "%s" published', event_data)
    except Exception:
        logger.exception('Error on publishing message. Traceback: %s', traceback.format_exc())
        task = ProcessTask.objects.get(id=event_data['data']['process_task_id'])
        task.status = ProcessTaskStatusEnum.failed
        task.traceback = traceback.format_exc()
        task.save()


@csrf_exempt
def process_repo_view(request: HttpRequest, repo_id: int) -> HttpResponse:
    """Webhook for process repo."""
    if (
        not request.headers.get('Authentication')
        or request.headers['Authentication'] != 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN)
    ):
        raise PermissionDenied
    repo = get_object_or_404(GhRepo, id=repo_id)
    process_task = ProcessTask.objects.create(
        repo=repo,
        status=ProcessTaskStatusEnum.pending,
    )
    publish_event({
        'event_id': str(uuid.uuid4()),
        'event_version': 1,
        'event_name': 'RepoOrdered',
        'event_time': str(datetime.datetime.now(tz=datetime.UTC)),
        'producer': 'revive_bot.django',
        'data': {'process_task_id': process_task.id},
    })
    return JsonResponse(
        {'process_task_id': process_task.id},
        status=201,
    )
