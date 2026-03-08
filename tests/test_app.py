def test_home_route(client):
    res = client.get('/')
    assert res.status_code == 200
    assert res.get_json()['message'] == "ACEest Fitness API is running"


def test_get_all_programs(client):
    res = client.get('/programs')
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert len(data) == 4


def test_get_valid_program(client):
    res = client.get('/programs/Beginner (BG)')
    assert res.status_code == 200
    data = res.get_json()
    assert 'workout' in data
    assert 'diet' in data
    assert 'color' in data
    assert 'factor' in data
    assert 'desc' in data


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
        'height': 175,
        'weight': 70,
        'program': 'Beginner (BG)',
        'adherence': 80,
        'target_weight': 65,
        'target_adherence': 90
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['client']['name'] == 'John'
    assert data['client']['calories'] == 70 * 26
    assert data['client']['height'] == 175
    assert data['client']['target_weight'] == 65
    assert data['client']['target_adherence'] == 90


def test_save_client_upsert_preserves_id(client):
    client.post('/clients', json={'name': 'John', 'age': 25, 'height': 175, 'weight': 70, 'program': 'Beginner (BG)'})
    original_id = client.get('/clients/John').get_json()['id']
    client.post('/clients', json={'name': 'John', 'age': 26, 'height': 180, 'weight': 75, 'program': 'Muscle Gain (MG) - PPL'})
    updated = client.get('/clients/John').get_json()
    assert updated['id'] == original_id
    assert updated['age'] == 26
    assert updated['height'] == 180
    assert updated['weight'] == 75


def test_save_client_upsert(client):
    client.post('/clients', json={'name': 'John', 'age': 25, 'weight': 70, 'program': 'Beginner (BG)'})
    client.post('/clients', json={'name': 'John', 'age': 26, 'weight': 75, 'program': 'Muscle Gain (MG) - PPL'})
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
    client.post('/clients', json={
        'name': 'John', 'age': 25, 'height': 175, 'weight': 70,
        'program': 'Beginner (BG)', 'target_weight': 65, 'target_adherence': 90
    })
    res = client.get('/clients/John')
    assert res.status_code == 200
    data = res.get_json()
    assert data['name'] == 'John'
    assert data['height'] == 175
    assert data['target_weight'] == 65
    assert data['target_adherence'] == 90


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


def test_get_progress_chart(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    client.post('/clients/John/progress', json={'adherence': 80})
    client.post('/clients/John/progress', json={'adherence': 90})
    res = client.get('/clients/John/progress/chart')
    assert res.status_code == 200
    data = res.get_json()
    assert data['client'] == 'John'
    assert len(data['chart_data']) == 2


def test_get_progress_chart_no_data(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/progress/chart')
    assert res.status_code == 404
    assert 'error' in res.get_json()


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


def test_get_summary(client):
    client.post('/clients', json={'name': 'John', 'height': 175, 'weight': 70, 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/summary')
    assert res.status_code == 200
    data = res.get_json()
    assert 'client' in data
    assert 'program_desc' in data
    assert 'progress_summary' in data
    assert 'last_metrics' in data


def test_get_summary_progress_stats(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    client.post('/clients/John/progress', json={'adherence': 80})
    client.post('/clients/John/progress', json={'adherence': 100})
    res = client.get('/clients/John/summary')
    assert res.status_code == 200
    data = res.get_json()
    assert data['progress_summary']['weeks_logged'] == 2
    assert data['progress_summary']['avg_adherence'] == 90.0


def test_get_summary_no_progress(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/summary')
    data = res.get_json()
    assert data['progress_summary']['weeks_logged'] == 0
    assert data['progress_summary']['avg_adherence'] == 0


def test_get_summary_not_found(client):
    res = client.get('/clients/NonExistent/summary')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_get_bmi_normal(client):
    client.post('/clients', json={'name': 'John', 'height': 175, 'weight': 70, 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/bmi')
    assert res.status_code == 200
    data = res.get_json()
    assert data['bmi'] == 22.9
    assert data['category'] == 'Normal'
    assert 'risk' in data


def test_get_bmi_categories(client):
    client.post('/clients', json={'name': 'Under', 'height': 175, 'weight': 50, 'program': 'Beginner (BG)'})
    client.post('/clients', json={'name': 'Over', 'height': 175, 'weight': 85, 'program': 'Beginner (BG)'})
    client.post('/clients', json={'name': 'Obese', 'height': 175, 'weight': 110, 'program': 'Beginner (BG)'})
    assert client.get('/clients/Under/bmi').get_json()['category'] == 'Underweight'
    assert client.get('/clients/Over/bmi').get_json()['category'] == 'Overweight'
    assert client.get('/clients/Obese/bmi').get_json()['category'] == 'Obese'


def test_get_bmi_missing_data(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/bmi')
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_get_bmi_not_found(client):
    res = client.get('/clients/NonExistent/bmi')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_log_workout(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.post('/clients/John/workouts', json={
        'date': '2026-03-08',
        'workout_type': 'Strength',
        'duration_min': 60,
        'notes': 'Felt strong',
        'exercises': [
            {'name': 'Squat', 'sets': 5, 'reps': 5, 'weight': 100}
        ]
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['workout_type'] == 'Strength'
    assert data['date'] == '2026-03-08'
    assert 'workout_id' in data


def test_log_workout_missing_type(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.post('/clients/John/workouts', json={'date': '2026-03-08'})
    assert res.status_code == 400
    assert 'error' in res.get_json()


def test_log_workout_client_not_found(client):
    res = client.post('/clients/NonExistent/workouts', json={'workout_type': 'Strength'})
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_get_workouts(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    client.post('/clients/John/workouts', json={'workout_type': 'Strength'})
    client.post('/clients/John/workouts', json={'workout_type': 'Conditioning'})
    res = client.get('/clients/John/workouts')
    assert res.status_code == 200
    assert len(res.get_json()) == 2


def test_get_workouts_empty(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/workouts')
    assert res.status_code == 200
    assert res.get_json() == []


def test_get_workouts_client_not_found(client):
    res = client.get('/clients/NonExistent/workouts')
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_log_metrics(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.post('/clients/John/metrics', json={
        'date': '2026-03-08',
        'weight': 70,
        'waist': 80,
        'bodyfat': 15
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['weight'] == 70
    assert data['waist'] == 80
    assert data['bodyfat'] == 15


def test_log_metrics_client_not_found(client):
    res = client.post('/clients/NonExistent/metrics', json={'date': '2026-03-08', 'weight': 70})
    assert res.status_code == 404
    assert 'error' in res.get_json()


def test_get_metrics(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    client.post('/clients/John/metrics', json={'date': '2026-03-01', 'weight': 72, 'waist': 82, 'bodyfat': 16})
    client.post('/clients/John/metrics', json={'date': '2026-03-08', 'weight': 70, 'waist': 80, 'bodyfat': 15})
    res = client.get('/clients/John/metrics')
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    assert data[0]['date'] == '2026-03-01'
    assert data[1]['date'] == '2026-03-08'


def test_get_metrics_empty(client):
    client.post('/clients', json={'name': 'John', 'program': 'Beginner (BG)'})
    res = client.get('/clients/John/metrics')
    assert res.status_code == 200
    assert res.get_json() == []


def test_get_metrics_client_not_found(client):
    res = client.get('/clients/NonExistent/metrics')
    assert res.status_code == 404
    assert 'error' in res.get_json()