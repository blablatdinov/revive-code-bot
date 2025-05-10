# The MIT License (MIT).
#
# Copyright (c) 2023-2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

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
        return process_task.updated_at - process_task.created_at
