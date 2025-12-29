# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""New issue."""

from typing import Protocol


class NewIssue(Protocol):
    """New issue."""

    def create(self, title: str, content: str) -> None:
        """Creating issue."""
