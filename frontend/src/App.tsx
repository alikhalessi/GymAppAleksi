import { FormEvent, useEffect, useMemo, useState } from "react";
import "./App.css";

type Program = {
  id: number;
  name: string;
  goal: string;
  duration_weeks: number;
  created_at: string;
};

type WorkoutDay = {
  id: number;
  program_id: number;
  name: string;
  day_order: number;
  created_at: string;
};

type WorkoutExercise = {
  id: number;
  workout_day_id: number;
  movement_name: string;
  sets: number;
  reps: string;
  rest_seconds: number;
  notes: string;
  exercise_order: number;
  created_at: string;
};

type ProgramFormState = {
  name: string;
  goal: string;
  duration_weeks: string;
};

type WorkoutDayFormState = {
  name: string;
  day_order: string;
};

type ExerciseFormState = {
  movement_name: string;
  sets: string;
  reps: string;
  rest_seconds: string;
  notes: string;
  exercise_order: string;
};

const API_BASE_URL = "http://127.0.0.1:8000";

const emptyProgramForm: ProgramFormState = {
  name: "",
  goal: "",
  duration_weeks: "8",
};

const emptyWorkoutDayForm: WorkoutDayFormState = {
  name: "",
  day_order: "1",
};

const emptyExerciseForm: ExerciseFormState = {
  movement_name: "",
  sets: "3",
  reps: "8-10",
  rest_seconds: "90",
  notes: "",
  exercise_order: "1",
};

const dashboardItems = [
  { label: "My Programs", description: "Create and manage plans" },
  { label: "Workout Days", description: "Build weekly structure" },
  { label: "Exercises", description: "Attach movements to days" },
  { label: "Progress", description: "Analysis comes after sessions" },
];

