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

### Using the app

Open http://localhost:8501. The landing page has a dropdown for each of the four personas — pick a user and click Login. There's no real authentication; selecting a user simulates them being signed in.

## Project Structure

```
app/src/
  Home.py           Landing page with persona selector
  pages/                16 feature pages (4 per persona)
  modules/nav.py        Persona-aware sidebar nav
api/backend/
  habits/               Habit tracking, logs, streaks, goals
  groups/               Accountability groups, members, notes
  admin/                Categories, flagged content, user mgmt
  analytics/            Platform-wide analytics
  rest_entry.py         Registers all four blueprints
database-files/         DDL + mock data (runs on container init)
docker-compose.yaml     Service orchestration
```

## Features

HabitSync has four personas, each with a home page and three feature pages.

**Everyday User** — create custom habits, mark them complete, view streaks and completion history, set daily and weekly goals, and join accountability groups with friends.

**Wellness Coach** — create and manage accountability groups, assign habits to members, track each member's completion rate and streak status, send motivational notes, and review weekly group summaries.

**System Administrator** — manage the platform's habit categories and default suggested habits, review and resolve flagged content, monitor platform-wide metrics (users, daily active, habits logged, groups), and activate or deactivate user accounts.

**Data Analyst** — view completion trends broken down by category, compare retention between group members and solo users, analyze time-of-day activity heatmaps, and track user growth over time.

## REST API

The backend exposes 40 routes across four blueprints (`habits`, `groups`, `admin`, `analytics`). The full REST API matrix — with user story mappings — is in the Phase 3 submission document.
