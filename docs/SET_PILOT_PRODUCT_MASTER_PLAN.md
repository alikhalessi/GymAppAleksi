# SetPilot Product Master Plan

## 1. Brutal Product Diagnosis

SetPilot is already beyond a toy. It can extract messy multilingual workout plans, enhance them with readiness/profile context, save structured programs, attach planned set weights, and connect exercises to YouTube examples.

The strength: SetPilot solves a real pain. Workout plans are usually scattered across WhatsApp, PDFs, screenshots, trainer notes, notebooks, and memory. Turning chaos into an executable program is valuable.

The weakness: the current interface still behaves like an admin panel. It exposes features as forms instead of guiding the user through a training ritual. The app currently asks the user to manage data; the product should help the user train.

The danger: adding more features without a stronger journey will create feature soup. The product will become powerful but exhausting. A user should not feel like they are doing database work before bench press.

The opportunity: SetPilot can become a training cockpit: before training it checks readiness, during training it guides sets/rest/videos, and after training it reflects progress and suggests next actions.

## 2. Core Product Positioning

### One sentence
SetPilot turns any messy workout plan into an AI-assisted, executable, trackable, and adjustable training experience.

### One paragraph
SetPilot helps trainees and trainers convert unstructured workout plans into structured programs, adapt them to readiness and personal limitations, guide each workout session with set-by-set execution, attach technique videos, and learn from performance history over time. It is not just a planner; it is a training companion and coach-support system.

### Investor pitch
Most gym apps assume users already have clean structured programs. Real training life is uglier: plans come as texts, PDFs, trainer messages, mixed-language notes, and incomplete instructions. SetPilot uses AI to turn that chaos into an executable workout system, then supports readiness-based adjustment, session tracking, video guidance, progression logic, and trainer review. The business expands from individual users to trainers and gyms who need scalable program delivery and monitoring.

## 3. Stakeholder Map

### Individual trainee
Needs: clarity, confidence, reminders, progression, technique support, motivation.
Fears: injury, confusion, wasting time, not progressing, being judged.
Value: knows exactly what to do today and why.

### Beginner trainee
Needs: simple guidance, exercise videos, conservative loads, encouragement.
Fears: looking stupid, doing exercises wrong, quitting.
Value: the app feels like a safe buddy.

### Advanced lifter
Needs: control, history, progression, readiness adjustment, PR tracking.
Fears: dumb generic advice, childish gamification, losing control.
Value: the app becomes a serious logbook and progression engine.

### Personal trainer
Needs: client compliance, plan delivery, review, scalable communication.
Fears: AI replacing them, clients modifying plans badly, admin overload.
Value: AI becomes assistant, not competitor. Trainer approves and monitors.

### Gym owner
Needs: retention, member engagement, differentiated services.
Fears: complexity, low adoption, staff resistance.
Value: SetPilot can become a gym-branded training layer.

### Physiotherapist / rehab-aware coach
Needs: limitations, pain notes, conservative adjustments, review flags.
Fears: unsafe AI, overreach, liability.
Value: controlled suggestions with review and transparency.

### Content/video ecosystem
Needs: exercise-video distribution, curated learning.
Fears: low-quality search results.
Value: exercise-level video mapping and trainer-approved libraries.

## 4. Jobs To Be Done

Trainee: “When I go to the gym, help me know exactly what to do, how hard to do it, and what to adjust today.”

Trainer: “When I give clients programs, help me deliver, monitor, and adjust them without drowning in messages.”

Gym: “When members train, help them stay engaged, guided, and retained.”

Rehab-aware coach: “When a client has limitations, help surface risk context and keep changes conservative and reviewable.”

## 5. Trainee User Journey

