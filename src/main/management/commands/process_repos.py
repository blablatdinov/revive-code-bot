from django.conf import settings
from django.core.management.base import BaseCommand

from main.service import process_repo
from main.models import GhRepo


class Command(BaseCommand):

    help = ''

    def handle(self, *args, **options):
        """Entrypoint."""
        for repo in GhRepo.objects.all():
            process_repo(repo.id)
