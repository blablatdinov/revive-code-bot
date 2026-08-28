# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Issue comment."""

from typing import Protocol


class IssueComment(Protocol):
    """Issue comment."""

    def publish(self) -> None:
        """Publish."""
