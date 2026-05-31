# User Stories

## Epic 1: Program Management

### Story 1.1: Create Workout Program

As a gym user, I want to create a workout program so that I can organize my training plan.

Acceptance criteria:

- User can enter a program name.
- User can optionally enter a description.
- Program is saved locally.
- Program appears in the list of available programs.

### Story 1.2: Add Workout Day

As a gym user, I want to add workout days to a program so that I can split training by day or focus area.

Acceptance criteria:

- User can add a workout day to an existing program.
- User can name the workout day.
- Workout day belongs to exactly one program.
- Workout days can be ordered within a program.

## Epic 2: Exercise Prescription

### Story 2.1: Create Exercise

As a gym user, I want to create an exercise by movement name so that I can reuse it in workout plans.

Acceptance criteria:

- User can create an exercise with a movement name.
- Movement name is required.
- Exercise can store optional notes.
- Exercise can be reused across programs and workout days.

### Story 2.2: Add Exercise To Workout Day

As a gym user, I want to add an exercise prescription to a workout day so that I know what to perform in the gym.

Acceptance criteria:

- User can select or create an exercise.
- User can define planned sets.
- User can define planned reps.
- User can define rest seconds.
- User can add optional notes for that prescription.
- Exercise prescriptions can be ordered within a workout day.

## Epic 3: Curated YouTube Examples

### Story 3.1: Store YouTube Examples

As a gym user, I want to store YouTube examples for an exercise so that I can review movement demonstrations.

Acceptance criteria:

- User can add a YouTube URL to an exercise.
- User can optionally add a title and channel name.
- Each exercise can have no more than 5 stored YouTube examples.
- Invalid or empty URLs are rejected.

### Story 3.2: View YouTube Examples During Workout

As a gym user, I want to see stored YouTube examples while viewing an exercise so that I can understand how to perform it.

Acceptance criteria:

- Exercise detail shows up to 5 stored examples.
- Examples are associated with the correct exercise.
- User can open a stored video link.

## Epic 4: Workout Session Execution

### Story 4.1: Start Workout Session

As a gym user, I want to start a workout session from a workout day so that I can track performance while training.

Acceptance criteria:

- User can start a session from a workout day.
- Session records start time.
- Session is linked to the selected program and workout day.
- Active session shows planned exercises.

### Story 4.2: Complete Set

As a gym user, I want to complete sets one by one so that I can track workout progress in real time.

Acceptance criteria:

- User can mark a set as completed.
- Completed set stores exercise reference.
- Completed set stores set number.
- Completed sets remain visible in the active session.

### Story 4.3: Record Set Performance

As a gym user, I want to save weight, reps, and difficulty per set so that I can analyze training progress.

Acceptance criteria:

- User can enter actual weight.
- User can enter actual reps.
- User can enter difficulty rating.
- Difficulty rating is constrained to an agreed range.
- Data is saved to the session set record.

## Epic 5: Timers

### Story 5.1: Use Workout Timer

As a gym user, I want a workout timer so that I know how long the session has been running.

Acceptance criteria:

- Timer starts when the workout session starts.
- Timer continues while the session is active.
- Final duration is saved when the session is finished.

### Story 5.2: Use Rest Timer

As a gym user, I want a rest timer after completing a set so that I can follow planned rest periods.

Acceptance criteria:

- Rest timer can use the exercise prescription rest seconds.
- User can start, stop, or reset the rest timer.
- Rest timer is available during active workout sessions.

## Epic 6: Summary And Progress

### Story 6.1: View Post-Session Summary

As a gym user, I want a summary after finishing a workout so that I can review what I completed.

Acceptance criteria:

- Summary shows completed exercises.
- Summary shows completed sets.
- Summary shows total duration.
- Summary shows total volume where weight and reps are available.

### Story 6.2: View Basic Progress Analysis

As a gym user, I want to compare recent performance so that I can understand whether I am improving.

Acceptance criteria:

- User can view recent performance for an exercise.
- System can compare the latest completed session against a previous session.
- System can show basic volume change.
- System can show best recorded weight for an exercise.

