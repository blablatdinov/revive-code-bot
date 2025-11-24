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
                    "method": "POST",
                    "headers": {
                        "Accept": "*/*",
                        "Connection": "keep-alive",
                        "User-Agent": "croniq/0.1.0",
                        "Authentication": "Basic ZPIsBFa38Ob8hz4ISw8UXT4qe4eDz9AEA4FIOLa4Xis6aK9GPP",
                        "Accept-Encoding": "deflate, zstd",
                    },
                },
                headers=auth_headers,
                timeout=5,
            )
            print(response.content)
            response.raise_for_status()
        else:
            response = requests.put(
                '{0}/api/v1/tasks/{1}'.format(settings.CRONIQ_DOMAIN, response.json()['results'][0]['id']),
                json={
                    'schedule': cron,
                    'name': name,
                    'schedule': cron,
                    'url': f'https://revive-code-bot.ilaletdinov.ru/process-repo/{self._repo_id}',
                    "method": "POST",
                    "headers": {
                        "Accept": "*/*",
                        "Connection": "keep-alive",
                        "User-Agent": "croniq/0.1.0",
                        "Authentication": "Basic ZPIsBFa38Ob8hz4ISw8UXT4qe4eDz9AEA4FIOLa4Xis6aK9GPP",
                        "Accept-Encoding": "deflate, zstd",
                    },
                },
                headers=auth_headers,
                timeout=5,
            )
            response.raise_for_status()
