# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Synchronize touch records."""

import datetime
from typing import Protocol, final, override

import attrs

from main.models import TouchRecord


class SynchronizeTouchRecords(Protocol):
    """Synchronize touch records."""

    def sync(self, files: list[str], repo_id: int) -> None:
        """Sync."""


@final
@attrs.define(frozen=True)
class PgSynchronizeTouchRecords(SynchronizeTouchRecords):
    """Synchronize touch records."""

    @override
    def sync(self, files: list[str], repo_id: int) -> None:
        """Synching touch records."""
        exists_touch_records = TouchRecord.objects.filter(gh_repo_id=repo_id)
        for tr in exists_touch_records:
            if tr.path in files:
                tr.date = datetime.datetime.now(tz=datetime.UTC).date()
                tr.save()
        for file in files:
            if not TouchRecord.objects.filter(gh_repo_id=repo_id, path=file).exists():
                TouchRecord.objects.create(
                    gh_repo_id=repo_id,
                    path=file,
                    date=datetime.datetime.now(tz=datetime.UTC).date(),
                )
