# Codex Prompts

Use these prompts in future work to keep SetPilot changes focused.

## Repository Orientation

```text
You are working in the SetPilot repository. Read README.md, AGENTS.md, and the relevant docs before making changes. Confirm the current sprint in docs/sprint-plan.md. Keep changes small and do not build features outside the current sprint.
```

## Sprint 1 Scaffolding

```text
Create the initial React + Vite + TypeScript frontend and FastAPI backend scaffolding for SetPilot. Do not build product features yet. Add only a frontend placeholder route, a backend health check endpoint, and setup instructions. Do not add authentication, payments, trainer features, smartwatch sync, nutrition, or AI workout planning.
```

## Program Builder

```text
Implement the SetPilot program builder MVP from docs/user-stories.md. Start with programs, workout days, exercises, and program_exercises. Use FastAPI, SQLAlchemy, and SQLite. Keep the UI simple and focused on creating and editing structured workout plans.
```

## YouTube Examples

```text
Add curated YouTube examples for exercises. Each exercise can store up to 5 videos. Validate URLs before saving. Do not generate videos or recommendations with AI.
```

## Workout Session

```text
Implement workout session execution for SetPilot. A user should be able to start a session from a workout day, view planned exercises, complete sets, and save actual weight, reps, and difficulty rating per set. Keep the workflow optimized for use during a gym session.
```

## Timers

```text
Add workout and rest timers to the active session experience. The workout timer starts with the session. The rest timer should use the planned rest seconds from the current exercise prescription and support start, stop, and reset.
```

## Summary And Progress

```text
Add post-session summary and basic progress analysis. Show completed exercises, completed sets, duration, total volume, latest versus previous session comparison, best recorded weight, and basic difficulty trend. Keep calculations simple and testable.
```

## Guardrail Prompt

```text
Before implementing, check whether the requested change is in MVP scope. Do not add authentication, payments, trainer dashboard, smartwatch sync, nutrition, AI-generated workout planning, social features, or advanced analytics unless the sprint plan has been updated to include them.
```

