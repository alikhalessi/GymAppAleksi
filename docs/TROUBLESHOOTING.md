# Troubleshooting

Common SetPilot local development issues and fixes.

## Backend Unreachable

Symptom:

- Frontend shows "Backend is unreachable."
- Program, import, session, profile, or readiness calls fail.

Likely cause:

- FastAPI backend is not running.
- Backend is running on the wrong port.

Fix:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Check:

```powershell
curl http://127.0.0.1:8000/health
```

## Frontend Cannot Fetch Backend

Symptom:

- Frontend opens, but data loading fails.
- Browser console shows failed requests to `127.0.0.1:8000`.

Likely cause:

- Backend is not running.
- Backend crashed after startup.
- Port `8000` is occupied by another process.

Fix:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

If port `8000` is already in use, stop the conflicting process or restart your terminal session.

## Missing OpenAI Key

Symptom:

- AI import, enhancement, or reflection reports that an OpenAI key is not configured.

Likely cause:

- No key was saved in Settings.
- `OPENAI_API_KEY` was not set before backend startup.
- Backend was not restarted after setting the environment variable.

Fix in app:

1. Open **Settings**.
2. Paste the OpenAI key.
3. Click **Save key**.

Fix with backend environment:

```powershell
cd backend
$env:OPENAI_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

Never commit real keys.

## Missing YouTube Key

Symptom:

- Automatic YouTube search fails with a key/configuration message.

Likely cause:

- `YOUTUBE_API_KEY` is not set in the backend environment.

Fix:

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

Manual YouTube link entry still works without this key.

## Invalid YouTube Key

Symptom:

- YouTube search is configured but still fails.
- Backend response mentions YouTube API or permission failure.

Likely cause:

- Key is invalid.
- YouTube Data API is not enabled for the key.
- API quota or permissions are blocked.

Fix:

1. Confirm the key in Google Cloud Console.
2. Enable YouTube Data API v3.
3. Restart backend after updating the environment variable.

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_updated_key_here"
uvicorn app.main:app --reload
```

## No Module Named Pytest

Symptom:

- `python -m pytest` fails with `No module named pytest`.

Likely cause:

- Backend virtual environment is not activated.
- Backend dependencies were not installed.

Fix:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m pytest
```

## Npm Cannot Find Package.Json

Symptom:

- `npm run dev` or `npm run build` fails with missing `package.json`.

Likely cause:

- Command was run from the wrong directory.

Fix:

```powershell
cd frontend
npm install
npm run build
npm run dev
```

## SQLite Schema Issue

Symptom:

- Backend errors mention missing columns or schema mismatch.
- Local app worked before a prototype schema change, then started failing.

Likely cause:

- Local SQLite database is stale.
- Proper migrations are not part of Phase 1 yet.

Fix:

Stop the backend, then delete the local database:

```powershell
cd backend
Remove-Item .\setpilot.db
uvicorn app.main:app --reload
```

This removes local test data only.

## Port Already In Use

Symptom:

- Backend or frontend cannot start because a port is already in use.

Likely cause:

- Another backend or Vite process is still running.

Fix:

Find the process:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen
Get-NetTCPConnection -LocalPort 5173 -State Listen
```

Stop the process by ID:

```powershell
Stop-Process -Id <PID>
```

Then restart backend or frontend.

## CORS Issue

Symptom:

- Browser console reports CORS errors.

Likely cause:

- Frontend is not running from a configured local origin.
- Backend is not the expected local app.

Fix:

Use the normal local URLs:

```text
Backend: http://127.0.0.1:8000
Frontend: http://localhost:5173
```

Restart both processes:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm run dev
```

## Working From Wrong Directory

Symptom:

- Commands cannot find `.venv`, `requirements.txt`, `package.json`, or `app.main`.

Likely cause:

- Terminal is in the wrong folder.

Fix:

From repository root:

```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest
```

Or:

```powershell
cd frontend
npm run build
```

## OpenAI Requests Fail After Key Is Set

Symptom:

- Key is configured, but AI import/enhancement/reflection fails.

Likely cause:

- Network issue.
- Model access issue.
- Invalid or expired key.

Fix:

1. Confirm the key is valid.
2. Confirm model/API access.
3. Restart backend.
4. Try a smaller sample plan from [DEMO_SAMPLE_WORKOUT_PLAN.md](DEMO_SAMPLE_WORKOUT_PLAN.md).

## Frontend Build Fails

Symptom:

- `npm run build` fails.

Likely cause:

- Missing npm dependencies.
- TypeScript error from recent frontend edits.

Fix:

```powershell
cd frontend
npm install
npm run build
```

Read the TypeScript error and fix the referenced file/line.
