# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""HTTP controller for process repo."""

import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from main.models import GhRepo, ProcessTask, ProcessTaskStatusEnum

logger = logging.getLogger(__name__)


def create_process_task(repo: GhRepo, trigger_issue_id: int | None = None) -> ProcessTask:
    """Create a process task for a repository."""
    return ProcessTask.objects.create(
        repo=repo,
        status=ProcessTaskStatusEnum.pending,
    )


@csrf_exempt
def process_repo_view(request: HttpRequest, repo_id: int) -> HttpResponse:
    """Webhook for process repo."""
    if (
        not request.headers.get('Authentication')
        or request.headers['Authentication'] != 'Basic {0}'.format(settings.BASIC_AUTH_TOKEN)
    ):
        raise PermissionDenied
    repo = get_object_or_404(GhRepo, id=repo_id)
    process_task = create_process_task(repo)
    return JsonResponse(
        {'process_task_id': process_task.id},
        status=201,
    )
