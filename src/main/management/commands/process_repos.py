# SPDX-FileCopyrightText: Copyright (c) 2023-2026 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
# SPDX-License-Identifier: MIT

"""Manual process repo."""

from typing import Any

from django.core.management.base import BaseCommand

from main.models import GhRepo
from main.service import process_repo
from main.services.github_objs.gh_cloned_repo import GhClonedRepo
from main.services.github_objs.gh_new_issue import GhNewIssue
from main.services.github_objs.github_client import github_repo


class Command(BaseCommand):
    """CLI command."""

    help = ''

    # "Any" annotation taken from
    # https://github.com/typeddjango/django-stubs/blob/c7df64/django-stubs/core/management/commands/check.pyi#L6
    def handle(self, *args: list[str], **options: Any) -> None:  # noqa: ANN401
        """Entrypoint."""
        for repo in GhRepo.objects.all():
            process_repo(
                repo.id,
                GhClonedRepo(repo),
                GhNewIssue(github_repo(repo.installation_id, repo.full_name)),
            )
