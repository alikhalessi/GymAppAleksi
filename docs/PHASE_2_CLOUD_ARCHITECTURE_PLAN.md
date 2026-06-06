# Phase 2 Cloud Architecture Plan

## Purpose

Phase 2 moves SetPilot from a local Phase 1 MVP toward a cloud-staging SaaS foundation. The goal is not production launch yet. The goal is to prepare a practical hosted environment where the React frontend, FastAPI backend, and relational data layer can be tested safely with real staging infrastructure.

Local development must continue to work while cloud readiness is added in small, reviewable sprints.

## Recommended Stack

### Frontend

- Vercel for the React/Vite frontend.
- GitHub-connected preview and staging deployments.
- Frontend configuration through `VITE_*` environment variables only.

### Backend

- Render Web Service for the FastAPI API.
- GitHub-connected deployments.
- Backend-owned environment variables for secrets and service URLs.

### Database/Auth

- Supabase for PostgreSQL.
- Supabase Auth starts in Sprint 6 after database compatibility, migrations, and Supabase Postgres setup are ready.
- Supabase Row Level Security later, once user-owned data is exposed.

## Architecture Diagram in Text

```text
User Browser
  -> Vercel React Frontend
  -> Render FastAPI Backend
  -> Supabase PostgreSQL
  -> Supabase Auth

External services:
  Render FastAPI Backend -> OpenAI API
  Render FastAPI Backend -> YouTube Data API
```

The frontend should never call OpenAI or the YouTube Data API directly. Those calls belong behind the backend.

## Why This Stack

- Fast GitHub-based deployment path for a solo founder.
- Low DevOps burden compared with managing a full cloud platform directly.
- Good fit for the current React/Vite frontend and FastAPI backend.
- Supabase gives a credible PostgreSQL, Auth, and RLS path without adding unnecessary infrastructure early.
- Easier Phase 2 staging path than starting with full Azure, AWS, or GCP complexity.
- Keeps the product focused on the core loop instead of cloud plumbing.

## Why Not One Big Cloud Yet

- Azure is a strong future enterprise path, but it adds heavier setup and more platform decisions now.
- AWS is powerful, but complexity is high for this stage.
- Google Cloud has a good Cloud Run option, but still requires more cloud plumbing than the current team needs.
- Vercel + Render + Supabase is the fastest reasonable staging path for a solo founder MVP.

This decision is about Phase 2 staging speed and operational simplicity, not a permanent claim that this is the final production architecture.

## Environments

### Local

- React/Vite frontend runs locally.
- FastAPI backend runs locally.
- SQLite remains allowed for local development at the start of Phase 2.
- Backend database configuration reads `DATABASE_URL`, keeps `SETPILOT_DATABASE_URL` as a legacy local/test override, and defaults to `sqlite:///./setpilot.db`.
- Frontend API configuration reads `VITE_API_BASE_URL` and falls back to `http://127.0.0.1:8000`.

### Staging

- Vercel hosts the frontend.
- Render hosts the FastAPI backend.
- Supabase hosts PostgreSQL.
- Supabase Auth starts in Sprint 6 after the database layer is ready.
- Staging data should be disposable and separate from any future production data.

### Production-Later

- Separate secrets from staging.
- Stronger monitoring and error reporting.
- Database backups and restore testing.
- Security review before real users or sensitive user-owned data.
- Auth, authorization, and RLS verified before multi-user release.

## Environment Variables

These are planned variables and placeholders only. Do not commit real values.

### Backend

