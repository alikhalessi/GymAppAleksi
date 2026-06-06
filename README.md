# SetPilot

SetPilot is a gym workout execution app for beginner-to-intermediate gym users who want to follow structured workout programs consistently.

The product focuses on helping users execute planned workouts in the gym: understand each movement through curated YouTube examples, track sets as they are completed, manage workout and rest timing, and review basic progress after each session.

## Current MVP Status

This repository is in MVP feature development. The scaffold is complete and the current product slices include **Workout Program CRUD**, **Workout Days under Programs**, **Exercises under Workout Days**, **Planned Set Weights**, **Stored YouTube Examples**, **Automatic YouTube Search**, **AI Workout Plan Import**, **Readiness-Based AI Enhancement**, **In-App OpenAI Key Settings**, **Workout Session Mode**, **Set Logging**, **Rest Timer**, **Recent Sessions**, **Human-Readable Session Detail History**, **AI Session Reflection**, **Progression Suggestions**, **Trainee Profile**, **Readiness Checks**, **Program Versions**, and a **Dashboard-First MVP Flow**.

The current scaffold includes:

- React + Vite + TypeScript frontend
- FastAPI backend package
- SQLite development database configuration
- `GET /health` backend endpoint
- Program CRUD endpoints under `/programs`
- Workout day CRUD endpoints under `/programs/{program_id}/workout-days`
- Exercise CRUD endpoints under `/programs/{program_id}/workout-days/{workout_day_id}/exercises`
- Planned set endpoints under `/exercises/{exercise_id}/planned-sets`
- Stored YouTube video endpoints under `/exercises/{exercise_id}/youtube-videos`
- Automatic YouTube search endpoint under `/exercises/{exercise_id}/youtube-videos/search-and-save`
- `GET /settings/openai-key` OpenAI key status endpoint
- `POST /settings/openai-key` session-only OpenAI key save endpoint
- `DELETE /settings/openai-key` session key clear endpoint
- `POST /imports/workout-plan/analyze` AI analysis endpoint
- `POST /imports/workout-plan/enhance` readiness-based AI enhancement endpoint
- `POST /imports/workout-plan/save` reviewed import save endpoint
- Workout session endpoints under `/sessions`
- Frontend OpenAI key settings panel with masked status, save, refresh, and clear controls
- Frontend program creation, editing, deletion, refresh, selection, and listing UI
- Frontend workout day creation, editing, deletion, refresh, selection, and listing UI for the selected program
- Frontend exercise creation, editing, deletion, refresh, and listing UI for the selected workout day
- Frontend AI import panel with plain-text paste, AI preview, warnings, trainer-review flag, and save flow
- Frontend readiness enhancement flow that preserves original plans until the user saves an adjusted version
- Frontend planned set weights, YouTube examples, workout session mode, set logging, rest timer, recent sessions, session detail view, AI reflection controls, progression suggestion controls, profile/readiness context, and dashboard guidance

Authentication, payments, trainer dashboard, smartwatch sync, and nutrition are not included yet.

## Phase 2 Cloud-Staging Plan

Phase 1 is the local MVP. Phase 2 will move SetPilot toward a cloud-staging SaaS foundation while preserving local development.

Phase 2 planning documents:

- [Phase 2 cloud architecture plan](docs/PHASE_2_CLOUD_ARCHITECTURE_PLAN.md)
- [Cloud decision record](docs/CLOUD_DECISION_RECORD.md)
- [Phase 2 manual setup checklist](docs/PHASE_2_MANUAL_SETUP_CHECKLIST.md)
- [Supabase Postgres setup](docs/SUPABASE_POSTGRES_SETUP.md)
- [Supabase validation checklist](docs/SUPABASE_VALIDATION_CHECKLIST.md)

## Environment Configuration

SetPilot keeps local development as the default. Cloud accounts are not required to run the local MVP.

Use [Environment configuration](docs/ENVIRONMENT_CONFIGURATION.md) for local, staging, and future-production configuration rules. Safe placeholder examples live in `backend/.env.example` and `frontend/.env.example`. Real `.env` files and secrets must not be committed.

## Database Migrations

SetPilot uses Alembic migration tooling for Phase 2 database discipline while keeping local SQLite development working. See [Database migrations](docs/DATABASE_MIGRATIONS.md) for local commands, safety rules, and the future Supabase/PostgreSQL migration path.

Sprint 5 adds the founder-facing [Supabase Postgres setup](docs/SUPABASE_POSTGRES_SETUP.md) and [Supabase validation checklist](docs/SUPABASE_VALIDATION_CHECKLIST.md) for safe staging database preparation. These docs use placeholders only; real Supabase database URLs and passwords must stay out of Git.

## MVP Scope

The local MVP should support:

1. Enter an OpenAI API key in the app for the current backend session.
2. Create workout programs.
3. Add workout days.
4. Add exercises with movement name, sets, reps, rest seconds, and notes.
5. Paste a plain-text workout plan and use AI to structure it.
6. Review AI import warnings, questions, and trainer-review recommendation.
7. Save the reviewed AI import into the program/day/exercise tables.
8. Show up to 5 stored YouTube examples per exercise.
9. Start a workout session.
10. Complete sets.
11. Use workout timer and rest timer.
12. Save weight, reps, and difficulty rating per set.
13. Show a post-session summary.
14. Generate an advisory AI session reflection after completion.
15. Show basic progression suggestions and progress analysis.

## Tech Direction

