from flask import Flask, Response, jsonify, request
import csv
import io
import sqlite3
from datetime import datetime, date

app = Flask(__name__)

DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "workout": (
            "Mon: Back Squat 5x5 + Core\n"
            "Wed: Bench Press + 21-15-9\n"
            "Fri: Zone 2 Cardio 30min"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2000 kcal"
        ),
        "color": "#e74c3c",
        "factor": 22,
        "desc": "3-day full-body fat loss"
    },
    "Fat Loss (FL) - 5 day": {
        "workout": (
            "Mon: Back Squat 5x5 + Core\n"
            "Tue: EMOM 20min Assault Bike\n"
            "Wed: Bench Press + 21-15-9\n"
            "Thu: Deadlift + Box Jumps\n"
            "Fri: Zone 2 Cardio 30min"
        ),
        "diet": (
            "Breakfast: Egg Whites + Oats\n"
            "Lunch: Grilled Chicken + Brown Rice\n"
            "Dinner: Fish Curry + Millet Roti\n"
            "Target: ~2200 kcal"
        ),
        "color": "#c0392b",
        "factor": 24,
        "desc": "5-day split, higher volume fat loss"
    },
    "Muscle Gain (MG) - PPL": {
        "workout": (
            "Mon: Squat 5x5\n"
            "Tue: Bench 5x5\n"
            "Wed: Deadlift 4x6\n"
            "Thu: Front Squat 4x8\n"
            "Fri: Incline Press 4x10\n"
            "Sat: Barbell Rows 4x10"
        ),
        "diet": (
            "Breakfast: Eggs + Peanut Butter Oats\n"
            "Lunch: Chicken Biryani\n"
            "Dinner: Mutton Curry + Rice\n"
            "Target: ~3200 kcal"
        ),
        "color": "#2ecc71",
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy"
    },
    "Beginner (BG)": {
        "workout": (
            "Full Body Circuit:\n"
            "- Air Squats\n"
            "- Ring Rows\n"
            "- Push-ups\n"
            "Focus: Technique & Consistency"
        ),
        "diet": (
            "Balanced Tamil Meals\n"
            "Idli / Dosa / Rice + Dal\n"
            "Protein Target: 120g/day"
        ),
        "color": "#3498db",
        "factor": 26,
        "desc": "3-day simple beginner full-body"
    }
}


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()


def get_calories(weight, program):
    return int(weight * PROGRAMS[program]['factor'])


init_db()


@app.route('/')
def home():
    return jsonify({
        "message": "ACEest Fitness API is running"
    })


@app.route('/programs', methods=['GET'])
def get_programs():
    return jsonify(list(PROGRAMS.keys()))


@app.route('/programs/<name>', methods=['GET'])
def get_program(name):
    if name not in PROGRAMS:
        return jsonify({'error': 'Program not found'}), 404
    return jsonify(PROGRAMS[name])


@app.route('/clients', methods=['GET'])
def get_clients():
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients").fetchall()
    conn.close()
    return jsonify([dict(c) for c in clients])


