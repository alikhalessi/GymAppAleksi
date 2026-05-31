# Sprint Plan

## Sprint 0: Repository And Product Foundation

Goal: Establish a clear product and technical foundation before implementation.

Deliverables:

- README
- AGENTS instructions
- Product vision
- MVP scope
- Sprint plan
- User stories
- Proposed data model
- Architecture notes
- Useful prompts for future Codex work

Definition of Done:

- Documentation explains what SetPilot is.
- MVP boundaries are clear.
- Future agents know what not to build yet.
- Data model includes the required core tables.

## Sprint 1: Project Scaffolding

Goal: Create the minimal frontend and backend project structure without building full features.

Planned work:

- Initialize React + Vite + TypeScript frontend.
- Initialize FastAPI backend.
- Add basic local development instructions.
- Add formatting and linting conventions where practical.
- Add health check endpoint.
- Add a placeholder frontend route.

Definition of Done:

- Frontend dev server can run.
- Backend dev server can run.
- README contains setup commands.
- No production feature workflows are implemented yet.

## Sprint 2: Program Builder MVP

Goal: Let users define workout programs, workout days, and exercise prescriptions.

Planned work:

- Create SQLAlchemy models and migrations or initial schema.
- Add CRUD endpoints for programs.
- Add CRUD endpoints for workout days.
- Add CRUD endpoints for exercises and program exercises.
- Build frontend screens for creating and editing programs.
- Add basic validation for sets, reps, and rest seconds.

Definition of Done:

- User can create a program.
- User can add workout days.
- User can add exercises to workout days.
- Data persists in SQLite.

## Sprint 3: YouTube Examples And Session Start

Goal: Add curated exercise videos and let users start workout sessions.

Planned work:

- Add YouTube video storage for exercises.
- Enforce up to 5 stored videos per exercise.
- Show exercise examples in the workout day view.
- Create workout session records.
- Show the active workout session screen.

Definition of Done:

- Exercise examples can be stored and viewed.
- A workout session can be started from a workout day.
- Session state is persisted.

## Sprint 4: Set Tracking And Timers

Goal: Support the core in-gym workout execution flow.

Planned work:

- Add set completion workflow.
- Save actual weight, reps, and difficulty rating per set.
- Add workout timer.
- Add rest timer.
- Support finishing a workout session.

Definition of Done:

- User can complete planned sets.
- User can record performance per set.
- User can use workout and rest timers.
- Session can be finished cleanly.

## Sprint 5: Summary And Basic Progress

Goal: Show useful post-session feedback and basic progress analysis.

Planned work:

- Build post-session summary screen.
- Calculate total duration and total volume.
- Show per-exercise summaries.
- Add basic progress comparison against previous sessions.
- Add simple tests for summary calculations.

Definition of Done:

- User sees a clear summary after finishing a session.
- User can inspect basic progress for exercises.
- Summary calculations are covered by tests.

