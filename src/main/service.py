import datetime
import tempfile
from operator import itemgetter
from pathlib import Path

from github import Auth, Github
from git import Repo
from django.template import Template, Context
from django.conf import settings

from main.algorithms import (
    apply_coefficient,
    file_editors_count,
    files_changes_count,
    files_sorted_by_last_changes,
    lines_count,
    merge_rating,
    files_sorted_by_last_changes_from_db,
)
from main.models import GhRepo, TouchRecord


def process_repo(repo_id: int):
    gh_repo = GhRepo.objects.get(id=repo_id)
    auth = Auth.AppAuth(874924, Path('revive-code-bot.2024-04-11.private-key.pem').read_text())
    gh = Github(auth=auth.get_installation_auth(gh_repo.gh_installation.installation_id))
    repo = gh.get_repo(gh_repo.full_name)
    gh.close()
    with tempfile.TemporaryDirectory() as tmpdirname:
        print(tmpdirname)
        Repo.clone_from(repo.clone_url, tmpdirname)
        print('Repo cloned')
    # time.sleep(60)
    # assert False
    # tmpdirname = '/Users/almazilaletdinov/code/quranbot/old'
        repo_path = Path(tmpdirname)
        files_for_search = list(repo_path.glob('**/*.py'))  # FIXME from config
        got = files_sorted_by_last_changes_from_db(
            repo_id,
            files_sorted_by_last_changes(repo_path, files_for_search),
        )
    limit = 10  # FIXME read from config
    stripped_file_list = sorted(
        [
            (
                Path(str(path).replace(
                    '{0}/'.format(tmpdirname),
                    '',
                )),
                points,
            )
            for path, points in got.items()
        ],
        key=itemgetter(1),
        reverse=True,
    )[:limit]
    issue = repo.create_issue(
        'Issue from revive-code-bot',
        Template('\n'.join([
            '{% for file in files %}- [ ] `{{ file }}`\n{% endfor %}\n',
            'Expected actions:\n'
            '1. Create new issues with reference to this issue',
            '2. Clean files must be marked in checklist',
            '3. Close issue',
            # FIXME add thanks to use text
        ])).render(Context({
            'files': [
                file
                for file, _ in stripped_file_list
            ],
        })),
    )
    TouchRecord.objects.bulk_create([
        TouchRecord(
            gh_repo_id=repo_id,
            path=file,
            date=datetime.datetime.now().date(),
        )
        for file, _ in stripped_file_list
        if file not in TouchRecord.objects.values_list('path', flat=True)
    ])