function App() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [programForm, setProgramForm] = useState<ProgramFormState>(emptyProgramForm);
  const [editingProgramId, setEditingProgramId] = useState<number | null>(null);
  const [selectedProgramId, setSelectedProgramId] = useState<number | null>(null);

  const [workoutDays, setWorkoutDays] = useState<WorkoutDay[]>([]);
  const [workoutDayForm, setWorkoutDayForm] = useState<WorkoutDayFormState>(emptyWorkoutDayForm);
  const [editingWorkoutDayId, setEditingWorkoutDayId] = useState<number | null>(null);
  const [selectedWorkoutDayId, setSelectedWorkoutDayId] = useState<number | null>(null);

  const [exercises, setExercises] = useState<WorkoutExercise[]>([]);
  const [exerciseForm, setExerciseForm] = useState<ExerciseFormState>(emptyExerciseForm);
  const [editingExerciseId, setEditingExerciseId] = useState<number | null>(null);

  const [isLoadingPrograms, setIsLoadingPrograms] = useState(false);
  const [isLoadingWorkoutDays, setIsLoadingWorkoutDays] = useState(false);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditingProgram = editingProgramId !== null;
  const isEditingWorkoutDay = editingWorkoutDayId !== null;
  const isEditingExercise = editingExerciseId !== null;

  const selectedProgram = useMemo(
    () => programs.find((program) => program.id === selectedProgramId) ?? null,
    [programs, selectedProgramId],
  );

  const selectedWorkoutDay = useMemo(
    () => workoutDays.find((day) => day.id === selectedWorkoutDayId) ?? null,
    [workoutDays, selectedWorkoutDayId],
  );

  async function loadPrograms() {
    setIsLoadingPrograms(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs`);
      if (!response.ok) throw new Error("Could not load programs from the backend.");
      const data = (await response.json()) as Program[];
      setPrograms(data);
      setSelectedProgramId((current) => {
        if (current && data.some((program) => program.id === current)) return current;
        return data[0]?.id ?? null;
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unexpected error while loading programs.");
    } finally {
      setIsLoadingPrograms(false);
    }
  }

  async function loadWorkoutDays(programId: number) {
    setIsLoadingWorkoutDays(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}/workout-days`);
      if (!response.ok) throw new Error("Could not load workout days for this program.");
      const data = (await response.json()) as WorkoutDay[];
      setWorkoutDays(data);
      setSelectedWorkoutDayId((current) => {
        if (current && data.some((day) => day.id === current)) return current;
        return data[0]?.id ?? null;
      });
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unexpected error while loading workout days.");
    } finally {
      setIsLoadingWorkoutDays(false);
    }
  }

  async function loadExercises(programId: number, workoutDayId: number) {
    setIsLoadingExercises(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}/workout-days/${workoutDayId}/exercises`);
      if (!response.ok) throw new Error("Could not load exercises for this workout day.");
      const data = (await response.json()) as WorkoutExercise[];
      setExercises(data);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Unexpected error while loading exercises.");
    } finally {
      setIsLoadingExercises(false);
    }
  }

  useEffect(() => {
    void loadPrograms();
  }, []);

  useEffect(() => {
    if (selectedProgramId === null) {
      setWorkoutDays([]);
      setSelectedWorkoutDayId(null);
      setExercises([]);
      return;
    }
    void loadWorkoutDays(selectedProgramId);
  }, [selectedProgramId]);

  useEffect(() => {
    if (selectedProgramId === null || selectedWorkoutDayId === null) {
      setExercises([]);
      return;
    }
    void loadExercises(selectedProgramId, selectedWorkoutDayId);
  }, [selectedProgramId, selectedWorkoutDayId]);

  function resetProgramForm() {
    setProgramForm(emptyProgramForm);
    setEditingProgramId(null);
  }

  function resetWorkoutDayForm() {
    setWorkoutDayForm(emptyWorkoutDayForm);
    setEditingWorkoutDayId(null);
  }

  function resetExerciseForm() {
    setExerciseForm(emptyExerciseForm);
    setEditingExerciseId(null);
  }

  async function handleProgramSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const payload = {
      name: programForm.name.trim(),
      goal: programForm.goal.trim(),
      duration_weeks: Number(programForm.duration_weeks),
    };

    if (!payload.name || !payload.goal || Number.isNaN(payload.duration_weeks)) {
      setError("Program name, goal, and duration are required.");
      return;
    }

    const url = isEditingProgram ? `${API_BASE_URL}/programs/${editingProgramId}` : `${API_BASE_URL}/programs`;

    try {
      const response = await fetch(url, {
        method: isEditingProgram ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Could not save the program.");
      const savedProgram = (await response.json()) as Program;
      resetProgramForm();
      setSelectedProgramId(savedProgram.id);
      await loadPrograms();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unexpected error while saving program.");
    }
  }

  async function handleWorkoutDaySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (selectedProgramId === null) {
      setError("Create or select a program before adding workout days.");
      return;
    }

    const payload = {
      name: workoutDayForm.name.trim(),
      day_order: Number(workoutDayForm.day_order),
    };

    if (!payload.name || Number.isNaN(payload.day_order)) {
      setError("Workout day name and order are required.");
      return;
    }

    const url = isEditingWorkoutDay
      ? `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${editingWorkoutDayId}`
      : `${API_BASE_URL}/programs/${selectedProgramId}/workout-days`;

    try {
      const response = await fetch(url, {
        method: isEditingWorkoutDay ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Could not save the workout day.");
      const savedDay = (await response.json()) as WorkoutDay;
      resetWorkoutDayForm();
      setSelectedWorkoutDayId(savedDay.id);
      await loadWorkoutDays(selectedProgramId);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unexpected error while saving workout day.");
    }
  }

  async function handleExerciseSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (selectedProgramId === null || selectedWorkoutDayId === null) {
      setError("Select a program and workout day before adding exercises.");
      return;
    }

    const payload = {
      movement_name: exerciseForm.movement_name.trim(),
      sets: Number(exerciseForm.sets),
      reps: exerciseForm.reps.trim(),
      rest_seconds: Number(exerciseForm.rest_seconds),
      notes: exerciseForm.notes.trim(),
      exercise_order: Number(exerciseForm.exercise_order),
    };

    if (!payload.movement_name || !payload.reps || Number.isNaN(payload.sets) || Number.isNaN(payload.rest_seconds) || Number.isNaN(payload.exercise_order)) {
      setError("Exercise name, sets, reps, rest, and order are required.");
      return;
    }

    const url = isEditingExercise
      ? `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${editingExerciseId}`
      : `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises`;

    try {
      const response = await fetch(url, {
        method: isEditingExercise ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) throw new Error("Could not save the exercise.");
      resetExerciseForm();
      await loadExercises(selectedProgramId, selectedWorkoutDayId);
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "Unexpected error while saving exercise.");
    }
  }

  function startEditingProgram(program: Program) {
    setEditingProgramId(program.id);
    setProgramForm({ name: program.name, goal: program.goal, duration_weeks: String(program.duration_weeks) });
  }

  function startEditingWorkoutDay(day: WorkoutDay) {
    setEditingWorkoutDayId(day.id);
    setWorkoutDayForm({ name: day.name, day_order: String(day.day_order) });
  }

  function startEditingExercise(exercise: WorkoutExercise) {
    setEditingExerciseId(exercise.id);
    setExerciseForm({
      movement_name: exercise.movement_name,
      sets: String(exercise.sets),
      reps: exercise.reps,
      rest_seconds: String(exercise.rest_seconds),
      notes: exercise.notes,
      exercise_order: String(exercise.exercise_order),
    });
  }

  async function deleteProgram(programId: number) {
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Could not delete the program.");
      if (editingProgramId === programId) resetProgramForm();
      if (selectedProgramId === programId) {
        setSelectedProgramId(null);
        setSelectedWorkoutDayId(null);
        setWorkoutDays([]);
        setExercises([]);
        resetWorkoutDayForm();
        resetExerciseForm();
      }
      await loadPrograms();
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Unexpected error while deleting program.");
    }
  }

  async function deleteWorkoutDay(workoutDayId: number) {
    setError(null);
    if (selectedProgramId === null) return;
    try {
      const response = await fetch(`${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${workoutDayId}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Could not delete the workout day.");
      if (editingWorkoutDayId === workoutDayId) resetWorkoutDayForm();
      if (selectedWorkoutDayId === workoutDayId) {
        setSelectedWorkoutDayId(null);
        setExercises([]);
        resetExerciseForm();
      }
      await loadWorkoutDays(selectedProgramId);
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Unexpected error while deleting workout day.");
    }
  }

  async function deleteExercise(exerciseId: number) {
    setError(null);
    if (selectedProgramId === null || selectedWorkoutDayId === null) return;
    try {
      const response = await fetch(`${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${exerciseId}`, { method: "DELETE" });
      if (!response.ok) throw new Error("Could not delete the exercise.");
      if (editingExerciseId === exerciseId) resetExerciseForm();
      await loadExercises(selectedProgramId, selectedWorkoutDayId);
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Unexpected error while deleting exercise.");
    }
  }

  function selectProgram(programId: number) {
    setSelectedProgramId(programId);
    setSelectedWorkoutDayId(null);
    resetWorkoutDayForm();
    resetExerciseForm();
  }

  function selectWorkoutDay(workoutDayId: number) {
    setSelectedWorkoutDayId(workoutDayId);
    resetExerciseForm();
  }

  return (
    <main className="app-shell">
      <header className="top-bar">
        <h1 className="brand">SetPilot</h1>
        <span className="phase-label">Sprint 1: Exercises</span>
      </header>

      <section className="dashboard" aria-labelledby="dashboard-title">
        <div className="intro">
          <h2 id="dashboard-title">Train from a clear plan.</h2>
          <p>SetPilot helps gym users build programs, structure workout days, attach exercises, and later execute sessions with timers and progress analysis.</p>
        </div>

        <div className="actions" aria-label="Dashboard overview">
          {dashboardItems.map((item) => (
            <button className="action-button" key={item.label} type="button">
              {item.label}
              <span>{item.description}</span>
            </button>
          ))}
        </div>
      </section>

      {error ? <section className="program-workspace"><p className="error-message global-error">{error}</p></section> : null}

      <section className="program-workspace" aria-labelledby="programs-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Layer 1</p>
            <h2 id="programs-title">Programs</h2>
          </div>
          <p>Create the big training container first. Days and exercises hang underneath it.</p>
        </div>

        <div className="program-grid">
          <form className="program-form" onSubmit={handleProgramSubmit}>
            <h3>{isEditingProgram ? "Edit program" : "Create program"}</h3>
            <label>Program name<input maxLength={120} onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })} placeholder="Strength Foundation" value={programForm.name} /></label>
            <label>Goal<textarea maxLength={255} onChange={(e) => setProgramForm({ ...programForm, goal: e.target.value })} placeholder="Build strength while learning core lifts" value={programForm.goal} /></label>
            <label>Duration in weeks<input max="104" min="1" onChange={(e) => setProgramForm({ ...programForm, duration_weeks: e.target.value })} type="number" value={programForm.duration_weeks} /></label>
            <div className="form-actions">
              <button className="primary-button" type="submit">{isEditingProgram ? "Save changes" : "Create program"}</button>
              {isEditingProgram ? <button className="secondary-button" onClick={resetProgramForm} type="button">Cancel edit</button> : null}
            </div>
          </form>

          <div className="program-list">
            <div className="list-header"><h3>Saved programs</h3><button className="text-button" onClick={() => void loadPrograms()} type="button">Refresh</button></div>
            {isLoadingPrograms ? <p className="muted">Loading programs...</p> : null}
            {!isLoadingPrograms && programs.length === 0 ? <p className="empty-state">No programs yet. Create one first; exercises without a program are just gym confetti.</p> : null}
            <div className="program-cards">
              {programs.map((program) => {
                const isSelected = selectedProgramId === program.id;
                return (
                  <article className={`program-card${isSelected ? " selected-card" : ""}`} key={program.id}>
                    <div><h4>{program.name}</h4><p>{program.goal}</p><span>{program.duration_weeks} weeks</span></div>
                    <div className="card-actions">
                      <button className="primary-button compact-button" onClick={() => selectProgram(program.id)} type="button">{isSelected ? "Selected" : "Select"}</button>
                      <button className="secondary-button compact-button" onClick={() => startEditingProgram(program)} type="button">Edit</button>
                      <button className="danger-button compact-button" onClick={() => void deleteProgram(program.id)} type="button">Delete</button>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="program-workspace" aria-labelledby="workout-days-title">
        <div className="section-heading">
          <div><p className="eyebrow">Layer 2</p><h2 id="workout-days-title">Workout Days</h2></div>
          <p>{selectedProgram ? `Selected program: ${selectedProgram.name}` : "Select or create a program before adding workout days."}</p>
        </div>

        <div className="program-grid">
          <form className="program-form" onSubmit={handleWorkoutDaySubmit}>
            <h3>{isEditingWorkoutDay ? "Edit workout day" : "Add workout day"}</h3>
            <label>Day name<input disabled={selectedProgramId === null} maxLength={120} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, name: e.target.value })} placeholder="Upper Body Strength" value={workoutDayForm.name} /></label>
            <label>Day order<input disabled={selectedProgramId === null} max="14" min="1" onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, day_order: e.target.value })} type="number" value={workoutDayForm.day_order} /></label>
            <div className="form-actions">
              <button className="primary-button" disabled={selectedProgramId === null} type="submit">{isEditingWorkoutDay ? "Save day" : "Add day"}</button>
              {isEditingWorkoutDay ? <button className="secondary-button" onClick={resetWorkoutDayForm} type="button">Cancel edit</button> : null}
            </div>
          </form>

          <div className="program-list">
            <div className="list-header"><h3>Days in selected program</h3><button className="text-button" disabled={selectedProgramId === null} onClick={() => selectedProgramId !== null ? void loadWorkoutDays(selectedProgramId) : undefined} type="button">Refresh</button></div>
            {isLoadingWorkoutDays ? <p className="muted">Loading workout days...</p> : null}
            {!isLoadingWorkoutDays && selectedProgramId === null ? <p className="empty-state">No selected program. The days need a home, not an existential crisis.</p> : null}
            {!isLoadingWorkoutDays && selectedProgramId !== null && workoutDays.length === 0 ? <p className="empty-state">No workout days yet. Add Day 1, Day 2, and so on.</p> : null}
            <div className="program-cards">
              {workoutDays.map((day) => {
                const isSelected = selectedWorkoutDayId === day.id;
                return (
                  <article className={`program-card workout-day-card${isSelected ? " selected-card" : ""}`} key={day.id}>
                    <div><h4>{day.name}</h4><p>Day order: {day.day_order}</p><span>Program ID: {day.program_id}</span></div>
                    <div className="card-actions">
                      <button className="primary-button compact-button" onClick={() => selectWorkoutDay(day.id)} type="button">{isSelected ? "Selected" : "Select"}</button>
                      <button className="secondary-button compact-button" onClick={() => startEditingWorkoutDay(day)} type="button">Edit</button>
                      <button className="danger-button compact-button" onClick={() => void deleteWorkoutDay(day.id)} type="button">Delete</button>
                    </div>
                  </article>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      <section className="program-workspace" aria-labelledby="exercises-title">
        <div className="section-heading">
          <div><p className="eyebrow">Layer 3</p><h2 id="exercises-title">Exercises</h2></div>
          <p>{selectedWorkoutDay ? `Selected day: ${selectedWorkoutDay.name}` : "Select a workout day before adding exercises."}</p>
        </div>

        <div className="program-grid">
          <form className="program-form" onSubmit={handleExerciseSubmit}>
            <h3>{isEditingExercise ? "Edit exercise" : "Add exercise"}</h3>
            <label>Movement name<input disabled={selectedWorkoutDayId === null} maxLength={160} onChange={(e) => setExerciseForm({ ...exerciseForm, movement_name: e.target.value })} placeholder="Bench Press" value={exerciseForm.movement_name} /></label>
            <div className="inline-fields">
              <label>Sets<input disabled={selectedWorkoutDayId === null} min="1" max="20" onChange={(e) => setExerciseForm({ ...exerciseForm, sets: e.target.value })} type="number" value={exerciseForm.sets} /></label>
              <label>Reps<input disabled={selectedWorkoutDayId === null} maxLength={40} onChange={(e) => setExerciseForm({ ...exerciseForm, reps: e.target.value })} placeholder="6-8" value={exerciseForm.reps} /></label>
            </div>
            <div className="inline-fields">
              <label>Rest seconds<input disabled={selectedWorkoutDayId === null} min="0" max="900" onChange={(e) => setExerciseForm({ ...exerciseForm, rest_seconds: e.target.value })} type="number" value={exerciseForm.rest_seconds} /></label>
              <label>Order<input disabled={selectedWorkoutDayId === null} min="1" max="100" onChange={(e) => setExerciseForm({ ...exerciseForm, exercise_order: e.target.value })} type="number" value={exerciseForm.exercise_order} /></label>
            </div>
            <label>Notes<textarea disabled={selectedWorkoutDayId === null} maxLength={1000} onChange={(e) => setExerciseForm({ ...exerciseForm, notes: e.target.value })} placeholder="Keep shoulder blades tight." value={exerciseForm.notes} /></label>
            <div className="form-actions">
              <button className="primary-button" disabled={selectedWorkoutDayId === null} type="submit">{isEditingExercise ? "Save exercise" : "Add exercise"}</button>
              {isEditingExercise ? <button className="secondary-button" onClick={resetExerciseForm} type="button">Cancel edit</button> : null}
            </div>
          </form>

          <div className="program-list">
            <div className="list-header"><h3>Exercises in selected day</h3><button className="text-button" disabled={selectedProgramId === null || selectedWorkoutDayId === null} onClick={() => selectedProgramId !== null && selectedWorkoutDayId !== null ? void loadExercises(selectedProgramId, selectedWorkoutDayId) : undefined} type="button">Refresh</button></div>
            {isLoadingExercises ? <p className="muted">Loading exercises...</p> : null}
            {!isLoadingExercises && selectedWorkoutDayId === null ? <p className="empty-state">No selected workout day. Pick a day before throwing exercises into the void.</p> : null}
            {!isLoadingExercises && selectedWorkoutDayId !== null && exercises.length === 0 ? <p className="empty-state">No exercises yet. Add the first movement and the plan finally starts looking like a gym program.</p> : null}
            <div className="program-cards">
              {exercises.map((exercise) => (
                <article className="program-card exercise-card" key={exercise.id}>
                  <div>
                    <h4>{exercise.exercise_order}. {exercise.movement_name}</h4>
                    <p>{exercise.sets} sets × {exercise.reps} reps · Rest {exercise.rest_seconds}s</p>
                    {exercise.notes ? <span>{exercise.notes}</span> : <span>No notes</span>}
                  </div>
                  <div className="card-actions">
                    <button className="secondary-button compact-button" onClick={() => startEditingExercise(exercise)} type="button">Edit</button>
                    <button className="danger-button compact-button" onClick={() => void deleteExercise(exercise.id)} type="button">Delete</button>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;
