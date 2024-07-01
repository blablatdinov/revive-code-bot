from typing import final
from django.db import models


@final
class GhRepo(models.Model):

    full_name = models.CharField(max_length=512, unique=True)
    has_webhook = models.BooleanField()
    installation_id = models.BigIntegerField()

    class Meta:
        db_table = 'gh_repos'


@final
class TouchRecord(models.Model):

    gh_repo = models.ForeignKey(GhRepo, on_delete=models.PROTECT)
    path = models.CharField(max_length=1024, unique=True)
    date = models.DateField()

    class Meta:
        db_table = 'touch_records'