- Frontend: React, Vite, TypeScript
- Backend: FastAPI
- Local MVP database: SQLite with SQLAlchemy
- Future production database: PostgreSQL
- AI import: OpenAI API with Structured Outputs style JSON schema
- API key handling for local MVP: session-only backend memory, with environment variable fallback
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
|   |   |   |-- imports.py
|   |   |   |-- planned_sets.py
|   |   |   |-- programs.py
|   |   |   |-- settings.py
|   |   |   |-- workout_days.py
|   |   |   |-- workout_exercises.py
|   |   |   |-- workout_sessions.py
|   |   |   |-- youtube_videos.py
|   |   |-- schemas.py
|   |   |-- services
|   |   |   |-- __init__.py
|   |   |   |-- ai_enhance.py
|   |   |   |-- ai_import.py
|   |   |   |-- runtime_settings.py
|   |   |   |-- youtube_search.py
|   |-- requirements.txt
|   |-- tests
|   |   |-- conftest.py
|   |   |-- test_health.py
|   |   |-- test_imports.py
|   |   |-- test_planned_sets.py
|   |   |-- test_programs.py
|   |   |-- test_settings.py
|   |   |-- test_workout_days.py
|   |   |-- test_workout_exercises.py
|   |   |-- test_workout_sessions.py
|   |   |-- test_youtube_videos.py
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
```

Start backend:

```bash
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

### OpenAI API Key Setup

The easiest local workflow is now inside the app:

1. Start the backend.
2. Start the frontend.
3. Open the app.
4. Paste your OpenAI API key into the **OpenAI API Key** settings card.
5. Click **Save key for this session**.
6. Use AI import.

The key is kept only in backend memory for the current running backend process. It disappears when the backend restarts.

Optional fallback: you can still use an environment variable instead of the app settings panel:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

Optional model override:

```powershell
$env:OPENAI_WORKOUT_IMPORT_MODEL="gpt-4.1-mini"
```

Check key status:

```bash
curl http://127.0.0.1:8000/settings/openai-key
```

Analyze a plain-text workout plan:

```bash
curl -X POST http://127.0.0.1:8000/imports/workout-plan/analyze \
  -H "Content-Type: application/json" \
  -d "{\"raw_text\":\"Day 1 Upper Body\\nBench Press 4x8 rest 120 seconds\"}"
```

Save a reviewed AI import:

```bash
curl -X POST http://127.0.0.1:8000/imports/workout-plan/save \
  -H "Content-Type: application/json" \
  -d "{\"parsed_plan\":{\"program\":{\"name\":\"Imported Plan\",\"goal\":\"Imported from text\",\"duration_weeks\":8},\"workout_days\":[{\"name\":\"Upper Body\",\"day_order\":1,\"exercises\":[{\"movement_name\":\"Bench Press\",\"sets\":4,\"reps\":\"8\",\"rest_seconds\":120,\"notes\":\"\",\"exercise_order\":1,\"confidence\":0.9,\"warnings\":[]}]}]},\"approval_status\":\"approved_by_user\"}"
```

Run backend tests:

```bash
cd backend
python -m pytest
```

If you use the repository virtual environment on Windows:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

### YouTube API Key Setup

Automatic YouTube search runs only on the backend and reads `YOUTUBE_API_KEY` from the backend environment. Do not put this key in frontend code or commit it to Git.

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_youtube_api_key_here"
uvicorn app.main:app --reload
```

Manual YouTube video entry does not require a YouTube API key.

### Local SQLite Notes

The local MVP uses `backend/setpilot.db` by default. Prototype schema changes may require a local reset:

```powershell
cd backend
Remove-Item .\setpilot.db
uvicorn app.main:app --reload
```

Backend tests use a separate SQLite file through `SETPILOT_DATABASE_URL` and should not write into `backend/setpilot.db`.

### Frontend

From the repository root:

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at the local URL printed by Vite, usually `http://localhost:5173`.

Important: run the backend and frontend at the same time when testing program, workout day, exercise creation, API key settings, and AI import. The frontend calls the backend at `http://127.0.0.1:8000`.

Build the frontend:

```bash
cd frontend
npm run build
```

## Security Notes

For local MVP use, the in-app API key setting is session-only and backend-only. The key is not stored in GitHub, not hardcoded in frontend code, and not intentionally kept in browser storage.

For production, this must be replaced with proper user accounts, encrypted secret storage, HTTPS, key rotation/deletion, access control, and usage limits.

## Documentation

- [Product vision](docs/product-vision.md)
- [MVP scope](docs/mvp-scope.md)
- [Sprint plan](docs/sprint-plan.md)
- [User stories](docs/user-stories.md)
- [Data model](docs/data-model.md)
- [Architecture](docs/architecture.md)
- [Codex prompts](docs/codex-prompts.md)
- [Environment configuration](docs/ENVIRONMENT_CONFIGURATION.md)
- [Database migrations](docs/DATABASE_MIGRATIONS.md)
- [Supabase Postgres setup](docs/SUPABASE_POSTGRES_SETUP.md)
- [Supabase validation checklist](docs/SUPABASE_VALIDATION_CHECKLIST.md)

## Current Development Rule

Keep changes small and understandable. During Sprint 1, focus on one product slice at a time. Programs, workout days, exercises, AI import, and in-app API key settings are now the base. The next slice should be stored YouTube examples or workout session mode. Do not add authentication, payments, nutrition, trainer dashboard, or smartwatch integration until their sprint arrives.
