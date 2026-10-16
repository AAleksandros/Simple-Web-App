# Full-Stack Web App (Vue.js, Django, PostgreSQL)

A simple web application using Vue.js, Django (Python), and a PostgreSQL database.

## Quick Setup Guide

### Prerequisites

Ensure the following dependencies are installed:

- **Node.js** and **npm** (required for Vue.js)
- **Python** (with Django)
- **Docker** and **Docker Compose** (optional but recommended)
- **Vue.js extension** (if using VS Code)

---

### 1. Backend and Database Setup

Create the backend environment file, then fill in the values (secret key, database credentials, Azure email settings):

```sh
cp backend/.env.example backend/.env
```

From the root directory (where `docker-compose.yml` is located), start the containers and run the migrations:

```sh
docker compose up --build -d
docker compose exec backend python manage.py migrate
```

This will:

- Set up the Django backend.
- Initialize the PostgreSQL database inside a Docker container.

The API is then available at `http://localhost:8000/api/`. This setup has been tested end to end against the Postgres container: register, verify email, log in, and an authenticated request. If another Postgres already uses port 5432 on your machine, publish the container on a different host port:

```sh
POSTGRES_HOST_PORT=5433 docker compose up --build -d
```

To manage containers, use:

```sh
docker compose down  # Stop and remove containers
docker compose up -d # Start containers in detached mode
docker ps            # Check running containers
```

---

### 2. Frontend Setup

Navigate to the `frontend/` directory:

```sh
cd frontend
npm install    # Install dependencies (first-time setup)
npm run dev    # Start the Vue.js development server
```

By default, the web app will be accessible at:

```
http://localhost:5173/
```

The frontend calls the API at `http://localhost:8000/api`. To point it somewhere else (for example an ngrok tunnel), set `VITE_API_URL` in `frontend/.env.local`. If the frontend is served from a different address, also update `CORS_ALLOWED_ORIGINS` and `FRONTEND_URL` in `backend/.env`; `FRONTEND_URL` is used to build the link in password-reset emails.

---

### 3. Running the tests

The backend tests use a self-contained settings module (`backend/backend/test_settings.py`) with an in-memory SQLite database, so you don't need Docker, Postgres or a `.env` file. Outgoing email is mocked, so the tests never contact Azure.

```sh
cd backend
pip install -r requirements.txt
python manage.py test --settings=backend.test_settings
```

GitHub Actions runs the same command on every push and pull request (`.github/workflows/backend-tests.yml`).

---

## Technology Stack

- **Frontend:** Vue.js (Vite, TypeScript)
- **Backend:** Django (Django REST Framework)
- **Database:** PostgreSQL (via Docker)

---

## Additional Notes

- The backend provides API endpoints for authentication, user management, and data handling.
- Ensure `.env` files are configured correctly for database connections and Django settings.
- Authentication is handled using JWT (JSON Web Token).
