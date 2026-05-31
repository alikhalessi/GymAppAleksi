import { FormEvent, useEffect, useMemo, useState } from "react";
import "./App.css";

type Program = {
  id: number;
  name: string;
  goal: string;
  duration_weeks: number;
  created_at: string;
};

type ProgramFormState = {
  name: string;
  goal: string;
  duration_weeks: string;
};

const API_BASE_URL = "http://127.0.0.1:8000";

const emptyForm: ProgramFormState = {
  name: "",
  goal: "",
  duration_weeks: "8",
};

const dashboardItems = [
  {
    label: "My Programs",
    description: "Create and manage plans",
  },
  {
    label: "Start Workout",
    description: "Session flow comes next",
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
  const [form, setForm] = useState<ProgramFormState>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditing = useMemo(() => editingId !== null, [editingId]);

  async function loadPrograms() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs`);
      if (!response.ok) {
        throw new Error("Could not load programs from the backend.");
      }
      const data = (await response.json()) as Program[];
      setPrograms(data);
    } catch (loadError) {
      setError(
        loadError instanceof Error
          ? loadError.message
          : "Unexpected error while loading programs.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadPrograms();
  }, []);

  function updateForm(field: keyof ProgramFormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    const payload = {
      name: form.name.trim(),
      goal: form.goal.trim(),
      duration_weeks: Number(form.duration_weeks),
    };

    if (!payload.name || !payload.goal || Number.isNaN(payload.duration_weeks)) {
      setError("Program name, goal, and duration are required.");
      return;
    }

    const url = isEditing
      ? `${API_BASE_URL}/programs/${editingId}`
      : `${API_BASE_URL}/programs`;

    try {
      const response = await fetch(url, {
        method: isEditing ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Could not save the program.");
      }

      resetForm();
      await loadPrograms();
    } catch (saveError) {
      setError(
        saveError instanceof Error
          ? saveError.message
          : "Unexpected error while saving program.",
      );
    }
  }

  function startEditing(program: Program) {
    setEditingId(program.id);
    setForm({
      name: program.name,
      goal: program.goal,
      duration_weeks: String(program.duration_weeks),
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

      if (editingId === programId) {
        resetForm();
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

  return (
    <main className="app-shell">
      <header className="top-bar">
        <h1 className="brand">SetPilot</h1>
        <span className="phase-label">Sprint 1: Program CRUD</span>
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
            <p className="eyebrow">First real product slice</p>
            <h2 id="programs-title">Workout Programs</h2>
          </div>
          <p>
            Create the training containers first. Workout days, exercises, video
            examples, timers, and session analysis will attach to these later.
          </p>
        </div>

        <div className="program-grid">
          <form className="program-form" onSubmit={handleSubmit}>
            <h3>{isEditing ? "Edit program" : "Create program"}</h3>

            <label>
              Program name
              <input
                maxLength={120}
                onChange={(event) => updateForm("name", event.target.value)}
                placeholder="Strength Foundation"
                type="text"
                value={form.name}
              />
            </label>

            <label>
              Goal
              <textarea
                maxLength={255}
                onChange={(event) => updateForm("goal", event.target.value)}
                placeholder="Build strength while learning core lifts"
                value={form.goal}
              />
            </label>

            <label>
              Duration in weeks
              <input
                max="104"
                min="1"
                onChange={(event) =>
                  updateForm("duration_weeks", event.target.value)
                }
                type="number"
                value={form.duration_weeks}
              />
            </label>

            {error ? <p className="error-message">{error}</p> : null}

            <div className="form-actions">
              <button className="primary-button" type="submit">
                {isEditing ? "Save changes" : "Create program"}
              </button>
              {isEditing ? (
                <button className="secondary-button" onClick={resetForm} type="button">
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

            {isLoading ? <p className="muted">Loading programs...</p> : null}

            {!isLoading && programs.length === 0 ? (
              <p className="empty-state">
                No programs yet. Create the first one and stop letting the app
                remain a motivational poster with a database.
              </p>
            ) : null}

            <div className="program-cards">
              {programs.map((program) => (
                <article className="program-card" key={program.id}>
                  <div>
                    <h4>{program.name}</h4>
                    <p>{program.goal}</p>
                    <span>{program.duration_weeks} weeks</span>
                  </div>
                  <div className="card-actions">
                    <button
                      className="secondary-button"
                      onClick={() => startEditing(program)}
                      type="button"
                    >
                      Edit
                    </button>
                    <button
                      className="danger-button"
                      onClick={() => void deleteProgram(program.id)}
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
