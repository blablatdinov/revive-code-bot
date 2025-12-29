# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""HTTP controller for render index page."""

from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render


def index(request: HttpRequest) -> HttpResponse:
    """Show index page."""
    return render(request, 'index.html')
