# SetPilot Backend

FastAPI backend scaffold for SetPilot.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000` by default.

## Health Check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Program Endpoints

- `POST /programs`
- `GET /programs`
- `GET /programs/{program_id}`
- `PUT /programs/{program_id}`
- `DELETE /programs/{program_id}`

Program fields:

- `id`
- `name`
- `goal`
- `duration_weeks`
- `created_at`
