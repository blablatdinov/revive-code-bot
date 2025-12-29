# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""App custom errors."""


class AppError(Exception):
    """Root error for app."""


class InvalidaCronError(AppError):
    """Invalid cron error."""


class ConfigFileNotFoundError(AppError):
    """Config file not found error."""


class UnexpectedGhFileContentError(AppError):
    """Unexpected github file content error."""


class InvalidConfigError(AppError):
    """Invalid config error."""


class UnavailableRepoError(AppError):
    """Unavailable repo error."""
