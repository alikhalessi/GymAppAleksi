# SetPilot

SetPilot is a gym workout execution app for beginner-to-intermediate gym users who want to follow structured workout programs consistently.

The product focuses on helping users execute planned workouts in the gym: understand each movement through curated YouTube examples, track sets as they are completed, manage workout and rest timing, and review basic progress after each session.

## Sprint 1 Status

This repository is in Sprint 1 preparation. The goal is to establish the initial full-stack project scaffold without implementing production workout features.

The current scaffold includes:

- React + Vite + TypeScript frontend placeholder
- FastAPI backend package
- SQLite development database configuration
- `GET /health` backend endpoint

Authentication, workout session logic, YouTube API integration, payments, trainer dashboard, smartwatch sync, nutrition, and AI-generated workout planning are not included.

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
- Authentication later: not included in Sprint 0

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
|   |   |-- schemas.py
|   |-- requirements.txt
|   |-- tests
|   |   |-- test_health.py
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

## Documentation

- [Product vision](docs/product-vision.md)
- [MVP scope](docs/mvp-scope.md)
- [Sprint plan](docs/sprint-plan.md)
- [User stories](docs/user-stories.md)
- [Data model](docs/data-model.md)
- [Architecture](docs/architecture.md)
- [Codex prompts](docs/codex-prompts.md)

## Current Development Rule

Keep changes small and understandable. During Sprint 1 preparation, focus on scaffold quality and local startup only. Do not add authentication, workout session logic, YouTube API integration, or unrelated product features.
