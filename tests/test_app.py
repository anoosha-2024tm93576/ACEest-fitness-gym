def test_home_route(client):
    res = client.get('/')
    assert res.status_code == 200
    assert res.get_json()['message'] == "ACEest Fitness API is running"


def test_get_all_programs(client):
    res = client.get('/programs')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_get_valid_program(client):
    res = client.get('/programs/Fat Loss (FL)')
    assert res.status_code == 200
    data = res.get_json()
    assert 'workout' in data
    assert 'diet' in data
    assert 'color' in data
    assert 'factor' in data


def test_get_invalid_program(client):
    res = client.get('/programs/NonExistent')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_get_clients_empty(client):
    res = client.get('/clients')
    assert res.status_code == 200
    assert res.get_json() == []


def test_save_client(client):
    res = client.post('/clients', json={
        'name': 'John',
        'age': 25,
        'weight': 70,
        'program': 'Beginner (BG)',
        'adherence': 80
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['client']['name'] == 'John'
    assert data['client']['calories'] == 70 * 26


def test_save_client_upsert(client):
    client.post('/clients', json={'name': 'John', 'age': 25, 'weight': 70, 'program': 'Beginner (BG)'})
    client.post('/clients', json={'name': 'John', 'age': 26, 'weight': 75, 'program': 'Muscle Gain (MG)'})
    res = client.get('/clients')
    assert len(res.get_json()) == 1


def test_save_client_missing_name(client):
    res = client.post('/clients', json={'program': 'Beginner (BG)'})
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_save_client_missing_program(client):
    res = client.post('/clients', json={'name': 'John'})
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_save_client_invalid_program(client):
    res = client.post('/clients', json={'name': 'John', 'program': 'NonExistent'})
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_load_client(client):
    client.post('/clients', json={'name': 'John', 'age': 25, 'weight': 70, 'program': 'Beginner (BG)'})
    res = client.get('/clients/John')
    assert res.status_code == 200
    assert res.get_json()['name'] == 'John'


def test_load_client_not_found(client):
    res = client.get('/clients/NonExistent')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_save_progress(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.post('/clients/John/progress', json={'adherence': 85})
    assert res.status_code == 200
    assert res.get_json()['adherence'] == 85


def test_save_progress_client_not_found(client):
    res = client.post('/clients/NonExistent/progress', json={'adherence': 85})
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_save_progress_missing_adherence(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.post('/clients/John/progress', json={})
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_get_progress(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    client.post('/clients/John/progress', json={'adherence': 80})
    client.post('/clients/John/progress', json={'adherence': 90})
    res = client.get('/clients/John/progress')
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_export_csv_no_clients(client):
    res = client.get('/clients/export')
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_export_csv_with_clients(client):
    client.post('/clients', json={
        'name': 'John', 'age': 25, 'weight': 70,
        'program': 'Beginner (BG)', 'adherence': 80
    })
    res = client.get('/clients/export')
    assert res.status_code == 200
    assert res.content_type == 'text/csv; charset=utf-8'
    assert b'John' in res.data