# ADR-001: Phase 2 Cloud Staging Stack

## Status

Accepted for Phase 2 staging.

## Context

SetPilot Phase 1 is a local MVP with a React/Vite frontend, FastAPI backend, SQLite development database, and backend-mediated AI and YouTube integrations. Phase 2 needs a cloud-staging SaaS foundation without prematurely adding heavy infrastructure, production operations, or auth before the database and deployment path are ready.

The selected stack must preserve local development and support a staged path toward PostgreSQL, authentication, user-owned data, and a cloud demo.

## Decision

Use:

- Vercel for the React/Vite frontend.
- Render Web Service for the FastAPI backend.
- Supabase for PostgreSQL and future Auth/RLS.

This decision applies to Phase 2 staging. It does not claim production readiness.

## Options Considered

### Vercel + Render + Supabase

Best fit for Phase 2 because it is fast to connect to GitHub, keeps DevOps burden low, matches the current app shape, and gives a clear PostgreSQL/Auth path through Supabase.

### Azure-only

Strong enterprise path and credible future option, but heavier setup for the current solo-founder staging need.

### AWS-only

Very powerful and flexible, but too much operational surface area for this phase.

### Google Cloud/Firebase

Good Cloud Run and Firebase options, but still adds more cloud plumbing than needed for the immediate React + FastAPI + PostgreSQL staging path.

## Consequences

- The team can move quickly toward a real staging demo.
- Cloud work remains understandable and reviewable across small Phase 2 sprints.
- Backend and database hosting are separate services, so environment variables and CORS must be handled carefully.
- Supabase Auth/RLS can be evaluated after the database migration path is stable.
- This stack may need revisiting if scale, enterprise requirements, costs, or platform limits change.

## Revisit Criteria

Revisit this decision if:

- Backend traffic grows enough that Render limits become painful.
- An enterprise buyer requires Azure, AWS, or GCP.
- Render cold starts, scaling, logs, networking, or cost structure block progress.
- Supabase Auth or RLS does not fit SetPilot's user-owned data model.
- Costs exceed expectations for staging or early production.
