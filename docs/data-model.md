# Data Model

This is the proposed local MVP data model. The local implementation should use SQLite with SQLAlchemy. The model should stay compatible with a future PostgreSQL migration.

## Entity Overview

Core tables required for the MVP:

- `users`
- `programs`
- `workout_days`
- `exercises`
- `program_exercises`
- `youtube_videos`
- `workout_sessions`
- `session_sets`

## Tables

### users

Stores local user identity. Authentication is out of scope for the MVP, but a user table keeps ownership relationships ready for future auth.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Local user id |
| display_name | string | Required |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One user has many programs.
- One user has many workout sessions.

### programs

Stores workout programs.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Program id |
| user_id | foreign key users.id | Required |
| name | string | Required |
| description | text | Optional |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One program belongs to one user.
- One program has many workout days.
- One program has many workout sessions.

### workout_days

Stores days within a program.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Workout day id |
| program_id | foreign key programs.id | Required |
| name | string | Required |
| sort_order | integer | Required, default 0 |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One workout day belongs to one program.
- One workout day has many program exercises.
- One workout day has many workout sessions.

### exercises

Stores reusable exercise movements.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Exercise id |
| movement_name | string | Required |
| notes | text | Optional |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One exercise can appear in many program exercises.
- One exercise can have many YouTube videos, with an MVP limit of 5.
- One exercise can have many session sets.

### program_exercises

Stores the planned prescription of an exercise inside a workout day.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Program exercise id |
| workout_day_id | foreign key workout_days.id | Required |
| exercise_id | foreign key exercises.id | Required |
| planned_sets | integer | Required, greater than 0 |
| planned_reps | string | Required, supports values like `8`, `8-10`, or `AMRAP` |
| rest_seconds | integer | Required, greater than or equal to 0 |
| notes | text | Optional |
| sort_order | integer | Required, default 0 |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One program exercise belongs to one workout day.
- One program exercise references one reusable exercise.
- One program exercise can produce many session sets over time.

### youtube_videos

Stores curated YouTube examples for exercises.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Video id |
| exercise_id | foreign key exercises.id | Required |
| title | string | Optional |
| channel_name | string | Optional |
| url | string | Required |
| sort_order | integer | Required, default 0 |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Rules:

- Each exercise can have up to 5 YouTube videos.
- URLs should be validated before saving.
- Videos are curated by the user or app content, not AI-generated.

Relationships:

- One YouTube video belongs to one exercise.

### workout_sessions

Stores an executed workout session.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Session id |
| user_id | foreign key users.id | Required |
| program_id | foreign key programs.id | Required |
| workout_day_id | foreign key workout_days.id | Required |
| started_at | datetime | Required |
| finished_at | datetime | Optional until session is completed |
| duration_seconds | integer | Optional until session is completed |
| status | string | Required, suggested values: `active`, `completed`, `cancelled` |
| notes | text | Optional |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One workout session belongs to one user.
- One workout session belongs to one program.
- One workout session belongs to one workout day.
- One workout session has many session sets.

### session_sets

Stores actual set performance during a workout session.

| Column | Type | Notes |
| --- | --- | --- |
| id | integer primary key | Session set id |
| workout_session_id | foreign key workout_sessions.id | Required |
| program_exercise_id | foreign key program_exercises.id | Required |
| exercise_id | foreign key exercises.id | Required denormalized reference for simpler progress queries |
| set_number | integer | Required |
| actual_weight | numeric | Optional |
| actual_reps | integer | Optional |
| difficulty_rating | integer | Optional, suggested 1 to 10 |
| completed_at | datetime | Required when set is completed |
| notes | text | Optional |
| created_at | datetime | Required |
| updated_at | datetime | Required |

Relationships:

- One session set belongs to one workout session.
- One session set references the planned program exercise.
- One session set references the reusable exercise.

## Suggested Indexes

- `programs.user_id`
- `workout_days.program_id`
- `program_exercises.workout_day_id`
- `program_exercises.exercise_id`
- `youtube_videos.exercise_id`
- `workout_sessions.user_id`
- `workout_sessions.program_id`
- `workout_sessions.workout_day_id`
- `session_sets.workout_session_id`
- `session_sets.exercise_id`

## Progress Calculation Notes

Basic MVP calculations can be derived from `session_sets`:

- Set volume: `actual_weight * actual_reps` when both values exist.
- Exercise session volume: sum of set volume by exercise and session.
- Best weight: max `actual_weight` by exercise.
- Latest performance: most recent completed `workout_sessions` joined through `session_sets`.
- Difficulty trend: compare average `difficulty_rating` for an exercise across recent sessions.

