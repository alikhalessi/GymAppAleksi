import { FormEvent, useEffect, useMemo, useState } from "react";

import "./App.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

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

const emptyForm: ProgramFormState = {
  name: "",
  goal: "",
  duration_weeks: "8",
};

function App() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [form, setForm] = useState<ProgramFormState>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isEditing = editingId !== null;

  const sortedPrograms = useMemo(
    () =>
      [...programs].sort(
        (a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime(),
      ),
    [programs],
  );

  async function loadPrograms() {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs`);
      if (!response.ok) {
        throw new Error("Could not load programs.");
      }
      const data = (await response.json()) as Program[];
      setPrograms(data);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not load programs.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadPrograms();
  }, []);

  function updateField(field: keyof ProgramFormState, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  function resetForm() {
    setForm(emptyForm);
    setEditingId(null);
  }

  function editProgram(program: Program) {
    setEditingId(program.id);
    setForm({
      name: program.name,
      goal: program.goal,
      duration_weeks: String(program.duration_weeks),
    });
  }

  async function submitProgram(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(null);

    const payload = {
      name: form.name.trim(),
      goal: form.goal.trim(),
      duration_weeks: Number(form.duration_weeks),
    };

    try {
      const response = await fetch(
        isEditing
          ? `${API_BASE_URL}/programs/${editingId}`
          : `${API_BASE_URL}/programs`,
        {
          method: isEditing ? "PUT" : "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        },
      );

      if (!response.ok) {
        throw new Error("Could not save program. Check the form values.");
      }

      const saved = (await response.json()) as Program;
      setPrograms((current) => {
        if (isEditing) {
          return current.map((program) =>
            program.id === saved.id ? saved : program,
          );
        }
        return [saved, ...current];
      });
      resetForm();
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not save program.",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function deleteProgram(programId: number) {
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error("Could not delete program.");
      }

      setPrograms((current) =>
        current.filter((program) => program.id !== programId),
      );
      if (editingId === programId) {
        resetForm();
      }
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Could not delete program.",
      );
    }
  }

  return (
    <main className="app-shell">
      <header className="top-bar">
        <h1 className="brand">SetPilot</h1>
        <span className="phase-label">Program builder</span>
      </header>

      <section className="dashboard" aria-labelledby="dashboard-title">
        <div className="intro">
          <h2 id="dashboard-title">Build your workout programs.</h2>
          <p>
            Create the program container first. Workout days, exercises,
            session tracking, and YouTube examples come in later sprints.
          </p>
        </div>

        <div className="actions" aria-label="Dashboard placeholders">
          <button className="action-button active" type="button">
            My Programs
            <span>Create and manage plans</span>
          </button>
          <button className="action-button" disabled type="button">
            Start Workout
            <span>Coming later</span>
          </button>
          <button className="action-button" disabled type="button">
            Exercise Library
            <span>Coming later</span>
          </button>
          <button className="action-button" disabled type="button">
            Progress
            <span>Coming later</span>
          </button>
        </div>

        <section className="programs-layout" aria-label="Programs">
          <form className="program-form" onSubmit={submitProgram}>
            <div>
              <p className="section-kicker">
                {isEditing ? "Edit program" : "New program"}
              </p>
              <h3>{isEditing ? "Update plan details" : "Create a program"}</h3>
            </div>

            <label>
              Program name
              <input
                maxLength={120}
                onChange={(event) => updateField("name", event.target.value)}
                placeholder="Upper Lower"
                required
                type="text"
                value={form.name}
              />
            </label>

            <label>
              Goal
              <input
                maxLength={240}
                onChange={(event) => updateField("goal", event.target.value)}
                placeholder="Build strength consistently"
                required
                type="text"
                value={form.goal}
              />
            </label>

            <label>
              Duration weeks
              <input
                max={104}
                min={1}
                onChange={(event) =>
                  updateField("duration_weeks", event.target.value)
                }
                required
                type="number"
                value={form.duration_weeks}
              />
            </label>

            <div className="form-actions">
              <button className="primary-button" disabled={isSaving} type="submit">
                {isSaving
                  ? "Saving..."
                  : isEditing
                    ? "Save changes"
                    : "Create program"}
              </button>
              {isEditing ? (
                <button className="secondary-button" onClick={resetForm} type="button">
                  Cancel
                </button>
              ) : null}
            </div>
          </form>

          <div className="program-list-panel">
            <div className="panel-heading">
              <div>
                <p className="section-kicker">My Programs</p>
                <h3>{programs.length} saved</h3>
              </div>
              <button className="secondary-button" onClick={loadPrograms} type="button">
                Refresh
              </button>
            </div>

            {error ? <p className="status-message error">{error}</p> : null}
            {isLoading ? <p className="status-message">Loading programs...</p> : null}

            {!isLoading && sortedPrograms.length === 0 ? (
              <p className="empty-state">
                No programs yet. Create your first plan to start building the
                workout structure.
              </p>
            ) : null}

            <div className="program-list">
              {sortedPrograms.map((program) => (
                <article className="program-card" key={program.id}>
                  <div>
                    <h4>{program.name}</h4>
                    <p>{program.goal}</p>
                  </div>
                  <dl>
                    <div>
                      <dt>Duration</dt>
                      <dd>{program.duration_weeks} weeks</dd>
                    </div>
                    <div>
                      <dt>Created</dt>
                      <dd>{new Date(program.created_at).toLocaleDateString()}</dd>
                    </div>
                  </dl>
                  <div className="card-actions">
                    <button
                      className="secondary-button"
                      onClick={() => editProgram(program)}
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
        </section>
      </section>
    </main>
  );
}

export default App;
