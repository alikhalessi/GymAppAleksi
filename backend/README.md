# SetPilot Backend

FastAPI backend for the local SetPilot MVP.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000` by default.

The local development database defaults to `setpilot.db` in this folder. To use another SQLite database, set `SETPILOT_DATABASE_URL` before starting the app.

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Tests

```bash
python -m pytest
```

On Windows, if you are using the repository virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Tests set `SETPILOT_DATABASE_URL` to a separate SQLite file in `backend/tests/`, so they do not write to the local development database.

## Environment Keys

Optional local environment variables:

- `OPENAI_API_KEY`: fallback key for AI import and enhancement.
- `YOUTUBE_API_KEY`: backend-only key for automatic YouTube search.

Do not commit real API keys.
