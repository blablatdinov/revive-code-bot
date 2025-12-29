# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Primary app config."""

from django.apps import AppConfig


class MainConfig(AppConfig):
    """Configuration for main app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'
