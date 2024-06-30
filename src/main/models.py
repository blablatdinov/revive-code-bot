from typing import final
from django.db import models


@final
class GhInstallation(models.Model):

    installation_id = models.BigIntegerField(unique=True)

    class Meta:
        db_table = 'gh_installations'


@final
class GhRepo(models.Model):

    full_name = models.CharField(max_length=512, unique=True)
    gh_installation = models.ForeignKey(GhInstallation, on_delete=models.PROTECT)

    class Meta:
        db_table = 'gh_repos'