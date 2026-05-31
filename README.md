# SetPilot

SetPilot is a gym workout execution app for beginner-to-intermediate gym users who want to follow structured workout programs consistently.

The product focuses on helping users execute planned workouts in the gym: understand each movement through curated YouTube examples, track sets as they are completed, manage workout and rest timing, and review basic progress after each session.

## Sprint 1 Status

This repository is now in Sprint 1 feature development. The initial scaffold is complete and the first real product slice, **Workout Program CRUD**, has been added.

The current scaffold includes:

- React + Vite + TypeScript frontend
- FastAPI backend package
- SQLite development database configuration
- `GET /health` backend endpoint
- `POST /programs` create program endpoint
- `GET /programs` list programs endpoint
- `GET /programs/{program_id}` read single program endpoint
- `PUT /programs/{program_id}` update program endpoint
- `DELETE /programs/{program_id}` delete program endpoint
- Frontend program creation, editing, deletion, refresh, and listing UI

Authentication, workout day management, workout session logic, YouTube API integration, payments, trainer dashboard, smartwatch sync, nutrition, and AI-generated workout planning are not included yet.

## MVP Scope

The local MVP should support:

1. Create workout programs.
2. Add workout days.
3. Add exercises with movement name, sets, reps, rest seconds, and notes.
4. Show up to 5 stored YouTube examples per exercise.
5. Start a workout session.
6. Complete sets.
7. Use workout timer and rest timer.
8. Save weight, reps, and difficulty rating per set.
9. Show a post-session summary.
10. Show basic progress analysis.

## Tech Direction

- Frontend: React, Vite, TypeScript
- Backend: FastAPI
- Local MVP database: SQLite with SQLAlchemy
- Future production database: PostgreSQL
- Charts later: Recharts
- Authentication later: not included in Sprint 1

## Repository Structure

```text
.
|-- AGENTS.md
|-- README.md
|-- backend
|   |-- README.md
|   |-- app
|   |   |-- database.py
|   |   |-- main.py
|   |   |-- models.py
|   |   |-- routers
|   |   |   |-- health.py
|   |   |   |-- programs.py
|   |   |-- schemas.py
|   |-- requirements.txt
|   |-- tests
|   |   |-- test_health.py
|   |   |-- test_programs.py
|-- docs
|   |-- architecture.md
|   |-- codex-prompts.md
|   |-- data-model.md
|   |-- mvp-scope.md
|   |-- product-vision.md
|   |-- sprint-plan.md
|   |-- user-stories.md
|-- frontend
|   |-- index.html
|   |-- package.json
|   |-- src
|   |   |-- App.css
|   |   |-- App.tsx
|   |   |-- main.tsx
|   |-- vite.config.ts
```

## Local Setup

Install dependencies only when you are ready to run the scaffold locally.

### Backend

From the repository root:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

Program endpoints:

```bash
curl http://127.0.0.1:8000/programs
```

Create a program:

```bash
curl -X POST http://127.0.0.1:8000/programs \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Strength Foundation\",\"goal\":\"Build strength while learning core lifts\",\"duration_weeks\":8}"
```

Run backend tests:

```bash
cd backend
pytest
```

### Frontend

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at the local URL printed by Vite, usually `http://localhost:5173`.

Important: run the backend and frontend at the same time when testing program creation. The frontend calls the backend at `http://127.0.0.1:8000`.

## Documentation

- [Product vision](docs/product-vision.md)
- [MVP scope](docs/mvp-scope.md)
- [Sprint plan](docs/sprint-plan.md)
- [User stories](docs/user-stories.md)
- [Data model](docs/data-model.md)
- [Architecture](docs/architecture.md)
- [Codex prompts](docs/codex-prompts.md)

## Current Development Rule

Keep changes small and understandable. During Sprint 1, focus on one product slice at a time. Program CRUD is now the base. The next slice should be workout days attached to programs. Do not add authentication, workout session logic, YouTube API integration, or unrelated product features until their sprint arrives.
