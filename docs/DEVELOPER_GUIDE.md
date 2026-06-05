# Developer Guide

This guide is for contributors, evaluators, and future maintainers who need to run SetPilot locally and make safe scoped changes.

SetPilot is currently a local Phase-1 MVP. It is not a deployed production SaaS.

## Local Setup

Prerequisites:

- Python 3.12
- Node.js and npm
- Git
- Optional OpenAI API key
- Optional YouTube Data API key

Clone the repository and open a terminal at the repository root.

## Backend Commands

Create and activate the virtual environment:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Run tests:

```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest
```

Start the backend:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend URLs:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

## Frontend Commands

Install dependencies:

```powershell
cd frontend
npm install
```

Build:

```powershell
cd frontend
npm run build
```

Start development server:

```powershell
cd frontend
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## Environment Variables

OpenAI:

- In-app Settings can save an OpenAI key for the current backend process.
- `OPENAI_API_KEY` is supported as a backend environment fallback.
- Used for AI import, AI enhancement, and AI session reflection.

```powershell
cd backend
$env:OPENAI_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

YouTube:

- `YOUTUBE_API_KEY` is used by the backend for automatic exercise video search.
- Manual YouTube link entry does not require this key.

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

Never commit real API keys or secrets.

## Running The Full App

Use two terminals.

Terminal 1:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173
```

## Phase-1 Demo

Use:

- [Phase-1 MVP demo flow](PHASE_1_MVP_DEMO_FLOW.md)
- [Demo sample workout plan](DEMO_SAMPLE_WORKOUT_PLAN.md)

The demo should prove the loop:

Import plan -> review -> save -> train -> log sets -> finish session -> view session detail -> generate reflection/progression -> check dashboard.

## Git Workflow

Create a branch for each sprint or focused change:

```powershell
git checkout -b sprint/name-of-sprint
```

Review changes before staging:

```powershell
git status --short
git diff
```

Run validation before commit:

```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest

cd ..\frontend
npm run build
```

Commit and push:

```powershell
git add .
git commit -m "Clear commit message"
git push -u origin sprint/name-of-sprint
```

Open a pull request and merge only after review and clean tests/build.

## Branch Naming Convention

Use short descriptive branch names:

```text
sprint/readme-developer-guide-v1
sprint/demo-sample-flow-v1
sprint/error-handling-empty-states-v1
```

Avoid vague names such as `fix`, `changes`, or `updates`.

## Safe Sprint Workflow

1. Read `README.md` and the relevant docs.
2. Confirm the current sprint scope.
3. Create a branch.
4. Keep changes small and scoped.
5. Do not add authentication, payments, trainer portal, cloud deployment, new models, or new dependencies unless explicitly planned.
6. Do not commit secrets.
7. Run backend tests.
8. Run frontend build.
9. Review `git diff`.
10. Commit, push, and open a pull request.

## Local SQLite

The local MVP uses SQLite at `backend/setpilot.db`.

If schema drift blocks local development, stop the backend and delete the database:

```powershell
cd backend
Remove-Item .\setpilot.db
uvicorn app.main:app --reload
```

This deletes local test data only. Proper migrations are planned for a later phase.
