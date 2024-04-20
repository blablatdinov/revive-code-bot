import pytest

pytestmark = [pytest.mark.django_db]


def test(client):
    got = client.get('/webhook')

    assert got.status_code == 200
