# Environment Configuration

## Purpose

This guide defines SetPilot environment configuration for local development, Phase 2 staging, and future production. The goal is explicit configuration without committing secrets or breaking the local SQLite MVP.

Local development remains the default. Cloud accounts are not required to run the app locally.

## Backend Environment Variables

| Variable | Required locally? | Required in staging? | Description | Example placeholder |
| --- | --- | --- | --- | --- |
| `ENVIRONMENT` | No | Yes | Environment label used to distinguish local, staging, and future production behavior. | `local` |
| `DATABASE_URL` | No | Yes | Canonical Phase 2 database URL. Defaults to local SQLite when unset. Unqualified `postgres://` and `postgresql://` URLs are normalized to `postgresql+psycopg://` for SQLAlchemy's selected PostgreSQL driver. | `sqlite:///./setpilot.db` |
| `OPENAI_API_KEY` | No | Yes for AI features | Backend-only OpenAI API key. The in-app local session key can still be used during local development. | empty |
| `OPENAI_WORKOUT_IMPORT_MODEL` | No | No | Model used for workout plan extraction. | `gpt-5.5` |
| `OPENAI_WORKOUT_ENHANCE_MODEL` | No | No | Model used for readiness-based plan enhancement. | `gpt-5.5` |
| `OPENAI_SESSION_REFLECTION_MODEL` | No | No | Model used for post-session AI reflection. | `gpt-5.5` |
| `OPENAI_CHANGE_PROPOSAL_MODEL` | No | No | Planned model setting for future reviewable change proposals. | `gpt-5.5` |
| `YOUTUBE_API_KEY` | No | Yes for YouTube search | Backend-only YouTube Data API key. Manual video entry does not require it. | empty |
| `ALLOWED_ORIGINS` | No | Yes | Comma-separated frontend origins allowed by CORS. Defaults to local Vite origins. | `http://localhost:5173,http://127.0.0.1:5173` |

Compatibility note: `SETPILOT_DATABASE_URL` is still supported as a legacy local/test override. `DATABASE_URL` takes priority when both are set.

Supported future PostgreSQL URL formats:

- `postgresql://user:password@host:5432/database`
- `postgresql+psycopg://user:password@host:5432/database`
- `postgresql+psycopg2://user:password@host:5432/database`
- `postgres://user:password@host:5432/database`, normalized internally to `postgresql+psycopg://...`

These are format examples only. Do not commit real usernames, passwords, hosts, or database names.

The backend dependency uses `psycopg[binary]`, the modern Psycopg 3 driver. Unqualified PostgreSQL URLs are normalized to the `postgresql+psycopg://` SQLAlchemy dialect so future Render/Supabase URLs can use that driver without adding psycopg2.

## Frontend Environment Variables

| Variable | Required locally? | Required in staging? | Description | Example placeholder |
| --- | --- | --- | --- | --- |
| `VITE_API_BASE_URL` | No | Yes | Frontend-visible backend API base URL. Falls back to `http://127.0.0.1:8000` locally. | `http://127.0.0.1:8000` |
| `VITE_SUPABASE_URL` | No | Later | Future frontend-visible Supabase project URL, only when Supabase Auth is implemented. | empty |
| `VITE_SUPABASE_ANON_KEY` | No | Later | Future frontend-visible Supabase anon key, only when Supabase Auth is implemented. | empty |

`VITE_*` values are public in browser builds. Never put backend secrets, database passwords, OpenAI keys, YouTube keys, or Supabase service-role keys in frontend environment variables.

## Local Setup Examples

### Backend With PowerShell Environment Variables

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

Optional local database override:

```powershell
cd backend
$env:DATABASE_URL="sqlite:///./setpilot.db"
uvicorn app.main:app --reload
```

Future staging placeholder only:

```powershell
$env:DATABASE_URL="postgresql+psycopg://setpilot_user:replace_me@db.example.invalid:5432/setpilot"
```

Do not use or commit real Supabase connection strings yet. PostgreSQL compatibility is prepared in Sprint 3, but actual Supabase connection comes later after Alembic migrations.

### Frontend With `.env.local`

Create `frontend/.env.local` if you want an explicit local API URL:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then run:

```powershell
cd frontend
npm run dev
```

The app still falls back to `http://127.0.0.1:8000` if `VITE_API_BASE_URL` is unset.

## Staging Plan Later

### Vercel

- Set `VITE_API_BASE_URL` to the Render backend URL.
- Do not put backend secrets in Vercel frontend variables.
- Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` only when Supabase Auth is implemented.

### Render

- Set `DATABASE_URL` to the Supabase PostgreSQL URL after PostgreSQL compatibility and migrations are ready.
- Set `OPENAI_API_KEY` in the Render environment.
- Set `YOUTUBE_API_KEY` in the Render environment.
- Set `ALLOWED_ORIGINS` to the Vercel frontend URL.

### Supabase

- Copy the database URL into Render only.
- Keep service-role keys out of frontend variables.
- Put the anon key in Vercel only when Supabase Auth is implemented.
- Sprint 3 prepares PostgreSQL URL and driver compatibility only. It does not connect this repository to Supabase.

## Secret Safety

- Never commit `.env` files.
- Commit only `.env.example` files with placeholder values.
- Backend secrets must never be placed in frontend environment variables.
- Frontend `VITE_*` variables are public in the browser bundle.
- Database URLs with passwords belong only in backend/server dashboards.
- Rotate any key that is accidentally committed or pasted into a public place.

## Troubleshooting

### Frontend Cannot Reach Backend

- Confirm the backend is running.
- Confirm `VITE_API_BASE_URL` points to the backend URL.
- Confirm the frontend was restarted after changing `.env.local`.
- Confirm the backend health check works at `/health`.

### CORS Error

- Confirm `ALLOWED_ORIGINS` includes the exact frontend origin.
- Include protocol and port, for example `http://localhost:5173`.
- Restart the backend after changing backend environment variables.

### OpenAI Key Missing

- Save a local session key in Settings, or set `OPENAI_API_KEY` in the backend environment.
- Restart the backend after setting PowerShell environment variables.
- Do not add `OPENAI_API_KEY` to frontend `.env` files.

### YouTube Key Missing

- Set `YOUTUBE_API_KEY` in the backend environment.
- Restart the backend.
- Confirm the YouTube Data API is enabled for the key.

### Wrong Working Directory

- Start the backend from `backend`.
- Start the frontend from `frontend`.
- Local SQLite defaults to `backend/setpilot.db` when running uvicorn from `backend`.

### Backend Running On Different Port

- Update `frontend/.env.local` with the actual backend URL.
- Restart the Vite dev server after changing `VITE_API_BASE_URL`.
