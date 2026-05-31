import { FormEvent, useEffect, useMemo, useState } from "react";
import "./App.css";

type Program = { id: number; name: string; goal: string; duration_weeks: number; created_at: string };
type WorkoutDay = { id: number; program_id: number; name: string; day_order: number; created_at: string };
type WorkoutExercise = { id: number; workout_day_id: number; movement_name: string; sets: number; reps: string; rest_seconds: number; notes: string; exercise_order: number; created_at: string };
type ProgramFormState = { name: string; goal: string; duration_weeks: string };
type WorkoutDayFormState = { name: string; day_order: string };
type ExerciseFormState = { movement_name: string; sets: string; reps: string; rest_seconds: string; notes: string; exercise_order: string };
type OpenAIKeyStatus = { configured: boolean; source: string | null; masked_key: string | null };
type AIParsedExercise = { movement_name: string; sets: number; reps: string; rest_seconds: number; notes: string; exercise_order: number; confidence: number; warnings: string[] };
type AIParsedWorkoutDay = { name: string; day_order: number; exercises: AIParsedExercise[] };
type AIParsedPlan = { program: { name: string; goal: string; duration_weeks: number }; workout_days: AIParsedWorkoutDay[] };
type ImportAnalysis = { parsed_plan: AIParsedPlan; overall_confidence: number; warnings: string[]; questions_for_user: string[]; trainer_review_required: boolean };

