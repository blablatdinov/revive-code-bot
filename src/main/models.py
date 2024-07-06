# The MIT License (MIT).
#
# Copyright (c) 2023-2024 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
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

"""DB models."""

from typing import final

from django.db import models
from django_celery_beat.models import CrontabSchedule


@final
class GhRepo(models.Model):
    """Table contain github repos."""

    full_name = models.CharField(max_length=512, unique=True)
    has_webhook = models.BooleanField()
    installation_id = models.BigIntegerField()
    scheduling = models.ForeignKey(CrontabSchedule, on_delete=models.PROTECT)

    class Meta:
        db_table = 'gh_repos'

    def __str__(self) -> str:
        """String representation."""
        return 'Gh repo <{0}>'.format(self.full_name)


@final
class TouchRecord(models.Model):
    """Table contain record about touching files."""

    gh_repo = models.ForeignKey(GhRepo, on_delete=models.PROTECT)
    path = models.CharField(max_length=1024, unique=True)
    date = models.DateField()

    class Meta:
        db_table = 'touch_records'

    def __str__(self) -> str:
        """String representation."""
        return 'Touch record <{0}>. {1} {2}'.format(self.gh_repo.full_name, self.path, self.date)
