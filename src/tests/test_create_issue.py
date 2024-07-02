from operator import attrgetter
import datetime

import pytest

from main.models import TouchRecord
from main.service import process_repo, pygithub_client

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def gh_repo(mixer):
    yield mixer.blend(
        'main.GhRepo',
        full_name='blablatdinov/iman-game-bot',
        installation_id=52326552,
    )
    repo = pygithub_client(52326552).get_repo('blablatdinov/iman-game-bot')
    for issue in repo.get_issues():
        if issue.title == 'Issue from revive-code-bot':
            issue.edit(state='closed')


@pytest.fixture()
def exist_touch_records(mixer, gh_repo):
    files = [
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
    mixer.cycle(10).blend(
        'main.TouchRecord',
        gh_repo=gh_repo,
        path=(f for f in files),
        date=datetime.datetime.now().date(),
    )


def test(gh_repo, time_machine):
    process_repo(gh_repo.id)
    today = datetime.datetime.now().date()

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
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 10
    assert next(iter(sorted(
        pygithub_client(gh_repo.installation_id).search_issues('Issue from revive-code-bot'),
        key=attrgetter('created_at'),
        reverse=True,
    ))).body == '\n'.join([
        '- [ ] `manage.py`',
        '- [ ] `config/asgi.py`',
        '- [ ] `config/wsgi.py`',
        '- [ ] `game/__init__.py`',
        '- [ ] `game/apps.py`',
        '- [ ] `game/views.py`',
        '- [ ] `bot_init/__init__.py`',
        '- [ ] `bot_init/apps.py`',
        '- [ ] `bot_init/urls.py`',
        '- [ ] `game/migrations/__init__.py`',
        '',
        '',
        'Expected actions:',
        '1. Create new issues with reference to this issue',
        '2. Clean files must be marked in checklist',
        '3. Close issue',
    ])


def test_double_process(exist_touch_records, gh_repo):
    process_repo(gh_repo.id)
    today = datetime.datetime.now().date()

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
        'bot_init/migrations/__init__.py',
        'bot_init/migrations/0001_initial.py',
        'bot_init/management/commands/update_webhook.py',
        'events/service.py',
        'events/models.py',
        'events/__init__.py',
        'events/apps.py',
        'events/admin.py',
        'events/migrations/__init__.py',
        'events/migrations/0001_initial.py',
    ]
    assert list(TouchRecord.objects.values_list('date', flat=True)) == [today] * 20
    assert next(iter(sorted(
        pygithub_client(gh_repo.installation_id).search_issues('Issue from revive-code-bot'),
        key=attrgetter('created_at'),
        reverse=True,
    ))).body == '\n'.join([
        '- [ ] `bot_init/migrations/__init__.py`',
        '- [ ] `bot_init/migrations/0001_initial.py`',
        '- [ ] `bot_init/management/commands/update_webhook.py`',
        '- [ ] `events/service.py`',
        '- [ ] `events/models.py`',
        '- [ ] `events/__init__.py`',
        '- [ ] `events/apps.py`',
        '- [ ] `events/admin.py`',
        '- [ ] `events/migrations/__init__.py`',
        '- [ ] `events/migrations/0001_initial.py`',
        '',
        '',
        'Expected actions:',
        '1. Create new issues with reference to this issue',
        '2. Clean files must be marked in checklist',
        '3. Close issue',
    ])
