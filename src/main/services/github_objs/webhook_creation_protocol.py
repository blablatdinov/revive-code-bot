# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Webhook creation protocol."""

from typing import Protocol

from main.models import GhRepo


class WebhookCreationProtocol(Protocol):
    """Manage webhook creation with idempotency."""

    def create_if_needed(self, repo_db_record: GhRepo) -> None:
        """Create webhook only if it does not already exist."""