- `DATABASE_URL`: planned canonical database URL for Phase 2 cloud and future PostgreSQL support.
- `OPENAI_API_KEY`: backend-only OpenAI key.
- `OPENAI_WORKOUT_IMPORT_MODEL`: model for workout plan extraction.
- `OPENAI_WORKOUT_ENHANCE_MODEL`: model for readiness-based plan enhancement.
- `OPENAI_SESSION_REFLECTION_MODEL`: model for session reflection.
- `OPENAI_CHANGE_PROPOSAL_MODEL`: planned model for future reviewable change proposals.
- `YOUTUBE_API_KEY`: backend-only YouTube Data API key.
- `ALLOWED_ORIGINS`: allowed frontend origins for CORS.
- `ENVIRONMENT`: local, staging, or production-later environment label.
- `SUPABASE_URL`: Supabase project URL for backend auth context.
- `SUPABASE_JWT_SECRET`: backend-only JWT verification secret, never exposed to the frontend.
- `SUPABASE_JWKS_URL`: future JWKS verification endpoint.
- `AUTH_REQUIRED`: auth enforcement flag, default false for local/demo compatibility.

Implementation note: Sprint 2 introduced `DATABASE_URL` handling and `ALLOWED_ORIGINS` parsing while preserving local SQLite and local Vite defaults. Sprint 3 added PostgreSQL URL normalization, a PostgreSQL driver dependency, and dialect-aware engine options without connecting to Supabase. Sprint 4 added Alembic tooling and an initial schema migration while keeping startup `create_all` for local prototype compatibility. Sprint 5 documented Supabase Postgres setup. Sprint 6 adds Supabase Auth foundation. Sprint 7 adds backend-enforced user-owned data and defers PostgreSQL RLS to a later hardening sprint.

### Frontend

- `VITE_API_BASE_URL`: planned frontend-visible API base URL.
- `VITE_SUPABASE_URL`: frontend-visible Supabase project URL for Auth.
- `VITE_SUPABASE_ANON_KEY`: Supabase publishable key or legacy anon public key for Auth.

Frontend variables are bundled into browser-accessible code. They must never contain backend secrets, private API keys, database passwords, service-role keys, or anything that would be unsafe if viewed by a user.

## Security Principles

- No secrets committed to Git.
- Backend owns OpenAI and YouTube API keys.
- Frontend calls the backend, not OpenAI or YouTube directly.
- Supabase Auth foundation is added in Sprint 6. Backend user-owned data and route protection are added in Sprint 7.
- RLS remains a future hardening item before a real multi-user cloud release.
- AI outputs remain advisory and must not make medical claims.
- AI changes to plans must remain reviewable and should not silently mutate user programs.
- Staging and production-later secrets must be separate.

## Phase 2 Sprint Roadmap

1. Cloud Architecture Decision
2. Environment Configuration
3. PostgreSQL Compatibility
4. Alembic Migrations
5. Supabase Postgres Setup
6. Authentication v1
7. User-Owned Data
8. Backend Staging Deployment
9. Frontend Staging Deployment
10. Cloud Security Hardening
11. Staging Demo Validation
12. Phase 2 Release Tag

## Migration Strategy

- Keep local SQLite working initially.
- Introduce `DATABASE_URL` handling in a controlled Sprint 2 change, with backwards compatibility for current local workflows.
- Sprint 3 prepares PostgreSQL compatibility checks before connecting to Supabase.
- Sprint 4 adds Alembic migrations after the database boundary is clear.
- Sprint 5 connects Supabase PostgreSQL only after migrations are ready.
- Avoid breaking local development while cloud staging is introduced.
- Keep production data out of the process until staging is proven.

## Risks

- CORS misconfiguration can make the deployed frontend unable to call the backend.
- Secret leakage can expose OpenAI, YouTube, database, or Supabase credentials.
- Cloud cost surprise can happen if free-tier limits or usage are misunderstood.
- Database migration mistakes can corrupt or lose data.
- Authentication complexity can slow the sprint plan if introduced too early.
- Cross-user data leaks become a serious risk once auth and user-owned data exist.
- Render cold starts may affect demo quality on free tiers.
- Frontend/backend URL mismatch can break staging even when both services are healthy.

## Decision

SetPilot Phase 2 will use Vercel for the React/Vite frontend, Render for the FastAPI backend, and Supabase for PostgreSQL plus Auth.

This is accepted as the Phase 2 cloud-staging stack. It is not yet a production launch decision.
