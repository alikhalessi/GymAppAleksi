# Authentication Setup

## Purpose

Sprint 6 adds the SetPilot authentication foundation with Supabase Auth. The goal is sign up, sign in, sign out, session state, and backend auth status endpoints without breaking the local MVP flow.

This sprint does not make existing workout data user-owned yet. Sprint 7 will add ownership fields, route protection, and data-access rules.

## Supabase Auth Role In Phase 2

Supabase Auth is the Phase 2 identity provider for staging. The React frontend uses Supabase Auth with public browser-safe configuration. The FastAPI backend receives bearer tokens and can verify them when backend verification is configured.

The frontend must never contain backend secrets, database passwords, JWT secrets, or Supabase service-role keys.

## Get Project URL

1. Open the Supabase project dashboard.
2. Go to project settings or API settings.
3. Copy the Project URL.
4. Store it as `VITE_SUPABASE_URL` in `frontend/.env.local`.

The Project URL is public enough for browser configuration, but still keep real project details out of committed docs.

## Get Publishable Or Anon Public Key

1. Open the Supabase project dashboard.
2. Go to API keys.
3. Copy the publishable key or legacy anon public key.
4. Store it as `VITE_SUPABASE_ANON_KEY` in `frontend/.env.local`.

Use only the publishable key or legacy anon public key in frontend variables. Never use the `service_role` key in the browser.

## Frontend Local Env

Create `frontend/.env.local`:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_SUPABASE_URL=https://YOUR_PROJECT_REF.example.invalid
VITE_SUPABASE_ANON_KEY=YOUR_PUBLISHABLE_OR_ANON_PUBLIC_KEY
```

These are placeholders. Do not commit real values.

After editing frontend env files, restart the Vite dev server:

```powershell
cd frontend
npm run dev
```

## Backend Auth Env

Local development keeps auth optional:

```text
AUTH_REQUIRED=false
SUPABASE_URL=
SUPABASE_JWT_SECRET=
SUPABASE_JWKS_URL=
```

`SUPABASE_JWT_SECRET` enables the current backend JWT verification path for `/auth/me`. `SUPABASE_JWKS_URL` is reserved for JWKS-based verification hardening. Do not commit real values.

## What Sprint 6 Does

- Adds Supabase JS client configuration in the frontend.
- Adds an Auth screen with sign up, sign in, sign out, and current user state.
- Shows auth state in the app header.
- Sends the Supabase access token to backend API calls when a session exists.
- Adds backend `/auth/status` and `/auth/me` endpoints.
- Keeps existing MVP data routes available in local/demo mode.

## What Sprint 6 Does Not Do

- Does not add `user_id` ownership columns to app tables.
- Does not add RLS policies.
- Does not protect all existing data endpoints.
- Does not deploy to Vercel or Render.
- Does not store service-role keys in the frontend.
- Does not claim production auth readiness.

## Sprint 7 Preview

Sprint 7 should add user-owned data. That means ownership columns, migrations, route protection, test coverage for cross-user isolation, and a clear RLS/backend authorization plan.

## Troubleshooting

### Auth Not Configured

- Confirm `frontend/.env.local` exists.
- Confirm it contains `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`.
- Restart `npm run dev` after editing env files.

### Sign In Fails

- Confirm the email and password are correct.
- Confirm email/password provider is enabled in Supabase Auth.
- Check whether Supabase requires email confirmation before sign in.

### Backend Auth Status Is Disabled

- This is expected for local development when `AUTH_REQUIRED=false` and no JWT secret is configured.
- Set backend auth env values only in private local env or later in Render.

### Token Not Reaching Backend

- Sign in from the Auth view.
- Refresh backend auth status.
- Confirm `/auth/me` receives a bearer token only after Supabase Auth has a browser session.
