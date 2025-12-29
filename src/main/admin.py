# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Revive bot admin configuration."""

from django.contrib import admin

from main.models import GhRepo, ProcessTask, ProcessTaskStatusEnum, RepoConfig, TouchRecord

admin.site.register(GhRepo)
admin.site.register(TouchRecord)
admin.site.register(RepoConfig)


@admin.register(ProcessTask)
class ProcessTaskAdmin(admin.ModelAdmin):
    """Admin panel for process task model."""

    list_display = ('__str__', 'status', 'process_time', 'repo')
    readonly_fields = ('formatted_created_at', 'formatted_updated_at')

    def formatted_created_at(self, process_task: ProcessTask) -> str:
        """Created at field."""
        return process_task.created_at.isoformat()

    def formatted_updated_at(self, process_task: ProcessTask) -> str:
        """Updated at field."""
        return process_task.updated_at.isoformat()

    def process_time(self, process_task: ProcessTask) -> str:
        """Calculate process time."""
        if process_task.status != ProcessTaskStatusEnum.success:
            return 'none'
        return str(process_task.updated_at - process_task.created_at)
