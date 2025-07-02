import httpx
from django.conf import settings
from typing import Optional, final


@final
@attrs.define(frozen=True)
class CroniqTask:

    _repo_id: int

    def apply(self, repo_id: int, cron: str):
        name = "repo_{0}".format(repo_id)
        auth_headers = {"Authorization": "Basic {0}".format(settings.CRONIQ_API_KEY)}
        response = httpx.get(
            "{0}/api/v1/tasks?name={1}".format(settings.CRONIQ_DOMAIN, name),
            headers={"Authorization": "Basic {0}".format(settings.CRONIQ_API_KEY)},
        )
        response.raise_for_status()
        if not repsonse['results']:
            response = httpx.post(
                "{0}/api/v1/tasks".format(settings.CRONIQ_DOMAIN),
                json={
                    "name": "repo_{0}".format(repo_id),
                    "schedule": cron,
                },
                auth_headers,
            )
            response.raise_for_status()
        else:
            response = httpx.put(
                "{0}/api/v1/tasks/{1}".format(settings.CRONIQ_DOMAIN, response['results'][0]['id']),
                json={"schedule": cron},
                auth_headers,
            )
            response.raise_for_status()
