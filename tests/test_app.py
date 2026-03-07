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