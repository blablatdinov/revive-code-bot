# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Routers."""

from django.conf import settings
from django.contrib import admin
from django.urls import path

from main.views.connected_repos import connected_repos
from main.views.gh_webhook import gh_webhook
from main.views.healthcheck import healthcheck
from main.views.index import index
from main.views.process_repo import process_repo_view

urlpatterns = [
    path('', index),
    path('health-check/', healthcheck),
    path('hook/github', gh_webhook),
    path('process-repo/<int:repo_id>', process_repo_view),
    path('connected-repos/', connected_repos),
    path('{0}admin/'.format(settings.ADMIN_SECRET_PATH), admin.site.urls),
]
