# Render Backend Deployment

## Purpose

Sprint 8 prepares the SetPilot FastAPI backend for staging deployment on Render. This is backend-only staging readiness. It does not deploy the Vercel frontend, does not claim production readiness, and does not move secrets into Git.

## Service Settings

- Render service name: `setpilot-api`
- Repository: `alikhalessi/GymAppAleksi`
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Render must bind to `0.0.0.0` and use `$PORT`. Do not use `localhost` or a hardcoded port for the deployed service.

## Deployment Config

The repo includes a root `render.yaml` blueprint for the backend web service. It contains no real secrets. Secret environment variables use `sync: false`, which means Render prompts for values during blueprint creation or requires manual dashboard entry later.

The blueprint is optional operational help. The same settings can be entered manually in the Render dashboard.

## Python Version

The backend currently runs on modern Python 3 and is validated locally with Python 3.12. If Render selects an incompatible Python runtime, set a Python version in the Render dashboard or add the Render-supported Python version setting in a later infrastructure-only change.

## Required Environment Variables

Set these in Render environment variables only:

| Variable | Required? | Notes |
| --- | --- | --- |
| `ENVIRONMENT` | Yes | Use `staging`. |
| `DATABASE_URL` | Yes | Supabase PostgreSQL URL. Never commit it. |
| `ALLOWED_ORIGINS` | Yes | Include local frontend during smoke tests and later the Vercel frontend URL. |
| `AUTH_REQUIRED` | Yes | Target is `true` for protected staging after JWT verification is configured. |
| `SUPABASE_URL` | Yes for auth staging | Supabase project URL. |
| `SUPABASE_JWT_SECRET` | Yes before `AUTH_REQUIRED=true` | Backend-only token verification secret. |

## Optional Environment Variables

| Variable | Required? | Notes |
| --- | --- | --- |
| `SUPABASE_JWKS_URL` | Optional | Reserved for future JWKS verification hardening. |
| `OPENAI_API_KEY` | Optional for deploy, required for AI features | Backend-only OpenAI key. |
| `YOUTUBE_API_KEY` | Optional for deploy, required for automatic YouTube search | Backend-only YouTube Data API key. |
| `OPENAI_WORKOUT_IMPORT_MODEL` | Optional | Defaults in code if unset. |
| `OPENAI_WORKOUT_ENHANCE_MODEL` | Optional | Defaults in code if unset. |
| `OPENAI_SESSION_REFLECTION_MODEL` | Optional | Defaults in code if unset. |
| `OPENAI_CHANGE_PROPOSAL_MODEL` | Optional | Defaults in code if unset. |

## Never Commit

- Real `DATABASE_URL`
- Supabase database password
- Supabase `service_role` key
- Supabase JWT secret
- OpenAI API key
- YouTube API key
- Render dashboard secrets
- Private `.env` files

Frontend `VITE_*` variables are browser-visible. Never place backend secrets in frontend environment variables.

## Migrations

Apply Alembic migrations deliberately before or alongside the staging deployment. Do not run destructive migrations blindly and do not place `DATABASE_URL` in Git.

Placeholder-only local command:

```powershell
cd backend
.\.venv\Scripts\activate
$env:DATABASE_URL="postgresql+psycopg://setpilot_user:replace_me@db.example.invalid:5432/setpilot"
alembic current
alembic upgrade head
```

Use a private Supabase connection string only in your local shell or Render dashboard.

## Smoke Tests After Deploy

Replace `https://setpilot-api.onrender.com` with the actual Render URL.

```powershell
curl https://setpilot-api.onrender.com/health
curl https://setpilot-api.onrender.com/auth/status
```

Expected `/health` response:

```json
{"status":"ok"}
```

Also open:

```text
https://setpilot-api.onrender.com/docs
```

The OpenAPI docs should load. Protected app data routes may reject requests when `AUTH_REQUIRED=true`, which is expected without a bearer token.

## Inspect Logs

In Render:

1. Open the `setpilot-api` service.
2. Open the **Logs** tab.
3. Check build logs for dependency installation failures.
4. Check runtime logs for startup, database, CORS, auth, or migration errors.

Do not paste logs containing secrets into GitHub, docs, or chat tools.

## Redeploy

Use one of:

- Push a new commit to the connected branch if auto-deploy is enabled.
- Click **Manual Deploy** in the Render dashboard.
- Re-sync the blueprint after `render.yaml` changes.

## Common Deployment Failures

### Wrong Root Directory

Symptom: Render cannot find `requirements.txt` or imports fail.

Fix: Set root directory to `backend`.

### Missing Requirements

Symptom: Import errors for FastAPI, SQLAlchemy, OpenAI, psycopg, Alembic, PyJWT, or uvicorn.

Fix: Confirm Render build command is `pip install -r requirements.txt`.

### Wrong Start Command

Symptom: Service starts locally but fails on Render.

Fix: Use `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.

### Localhost Binding

Symptom: Render deploys but health checks fail.

Fix: Bind to `0.0.0.0`, not `localhost` or `127.0.0.1`.

### Missing DATABASE_URL

Symptom: Backend falls back to SQLite or fails to reach Supabase.

Fix: Set `DATABASE_URL` in Render with the private Supabase PostgreSQL URL.

### Supabase Password Or URL Problem

Symptom: Database authentication or connection errors.

Fix: Re-copy the connection string from Supabase, verify the database password, URL-encode special characters, and prefer direct or session pooler URLs over transaction pooler URLs for migrations.

### CORS Issue

Symptom: Browser frontend cannot call the Render API.

Fix: Set `ALLOWED_ORIGINS` to include the exact frontend origin, including protocol and domain.

### Missing Allowed Origins

Symptom: Local frontend smoke tests fail against Render.

Fix: Include `http://localhost:5173` and `http://127.0.0.1:5173` during local smoke testing, then add the later Vercel URL in Sprint 9.

### Migration Not Applied

Symptom: Runtime database errors about missing tables or columns.

Fix: Run reviewed Alembic migrations against Supabase and verify `alembic_version`.
