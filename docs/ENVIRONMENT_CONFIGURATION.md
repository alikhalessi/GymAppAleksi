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
| `SUPABASE_URL` | No | Yes for auth staging | Supabase project URL for backend auth context. Do not use a service-role key here. | empty |
| `SUPABASE_JWT_SECRET` | No | Yes before `AUTH_REQUIRED=true` | Backend-only JWT verification secret for Supabase access tokens. Never expose in frontend. | empty |
| `SUPABASE_JWKS_URL` | No | Later | Future JWKS endpoint for stronger JWT verification flow. | empty |
| `AUTH_REQUIRED` | No | Yes for locked staging | Whether backend auth is required for protected app data routes. Defaults false for local/demo compatibility. | `false` |

Compatibility note: `SETPILOT_DATABASE_URL` is still supported as a legacy local/test override. `DATABASE_URL` takes priority when both are set.

Supported future PostgreSQL URL formats:

- `postgresql://user:password@host:5432/database`
- `postgresql+psycopg://user:password@host:5432/database`
- `postgresql+psycopg2://user:password@host:5432/database`
- `postgres://user:password@host:5432/database`, normalized internally to `postgresql+psycopg://...`

These are format examples only. Do not commit real usernames, passwords, hosts, or database names.

The backend dependency uses `psycopg[binary]`, the modern Psycopg 3 driver. Unqualified PostgreSQL URLs are normalized to the `postgresql+psycopg://` SQLAlchemy dialect so future Render/Supabase URLs can use that driver without adding psycopg2.

Alembic uses the same `DATABASE_URL` resolution as the app. If `DATABASE_URL` is unset, migration commands also fall back to local SQLite. Sprint 5 documents Supabase PostgreSQL validation, but the repository still must not contain real Supabase connection strings.

## Supabase PostgreSQL Configuration

Local development remains SQLite by default. Leave `DATABASE_URL` unset, or set it to `sqlite:///./setpilot.db`, when working on local MVP behavior.

For Sprint 5 validation, a Supabase PostgreSQL `DATABASE_URL` may be set only in a local shell or private, ignored `.env` file. Later, Render should receive the Supabase `DATABASE_URL` through Render environment variables, not through committed files.

Connection mode guidance:

- Direct connection is preferred for Alembic migrations when available.
- Session pooler can be used when direct connection is unavailable or an IPv4-only environment requires it.
- Transaction pooler is not preferred for migrations because transaction pooling can conflict with prepared statements, migration connection state, and DDL behavior.

See [Supabase Postgres setup](SUPABASE_POSTGRES_SETUP.md) and [Supabase validation checklist](SUPABASE_VALIDATION_CHECKLIST.md) before running Alembic against Supabase.

## Frontend Environment Variables

| Variable | Required locally? | Required in staging? | Description | Example placeholder |
| --- | --- | --- | --- | --- |
| `VITE_API_BASE_URL` | No | Yes | Frontend-visible backend API base URL. Falls back to `http://127.0.0.1:8000` locally. | `http://127.0.0.1:8000` |
| `VITE_SUPABASE_URL` | No | Yes for auth staging | Frontend-visible Supabase project URL for Auth. | empty |
| `VITE_SUPABASE_ANON_KEY` | No | Yes for auth staging | Supabase publishable key or legacy anon public key for browser Auth. Never use service-role. | empty |

`VITE_*` values are public in browser builds. Never put backend secrets, database passwords, OpenAI keys, YouTube keys, or Supabase service-role keys in frontend environment variables.

See [Authentication setup](AUTHENTICATION_SETUP.md) before enabling Supabase Auth locally or in staging. Sprint 6 adds sign up, sign in, sign out, and session state. Sprint 7 adds backend-enforced user-owned data for app routes.

## User-Owned Data Environment Behavior

Protected app data routes use a backend current-user dependency:

- `AUTH_REQUIRED=false` with no token uses the local fallback user id `local-dev-user`.
- `AUTH_REQUIRED=false` with a bearer JWT and no backend verification parses claims without signature verification for local or staging smoke testing only.
- `AUTH_REQUIRED=true` with no token rejects protected app data routes.
- `AUTH_REQUIRED=true` with a token requires backend JWT verification to be configured.

See [User-owned data](USER_OWNED_DATA.md) for table coverage and RLS status.

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

Do not commit real Supabase connection strings. PostgreSQL compatibility was prepared in Sprint 3, Alembic was added in Sprint 4, and Sprint 5 allows private manual Supabase validation only.

Local Alembic status check:

```powershell
cd backend
alembic current
```

Never commit real `DATABASE_URL` values in Alembic config or documentation.

### Frontend With `.env.local`

Create `frontend/.env.local` if you want an explicit local API URL:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

Then run:

```powershell
cd frontend
npm run dev
```

The app still falls back to `http://127.0.0.1:8000` if `VITE_API_BASE_URL` is unset. Supabase Auth is disabled in the UI until both Supabase frontend variables are set. Restart Vite after changing frontend env files.

## Staging Plan Later

### Vercel

- Set `VITE_API_BASE_URL` to the Render backend URL.
- Do not put backend secrets in Vercel frontend variables.
- Add `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` for Supabase Auth. Use only the publishable key or legacy anon public key.

### Render

- Set `DATABASE_URL` to the Supabase PostgreSQL URL after PostgreSQL compatibility and migrations are ready.
- Set `OPENAI_API_KEY` in the Render environment.
- Set `YOUTUBE_API_KEY` in the Render environment.
- Set `ALLOWED_ORIGINS` to the Vercel frontend URL.
- Set `AUTH_REQUIRED=true` only after `SUPABASE_JWT_SECRET` or the future JWKS verification path is configured.

### Supabase

- Copy the database URL into Render only.
- Keep service-role keys out of frontend variables.
- Put the publishable key or legacy anon public key in Vercel for Supabase Auth.
- Sprint 7 uses backend route ownership checks. PostgreSQL RLS policies are deferred to a later hardening sprint.

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
