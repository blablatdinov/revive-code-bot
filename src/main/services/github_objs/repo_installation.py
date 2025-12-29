# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Repository installation."""

from typing import TypedDict, final


@final
class RegisteredRepoFromGithub(TypedDict):
    """Github webhook needed fields."""

    full_name: str
