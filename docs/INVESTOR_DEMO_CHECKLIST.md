# Investor Demo Checklist

Use this checklist to prepare a short, honest Phase-1 SetPilot walkthrough for investors, advisors, trainers, gyms, or pilot-user conversations.

## Positioning

Say:

- "This is SetPilot, an AI workout operating system."
- "It turns messy workout plans into guided training sessions."
- "The app records reality: reps, weight, difficulty, rest, notes, and completed sessions."
- "After training, SetPilot provides an advisory reflection and progression suggestions."
- "The dashboard becomes training memory."

Do not claim:

- Production SaaS readiness
- Medical-grade recommendations
- Certified trainer replacement
- Cloud deployment
- HIPAA/GDPR compliance
- Payment readiness
- Trainer portal or multi-user mode

## Prepare Before Demo

1. Pull the latest branch for the demo.
2. Run backend tests.
3. Run frontend build.
4. Start backend.
5. Start frontend.
6. Decide whether OpenAI and YouTube keys will be configured.
7. Keep the sample workout plan ready.

Backend:

```powershell
cd backend
.\.venv\Scripts\activate
python -m pytest
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm install
npm run build
npm run dev
```

Open:

```text
http://localhost:5173
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

## Optional API Key Setup

OpenAI powers AI import, enhancement, and session reflection.

In app:

1. Open Settings.
2. Paste the OpenAI key.
3. Save the key for the current backend process.

Backend fallback:

```powershell
cd backend
$env:OPENAI_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

YouTube automatic search uses a backend environment variable:

```powershell
cd backend
$env:YOUTUBE_API_KEY="your_key_here"
uvicorn app.main:app --reload
```

Manual YouTube links work without a YouTube key.

Never commit real API keys.

## Demo Flow Script

### 1. Dashboard

Say:

"SetPilot starts as a training cockpit. The dashboard shows training status, latest workout, readiness, profile context, reflection state, and progression memory."

Show:

- Product positioning
- Quick Actions
- Training Status
- Recent Sessions if available

If database is empty:

- Use the cold-start card.
- Explain that the app does not auto-create fake demo data.

### 2. Import

Say:

"The user starts with messy workout text. SetPilot uses AI to extract structure, but it does not silently optimize or mutate the plan."

Show:

- Load sample workout plan
- Editable raw text area
- Extract plan
- Extracted plan preview
- Save extracted plan to Programs

### 3. Profile

Say:

"Profile is stable context. It helps future enhancement, but it is not a diagnosis and it does not change plans automatically."

Show:

- Training experience
- Primary goal
- Equipment
- Limitations
- BMI as context only

### 4. Readiness

Say:

"Readiness is today's context. It captures energy, sleep, soreness, stress, time, and limitations before training."

Show:

- Readiness form
- Score display
- Use in Enhance path

### 5. Enhance

Say:

"Profile and readiness are separate layers. Enhancement is an optional proposal. The original plan is preserved."

Show:

- Use saved profile
- Use latest readiness
- Enhance plan
- Adjusted plan preview
- Save adjusted plan only after review

### 6. Training

Say:

"Inside training, the app guides from the plan but records reality."

Show:

- Select program
- Select workout day
- Select exercise
- Start Session
- Current exercise
- Next set guidance
- Log actual reps, weight, difficulty, and notes
- Rest timer
- Finish Session

### 7. Session Detail

Say:

"Session history is readable. It keeps snapshots of the exercise, workout day, program, planned reps, weight, and actual performance."

Show:

- Recent Sessions
- View details
- Logged sets
- Session summary

### 8. Reflection And Progression

Say:

"After the session, AI can reflect if OpenAI is configured. Rule-based progression suggests next steps. Both are advisory. The plan is never silently changed."

Show:

- Generate AI reflection if key is configured
- Generate progression suggestions
- Advisory copy

### 9. Dashboard Memory

Say:

"The dashboard becomes training memory. It summarizes what has happened and points to the next useful action."

Show:

- Completed Sessions
- Completed Sets
- Average Difficulty
- Latest Workout
- Latest Reflection
- Next Session Suggestions

## Known Limitations To Say Out Loud

- This is a Phase-1 local MVP.
- It is an investor-demo ready local prototype, not production deployment.
- Local data uses SQLite.
- OpenAI features require a configured OpenAI key.
- YouTube search requires backend `YOUTUBE_API_KEY`.
- AI is advisory and can be wrong.
- SetPilot is not medical advice.
- No authentication, payments, cloud deployment, trainer portal, or mobile app yet.

## Recovery Lines

If OpenAI key is missing:

"This local demo can run without AI keys. The import, enhancement, and reflection layers use OpenAI when configured; otherwise the app shows a readable setup message."

If YouTube key is missing:

"Automatic YouTube search requires a backend key. Manual video links still work."

If dashboard already has old local data:

"This is local SQLite demo data. We can reset it by deleting `backend/setpilot.db`, but auto-seeding is intentionally not part of Phase 1."

## Links

- [Phase-1 MVP demo flow](PHASE_1_MVP_DEMO_FLOW.md)
- [Demo sample workout plan](DEMO_SAMPLE_WORKOUT_PLAN.md)
- [Phase-1 MVP validation report](PHASE_1_MVP_VALIDATION_REPORT.md)
- [Developer guide](DEVELOPER_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING.md)
