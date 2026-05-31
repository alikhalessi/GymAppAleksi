# AGENTS.md

This file defines rules for future Codex agents working in the SetPilot repository.

## Product Context

SetPilot is a gym workout execution app. It helps users follow structured workout programs, view curated YouTube examples for exercises, manage workout and rest timers, record set performance, and review post-session progress.

Target users are beginner-to-intermediate gym users who already have or want a structured workout plan and need help executing it consistently.

## Current Phase

This repository is in Sprint 0 unless the sprint documentation has been explicitly updated.

Sprint 0 is documentation and planning only. Do not build production app features during Sprint 0.

## Technical Direction

- Frontend: React + Vite + TypeScript
- Backend: FastAPI
- Local MVP database: SQLite with SQLAlchemy
- Future production database: PostgreSQL
- Charts later: Recharts
- Authentication later

## Repository Rules

- Keep changes small, understandable, and scoped to the user request.
- Prefer documentation and planning changes until app scaffolding is explicitly requested.
- Do not install dependencies unless explicitly asked.
- Do not create frontend or backend app code during Sprint 0 unless a placeholder is required and approved.
- Do not introduce AI-generated workout planning in the MVP foundation.
- Do not add payment, trainer dashboard, smartwatch sync, or nutrition features.
- Keep the MVP focused on workout execution, set tracking, timers, curated YouTube examples, session summary, and basic progress analysis.
- Preserve user changes. Do not revert files you did not modify unless explicitly instructed.
- When editing existing files, follow the structure and tone already present.

## Suggested Future Workflow

1. Read `README.md` and the relevant file in `docs/` before changing code.
2. Check the current sprint in `docs/sprint-plan.md`.
3. Confirm whether the requested work belongs in the current sprint.
4. Make the smallest useful change.
5. Update documentation when product behavior, architecture, or data shape changes.
6. Run relevant tests once tests exist.
7. Summarize exactly which files changed.

## MVP Boundaries

Allowed MVP areas:

- Programs
- Workout days
- Exercises
- Program exercise prescription
- Curated YouTube exercise examples
- Workout sessions
- Set completion
- Workout timer
- Rest timer
- Per-set weight, reps, and difficulty rating
- Post-session summary
- Basic progress analysis

Out of scope until explicitly planned:

- Authentication
- Payments
- Trainer dashboard
- Smartwatch sync
- Nutrition tracking
- AI-generated workout plans
- Social features
- Marketplace features
- Advanced analytics

