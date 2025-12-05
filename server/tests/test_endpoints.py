import pytest

from server import endpoints


@pytest.fixture(scope='module')
def client():
    endpoints.app.testing = True
    return endpoints.app.test_client()


def test_post_city_success(client, monkeypatch):
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


def test_get_city_item(client, monkeypatch):
    monkeypatch.setattr('cities.queries.get_by_id', lambda cid: {
        'name': 'X', 'state_code': 'Y'})
    r = client.get('/cities/507f1f77bcf86cd799439011')
    assert r.status_code == 200
    data = r.get_json()
    assert data.get('name') == 'X'


def test_put_city_item(client, monkeypatch):
    monkeypatch.setattr(
        'cities.queries.update_by_id', lambda cid, payload: True)
    r = client.put(
        '/cities/507f1f77bcf86cd799439011', json={'name': 'NewName'}
    )
    assert r.status_code == 200
    data = r.get_json()
    assert data.get('Message') == 'Updated'


def test_delete_city_item(client, monkeypatch):
    monkeypatch.setattr('cities.queries.delete_by_id', lambda cid: True)
    r = client.delete('/cities/507f1f77bcf86cd799439011')
    assert r.status_code == 200
    data = r.get_json()
    assert data.get('Message') == 'Deleted'


def test_get_cities_read(client, monkeypatch):
    monkeypatch.setattr(
        'cities.queries.read_sorted', lambda sort=None: [{'name': 'A'}]
    )
    r = client.get('/cities/read')
    assert r.status_code == 200
    data = r.get_json()
    assert 'Cities' in data and isinstance(data['Cities'], list)


def test_post_cities_read_create(client, monkeypatch):
    monkeypatch.setattr('cities.queries.create', lambda payload: 'db-2')
    r = client.post('/cities/read', json={'name': 'X'})
    assert r.status_code == 201
    assert r.get_json().get('id') == 'db-2'


def test_get_state_read(client, monkeypatch):
    monkeypatch.setattr('states.queries.read', lambda: [{'name': 'S'}])
    r = client.get('/state/read')
    assert r.status_code == 200
    data = r.get_json()
    assert 'States' in data


def test_get_countries_read(client, monkeypatch):
    monkeypatch.setattr('country.country.read', lambda: {'1': {'name': 'US'}})
    r = client.get('/countries/read')
    assert r.status_code == 200
    data = r.get_json()
    assert 'Countries' in data


def test_get_hello(client):
    r = client.get('/hello')
    assert r.status_code == 200
    assert r.get_json().get('hello') == 'world'


def test_get_endpoints(client):
    r = client.get('/endpoints')
    assert r.status_code == 200
    data = r.get_json()
    assert 'Available endpoints' in data


def test_health_endpoint(client, monkeypatch):
    # Mock connect_db so test doesn't require real Mongo
    monkeypatch.setattr('data.db_connect.connect_db', lambda: None)
    r = client.get('/health')
    assert r.status_code == 200
    assert r.get_json().get('status') == 'ok'


def test_post_state_success(client, monkeypatch):
    monkeypatch.setattr('states.queries.create', lambda payload: 'state-1')
    payload = {'name': 'TestState', 'code': 'TS', 'country_code': 'TC'}
    r = client.post('/state', json=payload)
    assert r.status_code == 201
    assert r.get_json().get('id') == 'state-1'


def test_get_state_item(client, monkeypatch):
    monkeypatch.setattr('states.queries.get_by_id', lambda sid: {'name': 'S'})
    r = client.get('/state/507f1f77bcf86cd799439011')
    assert r.status_code == 200


def test_put_state_item(client, monkeypatch):
    monkeypatch.setattr(
        'states.queries.update_by_id', lambda sid, payload: True
    )
    r = client.put('/state/507f1f77bcf86cd799439011', json={'name': 'New'})
    assert r.status_code == 200


def test_delete_state_item(client, monkeypatch):
    monkeypatch.setattr('states.queries.delete_by_id', lambda sid: True)
    r = client.delete('/state/507f1f77bcf86cd799439011')
    assert r.status_code == 200


def test_get_countries_root(client, monkeypatch):
    monkeypatch.setattr('country.country.read', lambda: {'1': {'name': 'US'}})
    r = client.get('/countries')
    assert r.status_code == 200
    assert 'Countries' in r.get_json()


def test_post_countries_root(client, monkeypatch):
    monkeypatch.setattr('country.country.create', lambda payload: 'c-1')
    r = client.post('/countries', json={'name': 'X', 'capital': 'Y'})
    assert r.status_code == 201
    assert r.get_json().get('id') == 'c-1'


def test_get_country_item(client, monkeypatch):
    monkeypatch.setattr('country.country.get_country_by_id',
                        lambda cid: {'name': 'US'})
    r = client.get('/countries/1')
    assert r.status_code == 200


def test_put_country_item(client, monkeypatch):
    monkeypatch.setattr('country.country.country_cache',
                        {'1': {'name': 'US'}})
    r = client.put('/countries/1', json={'name': 'USA'})
    assert r.status_code == 200


def test_delete_country_item(client, monkeypatch):
    monkeypatch.setattr('country.country.country_cache',
                        {'1': {'name': 'US'}})
    r = client.delete('/countries/1')
    assert r.status_code == 200


def test_counts_endpoint(client, monkeypatch):
    monkeypatch.setattr('cities.queries.num_cities', lambda: 2)
    monkeypatch.setattr('states.queries.count', lambda: 3)
    monkeypatch.setattr('country.country.read', lambda: {'1': {}, '2': {}})
    r = client.get('/counts')
    assert r.status_code == 200
    data = r.get_json()
    assert data.get('cities') == 2
    assert data.get('states') == 3
    assert data.get('countries') == 2
