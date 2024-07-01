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
        full_name='blablatdinov/iman-game-bot',
        installation_id=52326552,
    )


def test(gh_repo, time_machine):
    # time_machine.move_to('2024-07-01')
    process_repo(gh_repo.id)
    from pprint import pprint
    # pprint(list(TouchRecord.objects.values_list('path', flat=True)))
    # pprint(list(TouchRecord.objects.values_list('date', flat=True)))

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
        'manage.py',
        'config/asgi.py',
        'config/wsgi.py',
        'game/__init__.py',
        'game/apps.py',
        'game/views.py',
        'bot_init/__init__.py',
        'bot_init/apps.py',
        'bot_init/urls.py',
        'game/migrations/__init__.py',
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
        datetime.date(2024, 7, 1)
    ]

    process_repo(gh_repo.id)
    # pprint(list(TouchRecord.objects.values_list('path', flat=True)))
    # pprint(list(TouchRecord.objects.values_list('date', flat=True)))

    assert list(TouchRecord.objects.values_list('path', flat=True)) == [
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [
    ]


# def test_get_installations():


# eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MTk2ODIxODAsImV4cCI6MTcxOTY4MjU0MCwiaXNzIjo0ODcyMjk0NTN9.zHM6_YkYMOjRa45ud7rXJmduzrpwmL8M9SMsa9L1MZOIH4iJt2aHNUgfUiCZQ23weDUlBxNLG4Ma0nfSp4xJTo6pLXlTGzW-NfDVwOp-tL2A_s4Q_tpVzJXEWNKzHillPBHx1vkeFZhVfvG_yxh0s-gf9u51RKzU28H18z35XG7Qm5FoY_a1Mf6doHlSoEMuyK7koy4ReqQPKsKwusrEK-Kq4vDEMCEKNcolq6oASz9-5HrE8ktQvHCpDubF_0DDdTaW4DFp8G4-EjgBwP-uA5QTgxObX_FYbvtPji1Mv1In72211BgsEzHf2F-gYq3FteaX1_96frVw9QEQYy2Y1g