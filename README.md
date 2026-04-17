# HabitSync

HabitSync is a habit tracking platform built to help people build consistent routines, join accountability groups, and see patterns in their progress over time. The platform also supports coaches who manage groups, admins who keep the platform healthy, and analysts who study what drives retention.

## The Team

The Alphas:
- Sahib Chawla
- Kenneith Chu Chen
- Krish Soni
- Matvey Rolett

## Tech Stack

- Python 3.11
- Streamlit (frontend)
- Flask (REST API)
- MySQL 8 (database)
- Docker Compose (orchestration)

## Running the App

### Prerequisites

Docker Desktop must be installed and running.

### Environment files

Two `.env` files are required. Neither is checked into the repo, so you'll need to create them yourself.

At the project root, create `.env`:

```
MYSQL_ROOT_PASSWORD=habitsync123
```

Inside the `api/` directory, create `api/.env`:

```
DB_HOST=db
DB_USER=root
MYSQL_ROOT_PASSWORD=habitsync123
DB_NAME=HabitSync
```

### Starting the containers

From the project root:

```bash
docker compose up -d
```

This starts three services:

- `habitsync-web-app` — Streamlit UI on port 8501
- `habitsync-web-api` — Flask API on port 4000
- `habitsync-mysql-db` — MySQL on port 3200 (host) → 3306 (container)

The database is seeded from the SQL files in `database-files/` the first time the `db` container starts. If you change the schema or the mock data afterward, the existing volume has to be removed for the new files to take effect:

```bash
docker compose down -v
docker compose up -d
```
