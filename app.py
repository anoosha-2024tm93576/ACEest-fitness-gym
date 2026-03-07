from flask import Flask, jsonify, request

app = Flask(__name__)

programs = {
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
        "calorie_factor": 22
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
        "calorie_factor": 35
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
        "calorie_factor": 26
    }
}

@app.route('/')
def home():
    return jsonify({
        "message": "ACEest Fitness API is running"
    })

@app.route('/programs', methods=['GET'])
def get_programs():
    return jsonify(list(programs.keys()))

@app.route('/programs/<name>', methods=['GET'])
def get_program(name):
    if name not in programs:
        return jsonify({"error": "Program not found"}), 404
    return jsonify(programs[name])

@app.route('/clients', methods=['POST'])
def save_client():
    data = request.get_json()
    name = data.get('name', '').strip()
    program = data.get('program', '').strip()
    age = data.get('age')
    weight = data.get('weight')
    adherence = data.get('adherence', 0)

    if not name or not program:
        return jsonify({'error': 'Name and program are required'}), 400
    
    if program not in programs:
        return jsonify({'error': 'Program not found'}), 404

    calories = int(weight * programs[program]['calorie_factor']) if weight else None

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

@app.route('/clients/reset', methods=['POST'])
def reset_client():
    return jsonify({
        'message': 'Client form reset successfully',
        'client': {
            'name': '',
            'age': None,
            'weight': None,
            'program': '',
            'adherence': 0,
            'calories': None
        }
    })

if __name__ == '__main__':
    app.run(debug=True)