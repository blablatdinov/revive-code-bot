# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Module for working with Croniq API tasks."""

from typing import final

import attrs
import requests
from django.conf import settings


@final
@attrs.define(frozen=True)
class CroniqTask:
    """Class for managing tasks in Croniq API.

    Provides functionality for creating and updating tasks
    in the Croniq scheduler system.
    """

    _repo_id: int

    def apply(self, cron: str) -> None:
        """Apply cron expression to a task in Croniq.

        Creates a new task if it doesn't exist, or updates
        an existing task with a new schedule.
        """
        name = 'repo_{0}'.format(self._repo_id)
        auth_headers = {'Authorization': 'Basic {0}'.format(settings.CRONIQ_API_KEY)}
        response = requests.get(
            '{0}/api/v1/tasks?name={1}'.format(settings.CRONIQ_DOMAIN, name),
            headers=auth_headers,
            timeout=5,
        )
        response.raise_for_status()
        if not response.json()['results']:
            response = requests.post(
                '{0}/api/v1/tasks'.format(settings.CRONIQ_DOMAIN),
                json={
                    'name': name,
                    'schedule': cron,
                    'url': f'https://revive-code-bot.ilaletdinov.ru/process-repo/{self._repo_id}',
                    'method': 'POST',
                    'headers': {
                        'Accept': '*/*',
                        'Connection': 'keep-alive',
                        'User-Agent': 'croniq/0.1.0',
                        'Authentication': f'Basic {settings.BASIC_AUTH_TOKEN}',
                        'Accept-Encoding': 'deflate, zstd',
                    },
                },
                headers=auth_headers,
                timeout=5,
            )
            response.raise_for_status()
        else:
            response = requests.put(
                '{0}/api/v1/tasks/{1}'.format(settings.CRONIQ_DOMAIN, response.json()['results'][0]['id']),
                json={
                    'schedule': cron,
                    'name': name,
                    'url': f'https://revive-code-bot.ilaletdinov.ru/process-repo/{self._repo_id}',
                    'method': 'POST',
                    'headers': {
                        'Accept': '*/*',
                        'Connection': 'keep-alive',
                        'User-Agent': 'croniq/0.1.0',
                        'Authentication': f'Basic {settings.BASIC_AUTH_TOKEN}',
                        'Accept-Encoding': 'deflate, zstd',
                    },
                },
                headers=auth_headers,
                timeout=5,
            )
            response.raise_for_status()
