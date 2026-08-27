# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Github webhook."""

import hashlib
import hmac
import json
import secrets

from django.conf import settings
from django.db import transaction
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from main.exceptions import UnavailableRepoError
from main.models import GhRepo, ProcessTask, ProcessTaskStatusEnum, RepoStatusEnum
from main.service import (
    _RequestForCheckBranchDefault,
    get_or_create_repo,
    is_default_branch,
    update_config,
)
from main.services.github_objs.gh_repo_installation import GhRepoInstallation

SCAN_TRIGGER_COMMENT = '@revive-code-bot scan repo'


def verify_signature(request: HttpRequest) -> bool:
    """Verify GitHub webhook signature."""
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        return True
    signature = request.headers.get('X-Hub-Signature-256')
    if not signature:
        return False
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        request.body,
        hashlib.sha256,
    ).hexdigest()
    return secrets.compare_digest(signature, expected)


def _handle_push(pg_repo: GhRepo, request_json: _RequestForCheckBranchDefault) -> HttpResponse:
    """Handle push webhook event."""
    if pg_repo.status != RepoStatusEnum.active:
        return HttpResponse('Skip as inactive')
    if not is_default_branch(request_json):
        return HttpResponse('Skip not default branch')
    update_config(request_json['repository']['full_name'])
    return HttpResponse('Config updated')


@csrf_exempt
def gh_webhook(request: HttpRequest) -> HttpResponse:  # noqa: PLR0911 . TODO
    """Process webhooks from github."""
    with transaction.atomic():
        if not verify_signature(request):
            return HttpResponse('Invalid signature', status=403)
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
        match gh_event:
            case 'ping':
                return HttpResponse('Webhooks installed')
            case 'push':
                return _handle_push(pg_repo, request_json)
            case 'issue_comment' if SCAN_TRIGGER_COMMENT in request_json['comment']['body'].lower():
                ProcessTask.objects.create(
                    repo=pg_repo,
                    status=ProcessTaskStatusEnum.pending,
                    trigger_issue_id=request_json['issue']['number'],
                )
                return HttpResponse('Manual scan triggered')
        return HttpResponse('Unprocessable event type')
