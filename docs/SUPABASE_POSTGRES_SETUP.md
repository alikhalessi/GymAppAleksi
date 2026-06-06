# Supabase Postgres Setup

## Purpose

This sprint prepares the Supabase PostgreSQL database target for future SetPilot staging. It does not deploy the backend or frontend, does not add Supabase Auth, and does not introduce user-owned data yet.

Local SQLite remains the default development database. Supabase PostgreSQL is used only for manual validation now and later as the Render backend database through private environment variables.

## Create Supabase Project

1. Sign in to Supabase.
2. Create a new project.
3. Use the project name `setpilot-db`.
4. Choose an EU region if available and appropriate for the expected users and founder location.
5. Keep staging data disposable. Do not connect production or sensitive user data at this stage.

## Save Database Password Safely

During project creation, Supabase asks for a database password.

- Store the password in a password manager.
- Never commit it.
- Never paste it into documentation.
- Never paste it into ChatGPT, Codex, issue comments, PR comments, screenshots, or logs.
- Rotate it immediately if it is exposed.

## Get Connection String

1. Open the Supabase project dashboard.
2. Click **Connect**.
3. Copy a PostgreSQL database connection string privately.
4. Keep the connection string only in your local shell, private `.env` file, or later in Render environment variables.

Do not add real Supabase URLs, passwords, anon keys, or service-role keys to committed files.

## Which Connection String To Use

Use the safest connection mode for the task:

- Direct connection: preferred for Alembic migrations when available from your network.
- Session pooler: useful when an environment requires IPv4 connectivity or direct connection is blocked.
- Transaction pooler: not preferred for migrations because transaction pooling can conflict with migration behavior, prepared statements, and connection state.

If direct connection fails because of IPv6 or network restrictions, try the session pooler before changing migration code.

## Local PowerShell Migration Test

Run these commands from the repository root after installing backend dependencies:

```powershell
cd backend
.\.venv\Scripts\activate
$env:DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@YOUR_HOST:5432/postgres"
alembic current
alembic upgrade head
```

Pooler placeholder example:

```powershell
$env:DATABASE_URL="postgresql://postgres.YOUR_PROJECT_REF:YOUR_PASSWORD@aws-YOUR_REGION.pooler.supabase.com:5432/postgres"
```

These examples are placeholders. Replace them only in your local shell. Do not commit the resolved values.

Optional non-connection sanity check:

```powershell
python scripts\check_database_url.py
```

The helper reports the configured dialect and masks host and credential details. It does not connect to Supabase.

## Verify Tables

After `alembic upgrade head` succeeds:

1. Open the Supabase Table Editor or SQL editor.
2. Confirm the SetPilot tables exist, including `programs`, `workout_days`, `workout_exercises`, `workout_sessions`, `session_sets`, and `alembic_version`.
3. Confirm no unexpected tables were created.

## Reset Warning

Do not drop Supabase tables casually.

Local SQLite reset is a prototype convenience. A cloud database reset can destroy shared staging data, migration history, and validation evidence. Any destructive migration or manual reset must be reviewed before it is run.

## Troubleshooting

### Password Authentication Failed

- Confirm the database password is correct.
- Confirm special characters in the password are URL-encoded if required.
- Confirm you copied the database password, not a Supabase dashboard login password.
- Rotate the password if it may have been exposed.

### Connection Refused

- Confirm the host and port came from the Supabase **Connect** panel.
- Confirm your network allows outbound PostgreSQL traffic.
- Try the session pooler if direct connection is blocked.

### SSL Issue

- Confirm you are using the connection string format recommended by Supabase.
- Update local dependencies if your PostgreSQL driver or OpenSSL stack is stale.
- Do not disable SSL security casually for cloud validation.

### IPv6 Or Direct Connection Issue

- Some networks and hosting environments have IPv4-only connectivity.
- Use the Supabase session pooler if direct connection is not reachable.
- Keep Alembic migrations on direct connection when possible.

### Pooler Choice Confusion

- Use direct connection first for migrations.
- Use session pooler if direct connection is unavailable.
- Avoid transaction pooler for migrations.

### Wrong DATABASE_URL Format

- `postgresql://...` and `postgres://...` are normalized by the backend to the selected Psycopg driver.
- `postgresql+psycopg://...` is also supported.
- Do not include surrounding quotes inside `.env` values unless your tooling requires them.

### Accidentally Using Transaction Pooler

- Stop before running destructive commands.
- Switch to direct connection or session pooler.
- Re-run `alembic current` before `alembic upgrade head`.

### Alembic Cannot Find Config

- Run Alembic from the `backend` directory.
- Confirm `backend/alembic.ini` exists.
- Confirm dependencies were installed from `backend/requirements.txt`.
- Use `.\.venv\Scripts\activate` before running `alembic` on Windows.
