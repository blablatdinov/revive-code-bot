# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""DB models."""

from typing import final

from django.db import models


@final
class RepoStatusEnum(models.TextChoices):
    """Repository status."""

    active = 'active'
    inactive = 'inactive'


@final
class GhRepo(models.Model):
    """Table contain github repos."""

    full_name = models.CharField(max_length=512, unique=True)
    has_webhook = models.BooleanField()
    installation_id = models.BigIntegerField()
    status = models.CharField(max_length=16, choices=RepoStatusEnum.choices)

    class Meta:
        db_table = 'gh_repos'

    def __str__(self) -> str:
        """String representation."""
        return 'Gh repo <{0}>'.format(self.full_name)


@final
class TouchRecord(models.Model):
    """Table contain record about touching files."""

    gh_repo = models.ForeignKey(GhRepo, on_delete=models.PROTECT)
    path = models.CharField(max_length=1024)
    date = models.DateField()

    class Meta:
        db_table = 'touch_records'
        unique_together = ('gh_repo', 'path')

    def __str__(self) -> str:
        """String representation."""
        return 'Touch record <{0}>. {1} {2}'.format(self.gh_repo.full_name, self.path, self.date)


@final
class RepoConfig(models.Model):
    """Table contain configs for repos."""

    repo = models.ForeignKey(GhRepo, on_delete=models.PROTECT)  # TODO: one-to-one
    cron_expression = models.CharField(max_length=16)
    files_glob = models.CharField(max_length=128)

    class Meta:
        db_table = 'repo_configs'

    def __str__(self) -> str:
        """String representation."""
        return 'RepoConfig repo={0}. cron={1}'.format(self.repo.full_name, self.cron_expression)


@final
class ProcessTaskStatusEnum(models.TextChoices):
    """Process task status."""

    pending = 'pending'
    in_process = 'in_process'
    success = 'success'
    failed = 'failed'


@final
class ProcessTask(models.Model):
    """Represents an asynchronous processing task for a GitHub repository."""

    repo = models.ForeignKey(GhRepo, on_delete=models.PROTECT)
    status = models.CharField(max_length=16, choices=ProcessTaskStatusEnum.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    traceback = models.TextField(default=str)

    class Meta:
        db_table = 'process_tasks'

    def __str__(self) -> str:
        """String representation."""
        return 'Process task <{0}>'.format(self.id)
