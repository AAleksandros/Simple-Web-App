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

Navigate to the root directory (where `docker-compose.yml` is located) and run:

```sh
docker compose up --build -d
```

This will:

- Set up the Django backend.
- Initialize the PostgreSQL database inside a Docker container.

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
