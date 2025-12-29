#!/usr/bin/env python

# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Django management entrypoint."""

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line  # noqa: PLC0415
    except ImportError as exc:
        raise ImportError(' '.join([
            "Couldn't import Django. Are you sure it's installed and",
            'available on your PYTHONPATH environment variable? Did you',
            'forget to activate a virtual environment?',
        ])) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
