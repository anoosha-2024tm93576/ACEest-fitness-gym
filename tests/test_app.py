from app import app
import pytest

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

def test_save_client(client):
    res = client.post('/clients', json = {
        'name': 'Harry',
        'age': 28,
        'weight': 47,
        'program': 'Beginner (BG)',
        'adherence': 80
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['client']['name'] == 'Harry'
    assert data['client']['calories'] == 47 * 26

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
    assert data['client']['calories'] is None