1. First open: user sees Today’s Training Mission, not a wall of forms.
2. Import: user pastes a messy workout plan.
3. Extraction: AI extracts faithfully without coaching.
4. Review: user sees days/exercises/sets/reps/rest with confidence flags.
5. Save: user saves original extracted version.
6. Readiness check: user enters energy, sleep, soreness, stress, limitations, time.
7. Enhancement: AI proposes changes with explanations.
8. Approval: user accepts, rejects, or edits changes.
9. Session start: user enters workout mode.
10. During session: app shows exercise, set number, target reps, planned weight, rest timer, video support.
11. Logging: user enters actual weight/reps/difficulty.
12. Summary: app reflects performance, missed sets, readiness impact, and next suggestion.
13. Progress: weekly view shows consistency, strength trends, recovery trends, and technique learning.

## 6. Trainer Journey

1. Trainer creates/imports a plan.
2. AI extracts and structures the plan.
3. Trainer reviews confidence flags and corrections.
4. Trainer assigns plan to trainee.
5. Trainee completes readiness checks and sessions.
6. Trainer sees compliance, missed sets, pain notes, readiness trends.
7. Trainer comments or approves AI-suggested progression.
8. Trainer manages multiple clients with less admin.

## 7. Product Architecture

Core modules:

- Onboarding
- Trainee profile
- Readiness check
- Plan import
- AI extraction
- AI enhancement
- Program editor
- Planned set weights
- YouTube/video guidance
- Workout session mode
- Actual set logging
- Session summary
- Progress analytics
- Trainer review
- Chat assistant
- Settings and integrations

Immediate architectural principle: separate planning data from session execution data.

Planning:
- Program
- Workout Day
- Exercise
- Planned Set
- Video Example

Execution:
- Workout Session
- Performed Exercise
- Performed Set
- Actual Weight
- Actual Reps
- Difficulty/RPE
- Notes

## 8. UX Redesign Direction

The app should feel like a training cockpit, not a spreadsheet.

### Main navigation
- Dashboard
- Import
- Enhance
- Programs
- Session
- Progress
- Videos
- Settings

### Dashboard-first layout
The first screen should show:
- Today’s Training Mission
- Current program
- Start workout button
- Readiness snapshot
- Last session result
- Next recommended action

### Import screen
Focused only on:
- paste text
- extract
- review extracted plan
- save original plan

### Enhance screen
Focused only on:
- readiness/profile
- proposed changes
- original vs adjusted comparison
- approve/reject/edit changes

### Session screen
Focused only on:
- current exercise
- current set
- target reps
- planned weight
- actual weight/reps
- rest timer
- video/form support

### Program editor
Should be secondary. Powerful, but not the emotional center.

### Microcopy style
Direct, calm, and slightly sharp. No childish fitness slogans.

Examples:
- “Train the plan, not the chaos.”
- “Low readiness detected. Reduce volume or proceed carefully.”
- “Original plan preserved. Nothing changed without approval.”

## 9. Gamification and Retention System

No childish coins. Serious lifters do not need cartoon fireworks for leg press.

Useful gamification:
- Consistency streak
- Weekly mission completion
- Readiness trend
- Effort score
- Recovery score
- Progressive overload map
- Technique video completion
- Personal records
- Comeback protection after missed sessions
- “Protected muscle week” for fat-loss phases

Retention loop:
1. User plans session.
2. App gives readiness-aware adjustment.
3. User logs performance.
4. App gives useful reflection.
5. Next session becomes smarter.

The app must become more valuable with use.

## 10. AI Companion Design

AI roles:

### Before workout
- readiness check
- explain concerns
- propose adjustments
- preserve original plan

### During workout
- next set guidance
- rest timer
- planned vs actual comparison
- video support
- technique reminders

### After workout
- summarize performance
- identify missed sets
- record difficulty
- suggest next session approach

### Weekly
- analyze trends
- spot fatigue patterns
- show progression
- suggest review points

### Chat
Chat may propose changes, but must never silently mutate the plan. Every change must be reviewable.

## 11. Safety and Trust Rules

AI must not:
- diagnose medical conditions
- give medication advice
- silently change programs
- guarantee safe loads
- shame users based on BMI or weight
- override trainer approval

AI must:
- explain assumptions
- flag uncertainty
- preserve original plans
- request review for pain/limitations/high-risk context
- separate extraction from enhancement

