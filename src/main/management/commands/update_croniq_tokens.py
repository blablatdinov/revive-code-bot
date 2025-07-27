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

"""Command to update the token in all Croniq tasks."""

import logging

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from main.models import GhRepo, RepoConfig

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to update the token in all Croniq tasks (Authorization header)."""

    help = 'Updates the token in all Croniq tasks (Authorization header)'

    def handle(self, *args, **kwargs) -> None:
        """Update the token in all Croniq tasks."""
        success, failed = 0, 0
        for repo in GhRepo.objects.all():
            try:
                config = RepoConfig.objects.filter(repo=repo).first()
                if not config:
                    logger.warning('No config found for repository %s', repo.full_name)
                    continue
                name = f'repo_{repo.id}'
                croniq_auth_headers = {'authorization': f'Basic {settings.CRONIQ_API_KEY}'}
                resp = requests.get(
                    f'{settings.CRONIQ_DOMAIN}/api/v1/tasks?name={name}',
                    headers=croniq_auth_headers,
                    timeout=5,
                )
                resp.raise_for_status()
                results = resp.json().get('results', [])
                if not results:
                    logger.warning('Task %s not found in Croniq', name)
                    continue
                task = results[0]
                put_resp = requests.put(
                    f'{settings.CRONIQ_DOMAIN}/api/v1/tasks/{task["id"]}',
                    json={
                        'name': name,
                        'schedule': config.cron_expression,
                        'url': task.get('url'),
                        'headers': {
                            'Authentication': f'Basic {settings.BASIC_AUTH_TOKEN}',
                            'Accept': '*/*',
                            'Accept-Encoding': 'deflate, zstd',
                            'Connection': 'keep-alive',
                            'User-Agent': 'croniq/0.1.0',
                        },
                    },
                    headers=croniq_auth_headers,
                    timeout=5,
                )
                put_resp.raise_for_status()
                logger.info('Token updated for %s (id=%s)', repo.full_name, repo.id)
                success += 1
            except Exception:  # noqa: BLE001
                logger.exception('Error for %s', repo.full_name)
                failed += 1
        logger.info('Done! Success: %s, failed: %s', success, failed)
