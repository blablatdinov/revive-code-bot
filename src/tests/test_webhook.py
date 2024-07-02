from pathlib import Path

import pytest
from django.conf import settings

from main.models import GhRepo
from main.service import pygithub_client

pytestmark = [pytest.mark.django_db]


@pytest.fixture()
def _remove_exist_webhook():
    gh = pygithub_client(52326552)
    gh_repo = gh.get_repo('blablatdinov/ramadan2020marathon_bot')
    hook = next(iter(list(
        hook
        for hook in gh_repo.get_hooks()
        if 'revive-code-bot.ilaletdinov.ru' in hook.config['url']
    )))
    hook.delete()


@pytest.mark.usefixtures('_remove_exist_webhook')
def test_add_installation(client):
    response = client.post(
        '/hook/github',
        Path(settings.BASE_DIR / 'tests/fixtures/installation_added.json').read_text(),
        content_type='application/json',
        headers={
            'Accept': '*/*',
            'Content-Type': 'application/json',
            'User-Agent': 'GitHub-Hookshot/9729b30',
            'X-GitHub-Delivery': '18faf6d0-3662-11ef-9e2b-0e81d1f2cc20',
            'X-GitHub-Event': 'installation_repositories',
            'X-GitHub-Hook-ID': '487229453',
            'X-GitHub-Hook-Installation-Target-ID': '874924',
            'X-GitHub-Hook-Installation-Target-Type': 'integration',
        },
    )

    assert response.status_code == 200
    assert GhRepo.objects.filter(
        full_name='blablatdinov/ramadan2020marathon_bot',
        installation_id=52326552,
    ).count() == 1