@app.route('/clients', methods=['POST'])
def save_client():
    data = request.get_json()
    name = data.get('name', '').strip()
    program = data.get('program', '').strip()
    age = data.get('age')
    height = data.get('height')
    weight = data.get('weight')
    adherence = data.get('adherence', 0)
    target_weight = data.get('target_weight')
    target_adherence = data.get('target_adherence')

    if not name or not program:
        return jsonify({'error': 'name and program are required'}), 400

    if program not in PROGRAMS:
        return jsonify({'error': 'Program not found'}), 404

    calories = get_calories(weight, program) if weight else None

    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            age=excluded.age,
            height=excluded.height,
            weight=excluded.weight,
            program=excluded.program,
            calories=excluded.calories,
            target_weight=excluded.target_weight,
            target_adherence=excluded.target_adherence
    """, (name, age, height, weight, program, calories, target_weight, target_adherence))
    conn.commit()

    if adherence:
        week = datetime.now().strftime("Week %U - %Y")
        conn.execute("""
            INSERT INTO progress (client_name, week, adherence)
            VALUES (?, ?, ?)
        """, (name, week, adherence))
        conn.commit()

    conn.close()

    return jsonify({
        'message': f'Client {name} saved successfully',
        'client': {
            'name': name,
            'age': age,
            'height': height,
            'weight': weight,
            'program': program,
            'adherence': adherence,
            'calories': calories,
            'target_weight': target_weight,
            'target_adherence': target_adherence
        }
    })


@app.route('/clients/export', methods=['GET'])
def export_clients():
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients").fetchall()
    conn.close()

    if not clients:
        return jsonify({'error': 'No clients to export'}), 400

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=['id', 'name', 'age', 'height', 'weight', 'program', 'calories', 'target_weight', 'target_adherence']
    )
    writer.writeheader()
    writer.writerows([dict(c) for c in clients])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=clients.csv'}
    )


@app.route('/clients/<name>', methods=['GET'])
def load_client(name):
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()
    conn.close()

    if not client:
        return jsonify({'error': 'Client not found'}), 404

    return jsonify(dict(client))


@app.route('/clients/<name>/progress', methods=['GET'])
def get_progress(name):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM progress WHERE client_name=?", (name,)
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route('/clients/<name>/progress', methods=['POST'])
def save_progress(name):
    data = request.get_json()
    adherence = data.get('adherence')

    if adherence is None:
        return jsonify({'error': 'adherence is required'}), 400

    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    week = datetime.now().strftime("Week %U - %Y")
    conn.execute("""
        INSERT INTO progress (client_name, week, adherence)
        VALUES (?, ?, ?)
    """, (name, week, adherence))
    conn.commit()
    conn.close()

    return jsonify({
        'message': f'Progress saved for {name}',
        'week': week,
        'adherence': adherence
    })


@app.route('/clients/<name>/progress/chart', methods=['GET'])
def get_progress_chart(name):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    rows = conn.execute("""
        SELECT week, adherence
        FROM progress
        WHERE client_name=?
        ORDER BY id
    """, (name,)).fetchall()
    conn.close()

    if not rows:
        return jsonify({'error': 'No progress data available for this client'}), 404

    return jsonify({
        'client': name,
        'chart_data': [{'week': r['week'], 'adherence': r['adherence']} for r in rows]
    })


@app.route('/clients/<name>/summary', methods=['GET'])
def get_summary(name):
    conn = get_db()
    client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    total_weeks, avg_adherence = conn.execute("SELECT COUNT(*), AVG(adherence) FROM progress WHERE client_name=?", (name,)).fetchone()

    last_metric = conn.execute("""
        SELECT date, weight, waist, bodyfat FROM metrics
        WHERE client_name=? ORDER BY date DESC LIMIT 1
    """, (name,)).fetchone()

    conn.close()

    client_dict = dict(client)
    program = client_dict.get('program', '')
    program_desc = PROGRAMS.get(program, {}).get('desc', '')

    return jsonify({
        'client': client_dict,
        'program_desc': program_desc,
        'progress_summary': {
            'weeks_logged': total_weeks,
            'avg_adherence': round(avg_adherence, 1) if avg_adherence else 0
        },
        'last_metrics': dict(last_metric) if last_metric else None
    })


@app.route('/clients/<name>/bmi', methods=['GET'])
def get_bmi(name):
    conn = get_db()
    client = conn.execute(
        "SELECT height, weight FROM clients WHERE name=?", (name,)
    ).fetchone()
    conn.close()

    if not client:
        return jsonify({'error': 'Client not found'}), 404

    height = client['height']
    weight = client['weight']

    if not height or not weight:
        return jsonify({'error': 'Height and weight required for BMI calculation'}), 400

    h_m = height / 100.0
    bmi = round(weight / (h_m * h_m), 1)

    if bmi < 18.5:
        category = "Underweight"
        risk = "Potential nutrient deficiency, low energy."
    elif bmi < 25:
        category = "Normal"
        risk = "Low risk if active and strong."
    elif bmi < 30:
        category = "Overweight"
        risk = "Moderate risk; focus on adherence and progressive activity."
    else:
        category = "Obese"
        risk = "Higher risk; prioritize fat loss, consistency, and supervision."

    return jsonify({'bmi': bmi, 'category': category, 'risk': risk})


@app.route('/clients/<name>/workouts', methods=['POST'])
def log_workout(name):
    data = request.get_json()
    workout_date = data.get('date', date.today().isoformat())
    workout_type = data.get('workout_type', '').strip()
    duration_min = data.get('duration_min')
    notes = data.get('notes', '').strip()
    exercises = data.get('exercises', [])

    if not workout_type:
        return jsonify({'error': 'workout_type is required'}), 400

    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    cur = conn.execute("""
        INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, workout_date, workout_type, duration_min, notes))
    workout_id = cur.lastrowid

    for ex in exercises:
        conn.execute("""
            INSERT INTO exercises (workout_id, name, sets, reps, weight)
            VALUES (?, ?, ?, ?, ?)
        """, (workout_id, ex.get('name'), ex.get('sets'),
              ex.get('reps'), ex.get('weight')))

    conn.commit()
    conn.close()

    return jsonify({
        'message': f'Workout logged for {name}',
        'workout_id': workout_id,
        'date': workout_date,
        'workout_type': workout_type
    })


@app.route('/clients/<name>/workouts', methods=['GET'])
def get_workouts(name):
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    workouts = conn.execute("""
        SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC, id DESC
    """, (name,)).fetchall()
    conn.close()

    return jsonify([dict(w) for w in workouts])


@app.route('/clients/<name>/metrics', methods=['POST'])
def log_metrics(name):
    data = request.get_json()
    metric_date = data.get('date', date.today().isoformat())
    weight = data.get('weight')
    waist = data.get('waist')
    bodyfat = data.get('bodyfat')

    if not metric_date:
        return jsonify({'error': 'date is required'}), 400

    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    conn.execute("""
        INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
        VALUES (?, ?, ?, ?, ?)
    """, (name, metric_date, weight, waist, bodyfat))
    conn.commit()
    conn.close()

    return jsonify({
        'message': f'Metrics logged for {name}',
        'date': metric_date,
        'weight': weight,
        'waist': waist,
        'bodyfat': bodyfat
    })


@app.route('/clients/<name>/metrics', methods=['GET'])
def get_metrics(name):
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    metrics = conn.execute("""
        SELECT * FROM metrics WHERE client_name=? ORDER BY date
    """, (name,)).fetchall()
    conn.close()

    return jsonify([dict(m) for m in metrics])


@app.route('/clients/<name>/metrics/chart', methods=['GET'])
def get_metrics_chart(name):
    conn = get_db()
    client = conn.execute(
        "SELECT * FROM clients WHERE name=?", (name,)
    ).fetchone()

    if not client:
        conn.close()
        return jsonify({'error': 'Client not found'}), 404

    rows = conn.execute("""
        SELECT date, weight FROM metrics
        WHERE client_name=? AND weight IS NOT NULL ORDER BY date
    """, (name,)).fetchall()
    conn.close()

    if not rows:
        return jsonify({'error': 'No weight metrics available for this client'}), 404

    return jsonify({
        'client': name,
        'chart_data': [{'date': r['date'], 'weight': r['weight']} for r in rows]
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
