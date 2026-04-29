# ACEest Fitness & Gym

A Flask REST API for the ACEest Fitness & Gym management system, built as part of the BITS Pilani Introduction to DevOps assignment. The API manages client profiles, fitness programs, workout logging, body metrics, progress tracking and membership.

---

## Tech Stack

- **Python 3.11+** + **Flask**
- **SQLite** for persistence
- **Pytest** + **pytest-flask** for testing
- **Docker** for containerisation
- **GitHub Actions** for CI/CD
- **Jenkins** for on-premise CI/CD
- **SonarQube** for code quality analysis

---

## Prerequisites

- **Local development**: Python 3.11+ and `pip`
- **Docker run**: Docker Desktop / Docker Engine
- **CI/CD (optional)**:
  - GitHub Actions runs automatically in GitHub
  - Jenkins needs: `python3` + `pip3`, Docker CLI/daemon access, SonarScanner, and `kubectl` configured for your cluster

---

## Project Structure

```
.
├── .dockerignore
├── .gitignore
├── app.py
├── Dockerfile
├── Jenkinsfile
├── pytest.ini
├── README.md
├── requirements.txt
├── .github/
│   └── workflows/
│       └── main.yml
├── k8s/
│   ├── ab/
│   │   ├── deployment-a.yaml
│   │   ├── deployment-b.yaml
│   │   └── service.yaml
│   ├── base/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── blue-green/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── canary/
│   │   ├── canary-deployment.yaml
│   │   ├── service.yaml
│   │   └── stable-deployment.yaml
│   ├── rolling-update/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── shadow/
│       ├── service.yaml
│       ├── shadow-deployment.yaml
│       └── stable-deployment.yaml
├── postman/
│   └── ACEest Fitness & Gym.postman_collection.json
├── tests/
│   ├── conftest.py
│   └── test_app.py
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

## Postman Collection

Import the collection from `postman/ACEest Fitness & Gym.postman_collection.json` into Postman to try the API quickly.

---

## Kubernetes Manifests

Kubernetes YAMLs are under `k8s/`:

- **`k8s/base/`**: baseline `Deployment` + `Service`
- **`k8s/rolling-update/`**: rolling update strategy
- **`k8s/blue-green/`**: blue/green switch pattern
- **`k8s/canary/`**: stable + canary deployments
- **`k8s/ab/`**: A/B deployments
- **`k8s/shadow/`**: stable + shadow deployments

The Jenkins pipeline deploys by updating the image for the `deployment/aceest-fitness` resource (see `Jenkinsfile`).

---

## API Endpoints

### Health Check


| Method | Endpoint | Description      |
| ------ | -------- | ---------------- |
| GET    | `/`      | API health check |


### Auth


| Method | Endpoint         | Description         |
| ------ | ---------------- | ------------------- |
| POST   | `/auth/register` | Register a new user |
| POST   | `/auth/login`    | Login and get role  |


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


| Method | Endpoint           | Description            |
| ------ | ------------------ | ---------------------- |
| GET    | `/programs`        | List all program names |
| GET    | `/programs/<name>` | Get program details    |


Available programs: `Fat Loss (FL) - 3 day`, `Fat Loss (FL) - 5 day`, `Muscle Gain (MG) - PPL`, `Beginner (BG)`

---

### Clients


| Method | Endpoint                                      | Description                                   |
| ------ | --------------------------------------------- | --------------------------------------------- |
| GET    | `/clients`                                    | List all clients                              |
| POST   | `/clients`                                    | Save or update a client                       |
| GET    | `/clients/export`                             | Export all clients as CSV                     |
| GET    | `/clients/<name>`                             | Load a single client                          |
| GET    | `/clients/<name>/summary`                     | Full client summary with progress and metrics |
| GET    | `/clients/<name>/bmi`                         | BMI with category and health risk             |
| GET    | `/clients/<name>/membership`                  | Check membership status and end date          |
| GET    | `/clients/<name>/program/generate?exp_level=` | Generate AI workout program                   |


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


| Method | Endpoint                         | Description              |
| ------ | -------------------------------- | ------------------------ |
| POST   | `/clients/<name>/progress`       | Save weekly adherence    |
| GET    | `/clients/<name>/progress`       | Get all progress entries |
| GET    | `/clients/<name>/progress/chart` | Get ordered chart data   |


**Save client progress(weekly adherence) body:**

```json
{
  "adherence": 80
}
```

---

### Workouts


| Method | Endpoint                   | Description                          |
| ------ | -------------------------- | ------------------------------------ |
| POST   | `/clients/<name>/workouts` | Log a workout session with exercises |
| GET    | `/clients/<name>/workouts` | Get workout history                  |


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


| Method | Endpoint                        | Description           |
| ------ | ------------------------------- | --------------------- |
| POST   | `/clients/<name>/metrics`       | Log body metrics      |
| GET    | `/clients/<name>/metrics`       | Get all metrics       |
| GET    | `/clients/<name>/metrics/chart` | Get weight trend data |


**Save client body-metrics details body:**

```json
{
  "date": "2026-03-22",
  "weight": 58,
  "waist": 79,
  "bodyfat": 14
}
```

---

## Database Schema


| Table       | Key Columns                                                                                                          |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| `users`     | username, password, role                                                                                             |
| `clients`   | id, name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end |
| `progress`  | id, client_name, week, adherence                                                                                     |
| `workouts`  | id, client_name, date, workout_type, duration_min, notes                                                             |
| `exercises` | id, workout_id, name, sets, reps, weight                                                                             |
| `metrics`   | id, client_name, date, weight, waist, bodyfat                                                                        |


---

## CI/CD Pipeline

### GitHub Actions

Triggered on every push and pull request to `main`. Four stages:

1. **Lint** — flake8 code quality check
2. **Test** — pytest test suite
3. **Docker Build** — builds the Docker image
4. **Docker Test** — runs tests inside the container

### Jenkins

Stages:

1. **Checkout**
2. **Install Dependencies**
3. **Lint**
4. **Test**
5. **SonarQube Analysis**
6. **Build Docker Image**
7. **Login to Docker Hub**
8. **Push Docker Image**
9. **Deploy to Kubernetes**

On pipeline failure, Jenkins rolls back the Kubernetes deployment to the last stable revision.

---

## Assumptions

### Jenkins
- Jenkins is run locally using Docker with the `jenkins/jenkins:lts` image
- Required tooling must be available inside the Jenkins environment:
  - Python + pip (to run lint/tests)
  - Docker CLI (to build/push images)
  - SonarScanner (to run SonarQube analysis)
  - kubectl access (to deploy/rollback)
- If you run Jenkins via Docker, you may need to install Python 3 and pip inside the Jenkins container:
```bash
  docker exec -it --user root jenkins apt-get install -y python3 python3-pip
```
- This is a one-time setup step and does not need to be repeated unless the container is recreated
- Jenkins credentials expected by the pipeline:
  - `sonar-token` (Secret text)
  - `dockerhub-credentials` (Username + Password)

### Docker
- A `.dockerignore` file is included to prevent the local `aceest_fitness.db` from being copied into the image, ensuring a clean database is created on every container start
- The application runs as a non-root user (`appuser`) inside the container for security


## Version History


| Version | Highlights                                                |
| ------- | --------------------------------------------------------- |
| v1.0    | Initial Flask app, program selector API                   |
| v1.1    | Client profile, calorie calculator                        |
| v1.1.2  | Multi-client list, CSV export                             |
| v2.0.1  | SQLite database, progress tracking                        |
| v2.2.1  | Progress chart data endpoint                              |
| v2.2.4  | BMI, workout logging, body metrics, client summary        |
| v3.1.2  | Login system, user registration, AI program generator     |
| v3.2.4  | Membership status and end date, membership check endpoint |
| v4.1.x  | Jenkins: SonarQube analysis, Docker push, Kubernetes deploy with rollback |

> v2.1.2 and v3.0.1 are stability releases with no code changes — no commits exist for these versions.
