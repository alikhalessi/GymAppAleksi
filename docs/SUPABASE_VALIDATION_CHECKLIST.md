# Supabase Validation Checklist

Use this checklist for the manual Sprint 5 database validation. Do not paste real credentials into this file.

- [ ] Supabase project `setpilot-db` created.
- [ ] EU region selected if available and appropriate.
- [ ] Database password stored safely in a password manager.
- [ ] Direct connection URL or session pooler URL copied privately.
- [ ] `DATABASE_URL` set only in a local shell, private `.env`, or later in Render environment variables.
- [ ] No real `DATABASE_URL` committed.
- [ ] No Supabase password committed.
- [ ] No Supabase service-role key committed.
- [ ] No Supabase anon key committed except future placeholders in `.env.example`.
- [ ] `cd backend` completed before running Alembic.
- [ ] Backend virtual environment activated.
- [ ] `alembic current` runs against the selected Supabase URL.
- [ ] `alembic upgrade head` runs against the selected Supabase URL.
- [ ] SetPilot tables are visible in the Supabase Table Editor or SQL editor.
- [ ] `alembic_version` table is visible in Supabase.
- [ ] Local SQLite backend tests still pass.
- [ ] Frontend build still passes.
- [ ] Frontend Supabase Auth configuration is validated separately in Sprint 6.
- [ ] Sprint 7 `user_id` ownership migration is applied.
- [ ] Backend route ownership checks are validated with separate test users.
- [ ] PostgreSQL RLS remains deferred to a later hardening sprint.
