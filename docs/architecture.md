# Architecture

## Overview

SetPilot should start as a local MVP with a React frontend, FastAPI backend, and SQLite database. The architecture should stay simple and easy to migrate toward PostgreSQL later.

## Planned Stack

Frontend:

- React
- Vite
- TypeScript
- Recharts later for progress charts

Backend:

- FastAPI
- SQLAlchemy
- SQLite for local MVP
- PostgreSQL later

Authentication:

- Not included in Sprint 0 or the initial MVP implementation.
- The data model includes `users` to prepare for future ownership and authentication.

## Proposed Repository Layout For Future Sprints

This layout is not created in Sprint 0 unless implementation begins in a future sprint.

```text
.
├── frontend
│   ├── src
│   └── package.json
├── backend
│   ├── app
│   │   ├── api
│   │   ├── models
│   │   ├── schemas
│   │   ├── services
│   │   └── main.py
│   └── pyproject.toml
├── docs
└── README.md
```

## Backend Responsibilities

- Persist programs, workout days, exercises, videos, sessions, and set records.
- Validate core business rules.
- Provide APIs for frontend workflows.
- Calculate or provide data for post-session summaries and basic progress analysis.

Important backend rules:

- Enforce maximum 5 YouTube videos per exercise.
- Validate positive planned set counts.
- Validate non-negative rest seconds.
- Validate difficulty rating range.
- Keep session status explicit.

## Frontend Responsibilities

- Provide program creation and editing flows.
- Provide active workout execution UI.
- Provide workout and rest timers.
- Provide fast set entry during workouts.
- Show curated YouTube examples.
- Show post-session summary and basic progress views.

## API Shape

The exact API should be defined during implementation, but likely resource groups are:

- `/programs`
- `/programs/{program_id}/workout-days`
- `/workout-days/{workout_day_id}/exercises`
- `/exercises`
- `/exercises/{exercise_id}/youtube-videos`
- `/workout-sessions`
- `/workout-sessions/{session_id}/sets`
- `/progress/exercises/{exercise_id}`

## Data Flow

1. User creates a program.
2. User adds workout days.
3. User adds exercise prescriptions to workout days.
4. User optionally stores YouTube examples for exercises.
5. User starts a workout session from a workout day.
6. User completes sets and records performance.
7. Backend stores session set records.
8. User finishes the session.
9. App displays summary and basic progress analysis.

## Local MVP Constraints

- Optimize for clarity over abstraction.
- Keep business logic testable outside route handlers.
- Avoid premature production infrastructure.
- Avoid authentication until it is explicitly planned.
- Avoid AI-generated workout planning.

## Future Production Considerations

- PostgreSQL migration.
- Authentication and user accounts.
- Hosted backend and frontend deployment.
- More robust media validation.
- Deeper analytics and charts.
- Data export.

