# User-Owned Data

## Purpose

Sprint 7 adds the user-owned data foundation for SetPilot. App data is scoped by the backend current user so signed-in users do not read or mutate another user's programs, profile, readiness checks, sessions, videos, reflections, progression suggestions, or dashboard data.

The frontend does not query Supabase app tables directly. It sends a Supabase access token to FastAPI when a browser session exists, and FastAPI applies ownership checks before database access.

## Current User Resolution

Backend app data routes depend on `get_current_user`.

- Verified token path: when `SUPABASE_JWT_SECRET` is configured, bearer tokens are verified and the Supabase `sub` claim becomes the effective `user_id`.
- Local unverified token path: when verification is not configured and `AUTH_REQUIRED=false`, bearer JWT claims may be parsed without signature verification for local or staging smoke testing only. This is unsafe and must not be treated as production verification.
- Local fallback path: when no token is present and `AUTH_REQUIRED=false`, the backend uses the stable fallback user id `local-dev-user`.
- Locked path: when `AUTH_REQUIRED=true` and no token is present, protected app data routes return `401 Authentication required.`
- Misconfigured locked path: when `AUTH_REQUIRED=true` and backend verification is not configured, bearer tokens return a `503` setup error.

## User-Owned Tables

The Sprint 7 migration adds nullable `user_id` columns and indexes to:

- `programs`
- `workout_days`
- `workout_exercises`
- `planned_sets`
- `workout_sessions`
- `session_sets`
- `session_reflections`
- `progression_suggestions`
- `trainee_profiles`
- `readiness_checks`
- `program_versions`
- `youtube_videos`

Columns are nullable so existing local SQLite rows and any early Supabase validation data are not destroyed. Local fallback mode can still read legacy `NULL` rows for continuity. New writes set the current effective user id.

## Route Scope

Protected app data routes now apply ownership checks to:

- Programs and program versions.
- Workout days, exercises, planned sets, and YouTube videos.
- Workout sessions, set logs, reflections, progression suggestions, recent sessions, and dashboard summary.
- Trainee profile and readiness checks.
- Workout plan import save.

AI analyze and enhance endpoints can still run without creating owned database rows. Save operations are owned.

Cross-user records return `404` rather than exposing whether another user's record exists.

## RLS Status

PostgreSQL Row Level Security policies are not added in Sprint 7. Backend authorization is the current enforcement layer. RLS should be added in a later hardening sprint after staging auth verification and deployment configuration are stable.

## Validation

Backend tests cover:

- User A program isolation from User B.
- Dashboard summary excluding another user's sessions.
- Trainee profile scoping.
- Readiness check scoping.
- Workout session scoping.
- Child record creation blocked under another user's parent.
- `AUTH_REQUIRED=true` rejecting missing tokens on protected app data routes.
- `AUTH_REQUIRED=false` local fallback CRUD compatibility.
