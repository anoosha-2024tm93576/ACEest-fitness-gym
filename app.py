from flask import Flask, Response, jsonify, request
import csv
import io
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL)": {
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
            "Target: ~2000 kcal"
        ),
        "color": "#e74c3c",
        "factor": 22
    },
    "Muscle Gain (MG)": {
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
        "factor": 35
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
        "factor": 26
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
            weight REAL,
            program TEXT,
            calories INTEGER
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
    weight = data.get('weight')
    adherence = data.get('adherence', 0)

    if not name or not program:
        return jsonify({'error': 'name and program are required'}), 400

    if program not in PROGRAMS:
        return jsonify({'error': 'Program not found'}), 404

    calories = get_calories(weight, program) if weight else None

    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO clients (name, age, weight, program, calories)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, weight, program, calories))
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
            'weight': weight,
            'program': program,
            'adherence': adherence,
            'calories': calories
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
        fieldnames=['id', 'name', 'age', 'weight', 'program', 'calories']
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
