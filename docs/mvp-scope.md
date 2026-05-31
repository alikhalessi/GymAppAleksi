# MVP Scope

## MVP Goal

The MVP should prove that SetPilot can help a user follow a structured gym workout, understand exercises through stored YouTube examples, record set performance, and review basic progress after a session.

## Included Features

### Program Creation

Users can create workout programs with a name and optional description.

### Workout Days

Users can add workout days to a program, such as Push Day, Pull Day, Legs, Upper, Lower, or Day 1.

### Exercise Prescription

Users can add exercises to workout days with:

- Movement name
- Planned sets
- Planned reps
- Rest seconds
- Notes

### YouTube Examples

Each exercise can have up to 5 stored YouTube video examples. These are curated links stored in the app, not generated dynamically.

### Workout Session

Users can start a workout session from a workout day.

During a session, users can:

- View the planned exercises.
- Complete sets.
- Record actual weight.
- Record actual reps.
- Record difficulty rating.
- Use a workout timer.
- Use a rest timer between sets.

### Post-Session Summary

After finishing a session, users can see:

- Completed exercises.
- Completed sets.
- Total workout duration.
- Total volume where weight is available.
- Per-exercise performance summary.

### Basic Progress Analysis

Users can see simple progress signals, such as:

- Last session versus previous session for an exercise.
- Estimated volume trend.
- Best recorded weight for an exercise.
- Difficulty rating trend at a basic level.

## Explicitly Out Of Scope

- Authentication and account management
- Payment or subscription features
- Trainer dashboard
- Smartwatch sync
- Nutrition tracking
- AI-generated workout plans
- AI-generated exercise recommendations
- Social sharing
- Multi-user coaching workflows
- Advanced periodization tools
- Advanced analytics dashboards

## MVP Success Criteria

- A user can define a simple program.
- A user can execute a workout from that program.
- A user can track set performance during the workout.
- A user can use rest timing while training.
- A user can review what happened after the session.
- The system has a clear path from SQLite local MVP to PostgreSQL production later.

