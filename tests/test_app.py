import app as app_module
from app import app
import pytest

@pytest.fixture(autouse=True)
def clear_clients():
    app_module.clients.clear()
    yield
    app_module.clients.clear()

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_home(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert 'message' in data
    assert data['message'] == "ACEest Fitness API is running"

def test_get_all_programs(client):
    res = client.get('/programs')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 3

def test_get_valid_program(client):
    res = client.get('programs/Fat Loss (FL)')
    assert res.status_code == 200
    data = res.get_json()
    assert 'workout' in data
    assert 'diet' in data

def test_get_invalid_program(client):
    res = client.get('programs/NonExistingProgram')
    assert res.status_code == 404
    data = res.get_json()
    assert 'error' in data

def test_get_clinet_empty(client):
    res = client.get('clients')
    assert res.status_code == 200
    assert res.get_json() == []

def test_save_client(client):
    res = client.post('/clients', json = {
        'name': 'Harry',
        'age': 28,
        'weight': 47,
        'program': 'Beginner (BG)',
        'adherence': 80,
        'notes': 'Progress as expected'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['client']['name'] == 'Harry'
    assert data['client']['calories'] == 47 * 26
    assert data['client']['notes'] == 'Progress as expected'

def test_save_client_missing_name(client):
    res = client.post('/clients', json = {
        'program': 'Beginner (BG)'
    })
    assert res.status_code == 400
    assert 'error' in res.get_json()

def test_save_client_missing_program(client):
    res = client.post('/clients', json = {
        'name': 'Harry'
    })
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_reset_client(client):
    res = client.post('/clients/reset')
    assert res.status_code == 200
    data = res.get_json()
    assert data['client']['name'] == ''
    assert data['client']['adherence'] == 0
    assert data['client']['notes'] == ''
    assert data['client']['calories'] is None

def test_export_csv_no_clients(client):
    res = client.get('/clients/export')
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_export_csv_with_clients(client):
    client.post('/clients', json={
        'name': 'John', 
        'age': 25, 
        'weight': 70,
        'program': 'Beginner (BG)', 
        'adherence': 80, 
        'notes': 'Good'
    })
    res = client.get('/clients/export')
    assert res.status_code == 200
    assert res.content_type == 'text/csv; charset=utf-8'
    assert b'John' in res.data