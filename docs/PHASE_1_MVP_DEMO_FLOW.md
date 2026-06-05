# Phase-1 MVP Demo Flow

This guide shows the reliable local demo path for SetPilot's Phase-1 MVP.

The demo loop is:

Open app -> load sample plan -> AI extract -> save plan -> add profile/readiness if useful -> enhance plan if an OpenAI key exists -> start workout -> log sets -> use rest timer -> finish session -> view session detail -> generate reflection/progression if available -> confirm dashboard updates.

## 1. Start The Backend

From the repository root:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

Health check:

```powershell
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

## 2. Start The Frontend

Open a second terminal from the repository root:

```powershell
cd frontend
npm run dev
```

Open the Vite URL, usually:

```text
http://127.0.0.1:5173
```

## 3. Configure Optional AI And Video Keys

AI import, AI enhancement, and AI session reflection require an OpenAI key.

In the app:

1. Open **Settings**.
2. Paste the OpenAI key into the OpenAI access card.
3. Click **Save key**.
4. Click **Check** if you want to confirm the masked key status.

Backend environment fallback:

```powershell
cd backend
$env:OPENAI_API_KEY="your_openai_key_here"
uvicorn app.main:app --reload
```

YouTube automatic search requires a backend environment key:

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_youtube_key_here"
uvicorn app.main:app --reload
```

Manual YouTube links do not require a YouTube key.

Do not commit real API keys.

## 4. Load The Sample Plan

The sample plan lives at:

- [DEMO_SAMPLE_WORKOUT_PLAN.md](DEMO_SAMPLE_WORKOUT_PLAN.md)

In the app:

1. Open **Import**.
2. Click **Load sample workout plan**.
3. Confirm the text area fills.
4. Edit one line manually to confirm the user remains in control.
5. Click **Extract plan** if an OpenAI key is configured.
6. Review the extracted plan preview.
7. Click **Save extracted plan to Programs**.

The app should return to the dashboard and show a saved-plan handoff with links to Training and Programs.

## 5. Optional Profile And Readiness Context

Profile:

1. Open **Profile**.
2. Add basic training context, limitations, equipment, and preferred session time.
3. Save the profile.

Readiness:

1. Open **Readiness**.
2. Add energy, sleep, soreness, stress, pain/limitations, and available time.
3. Save readiness.

Enhancement:

1. Open **Enhance**.
2. Use saved profile or latest readiness if available.
3. Click **Enhance plan** if an OpenAI key is configured.
4. Review the adjusted plan.
5. Save the adjusted plan only if you want to create a reviewed version.

The original imported plan remains preserved. The app must not mutate workout plans silently.

## 6. Run A Workout Session

1. Open **Training**.
2. Select the saved program.
3. Select a workout day.
4. Select the first exercise.
5. Click **Start Session**.
6. Log at least two sets:
   - set number
   - actual reps
   - actual weight
   - difficulty 1-10
   - notes if useful
7. Use the rest timer after a logged set.
8. Click **Finish Session**.

## 7. Review Session Detail

1. Open **Dashboard**.
2. Confirm Training Status metrics update.
3. Open a recent or latest session detail.
4. Review logged sets, status, notes, and average difficulty.
5. If the session is completed and OpenAI is configured, click **Generate AI reflection**.
6. Click **Generate progression suggestions** to create advisory next-session suggestions.

Progression suggestions are advisory and do not modify the workout plan.

## Troubleshooting

### Backend Unreachable

Symptoms:

- Frontend shows backend unreachable.
- Program, import, session, profile, or readiness calls fail.

Fix:

```powershell
cd backend
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

Confirm:

```powershell
curl http://127.0.0.1:8000/health
```

### OpenAI Key Missing

Symptoms:

- Import, enhancement, or AI reflection says an OpenAI key is required.

Fix:

- Save a key in **Settings**, or set `OPENAI_API_KEY` in the backend environment and restart the backend.

### YouTube Key Missing

Symptoms:

- Automatic YouTube search is unavailable or returns a key/configuration error.

Fix:

- Set `YOUTUBE_API_KEY` in the backend environment and restart the backend.
- Manual YouTube video entry still works without this key.

### Local SQLite Reset

Use this only when local prototype data or schema drift blocks the demo.

```powershell
cd backend
Remove-Item .\setpilot.db
uvicorn app.main:app --reload
```

The app does not auto-seed demo data. Resetting SQLite deletes local demo/user data.

### Backend Tests

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest
```

### Frontend Build

```powershell
cd frontend
npm run build
```

## Demo Completion Checklist

- Backend health endpoint returns ok.
- Frontend opens.
- Import screen loads the sample plan on button click.
- User can edit the sample before analysis.
- Extracted plan can be reviewed and saved.
- Training session can be started.
- At least two sets can be logged.
- Rest timer can be started.
- Session can be finished.
- Dashboard metrics update.
- Session detail shows logged sets.
- AI reflection works when an OpenAI key is configured.
- Progression suggestions can be generated for a completed session.
