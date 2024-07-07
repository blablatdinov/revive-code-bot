from celery import shared_task

from main.service import GhClonedRepo, GhNewIssue, process_repo, pygithub_client
from main.models import GhRepo


@shared_task
def process_repo_task(repo_id):
    repo = GhRepo.objects.get(id=repo_id)
    process_repo(
        repo.id,
        GhClonedRepo(repo),
        GhNewIssue(pygithub_client(repo.installation_id).get_repo(repo.full_name)),
    )
