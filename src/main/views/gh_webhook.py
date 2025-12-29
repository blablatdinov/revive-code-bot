# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Github webhook."""

import json

from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from main.exceptions import UnavailableRepoError
from main.models import RepoStatusEnum
from main.service import get_or_create_repo, is_default_branch, update_config
from main.services.github_objs.gh_repo_installation import GhRepoInstallation


@csrf_exempt
def gh_webhook(request: HttpRequest) -> HttpResponse:  # noqa: PLR0911 . TODO
    """Process webhooks from github."""
    with transaction.atomic():
        gh_event = request.headers.get('X-GitHub-Event')
        if not gh_event:
            return HttpResponse(status=422)
        request_json = json.loads(request.body)
        if gh_event == 'installation':
            installation_id = request_json['installation']['id']
            GhRepoInstallation(
                request_json['repositories'],
                installation_id,
            ).register()
            return HttpResponse('Repos installed')
        elif gh_event == 'installation_repositories':
            installation_id = request_json['installation']['id']
            GhRepoInstallation(
                request_json['repositories_added'],
                installation_id,
            ).register()
            return HttpResponse('Repos installed')
        try:
            pg_repo = get_or_create_repo(
                request_json['repository']['full_name'],
                int(request.headers['X-Github-Hook-Installation-Target-Id']),
            )
        except UnavailableRepoError:
            return HttpResponse('Repo unavailable', status=404)
        if gh_event == 'ping':
            return HttpResponse('Webhooks installed')
        elif gh_event == 'push':
            if pg_repo.status != RepoStatusEnum.active:
                return HttpResponse('Skip as inactive')
            if not is_default_branch(request_json):
                return HttpResponse('Skip not default branch')
            update_config(request_json['repository']['full_name'])
            return HttpResponse('Config updated')
        return HttpResponse('Unprocessable event type')
