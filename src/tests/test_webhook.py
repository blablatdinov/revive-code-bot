import pytest
from pathlib import Path

from main.models import GhInstallation, GhRepo

pytestmark = [pytest.mark.django_db]


def test_add_installation(client):
    response = client.post(
        '/hook/github',
        Path('src/tests/fixtures/installation_added.json').read_text(),
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
    assert GhInstallation.objects.filter(installation_id=52326552).exists()
    assert GhRepo.objects.filter(full_name="blablatdinov/ramadan2020marathon_bot").count() == 1