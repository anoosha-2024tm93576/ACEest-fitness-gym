# ACEest Fitness & Gym API

A Flask REST API for the ACEest Fitness & Gym management system, built as part of the BITS Pilani Introduction to DevOps assignment. The API manages client profiles, fitness programs, workout logging, body metrics, progress tracking and membership.

---

## Tech Stack

- **Python 3.14** + **Flask**
- **SQLite** for persistence
- **Pytest** + **pytest-flask** for testing
- **Docker** for containerisation
- **GitHub Actions** for CI/CD
- **Jenkins** for on-premise CI/CD

---

## Project Structure

```
aceest/
├── app.py                        # Flask application
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Container definition
├── Jenkinsfile                   # Jenkins CI/CD pipeline
├── pytest.ini                    # Pytest configuration
├── .dockerignore
├── .gitignore
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   └── test_app.py               # Test suite (58 tests)
└── .github/
    └── workflows/
        └── main.yml              # GitHub Actions CI/CD pipeline
```

---

## Setup & Running Locally

```bash
# Clone the repo
git clone https://github.com/anoosha-2024tm93576/ACEest-fitness-gym
cd ACEest-fitness-gym

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

API will be available at `http://localhost:5000`.

---

## Running with Docker

```bash
# Build the image
docker build -t aceest-fitness .

# Run the container
docker run -p 5000:5000 aceest-fitness
```

---

## Running Tests

```bash
python -m pytest -v
```

---

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API health check |

### Auth

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get role |

**Register request body:**
```json
{ "username": "trainer1", "password": "pass123", "role": "Trainer" }
```

**Login request body:**
```json
{ "username": "admin", "password": "admin" }
```

Default admin credentials: `admin / admin`

---

### Programs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/programs` | List all program names |
| GET | `/programs/<name>` | Get program details |

Available programs: `Fat Loss (FL) - 3 day`, `Fat Loss (FL) - 5 day`, `Muscle Gain (MG) - PPL`, `Beginner (BG)`

---

### Clients

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients` | List all clients |
| POST | `/clients` | Save or update a client |
| GET | `/clients/export` | Export all clients as CSV |
| GET | `/clients/<name>` | Load a single client |
| GET | `/clients/<name>/summary` | Full client summary with progress and metrics |
| GET | `/clients/<name>/bmi` | BMI with category and health risk |
| GET | `/clients/<name>/membership` | Check membership status and end date |
| GET | `/clients/<name>/program/generate?exp_level=` | Generate AI workout program |

**Save client request body:**
```json
{
  "name": "John",
  "age": 25,
  "height": 175,
  "weight": 70,
  "program": "Beginner (BG)",
  "adherence": 80,
  "target_weight": 65,
  "target_adherence": 90,
  "membership_status": "Active",
  "membership_end": "2026-12-31"
}
```

**Generate program query params:** `exp_level` = `beginner` | `intermediate` | `advanced`

---

### Progress

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clients/<name>/progress` | Save weekly adherence |
| GET | `/clients/<name>/progress` | Get all progress entries |
| GET | `/clients/<name>/progress/chart` | Get ordered chart data |

---

### Workouts

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clients/<name>/workouts` | Log a workout session with exercises |
| GET | `/clients/<name>/workouts` | Get workout history |

**Log workout request body:**
```json
{
  "date": "2026-03-08",
  "workout_type": "Strength",
  "duration_min": 60,
  "notes": "Felt strong",
  "exercises": [
    { "name": "Squat", "sets": 5, "reps": 5, "weight": 100 }
  ]
}
```

---

### Body Metrics

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clients/<name>/metrics` | Log body metrics |
| GET | `/clients/<name>/metrics` | Get all metrics |
| GET | `/clients/<name>/metrics/chart` | Get weight trend data |

---

## Database Schema

| Table | Key Columns |
|-------|-------------|
| `users` | username, password, role |
| `clients` | id, name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end |
| `progress` | id, client_name, week, adherence |
| `workouts` | id, client_name, date, workout_type, duration_min, notes |
| `exercises` | id, workout_id, name, sets, reps, weight |
| `metrics` | id, client_name, date, weight, waist, bodyfat |

---

## CI/CD Pipeline

### GitHub Actions

Triggered on every push and pull request to `main`. Four stages:

1. **Lint** — flake8 code quality check
2. **Test** — pytest test suite
3. **Docker Build** — builds the Docker image
4. **Docker Test** — runs tests inside the container

### Jenkins

Six stages: Checkout → Install Dependencies → Lint → Test → Docker Build → Docker Test

---

## Version History

| Version | highlights |
|---------|-----------|
| v1.0 | Initial Flask app, program selector API |
| v1.1 | Client profile, calorie calculator |
| v1.1.2 | Multi-client list, CSV export |
| v2.0.1 | SQLite database, progress tracking |
| v2.2.1 | Progress chart data endpoint |
| v2.2.4 | BMI, workout logging, body metrics, client summary |
| v3.1.2 | Login system, user registration, AI program generator |
| v3.2.4 | Membership status and end date, membership check endpoint |

> Versions (v2.1.2, v3.0.1) contain no new endpoints or schema changes