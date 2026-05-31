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

type ProgramFormState = {
  name: string;
  goal: string;
  duration_weeks: string;
};

type WorkoutDayFormState = {
  name: string;
  day_order: string;
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

const dashboardItems = [
  {
    label: "My Programs",
    description: "Create and manage plans",
  },
  {
    label: "Workout Days",
    description: "Build weekly structure",
  },
  {
    label: "Exercise Library",
    description: "Movement videos come later",
  },
  {
    label: "Progress",
    description: "Analysis comes after sessions",
  },
];

function App() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [programForm, setProgramForm] = useState<ProgramFormState>(emptyProgramForm);
  const [editingProgramId, setEditingProgramId] = useState<number | null>(null);
  const [selectedProgramId, setSelectedProgramId] = useState<number | null>(null);

  const [workoutDays, setWorkoutDays] = useState<WorkoutDay[]>([]);
  const [workoutDayForm, setWorkoutDayForm] =
    useState<WorkoutDayFormState>(emptyWorkoutDayForm);
  const [editingWorkoutDayId, setEditingWorkoutDayId] = useState<number | null>(null);

  const [isLoadingPrograms, setIsLoadingPrograms] = useState(false);
  const [isLoadingWorkoutDays, setIsLoadingWorkoutDays] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditingProgram = useMemo(
    () => editingProgramId !== null,
    [editingProgramId],
  );
  const isEditingWorkoutDay = useMemo(
    () => editingWorkoutDayId !== null,
    [editingWorkoutDayId],
  );
  const selectedProgram = useMemo(
    () => programs.find((program) => program.id === selectedProgramId) ?? null,
    [programs, selectedProgramId],
  );

  async function loadPrograms() {
    setIsLoadingPrograms(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs`);
      if (!response.ok) {
        throw new Error("Could not load programs from the backend.");
      }
      const data = (await response.json()) as Program[];
      setPrograms(data);

      setSelectedProgramId((currentSelectedId) => {
        if (currentSelectedId && data.some((program) => program.id === currentSelectedId)) {
          return currentSelectedId;
        }
        return data[0]?.id ?? null;
      });
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unexpected error while loading programs.",
      );
    } finally {
      setIsLoadingPrograms(false);
    }
  }

  async function loadWorkoutDays(programId: number) {
    setIsLoadingWorkoutDays(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}/workout-days`);
      if (!response.ok) {
        throw new Error("Could not load workout days for this program.");
      }
      const data = (await response.json()) as WorkoutDay[];
      setWorkoutDays(data);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unexpected error while loading workout days.",
      );
    } finally {
      setIsLoadingWorkoutDays(false);
    }
  }

  useEffect(() => {
    void loadPrograms();
  }, []);

  useEffect(() => {
    if (selectedProgramId === null) {
      setWorkoutDays([]);
      return;
    }
    void loadWorkoutDays(selectedProgramId);
  }, [selectedProgramId]);

  function updateProgramForm(field: keyof ProgramFormState, value: string) {
    setProgramForm((current) => ({ ...current, [field]: value }));
  }

  function updateWorkoutDayForm(field: keyof WorkoutDayFormState, value: string) {
    setWorkoutDayForm((current) => ({ ...current, [field]: value }));
  }

  function resetProgramForm() {
    setProgramForm(emptyProgramForm);
    setEditingProgramId(null);
  }

  function resetWorkoutDayForm() {
    setWorkoutDayForm(emptyWorkoutDayForm);
    setEditingWorkoutDayId(null);
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

    const url = isEditingProgram
      ? `${API_BASE_URL}/programs/${editingProgramId}`
      : `${API_BASE_URL}/programs`;

    try {
      const response = await fetch(url, {
        method: isEditingProgram ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Could not save the program.");
      }

      const savedProgram = (await response.json()) as Program;
      resetProgramForm();
      setSelectedProgramId(savedProgram.id);
      await loadPrograms();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Unexpected error while saving program.",
      );
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

      if (!response.ok) {
        throw new Error("Could not save the workout day.");
      }

      resetWorkoutDayForm();
      await loadWorkoutDays(selectedProgramId);
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Unexpected error while saving workout day.",
      );
    }
  }

  function startEditingProgram(program: Program) {
    setEditingProgramId(program.id);
    setProgramForm({
      name: program.name,
      goal: program.goal,
      duration_weeks: String(program.duration_weeks),
    });
  }

  function startEditingWorkoutDay(workoutDay: WorkoutDay) {
    setEditingWorkoutDayId(workoutDay.id);
    setWorkoutDayForm({
      name: workoutDay.name,
      day_order: String(workoutDay.day_order),
    });
  }

  async function deleteProgram(programId: number) {
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Could not delete the program.");
      }

      if (editingProgramId === programId) {
        resetProgramForm();
      }
      if (selectedProgramId === programId) {
        setSelectedProgramId(null);
        setWorkoutDays([]);
        resetWorkoutDayForm();
      }
      await loadPrograms();
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "Unexpected error while deleting program.",
      );
    }
  }

  async function deleteWorkoutDay(workoutDayId: number) {
    setError(null);

    if (selectedProgramId === null) {
      setError("Select a program before deleting workout days.");
      return;
    }

    try {
      const response = await fetch(
        `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${workoutDayId}`,
        { method: "DELETE" },
      );

      if (!response.ok) {
        throw new Error("Could not delete the workout day.");
      }

      if (editingWorkoutDayId === workoutDayId) {
        resetWorkoutDayForm();
      }
      await loadWorkoutDays(selectedProgramId);
    } catch (deleteError) {
      setError(
        deleteError instanceof Error
          ? deleteError.message
          : "Unexpected error while deleting workout day.",
      );
    }
  }

  function selectProgram(programId: number) {
    setSelectedProgramId(programId);
    resetWorkoutDayForm();
  }

  return (
    <main className="app-shell">
      <header className="top-bar">
        <h1 className="brand">SetPilot</h1>
        <span className="phase-label">Sprint 1: Workout Days</span>
      </header>

      <section className="dashboard" aria-labelledby="dashboard-title">
        <div className="intro">
          <h2 id="dashboard-title">Train from a clear plan.</h2>
          <p>
            SetPilot helps gym users follow structured workout programs, review
            movement examples, manage workout timing, and understand progress
            after each session.
          </p>
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

      <section className="program-workspace" aria-labelledby="programs-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Product structure</p>
            <h2 id="programs-title">Programs and Workout Days</h2>
          </div>
          <p>
            First create the program. Then select it and build its weekly day
            structure. Exercises will attach to these days next.
          </p>
        </div>

        {error ? <p className="error-message global-error">{error}</p> : null}

        <div className="program-grid">
          <form className="program-form" onSubmit={handleProgramSubmit}>
            <h3>{isEditingProgram ? "Edit program" : "Create program"}</h3>

            <label>
              Program name
              <input
                maxLength={120}
                onChange={(event) => updateProgramForm("name", event.target.value)}
                placeholder="Strength Foundation"
                type="text"
                value={programForm.name}
              />
            </label>

            <label>
              Goal
              <textarea
                maxLength={255}
                onChange={(event) => updateProgramForm("goal", event.target.value)}
                placeholder="Build strength while learning core lifts"
                value={programForm.goal}
              />
            </label>

            <label>
              Duration in weeks
              <input
                max="104"
                min="1"
                onChange={(event) =>
                  updateProgramForm("duration_weeks", event.target.value)
                }
                type="number"
                value={programForm.duration_weeks}
              />
            </label>

            <div className="form-actions">
              <button className="primary-button" type="submit">
                {isEditingProgram ? "Save changes" : "Create program"}
              </button>
              {isEditingProgram ? (
                <button className="secondary-button" onClick={resetProgramForm} type="button">
                  Cancel edit
                </button>
              ) : null}
            </div>
          </form>

          <div className="program-list">
            <div className="list-header">
              <h3>Saved programs</h3>
              <button className="text-button" onClick={() => void loadPrograms()} type="button">
                Refresh
              </button>
            </div>

            {isLoadingPrograms ? <p className="muted">Loading programs...</p> : null}

            {!isLoadingPrograms && programs.length === 0 ? (
              <p className="empty-state">
                No programs yet. Create the first one and stop letting the app
                remain a motivational poster with a database.
              </p>
            ) : null}

            <div className="program-cards">
              {programs.map((program) => {
                const isSelected = selectedProgramId === program.id;
                return (
                  <article
                    className={`program-card${isSelected ? " selected-card" : ""}`}
                    key={program.id}
                  >
                    <div>
                      <h4>{program.name}</h4>
                      <p>{program.goal}</p>
                      <span>{program.duration_weeks} weeks</span>
                    </div>
                    <div className="card-actions">
                      <button
                        className="primary-button compact-button"
                        onClick={() => selectProgram(program.id)}
                        type="button"
                      >
                        {isSelected ? "Selected" : "Select"}
                      </button>
                      <button
                        className="secondary-button compact-button"
                        onClick={() => startEditingProgram(program)}
                        type="button"
                      >
                        Edit
                      </button>
                      <button
                        className="danger-button compact-button"
                        onClick={() => void deleteProgram(program.id)}
                        type="button"
                      >
                        Delete
                      </button>
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
          <div>
            <p className="eyebrow">Weekly structure</p>
            <h2 id="workout-days-title">Workout Days</h2>
          </div>
          <p>
            {selectedProgram
              ? `Selected program: ${selectedProgram.name}`
              : "Select or create a program before adding workout days."}
          </p>
        </div>

        <div className="program-grid">
          <form className="program-form" onSubmit={handleWorkoutDaySubmit}>
            <h3>{isEditingWorkoutDay ? "Edit workout day" : "Add workout day"}</h3>

            <label>
              Day name
              <input
                disabled={selectedProgramId === null}
                maxLength={120}
                onChange={(event) => updateWorkoutDayForm("name", event.target.value)}
                placeholder="Upper Body Strength"
                type="text"
                value={workoutDayForm.name}
              />
            </label>

            <label>
              Day order
              <input
                disabled={selectedProgramId === null}
                max="14"
                min="1"
                onChange={(event) => updateWorkoutDayForm("day_order", event.target.value)}
                type="number"
                value={workoutDayForm.day_order}
              />
            </label>

            <div className="form-actions">
              <button
                className="primary-button"
                disabled={selectedProgramId === null}
                type="submit"
              >
                {isEditingWorkoutDay ? "Save day" : "Add day"}
              </button>
              {isEditingWorkoutDay ? (
                <button className="secondary-button" onClick={resetWorkoutDayForm} type="button">
                  Cancel edit
                </button>
              ) : null}
            </div>
          </form>

          <div className="program-list">
            <div className="list-header">
              <h3>Days in selected program</h3>
              <button
                className="text-button"
                disabled={selectedProgramId === null}
                onClick={() =>
                  selectedProgramId !== null ? void loadWorkoutDays(selectedProgramId) : undefined
                }
                type="button"
              >
                Refresh
              </button>
            </div>

            {isLoadingWorkoutDays ? <p className="muted">Loading workout days...</p> : null}

            {!isLoadingWorkoutDays && selectedProgramId === null ? (
              <p className="empty-state">No selected program. The days need a home, not an existential crisis.</p>
            ) : null}

            {!isLoadingWorkoutDays && selectedProgramId !== null && workoutDays.length === 0 ? (
              <p className="empty-state">
                No workout days yet. Add Day 1, Day 2, and so on. This is where
                the weekly plan stops being fog and starts becoming structure.
              </p>
            ) : null}

            <div className="program-cards">
              {workoutDays.map((workoutDay) => (
                <article className="program-card workout-day-card" key={workoutDay.id}>
                  <div>
                    <h4>{workoutDay.name}</h4>
                    <p>Day order: {workoutDay.day_order}</p>
                    <span>Program ID: {workoutDay.program_id}</span>
                  </div>
                  <div className="card-actions">
                    <button
                      className="secondary-button compact-button"
                      onClick={() => startEditingWorkoutDay(workoutDay)}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="danger-button compact-button"
                      onClick={() => void deleteWorkoutDay(workoutDay.id)}
                      type="button"
                    >
                      Delete
                    </button>
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
