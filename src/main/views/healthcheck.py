# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""HTTP healthcheck."""


from django.http import HttpRequest, JsonResponse


def healthcheck(request: HttpRequest) -> JsonResponse:
    """Endpoint for checking app."""
    return JsonResponse({
        'app': 'ok',
    })
