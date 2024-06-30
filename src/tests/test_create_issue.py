from pathlib import Path

from github import Auth, Github

import pytest
from main.service import process_repo

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def gh_repo(mixer):
    return mixer.blend(
        'main.GhRepo',
        full_name='blablatdinov/ramadan2020marathon_bot',
        gh_installation__installation_id=52326552,
    )


def test(gh_repo):
    process_repo(gh_repo.id)
    assert False
    # assert False, Path('revive-code-bot.2024-04-11.private-key.pem').read_text()
    auth = Auth.AppAuth(874924, Path('revive-code-bot.2024-04-11.private-key.pem').read_text())
    print(auth.token)
    gh = Github(auth=auth.get_installation_auth(52326552))
    repo = gh.get_repo('blablatdinov/quranbot')
    issue = repo.create_issue(
        'Issue from revive-code-bot',
        'Please review some files...',
    )
    assert False


# def test_get_installations():


# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MTk2ODIxODAsImV4cCI6MTcxOTY4MjU0MCwiaXNzIjo0ODcyMjk0NTN9.zHM6_YkYMOjRa45ud7rXJmduzrpwmL8M9SMsa9L1MZOIH4iJt2aHNUgfUiCZQ23weDUlBxNLG4Ma0nfSp4xJTo6pLXlTGzW-NfDVwOp-tL2A_s4Q_tpVzJXEWNKzHillPBHx1vkeFZhVfvG_yxh0s-gf9u51RKzU28H18z35XG7Qm5FoY_a1Mf6doHlSoEMuyK7koy4ReqQPKsKwusrEK-Kq4vDEMCEKNcolq6oASz9-5HrE8ktQvHCpDubF_0DDdTaW4DFp8G4-EjgBwP-uA5QTgxObX_FYbvtPji1Mv1In72211BgsEzHf2F-gYq3FteaX1_96frVw9QEQYy2Y1g