## 12. Business Model

### Free individual tier
- manual programs
- limited imports
- basic videos

### Premium trainee tier
- unlimited AI imports
- readiness enhancement
- session tracking
- progression analytics

### Trainer subscription
- client management
- plan assignment
- review queue
- compliance tracking
- comments

### Gym dashboard
- member engagement
- gym-branded plans
- trainer/client workflows

### White-label version
For gyms, clinics, and coaching businesses.

### Future partnerships
- equipment brands
- fitness content creators
- education/video libraries

## 13. MVP Prioritization

### Current MVP
- AI plan extraction
- readiness enhancement
- program editor
- planned set weights
- YouTube videos

### Next sprint
- dashboard-first layout
- session mode skeleton
- actual set logging
- rest timer

### One-month version
- workout session execution
- session summary
- planned vs actual comparison
- simple progression suggestions

### Three-month version
- program versioning
- chat-based proposed changes
- trainer review prototype
- progress dashboard

### Six-month version
- trainer portal
- client assignment
- analytics
- gym pilot

### Investor-demo version
A polished loop:
Import plan -> enhance -> start workout -> log sets -> get summary -> next-session suggestion.

## 14. Scrum Backlog

### Epic 1: Dashboard-first UX
User story: As a trainee, I want to see today’s workout immediately so I know what to do.
Acceptance criteria:
- Dashboard shows current program, next workout, readiness, start session button.
Priority: P0

### Epic 2: Workout Session Mode
User story: As a trainee, I want set-by-set guidance during training.
Acceptance criteria:
- Start session from selected workout day.
- Show exercises in order.
- Log actual reps/weight.
- Use rest timer.
Priority: P0

### Epic 3: Session Summary
User story: As a trainee, I want feedback after training.
Acceptance criteria:
- Show completed sets.
- Show missed targets.
- Save notes.
- Suggest next action.
Priority: P0

### Epic 4: Program Versioning
User story: As a user, I want original and adjusted plans preserved separately.
Acceptance criteria:
- Imported version remains unchanged.
- Enhanced version saved separately.
- Version label visible.
Priority: P1

### Epic 5: Trainer Review
User story: As a trainer, I want to approve AI changes.
Acceptance criteria:
- Pending changes are visible.
- Trainer can approve/reject/comment.
Priority: P1

### Epic 6: AI Chat Proposals
User story: As a trainee, I want to ask for modifications without losing control.
Acceptance criteria:
- Chat creates proposed changes only.
- User approves before applying.
Priority: P2

## 15. Immediate GUI Redesign Plan

The next implementation must not be another color pass. It must restructure the app.

### Remove from first screen
- API key form
- manual program editor
- raw YouTube tools
- long readiness form

### First screen becomes Dashboard
Sections:
- Today’s Training Mission
- Current Program
- Readiness Snapshot
- Start Session
- Last Session Reflection
- Quick Actions

### Import becomes a tab/screen
Only import/extract/review/save.

### Enhance becomes a tab/screen
Only readiness/profile/proposed changes.

### Programs becomes a tab/screen
Manual editor lives here.

### Exercise Detail becomes a right-side panel
When exercise selected:
- details
- planned sets
- videos
- edit actions

### Settings becomes hidden utility screen
API keys and environment configuration do not belong in the emotional center of the product.

## 16. Final Investor Verdict

SetPilot is investable if it proves that users return for actual workouts, not just import novelty.

The strongest proof needed:
- users complete sessions inside the app
- users log actual sets
- users accept readiness-based changes
- trainers approve client workflows
- progress recommendations improve retention

Biggest risk:
The product becomes a powerful but annoying form machine.

Defensibility:
- multilingual workout extraction
- structured training memory
- readiness/profile adjustment
- trainer approval workflow
- performance history
- serious session execution loop

Investor verdict: promising, but only if the next milestone is session execution. Without session mode, SetPilot is a smart planner. With session mode, it becomes a training operating system.
