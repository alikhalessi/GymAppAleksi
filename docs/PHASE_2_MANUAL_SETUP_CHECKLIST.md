# Phase 2 Manual Setup Checklist

This checklist is for the human founder. It prepares cloud accounts and decisions, but it does not deploy SetPilot yet.

## GitHub

- [ ] Confirm `main` is clean before starting each Phase 2 sprint.
- [ ] Confirm the Phase 1 release tag exists.
- [ ] Consider protecting the `main` branch later.
- [ ] Use branches and pull requests for Phase 2 cloud work.

## Vercel

- [ ] Create or sign in to Vercel.
- [ ] Connect GitHub.
- [ ] Prepare frontend project name: `setpilot-frontend`.
- [ ] Do not deploy until Sprint 9.

## Render

- [ ] Create or sign in to Render.
- [ ] Connect GitHub.
- [ ] Prepare backend service name: `setpilot-api`.
- [ ] Do not deploy until Sprint 8.

## Supabase

- [ ] Create or sign in to Supabase.
- [ ] Prepare project name: `setpilot-db`.
- [ ] Choose an EU region if available and appropriate.
- [ ] Store the database password in a password manager.
- [ ] Use [Supabase Postgres setup](SUPABASE_POSTGRES_SETUP.md) before running Alembic against Supabase.
- [ ] Complete [Supabase validation checklist](SUPABASE_VALIDATION_CHECKLIST.md) during Sprint 5 validation.
- [ ] Do not connect production data yet.

## Secrets

- [ ] Keep the OpenAI key out of GitHub.
- [ ] Keep the YouTube key out of GitHub.
- [ ] Keep database URLs out of GitHub.
- [ ] Use Vercel, Render, and Supabase dashboard environment-variable settings.
- [ ] Do not paste service-role keys into frontend environment variables.

## Manual Decisions

- [ ] Final cloud region.
- [ ] Staging domain names.
- [ ] Free or paid tiers for Vercel, Render, and Supabase.
- [ ] Whether every Phase 2 cloud sprint must use a PR workflow before merge.
- [ ] Who owns cloud account recovery and billing access.