const API_BASE_URL = "http://127.0.0.1:8000";
const emptyProgramForm: ProgramFormState = { name: "", goal: "", duration_weeks: "8" };
const emptyWorkoutDayForm: WorkoutDayFormState = { name: "", day_order: "1" };
const emptyExerciseForm: ExerciseFormState = { movement_name: "", sets: "3", reps: "8-10", rest_seconds: "90", notes: "", exercise_order: "1" };
const sampleImportText = `Program: Strength Foundation\nDuration: 8 weeks\nGoal: Build strength and muscle\n\nDay 1 - Upper Body\nBench Press - 4 sets - 6-8 reps - 120 sec rest\nLat Pulldown - 3 sets - 10 reps - 90 sec rest\n\nDay 2 - Lower Body\nSquat - 5x5 - 180 sec rest\nRomanian Deadlift - 3x8 - 120 sec rest`;

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
  const [openAIKeyInput, setOpenAIKeyInput] = useState("");
  const [openAIKeyStatus, setOpenAIKeyStatus] = useState<OpenAIKeyStatus>({ configured: false, source: null, masked_key: null });
  const [isSavingKey, setIsSavingKey] = useState(false);
  const [importText, setImportText] = useState(sampleImportText);
  const [importAnalysis, setImportAnalysis] = useState<ImportAnalysis | null>(null);
  const [isAnalyzingImport, setIsAnalyzingImport] = useState(false);
  const [isSavingImport, setIsSavingImport] = useState(false);
  const [isLoadingPrograms, setIsLoadingPrograms] = useState(false);
  const [isLoadingWorkoutDays, setIsLoadingWorkoutDays] = useState(false);
  const [isLoadingExercises, setIsLoadingExercises] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectedProgram = useMemo(() => programs.find((p) => p.id === selectedProgramId) ?? null, [programs, selectedProgramId]);
  const selectedWorkoutDay = useMemo(() => workoutDays.find((d) => d.id === selectedWorkoutDayId) ?? null, [workoutDays, selectedWorkoutDayId]);

  async function loadOpenAIKeyStatus() {
    try {
      const response = await fetch(`${API_BASE_URL}/settings/openai-key`);
      if (!response.ok) throw new Error("Could not load OpenAI key status.");
      setOpenAIKeyStatus((await response.json()) as OpenAIKeyStatus);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error while loading OpenAI key status.");
    }
  }

  async function saveOpenAIKey(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setIsSavingKey(true);
    try {
      const response = await fetch(`${API_BASE_URL}/settings/openai-key`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ api_key: openAIKeyInput }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Could not save OpenAI API key.");
      setOpenAIKeyStatus(data as OpenAIKeyStatus); setOpenAIKeyInput("");
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while saving OpenAI key."); }
    finally { setIsSavingKey(false); }
  }

  async function clearOpenAIKey() {
    setError(null); setIsSavingKey(true);
    try {
      const response = await fetch(`${API_BASE_URL}/settings/openai-key`, { method: "DELETE" });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Could not clear OpenAI API key.");
      setOpenAIKeyStatus(data as OpenAIKeyStatus);
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while clearing OpenAI key."); }
    finally { setIsSavingKey(false); }
  }

  async function loadPrograms() {
    setIsLoadingPrograms(true); setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/programs`);
      if (!response.ok) throw new Error("Could not load programs from the backend.");
      const data = (await response.json()) as Program[];
      setPrograms(data);
      setSelectedProgramId((current) => current && data.some((p) => p.id === current) ? current : data[0]?.id ?? null);
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while loading programs."); }
    finally { setIsLoadingPrograms(false); }
  }

  async function loadWorkoutDays(programId: number) {
    setIsLoadingWorkoutDays(true); setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}/workout-days`);
      if (!response.ok) throw new Error("Could not load workout days for this program.");
      const data = (await response.json()) as WorkoutDay[];
      setWorkoutDays(data);
      setSelectedWorkoutDayId((current) => current && data.some((d) => d.id === current) ? current : data[0]?.id ?? null);
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while loading workout days."); }
    finally { setIsLoadingWorkoutDays(false); }
  }

  async function loadExercises(programId: number, workoutDayId: number) {
    setIsLoadingExercises(true); setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/programs/${programId}/workout-days/${workoutDayId}/exercises`);
      if (!response.ok) throw new Error("Could not load exercises for this workout day.");
      setExercises((await response.json()) as WorkoutExercise[]);
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while loading exercises."); }
    finally { setIsLoadingExercises(false); }
  }

  useEffect(() => { void loadOpenAIKeyStatus(); void loadPrograms(); }, []);
  useEffect(() => { if (selectedProgramId === null) { setWorkoutDays([]); setSelectedWorkoutDayId(null); setExercises([]); return; } void loadWorkoutDays(selectedProgramId); }, [selectedProgramId]);
  useEffect(() => { if (selectedProgramId === null || selectedWorkoutDayId === null) { setExercises([]); return; } void loadExercises(selectedProgramId, selectedWorkoutDayId); }, [selectedProgramId, selectedWorkoutDayId]);

  function resetProgramForm() { setProgramForm(emptyProgramForm); setEditingProgramId(null); }
  function resetWorkoutDayForm() { setWorkoutDayForm(emptyWorkoutDayForm); setEditingWorkoutDayId(null); }
  function resetExerciseForm() { setExerciseForm(emptyExerciseForm); setEditingExerciseId(null); }

  async function analyzeImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setIsAnalyzingImport(true); setImportAnalysis(null);
    try {
      const response = await fetch(`${API_BASE_URL}/imports/workout-plan/analyze`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ raw_text: importText }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Could not analyze workout plan.");
      setImportAnalysis(data as ImportAnalysis);
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while analyzing workout plan."); }
    finally { setIsAnalyzingImport(false); }
  }

  async function saveImportedPlan() {
    if (!importAnalysis) return;
    setError(null); setIsSavingImport(true);
    try {
      const response = await fetch(`${API_BASE_URL}/imports/workout-plan/save`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ parsed_plan: importAnalysis.parsed_plan, approval_status: "approved_by_user" }) });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail ?? "Could not save imported plan.");
      setImportAnalysis(null); setImportText(sampleImportText); setSelectedProgramId(data.program.id); await loadPrograms();
    } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while saving imported plan."); }
    finally { setIsSavingImport(false); }
  }

  async function handleProgramSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null);
    const payload = { name: programForm.name.trim(), goal: programForm.goal.trim(), duration_weeks: Number(programForm.duration_weeks) };
    if (!payload.name || !payload.goal || Number.isNaN(payload.duration_weeks)) { setError("Program name, goal, and duration are required."); return; }
    const url = editingProgramId ? `${API_BASE_URL}/programs/${editingProgramId}` : `${API_BASE_URL}/programs`;
    try { const r = await fetch(url, { method: editingProgramId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error("Could not save the program."); const saved = await r.json() as Program; resetProgramForm(); setSelectedProgramId(saved.id); await loadPrograms(); }
    catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while saving program."); }
  }

  async function handleWorkoutDaySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); if (selectedProgramId === null) { setError("Create or select a program before adding workout days."); return; }
    const payload = { name: workoutDayForm.name.trim(), day_order: Number(workoutDayForm.day_order) };
    if (!payload.name || Number.isNaN(payload.day_order)) { setError("Workout day name and order are required."); return; }
    const url = editingWorkoutDayId ? `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${editingWorkoutDayId}` : `${API_BASE_URL}/programs/${selectedProgramId}/workout-days`;
    try { const r = await fetch(url, { method: editingWorkoutDayId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error("Could not save the workout day."); const saved = await r.json() as WorkoutDay; resetWorkoutDayForm(); setSelectedWorkoutDayId(saved.id); await loadWorkoutDays(selectedProgramId); }
    catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while saving workout day."); }
  }

  async function handleExerciseSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); if (selectedProgramId === null || selectedWorkoutDayId === null) { setError("Select a program and workout day before adding exercises."); return; }
    const payload = { movement_name: exerciseForm.movement_name.trim(), sets: Number(exerciseForm.sets), reps: exerciseForm.reps.trim(), rest_seconds: Number(exerciseForm.rest_seconds), notes: exerciseForm.notes.trim(), exercise_order: Number(exerciseForm.exercise_order) };
    if (!payload.movement_name || !payload.reps || Number.isNaN(payload.sets) || Number.isNaN(payload.rest_seconds) || Number.isNaN(payload.exercise_order)) { setError("Exercise name, sets, reps, rest, and order are required."); return; }
    const url = editingExerciseId ? `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${editingExerciseId}` : `${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises`;
    try { const r = await fetch(url, { method: editingExerciseId ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); if (!r.ok) throw new Error("Could not save the exercise."); resetExerciseForm(); await loadExercises(selectedProgramId, selectedWorkoutDayId); }
    catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while saving exercise."); }
  }

  function startEditingProgram(p: Program) { setEditingProgramId(p.id); setProgramForm({ name: p.name, goal: p.goal, duration_weeks: String(p.duration_weeks) }); }
  function startEditingWorkoutDay(d: WorkoutDay) { setEditingWorkoutDayId(d.id); setWorkoutDayForm({ name: d.name, day_order: String(d.day_order) }); }
  function startEditingExercise(e: WorkoutExercise) { setEditingExerciseId(e.id); setExerciseForm({ movement_name: e.movement_name, sets: String(e.sets), reps: e.reps, rest_seconds: String(e.rest_seconds), notes: e.notes, exercise_order: String(e.exercise_order) }); }
  async function deleteProgram(id: number) { setError(null); try { const r = await fetch(`${API_BASE_URL}/programs/${id}`, { method: "DELETE" }); if (!r.ok) throw new Error("Could not delete the program."); if (editingProgramId === id) resetProgramForm(); if (selectedProgramId === id) { setSelectedProgramId(null); setSelectedWorkoutDayId(null); setWorkoutDays([]); setExercises([]); resetWorkoutDayForm(); resetExerciseForm(); } await loadPrograms(); } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while deleting program."); } }
  async function deleteWorkoutDay(id: number) { if (selectedProgramId === null) return; setError(null); try { const r = await fetch(`${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${id}`, { method: "DELETE" }); if (!r.ok) throw new Error("Could not delete the workout day."); if (editingWorkoutDayId === id) resetWorkoutDayForm(); if (selectedWorkoutDayId === id) { setSelectedWorkoutDayId(null); setExercises([]); resetExerciseForm(); } await loadWorkoutDays(selectedProgramId); } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while deleting workout day."); } }
  async function deleteExercise(id: number) { if (selectedProgramId === null || selectedWorkoutDayId === null) return; setError(null); try { const r = await fetch(`${API_BASE_URL}/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${id}`, { method: "DELETE" }); if (!r.ok) throw new Error("Could not delete the exercise."); if (editingExerciseId === id) resetExerciseForm(); await loadExercises(selectedProgramId, selectedWorkoutDayId); } catch (err) { setError(err instanceof Error ? err.message : "Unexpected error while deleting exercise."); } }
  function selectProgram(id: number) { setSelectedProgramId(id); setSelectedWorkoutDayId(null); resetWorkoutDayForm(); resetExerciseForm(); }
  function selectWorkoutDay(id: number) { setSelectedWorkoutDayId(id); resetExerciseForm(); }

  return (
    <main className="app-shell">
      <header className="top-bar"><h1 className="brand">SetPilot</h1><span className="phase-label">AI Import + Program Builder</span></header>
      <section className="dashboard"><div className="intro"><h2>Paste a plan. Make it trainable.</h2><p>SetPilot converts messy workout text into structured programs, workout days, and exercises. Manual editing stays available because AI should assist, not hallucinate with a whistle.</p></div><div className="actions">{["AI Key", "AI Import", "Programs", "Exercises"].map((label) => <button className="action-button" key={label} type="button">{label}<span>Current MVP layer</span></button>)}</div></section>
      {error ? <section className="program-workspace"><p className="error-message global-error">{error}</p></section> : null}

      <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Settings</p><h2>OpenAI API Key</h2></div><p>The key is sent to the backend and kept only in backend memory for this running session. It is not hardcoded and not saved in GitHub.</p></div><div className="program-grid"><form className="program-form" onSubmit={saveOpenAIKey}><h3>AI access</h3><p className="muted">Status: {openAIKeyStatus.configured ? `Configured from ${openAIKeyStatus.source} (${openAIKeyStatus.masked_key})` : "Not configured"}</p><label>API key<input autoComplete="off" onChange={(e) => setOpenAIKeyInput(e.target.value)} placeholder="sk-..." type="password" value={openAIKeyInput} /></label><div className="form-actions"><button className="primary-button" disabled={isSavingKey || !openAIKeyInput.trim()} type="submit">{isSavingKey ? "Saving..." : "Save key for this session"}</button><button className="secondary-button" disabled={isSavingKey} onClick={() => void loadOpenAIKeyStatus()} type="button">Check status</button><button className="danger-button" disabled={isSavingKey || !openAIKeyStatus.configured} onClick={() => void clearOpenAIKey()} type="button">Clear session key</button></div></form><div className="program-list"><h3>Safety rule</h3><p>The browser only sends the key to your local backend. The backend uses it for AI import. When the backend restarts, the session key disappears. For production, this needs real accounts and encrypted storage.</p></div></div></section>

      <section className="program-workspace import-panel"><div className="section-heading"><div><p className="eyebrow">Fast input</p><h2>AI Workout Plan Import</h2></div><p>Paste plain text, analyze it, review the preview, then save it into the existing app structure.</p></div><form className="program-form import-form" onSubmit={analyzeImport}><label>Plain text workout plan<textarea className="import-textarea" onChange={(e) => setImportText(e.target.value)} value={importText} /></label><button className="primary-button" disabled={isAnalyzingImport || !openAIKeyStatus.configured} type="submit">{isAnalyzingImport ? "Analyzing..." : openAIKeyStatus.configured ? "Analyze with AI" : "Add API key first"}</button></form>{importAnalysis ? <div className="program-list import-preview"><div className="list-header"><h3>AI Preview</h3><button className="primary-button compact-button" disabled={isSavingImport} onClick={() => void saveImportedPlan()} type="button">{isSavingImport ? "Saving..." : "Save imported plan"}</button></div><p><strong>{importAnalysis.parsed_plan.program.name}</strong> · {importAnalysis.parsed_plan.program.duration_weeks} weeks · confidence {Math.round(importAnalysis.overall_confidence * 100)}%</p><p>{importAnalysis.parsed_plan.program.goal}</p>{importAnalysis.trainer_review_required ? <p className="warning-pill">Trainer review recommended</p> : null}{importAnalysis.warnings.length > 0 ? <ul>{importAnalysis.warnings.map((w) => <li key={w}>{w}</li>)}</ul> : null}{importAnalysis.questions_for_user.length > 0 ? <ul>{importAnalysis.questions_for_user.map((q) => <li key={q}>{q}</li>)}</ul> : null}<div className="program-cards">{importAnalysis.parsed_plan.workout_days.map((day) => <article className="program-card" key={`${day.day_order}-${day.name}`}><div><h4>Day {day.day_order}: {day.name}</h4>{day.exercises.map((ex) => <p key={`${day.day_order}-${ex.exercise_order}-${ex.movement_name}`}>{ex.exercise_order}. {ex.movement_name}: {ex.sets} × {ex.reps}, rest {ex.rest_seconds}s {ex.warnings.length ? `— ${ex.warnings.join("; ")}` : ""}</p>)}</div></article>)}</div></div> : null}</section>

      <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Layer 1</p><h2>Programs</h2></div><p>Create manually or save from AI import.</p></div><div className="program-grid"><form className="program-form" onSubmit={handleProgramSubmit}><h3>{editingProgramId ? "Edit program" : "Create program"}</h3><label>Program name<input onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })} value={programForm.name} /></label><label>Goal<textarea onChange={(e) => setProgramForm({ ...programForm, goal: e.target.value })} value={programForm.goal} /></label><label>Duration in weeks<input type="number" onChange={(e) => setProgramForm({ ...programForm, duration_weeks: e.target.value })} value={programForm.duration_weeks} /></label><div className="form-actions"><button className="primary-button" type="submit">{editingProgramId ? "Save" : "Create"}</button>{editingProgramId ? <button className="secondary-button" onClick={resetProgramForm} type="button">Cancel</button> : null}</div></form><div className="program-list"><div className="list-header"><h3>Saved programs</h3><button className="text-button" onClick={() => void loadPrograms()} type="button">Refresh</button></div>{isLoadingPrograms ? <p className="muted">Loading...</p> : null}<div className="program-cards">{programs.map((p) => <article className={`program-card${selectedProgramId === p.id ? " selected-card" : ""}`} key={p.id}><div><h4>{p.name}</h4><p>{p.goal}</p><span>{p.duration_weeks} weeks</span></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => selectProgram(p.id)} type="button">{selectedProgramId === p.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => startEditingProgram(p)} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteProgram(p.id)} type="button">Delete</button></div></article>)}</div></div></div></section>

      <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Layer 2</p><h2>Workout Days</h2></div><p>{selectedProgram ? `Selected program: ${selectedProgram.name}` : "Select a program first."}</p></div><div className="program-grid"><form className="program-form" onSubmit={handleWorkoutDaySubmit}><h3>{editingWorkoutDayId ? "Edit day" : "Add day"}</h3><label>Day name<input disabled={selectedProgramId === null} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, name: e.target.value })} value={workoutDayForm.name} /></label><label>Order<input disabled={selectedProgramId === null} type="number" onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, day_order: e.target.value })} value={workoutDayForm.day_order} /></label><div className="form-actions"><button className="primary-button" disabled={selectedProgramId === null} type="submit">{editingWorkoutDayId ? "Save" : "Add"}</button>{editingWorkoutDayId ? <button className="secondary-button" onClick={resetWorkoutDayForm} type="button">Cancel</button> : null}</div></form><div className="program-list"><div className="list-header"><h3>Days</h3><button className="text-button" disabled={selectedProgramId === null} onClick={() => selectedProgramId !== null ? void loadWorkoutDays(selectedProgramId) : undefined} type="button">Refresh</button></div>{isLoadingWorkoutDays ? <p className="muted">Loading...</p> : null}<div className="program-cards">{workoutDays.map((d) => <article className={`program-card workout-day-card${selectedWorkoutDayId === d.id ? " selected-card" : ""}`} key={d.id}><div><h4>{d.name}</h4><p>Day order: {d.day_order}</p></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => selectWorkoutDay(d.id)} type="button">{selectedWorkoutDayId === d.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => startEditingWorkoutDay(d)} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteWorkoutDay(d.id)} type="button">Delete</button></div></article>)}</div></div></div></section>

      <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Layer 3</p><h2>Exercises</h2></div><p>{selectedWorkoutDay ? `Selected day: ${selectedWorkoutDay.name}` : "Select a workout day first."}</p></div><div className="program-grid"><form className="program-form" onSubmit={handleExerciseSubmit}><h3>{editingExerciseId ? "Edit exercise" : "Add exercise"}</h3><label>Movement<input disabled={selectedWorkoutDayId === null} onChange={(e) => setExerciseForm({ ...exerciseForm, movement_name: e.target.value })} value={exerciseForm.movement_name} /></label><div className="inline-fields"><label>Sets<input disabled={selectedWorkoutDayId === null} type="number" onChange={(e) => setExerciseForm({ ...exerciseForm, sets: e.target.value })} value={exerciseForm.sets} /></label><label>Reps<input disabled={selectedWorkoutDayId === null} onChange={(e) => setExerciseForm({ ...exerciseForm, reps: e.target.value })} value={exerciseForm.reps} /></label></div><div className="inline-fields"><label>Rest seconds<input disabled={selectedWorkoutDayId === null} type="number" onChange={(e) => setExerciseForm({ ...exerciseForm, rest_seconds: e.target.value })} value={exerciseForm.rest_seconds} /></label><label>Order<input disabled={selectedWorkoutDayId === null} type="number" onChange={(e) => setExerciseForm({ ...exerciseForm, exercise_order: e.target.value })} value={exerciseForm.exercise_order} /></label></div><label>Notes<textarea disabled={selectedWorkoutDayId === null} onChange={(e) => setExerciseForm({ ...exerciseForm, notes: e.target.value })} value={exerciseForm.notes} /></label><div className="form-actions"><button className="primary-button" disabled={selectedWorkoutDayId === null} type="submit">{editingExerciseId ? "Save" : "Add"}</button>{editingExerciseId ? <button className="secondary-button" onClick={resetExerciseForm} type="button">Cancel</button> : null}</div></form><div className="program-list"><div className="list-header"><h3>Exercises</h3><button className="text-button" disabled={selectedProgramId === null || selectedWorkoutDayId === null} onClick={() => selectedProgramId !== null && selectedWorkoutDayId !== null ? void loadExercises(selectedProgramId, selectedWorkoutDayId) : undefined} type="button">Refresh</button></div>{isLoadingExercises ? <p className="muted">Loading...</p> : null}<div className="program-cards">{exercises.map((e) => <article className="program-card exercise-card" key={e.id}><div><h4>{e.exercise_order}. {e.movement_name}</h4><p>{e.sets} sets × {e.reps} reps · Rest {e.rest_seconds}s</p><span>{e.notes || "No notes"}</span></div><div className="card-actions"><button className="secondary-button compact-button" onClick={() => startEditingExercise(e)} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteExercise(e.id)} type="button">Delete</button></div></article>)}</div></div></div></section>
    </main>
  );
}

export default App;
