# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Connected repos badge."""

from django.http import HttpRequest, JsonResponse

from main.models import GhRepo


def connected_repos(request: HttpRequest) -> JsonResponse:
    """Endpoint for README badge.

    https://img.shields.io/badges/endpoint-badge
    """
    return JsonResponse({
        'schemaVersion': 1,
        'label': 'Connected repos',
        'message': str(GhRepo.objects.count()),
        'color': 'blue',
    })
