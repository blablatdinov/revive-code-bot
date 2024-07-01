import datetime
from pathlib import Path

from github import Auth, Github

import pytest
from main.service import process_repo
from main.models import TouchRecord

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def gh_repo(mixer):
    return mixer.blend(
        'main.GhRepo',
        full_name='blablatdinov/ramadan2020marathon_bot',
        gh_installation__installation_id=52326552,
    )


def test(gh_repo, time_machine):
    time_machine.move_to('2024-07-01')
    process_repo(gh_repo.id)

    # assert False, TouchRecord.objects.all()
    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'bot_init/__init__.py',
        'bot_init/migrations/__init__.py',
        'dialog/__init__.py',
        'dialog/migrations/__init__.py',
        'marathon/__init__.py',
        'marathon/migrations/__init__.py',
        'bot_init/tests.py',
        'dialog/models.py',
        'dialog/tests.py',
        'dialog/views.py',
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
        datetime.date(2024, 7, 1),
    ]


# def test_get_installations():


# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MTk2ODIxODAsImV4cCI6MTcxOTY4MjU0MCwiaXNzIjo0ODcyMjk0NTN9.zHM6_YkYMOjRa45ud7rXJmduzrpwmL8M9SMsa9L1MZOIH4iJt2aHNUgfUiCZQ23weDUlBxNLG4Ma0nfSp4xJTo6pLXlTGzW-NfDVwOp-tL2A_s4Q_tpVzJXEWNKzHillPBHx1vkeFZhVfvG_yxh0s-gf9u51RKzU28H18z35XG7Qm5FoY_a1Mf6doHlSoEMuyK7koy4ReqQPKsKwusrEK-Kq4vDEMCEKNcolq6oASz9-5HrE8ktQvHCpDubF_0DDdTaW4DFp8G4-EjgBwP-uA5QTgxObX_FYbvtPji1Mv1In72211BgsEzHf2F-gYq3FteaX1_96frVw9QEQYy2Y1g