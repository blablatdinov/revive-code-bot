# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Open issues search."""

from typing import Protocol


class OpenIssues(Protocol):
    """Open issues search."""

    def find(self) -> bool:
        """Return True if open issues with configured label exist."""
