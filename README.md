# SetPilot — AI Workout Operating System

SetPilot is a local Phase-1 MVP for turning messy workout plans into executable training sessions.

It supports AI-powered workout plan import, readiness/profile-aware enhancement, a focused workout session cockpit, set logging with a rest timer, AI session reflection, progression suggestions, and a dashboard that builds training memory from completed sessions.

This repository is not a production SaaS deployment yet. AI suggestions are advisory, do not diagnose medical conditions, and do not silently change workout plans.

## Current Phase-1 MVP Capabilities

- AI workout plan extraction from raw pasted text
- AI workout enhancement using trainee profile and readiness context
- Trainee profile
- Readiness checks
- Program versioning
- Workout programs, days, exercises, and planned sets
- Workout sessions
- Set logging with actual reps, weight, difficulty, and notes
- Rest timer
- Session history and human-readable session detail
- AI session reflection
- Progression suggestions
- Progress dashboard / training memory
- Stored YouTube exercise videos and optional automatic YouTube search
- Error handling and empty states for common local MVP failures
- Demo sample workout plan and Phase-1 MVP demo flow

## Tech Stack

Frontend:

- React
- TypeScript
- Vite

Backend:

- FastAPI
- SQLAlchemy
- Pydantic
- SQLite for the local prototype

AI / integrations:

- OpenAI Responses API
- YouTube Data API

## Repository Structure

```text
.
|-- backend/              FastAPI app, SQLAlchemy models, routers, services
|-- backend/tests/        Pytest backend test suite
|-- docs/                 Product, architecture, demo, and developer docs
|-- frontend/             React + TypeScript + Vite frontend
|-- README.md             Main project overview and setup entry point
```

## Prerequisites

- Python 3.12
- Node.js and npm
- Git
- Optional OpenAI API key for AI import, enhancement, and reflection
- Optional YouTube Data API key for automatic exercise video search

## Backend Setup

From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

From the repository root:

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

The frontend calls the backend at `http://127.0.0.1:8000`, so run the backend and frontend at the same time for normal app testing.

## Environment Variables And API Keys

OpenAI is used for:

- AI workout plan import
- AI workout plan enhancement
- AI session reflection

The app supports saving an OpenAI key from **Settings** for the current backend process. The backend also supports `OPENAI_API_KEY` as an environment fallback.

Example:

```powershell
cd backend
$env:OPENAI_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

YouTube automatic search uses the backend environment variable `YOUTUBE_API_KEY`.

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

Manual YouTube video entry does not require a YouTube key.

Never commit real API keys, secrets, `.env` files, or terminal history containing secrets.

## Running The App Locally

Use two terminals.

Terminal 1, backend:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Terminal 2, frontend:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

## Phase-1 MVP Demo Flow

Full runbook:

- [Phase-1 MVP demo flow](docs/PHASE_1_MVP_DEMO_FLOW.md)

Summary:

1. Load or paste the sample workout plan.
2. Analyze/import the raw plan with AI.
3. Review and save the structured plan.
4. Add trainee profile and readiness context if useful.
5. Enhance the plan if desired and if OpenAI is configured.
6. Start a workout.
7. Log sets.
8. Use the rest timer.
9. Finish the session.
10. View session details.
11. Generate AI reflection if OpenAI is configured.
12. Generate progression suggestions.
13. Check dashboard updates.

## Sample Workout Plan

Use this realistic three-day sample plan for demos and evaluator walkthroughs:

- [Demo sample workout plan](docs/DEMO_SAMPLE_WORKOUT_PLAN.md)

The Import screen also includes a **Load sample workout plan** button. It fills the raw text area only; it does not analyze or save automatically.

## Investor Demo

Use these docs for a short, honest Phase-1 walkthrough:

- [Investor demo checklist](docs/INVESTOR_DEMO_CHECKLIST.md)
- [Bug fix freeze report](docs/BUG_FIX_FREEZE_REPORT.md)
- [Phase-1 MVP demo flow](docs/PHASE_1_MVP_DEMO_FLOW.md)
- [Phase-1 MVP validation report](docs/PHASE_1_MVP_VALIDATION_REPORT.md)

## Tests And Validation

Backend:

```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest
```

Frontend:

```powershell
cd frontend
npm run build
```

## Local SQLite Note

The local prototype uses SQLite at `backend/setpilot.db`.

If local schema drift blocks development, stop the backend and delete the local database:

```powershell
cd backend
Remove-Item .\setpilot.db
uvicorn app.main:app --reload
```

This removes local test data only. Proper migrations are a future Phase 2 concern.

## What This MVP Is Not Yet

- Not production SaaS
- No multi-user authentication yet
- No trainer portal yet
- No payments yet
- No cloud deployment yet
- No HIPAA/GDPR compliance claim
- No medical diagnosis
- AI suggestions are advisory and must not be treated as medical or safety guarantees

## Roadmap

Phase 1:

- Local MVP and investor demo
- Reliable import -> review -> train -> reflect -> dashboard loop

Phase 2:

- PostgreSQL
- Alembic migrations
- Authentication
- User-owned data
- Cloud staging

Phase 3:

- Trainer/client mode
- PWA/mobile gym mode
- Subscriptions
- Pilot users

## More Documentation

- [SetPilot product master plan](docs/SET_PILOT_PRODUCT_MASTER_PLAN.md)
- [Investor demo checklist](docs/INVESTOR_DEMO_CHECKLIST.md)
- [Phase-1 MVP demo flow](docs/PHASE_1_MVP_DEMO_FLOW.md)
- [Phase-1 MVP validation report](docs/PHASE_1_MVP_VALIDATION_REPORT.md)
- [Demo sample workout plan](docs/DEMO_SAMPLE_WORKOUT_PLAN.md)
- [Developer guide](docs/DEVELOPER_GUIDE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Product vision](docs/product-vision.md)
- [MVP scope](docs/mvp-scope.md)
- [Sprint plan](docs/sprint-plan.md)
- [User stories](docs/user-stories.md)
- [Data model](docs/data-model.md)
- [Architecture](docs/architecture.md)
