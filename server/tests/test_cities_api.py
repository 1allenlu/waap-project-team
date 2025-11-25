# import json

import pytest

from server import endpoints


@pytest.fixture(scope='module')
def client():
    endpoints.app.testing = True
    return endpoints.app.test_client()


def test_post_city_success(client, monkeypatch):
    # patch the create function to return a known id
    monkeypatch.setattr('cities.queries.create', lambda payload: 'db-1')
    payload = {'name': 'TestCity', 'state_code': 'TS'}
    r = client.post('/cities', json=payload)
    assert r.status_code == 201
    data = r.get_json()
    assert data.get('id') == 'db-1'


def test_post_city_bad_payload(client):
    r = client.post('/cities', json={'bad': 'payload'})
    assert r.status_code == 400
    data = r.get_json()
    assert 'Error' in data
