import { FormEvent, useEffect, useMemo, useState } from "react";
import "./App.css";

type Program = { id: number; name: string; goal: string; duration_weeks: number; created_at: string };
type WorkoutDay = { id: number; program_id: number; name: string; day_order: number; created_at: string };
type WorkoutExercise = { id: number; workout_day_id: number; movement_name: string; sets: number; reps: string; rest_seconds: number; notes: string; exercise_order: number; created_at: string };
type PlannedSet = { id: number; workout_exercise_id: number; set_number: number; target_reps: string; suggested_weight: number | null; weight_unit: string; note: string; created_at: string };
type YouTubeVideo = { id: number; workout_exercise_id: number; youtube_video_id: string; title: string; channel_name: string; thumbnail_url: string; display_order: number; approved: boolean; created_at: string };
type OpenAIKeyStatus = { configured: boolean; source: string | null; masked_key: string | null };
type AIParsedExercise = { movement_name: string; sets: number; reps: string; rest_seconds: number; notes: string; exercise_order: number; confidence: number; warnings: string[] };
type AIParsedWorkoutDay = { name: string; day_order: number; exercises: AIParsedExercise[] };
type AIParsedPlan = { program: { name: string; goal: string; duration_weeks: number }; workout_days: AIParsedWorkoutDay[] };
type ImportAnalysis = { parsed_plan: AIParsedPlan; overall_confidence: number; warnings: string[]; questions_for_user: string[]; trainer_review_required: boolean };
type ReadinessProfile = { age: number | null; sex: string; height_cm: number | null; weight_kg: number | null; bmi: number | null; training_experience: string; primary_goal: string; energy_level: number; sleep_quality: number; soreness_level: number; stress_level: number; pain_or_limitations: string; available_equipment: string; session_time_limit_minutes: number | null; difficulty_preference: string; extra_notes: string };
type EnhancementResponse = { adjusted_plan: AIParsedPlan; changes: { day_name: string; exercise_name: string | null; change_type: string; original: string; adjusted: string; reason: string }[]; summary: string; warnings: string[]; questions_for_user: string[]; trainer_review_required: boolean };

const API_BASE_URL = "http://127.0.0.1:8000";
const sampleImportText = `Program: Strength Foundation\nDuration: 8 weeks\nGoal: Build strength and muscle\n\nDay 1 - Upper Body\nBench Press - 4 sets - 6-8 reps - 120 sec rest\nLat Pulldown - 3 sets - 10 reps - 90 sec rest\n\nDay 2 - Lower Body\nSquat - 5x5 - 180 sec rest\nRomanian Deadlift - 3x8 - 120 sec rest`;
const defaultReadiness: ReadinessProfile = { age: 45, sex: "", height_cm: 167, weight_kg: 98, bmi: 35.1, training_experience: "intermediate", primary_goal: "strength and fat loss", energy_level: 7, sleep_quality: 7, soreness_level: 4, stress_level: 5, pain_or_limitations: "", available_equipment: "full gym", session_time_limit_minutes: 75, difficulty_preference: "moderate", extra_notes: "" };

function formatApiError(data: unknown, fallback: string): string {
  if (!data) return fallback;
  if (typeof data === "string") return data;
  if (Array.isArray(data)) return data.map((item) => formatApiError(item, fallback)).join("\n");
  if (typeof data === "object") {
    const record = data as { detail?: unknown; message?: unknown; error?: unknown; loc?: unknown[]; msg?: string };
    if (record.detail) return formatApiError(record.detail, fallback);
    if (record.message) return formatApiError(record.message, fallback);
    if (record.error) return formatApiError(record.error, fallback);
    if (record.msg) return `${Array.isArray(record.loc) ? record.loc.join(".") : "field"}: ${record.msg}`;
    return JSON.stringify(data, null, 2);
  }
  return String(data);
}

function extractYouTubeVideoId(input: string): string {
  const value = input.trim();
  if (!value) return "";
  if (/^[a-zA-Z0-9_-]{11}$/.test(value)) return value;

  try {
    const url = new URL(value);
    if (url.hostname.includes("youtu.be")) return url.pathname.split("/").filter(Boolean)[0] ?? "";
    const watchId = url.searchParams.get("v");
    if (watchId) return watchId;
    const parts = url.pathname.split("/").filter(Boolean);
    const markerIndex = parts.findIndex((part) => ["embed", "shorts", "live"].includes(part));
    if (markerIndex >= 0 && parts[markerIndex + 1]) return parts[markerIndex + 1];
    return parts[parts.length - 1] ?? "";
  } catch {
    return value;
  }
}

function App() {
  const [programs, setPrograms] = useState<Program[]>([]);
  const [workoutDays, setWorkoutDays] = useState<WorkoutDay[]>([]);
  const [exercises, setExercises] = useState<WorkoutExercise[]>([]);
  const [plannedSets, setPlannedSets] = useState<PlannedSet[]>([]);
  const [youtubeVideos, setYoutubeVideos] = useState<YouTubeVideo[]>([]);

  const [selectedProgramId, setSelectedProgramId] = useState<number | null>(null);
  const [selectedWorkoutDayId, setSelectedWorkoutDayId] = useState<number | null>(null);
  const [selectedExerciseId, setSelectedExerciseId] = useState<number | null>(null);

  const [programForm, setProgramForm] = useState({ name: "", goal: "", duration_weeks: "8" });
  const [workoutDayForm, setWorkoutDayForm] = useState({ name: "", day_order: "1" });
  const [exerciseForm, setExerciseForm] = useState({ movement_name: "", sets: "3", reps: "8-10", rest_seconds: "90", notes: "", exercise_order: "1" });
  const [plannedSetForm, setPlannedSetForm] = useState({ set_number: "1", target_reps: "8-10", suggested_weight: "", weight_unit: "kg", note: "" });
  const [youtubeForm, setYoutubeForm] = useState({ input: "", title: "", channel_name: "", thumbnail_url: "", display_order: "1" });

  const [editingProgramId, setEditingProgramId] = useState<number | null>(null);
  const [editingWorkoutDayId, setEditingWorkoutDayId] = useState<number | null>(null);
  const [editingExerciseId, setEditingExerciseId] = useState<number | null>(null);
  const [editingPlannedSetId, setEditingPlannedSetId] = useState<number | null>(null);

  const [openAIKeyInput, setOpenAIKeyInput] = useState("");
  const [openAIKeyStatus, setOpenAIKeyStatus] = useState<OpenAIKeyStatus>({ configured: false, source: null, masked_key: null });
  const [importText, setImportText] = useState(sampleImportText);
  const [importAnalysis, setImportAnalysis] = useState<ImportAnalysis | null>(null);
  const [readiness, setReadiness] = useState<ReadinessProfile>(defaultReadiness);
  const [enhancement, setEnhancement] = useState<EnhancementResponse | null>(null);

  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedProgram = useMemo(() => programs.find((p) => p.id === selectedProgramId) ?? null, [programs, selectedProgramId]);
  const selectedWorkoutDay = useMemo(() => workoutDays.find((d) => d.id === selectedWorkoutDayId) ?? null, [workoutDays, selectedWorkoutDayId]);
  const selectedExercise = useMemo(() => exercises.find((e) => e.id === selectedExerciseId) ?? null, [exercises, selectedExerciseId]);
  const computedBmi = useMemo(() => {
    if (!readiness.height_cm || !readiness.weight_kg) return null;
    const meters = readiness.height_cm / 100;
    return Number((readiness.weight_kg / (meters * meters)).toFixed(1));
  }, [readiness.height_cm, readiness.weight_kg]);

  async function api<T>(path: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    const data = await response.json().catch(() => null);
    if (!response.ok) throw new Error(formatApiError(data, `Request failed: ${path}`));
    return data as T;
  }

  async function loadOpenAIKeyStatus() { setOpenAIKeyStatus(await api<OpenAIKeyStatus>("/settings/openai-key")); }
  async function loadPrograms() {
    const data = await api<Program[]>("/programs");
    setPrograms(data);
    setSelectedProgramId((current) => current && data.some((p) => p.id === current) ? current : data[0]?.id ?? null);
  }
  async function loadWorkoutDays(programId: number) {
    const data = await api<WorkoutDay[]>(`/programs/${programId}/workout-days`);
    setWorkoutDays(data);
    setSelectedWorkoutDayId((current) => current && data.some((d) => d.id === current) ? current : data[0]?.id ?? null);
  }
  async function loadExercises(programId: number, workoutDayId: number) {
    const data = await api<WorkoutExercise[]>(`/programs/${programId}/workout-days/${workoutDayId}/exercises`);
    setExercises(data);
    setSelectedExerciseId((current) => current && data.some((e) => e.id === current) ? current : data[0]?.id ?? null);
  }
  async function loadPlannedSets(exerciseId: number) { setPlannedSets(await api<PlannedSet[]>(`/exercises/${exerciseId}/planned-sets`)); }
  async function loadYouTubeVideos(exerciseId: number) { setYoutubeVideos(await api<YouTubeVideo[]>(`/exercises/${exerciseId}/youtube-videos`)); }

  useEffect(() => { void loadOpenAIKeyStatus().catch((e) => setError(e.message)); void loadPrograms().catch((e) => setError(e.message)); }, []);
  useEffect(() => {
    if (selectedProgramId === null) { setWorkoutDays([]); setSelectedWorkoutDayId(null); setExercises([]); setSelectedExerciseId(null); setPlannedSets([]); setYoutubeVideos([]); return; }
    void loadWorkoutDays(selectedProgramId).catch((e) => setError(e.message));
  }, [selectedProgramId]);
  useEffect(() => {
    if (selectedProgramId === null || selectedWorkoutDayId === null) { setExercises([]); setSelectedExerciseId(null); setPlannedSets([]); setYoutubeVideos([]); return; }
    void loadExercises(selectedProgramId, selectedWorkoutDayId).catch((e) => setError(e.message));
  }, [selectedProgramId, selectedWorkoutDayId]);
  useEffect(() => {
    if (selectedExerciseId === null) { setPlannedSets([]); setYoutubeVideos([]); return; }
    void loadPlannedSets(selectedExerciseId).catch((e) => setError(e.message));
    void loadYouTubeVideos(selectedExerciseId).catch((e) => setError(e.message));
  }, [selectedExerciseId]);
  useEffect(() => { setReadiness((current) => ({ ...current, bmi: computedBmi })); }, [computedBmi]);

  async function saveOpenAIKey(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setLoading("Saving key");
    try { setOpenAIKeyStatus(await api<OpenAIKeyStatus>("/settings/openai-key", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ api_key: openAIKeyInput }) })); setOpenAIKeyInput(""); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save key."); }
    finally { setLoading(null); }
  }
  async function clearOpenAIKey() { setError(null); setLoading("Clearing key"); try { setOpenAIKeyStatus(await api<OpenAIKeyStatus>("/settings/openai-key", { method: "DELETE" })); } catch (e) { setError(e instanceof Error ? e.message : "Could not clear key."); } finally { setLoading(null); } }
  async function analyzeImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setEnhancement(null); setImportAnalysis(null); setLoading("Extracting plan");
    try { setImportAnalysis(await api<ImportAnalysis>("/imports/workout-plan/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ raw_text: importText }) })); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not analyze workout plan."); }
    finally { setLoading(null); }
  }
  async function enhancePlan() {
    if (!importAnalysis) return;
    setError(null); setEnhancement(null); setLoading("Enhancing plan");
    try { setEnhancement(await api<EnhancementResponse>("/imports/workout-plan/enhance", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ parsed_plan: importAnalysis.parsed_plan, readiness }) })); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not enhance workout plan."); }
    finally { setLoading(null); }
  }
  async function savePlan(plan: AIParsedPlan, approvalStatus: string) {
    setError(null); setLoading("Saving plan");
    try { const saved = await api<{ program: Program }>("/imports/workout-plan/save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ parsed_plan: plan, approval_status: approvalStatus }) }); setSelectedProgramId(saved.program.id); await loadPrograms(); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save plan."); }
    finally { setLoading(null); }
  }

  async function handleProgramSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); const payload = { name: programForm.name.trim(), goal: programForm.goal.trim(), duration_weeks: Number(programForm.duration_weeks) };
    const url = editingProgramId ? `/programs/${editingProgramId}` : "/programs";
    const method = editingProgramId ? "PUT" : "POST";
    try { const saved = await api<Program>(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); setEditingProgramId(null); setProgramForm({ name: "", goal: "", duration_weeks: "8" }); setSelectedProgramId(saved.id); await loadPrograms(); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save program."); }
  }
  async function handleWorkoutDaySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (selectedProgramId === null) return;
    const payload = { name: workoutDayForm.name.trim(), day_order: Number(workoutDayForm.day_order) };
    const url = editingWorkoutDayId ? `/programs/${selectedProgramId}/workout-days/${editingWorkoutDayId}` : `/programs/${selectedProgramId}/workout-days`;
    const method = editingWorkoutDayId ? "PUT" : "POST";
    try { const saved = await api<WorkoutDay>(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); setEditingWorkoutDayId(null); setWorkoutDayForm({ name: "", day_order: "1" }); setSelectedWorkoutDayId(saved.id); await loadWorkoutDays(selectedProgramId); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save day."); }
  }
  async function handleExerciseSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (selectedProgramId === null || selectedWorkoutDayId === null) return;
    const payload = { movement_name: exerciseForm.movement_name.trim(), sets: Number(exerciseForm.sets), reps: exerciseForm.reps.trim(), rest_seconds: Number(exerciseForm.rest_seconds), notes: exerciseForm.notes.trim(), exercise_order: Number(exerciseForm.exercise_order) };
    const url = editingExerciseId ? `/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${editingExerciseId}` : `/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises`;
    const method = editingExerciseId ? "PUT" : "POST";
    try { const saved = await api<WorkoutExercise>(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); setEditingExerciseId(null); setExerciseForm({ movement_name: "", sets: "3", reps: "8-10", rest_seconds: "90", notes: "", exercise_order: "1" }); selectExercise(saved); await loadExercises(selectedProgramId, selectedWorkoutDayId); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save exercise."); }
  }
  async function handlePlannedSetSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (selectedExerciseId === null) return;
    const payload = { set_number: Number(plannedSetForm.set_number), target_reps: plannedSetForm.target_reps.trim(), suggested_weight: plannedSetForm.suggested_weight ? Number(plannedSetForm.suggested_weight) : null, weight_unit: plannedSetForm.weight_unit, note: plannedSetForm.note.trim() };
    const url = editingPlannedSetId ? `/exercises/${selectedExerciseId}/planned-sets/${editingPlannedSetId}` : `/exercises/${selectedExerciseId}/planned-sets`;
    const method = editingPlannedSetId ? "PUT" : "POST";
    try { await api<PlannedSet>(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); setEditingPlannedSetId(null); setPlannedSetForm({ set_number: String(Number(plannedSetForm.set_number || "0") + 1), target_reps: selectedExercise?.reps ?? "8-10", suggested_weight: "", weight_unit: "kg", note: "" }); await loadPlannedSets(selectedExerciseId); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save planned set."); }
  }
  async function handleYouTubeSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); if (selectedExerciseId === null) return;
    const youtube_video_id = extractYouTubeVideoId(youtubeForm.input);
    if (!youtube_video_id) { setError("Paste a YouTube video ID or link first."); return; }
    const payload = {
      youtube_video_id,
      title: youtubeForm.title.trim() || `${selectedExercise?.movement_name ?? "Exercise"} example`,
      channel_name: youtubeForm.channel_name.trim(),
      thumbnail_url: youtubeForm.thumbnail_url.trim() || `https://img.youtube.com/vi/${youtube_video_id}/hqdefault.jpg`,
      display_order: Number(youtubeForm.display_order || youtubeVideos.length + 1),
      approved: true,
    };
    try { await api<YouTubeVideo>(`/exercises/${selectedExerciseId}/youtube-videos`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); setYoutubeForm({ input: "", title: "", channel_name: "", thumbnail_url: "", display_order: String(youtubeVideos.length + 2) }); await loadYouTubeVideos(selectedExerciseId); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save YouTube video."); }
  }
  async function findYouTubeExamples() {
    if (selectedExerciseId === null) return;
    setError(null); setLoading("Finding YouTube examples");
    try { await api<YouTubeVideo[]>(`/exercises/${selectedExerciseId}/youtube-videos/search-and-save`, { method: "POST" }); await loadYouTubeVideos(selectedExerciseId); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not find YouTube examples."); }
    finally { setLoading(null); }
  }

  async function deleteProgram(id: number) { await api(`/programs/${id}`, { method: "DELETE" }); await loadPrograms(); }
  async function deleteWorkoutDay(id: number) { if (selectedProgramId !== null) { await api(`/programs/${selectedProgramId}/workout-days/${id}`, { method: "DELETE" }); await loadWorkoutDays(selectedProgramId); } }
  async function deleteExercise(id: number) { if (selectedProgramId !== null && selectedWorkoutDayId !== null) { await api(`/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${id}`, { method: "DELETE" }); await loadExercises(selectedProgramId, selectedWorkoutDayId); } }
  async function deletePlannedSet(id: number) { if (selectedExerciseId !== null) { await api(`/exercises/${selectedExerciseId}/planned-sets/${id}`, { method: "DELETE" }); await loadPlannedSets(selectedExerciseId); } }
  async function deleteYouTubeVideo(id: number) { if (selectedExerciseId !== null) { await api(`/exercises/${selectedExerciseId}/youtube-videos/${id}`, { method: "DELETE" }); await loadYouTubeVideos(selectedExerciseId); } }

  function updateReadiness<K extends keyof ReadinessProfile>(key: K, value: ReadinessProfile[K]) { setReadiness((current) => ({ ...current, [key]: value })); }
  function selectExercise(exercise: WorkoutExercise) { setSelectedExerciseId(exercise.id); setPlannedSetForm({ set_number: "1", target_reps: exercise.reps, suggested_weight: "", weight_unit: "kg", note: "" }); setYoutubeForm({ input: "", title: "", channel_name: "", thumbnail_url: "", display_order: "1" }); }
  function renderPlan(plan: AIParsedPlan) { return <div className="program-cards">{plan.workout_days.map((day) => <article className="program-card" key={`${day.day_order}-${day.name}`}><div><h4>Day {day.day_order}: {day.name}</h4>{day.exercises.map((ex) => <p key={`${day.name}-${ex.exercise_order}-${ex.movement_name}`}>{ex.exercise_order}. {ex.movement_name}: {ex.sets} × {ex.reps}, rest {ex.rest_seconds}s {ex.notes ? `— ${ex.notes}` : ""}</p>)}</div></article>)}</div>; }

  return <main className="app-shell">
    <header className="top-bar"><h1 className="brand">SetPilot</h1><span className="phase-label">Extract → Enhance → Weights → Videos</span></header>
    <section className="dashboard"><div className="intro"><h2>Paste chaos. Train with structure.</h2><p>Extract the plan, enhance it, prepare set-level weights, and attach video examples. Investor brain says: this is becoming a gym operating system, not another sad tracker.</p></div><div className="actions">{["API Key", "Extract", "Enhance", "Videos"].map((label) => <button className="action-button" key={label} type="button">{label}<span>Current workflow</span></button>)}</div></section>
    {error ? <section className="program-workspace"><p className="error-message global-error">{error}</p></section> : null}
    {loading ? <section className="program-workspace"><p className="global-error">{loading}... High-reasoning/API calls may take time. The beast is working, not sleeping.</p></section> : null}

    <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Settings</p><h2>OpenAI API Key</h2></div><p>Session-only backend storage. No GitHub leak. No front-door key under the doormat.</p></div><div className="program-grid"><form className="program-form" onSubmit={saveOpenAIKey}><h3>AI access</h3><p className="muted">Status: {openAIKeyStatus.configured ? `Configured from ${openAIKeyStatus.source} (${openAIKeyStatus.masked_key})` : "Not configured"}</p><label>API key<input autoComplete="off" type="password" value={openAIKeyInput} onChange={(e) => setOpenAIKeyInput(e.target.value)} /></label><div className="form-actions"><button className="primary-button" disabled={!openAIKeyInput.trim()} type="submit">Save key</button><button className="secondary-button" type="button" onClick={() => void loadOpenAIKeyStatus()}>Check</button><button className="danger-button" type="button" onClick={() => void clearOpenAIKey()}>Clear</button></div></form><div className="program-list"><h3>Workflow rule</h3><p>Extraction stays faithful. Enhancement is optional. Videos are stored per exercise so we do not keep searching like quota-burning maniacs.</p></div></div></section>

    <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Step 1</p><h2>AI Workout Plan Import</h2></div><p>Pure extraction. No coaching. No judging. No creative nonsense.</p></div><form className="program-form import-form" onSubmit={analyzeImport}><label>Plain text workout plan<textarea className="import-textarea" value={importText} onChange={(e) => setImportText(e.target.value)} /></label><button className="primary-button" disabled={!openAIKeyStatus.configured || loading !== null} type="submit">{openAIKeyStatus.configured ? "Extract plan" : "Add API key first"}</button></form>{importAnalysis ? <div className="program-list import-preview"><div className="list-header"><h3>Extracted Plan Preview</h3><button className="primary-button compact-button" onClick={() => void savePlan(importAnalysis.parsed_plan, "approved_extracted_plan")}>Save extracted plan</button></div><p><strong>{importAnalysis.parsed_plan.program.name}</strong> · {importAnalysis.parsed_plan.program.duration_weeks} weeks · extraction confidence {Math.round(importAnalysis.overall_confidence * 100)}%</p><p>{importAnalysis.parsed_plan.program.goal}</p>{importAnalysis.trainer_review_required ? <p className="warning-pill">Review recommended because extraction used assumptions or ambiguity exists.</p> : null}{renderPlan(importAnalysis.parsed_plan)}</div> : null}</section>

    {importAnalysis ? <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Step 2</p><h2>Enhance Based on Profile & Readiness</h2></div><p>Optional adjustment. BMI is calculated as context, not a verdict. The app is not a judgmental bathroom scale with Wi‑Fi.</p></div><div className="program-grid"><div className="program-form"><h3>Trainee profile</h3><div className="inline-fields"><label>Age<input type="number" value={readiness.age ?? ""} onChange={(e) => updateReadiness("age", e.target.value ? Number(e.target.value) : null)} /></label><label>Sex / optional<input value={readiness.sex} onChange={(e) => updateReadiness("sex", e.target.value)} /></label></div><div className="inline-fields"><label>Height cm<input type="number" value={readiness.height_cm ?? ""} onChange={(e) => updateReadiness("height_cm", e.target.value ? Number(e.target.value) : null)} /></label><label>Weight kg<input type="number" value={readiness.weight_kg ?? ""} onChange={(e) => updateReadiness("weight_kg", e.target.value ? Number(e.target.value) : null)} /></label></div><p className="muted">Calculated BMI: {computedBmi ?? "add height and weight"}</p><h3>Readiness</h3><div className="inline-fields"><label>Experience<input value={readiness.training_experience} onChange={(e) => updateReadiness("training_experience", e.target.value)} /></label><label>Goal<input value={readiness.primary_goal} onChange={(e) => updateReadiness("primary_goal", e.target.value)} /></label></div><div className="inline-fields"><label>Energy 1-10<input type="number" min="1" max="10" value={readiness.energy_level} onChange={(e) => updateReadiness("energy_level", Number(e.target.value))} /></label><label>Sleep 1-10<input type="number" min="1" max="10" value={readiness.sleep_quality} onChange={(e) => updateReadiness("sleep_quality", Number(e.target.value))} /></label></div><div className="inline-fields"><label>Soreness 1-10<input type="number" min="1" max="10" value={readiness.soreness_level} onChange={(e) => updateReadiness("soreness_level", Number(e.target.value))} /></label><label>Stress 1-10<input type="number" min="1" max="10" value={readiness.stress_level} onChange={(e) => updateReadiness("stress_level", Number(e.target.value))} /></label></div><div className="inline-fields"><label>Difficulty<input value={readiness.difficulty_preference} onChange={(e) => updateReadiness("difficulty_preference", e.target.value)} /></label><label>Time limit minutes<input type="number" value={readiness.session_time_limit_minutes ?? ""} onChange={(e) => updateReadiness("session_time_limit_minutes", e.target.value ? Number(e.target.value) : null)} /></label></div><label>Limitations / difficulties<textarea value={readiness.pain_or_limitations} onChange={(e) => updateReadiness("pain_or_limitations", e.target.value)} /></label><label>Available equipment<textarea value={readiness.available_equipment} onChange={(e) => updateReadiness("available_equipment", e.target.value)} /></label><label>Extra notes<textarea value={readiness.extra_notes} onChange={(e) => updateReadiness("extra_notes", e.target.value)} /></label><button className="primary-button" disabled={loading !== null} type="button" onClick={() => void enhancePlan()}>Enhance plan</button></div><div className="program-list"><h3>Enhancement promise</h3><p>The adjusted plan is a proposal. Original extraction remains untouched. Save adjusted version only after review.</p></div></div>{enhancement ? <div className="program-list import-preview"><div className="list-header"><h3>Adjusted Plan Preview</h3><button className="primary-button compact-button" onClick={() => void savePlan(enhancement.adjusted_plan, "approved_adjusted_plan")}>Save adjusted plan</button></div><p>{enhancement.summary}</p>{enhancement.trainer_review_required ? <p className="warning-pill">Trainer review recommended.</p> : null}<h4>Changes</h4>{enhancement.changes.length ? <ul>{enhancement.changes.map((change, index) => <li key={`${change.day_name}-${change.change_type}-${index}`}><strong>{change.change_type}</strong> — {change.original} → {change.adjusted}. {change.reason}</li>)}</ul> : <p>No major changes proposed.</p>}{renderPlan(enhancement.adjusted_plan)}</div> : null}</section> : null}

    <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Manual editor</p><h2>Programs</h2></div><p>Create manually or save from AI import/enhancement.</p></div><div className="program-grid"><form className="program-form" onSubmit={handleProgramSubmit}><h3>{editingProgramId ? "Edit program" : "Create program"}</h3><label>Program name<input value={programForm.name} onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })} /></label><label>Goal<textarea value={programForm.goal} onChange={(e) => setProgramForm({ ...programForm, goal: e.target.value })} /></label><label>Duration weeks<input type="number" value={programForm.duration_weeks} onChange={(e) => setProgramForm({ ...programForm, duration_weeks: e.target.value })} /></label><button className="primary-button" type="submit">{editingProgramId ? "Save" : "Create"}</button></form><div className="program-list"><h3>Saved programs</h3><div className="program-cards">{programs.map((p) => <article className={`program-card${selectedProgramId === p.id ? " selected-card" : ""}`} key={p.id}><div><h4>{p.name}</h4><p>{p.goal}</p><span>{p.duration_weeks} weeks</span></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => setSelectedProgramId(p.id)} type="button">{selectedProgramId === p.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingProgramId(p.id); setProgramForm({ name: p.name, goal: p.goal, duration_weeks: String(p.duration_weeks) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteProgram(p.id)} type="button">Delete</button></div></article>)}</div></div></div></section>

    <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Manual editor</p><h2>Workout Days, Exercises, Weights & Videos</h2></div><p>{selectedProgram ? `Selected program: ${selectedProgram.name}` : "Select a program first."}</p></div><div className="program-grid"><form className="program-form" onSubmit={handleWorkoutDaySubmit}><h3>{editingWorkoutDayId ? "Edit day" : "Add day"}</h3><label>Day name<input disabled={selectedProgramId === null} value={workoutDayForm.name} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, name: e.target.value })} /></label><label>Order<input disabled={selectedProgramId === null} type="number" value={workoutDayForm.day_order} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, day_order: e.target.value })} /></label><button className="primary-button" disabled={selectedProgramId === null} type="submit">{editingWorkoutDayId ? "Save day" : "Add day"}</button></form><div className="program-list"><h3>Days</h3><div className="program-cards">{workoutDays.map((d) => <article className={`program-card${selectedWorkoutDayId === d.id ? " selected-card" : ""}`} key={d.id}><div><h4>{d.name}</h4><p>Order: {d.day_order}</p></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => setSelectedWorkoutDayId(d.id)} type="button">{selectedWorkoutDayId === d.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingWorkoutDayId(d.id); setWorkoutDayForm({ name: d.name, day_order: String(d.day_order) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteWorkoutDay(d.id)} type="button">Delete</button></div></article>)}</div></div></div>

      <div className="program-grid"><form className="program-form" onSubmit={handleExerciseSubmit}><h3>{editingExerciseId ? "Edit exercise" : "Add exercise"}</h3><label>Movement<input disabled={selectedWorkoutDayId === null} value={exerciseForm.movement_name} onChange={(e) => setExerciseForm({ ...exerciseForm, movement_name: e.target.value })} /></label><div className="inline-fields"><label>Sets<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.sets} onChange={(e) => setExerciseForm({ ...exerciseForm, sets: e.target.value })} /></label><label>Reps<input disabled={selectedWorkoutDayId === null} value={exerciseForm.reps} onChange={(e) => setExerciseForm({ ...exerciseForm, reps: e.target.value })} /></label></div><div className="inline-fields"><label>Rest seconds<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.rest_seconds} onChange={(e) => setExerciseForm({ ...exerciseForm, rest_seconds: e.target.value })} /></label><label>Order<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.exercise_order} onChange={(e) => setExerciseForm({ ...exerciseForm, exercise_order: e.target.value })} /></label></div><label>Notes<textarea disabled={selectedWorkoutDayId === null} value={exerciseForm.notes} onChange={(e) => setExerciseForm({ ...exerciseForm, notes: e.target.value })} /></label><button className="primary-button" disabled={selectedWorkoutDayId === null} type="submit">{editingExerciseId ? "Save exercise" : "Add exercise"}</button></form><div className="program-list"><h3>Exercises {selectedWorkoutDay ? `for ${selectedWorkoutDay.name}` : ""}</h3><div className="program-cards">{exercises.map((e) => <article className={`program-card exercise-card${selectedExerciseId === e.id ? " selected-card" : ""}`} key={e.id}><div><h4>{e.exercise_order}. {e.movement_name}</h4><p>{e.sets} sets × {e.reps} · Rest {e.rest_seconds}s</p><span>{e.notes || "No notes"}</span></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => selectExercise(e)} type="button">{selectedExerciseId === e.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingExerciseId(e.id); setExerciseForm({ movement_name: e.movement_name, sets: String(e.sets), reps: e.reps, rest_seconds: String(e.rest_seconds), notes: e.notes, exercise_order: String(e.exercise_order) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteExercise(e.id)} type="button">Delete</button></div></article>)}</div></div></div>

      <div className="program-grid"><form className="program-form" onSubmit={handlePlannedSetSubmit}><h3>{editingPlannedSetId ? "Edit planned set" : "Add planned set weight"}</h3><p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none"}</p><div className="inline-fields"><label>Set number<input disabled={selectedExerciseId === null} type="number" value={plannedSetForm.set_number} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, set_number: e.target.value })} /></label><label>Target reps<input disabled={selectedExerciseId === null} value={plannedSetForm.target_reps} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, target_reps: e.target.value })} /></label></div><div className="inline-fields"><label>Suggested weight<input disabled={selectedExerciseId === null} list="weight-options" type="number" step="0.5" value={plannedSetForm.suggested_weight} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, suggested_weight: e.target.value })} /><datalist id="weight-options"><option value="20" /><option value="30" /><option value="40" /><option value="50" /><option value="60" /><option value="80" /><option value="100" /></datalist></label><label>Unit<select disabled={selectedExerciseId === null} value={plannedSetForm.weight_unit} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, weight_unit: e.target.value })}><option value="kg">kg</option><option value="lb">lb</option><option value="bodyweight">bodyweight</option></select></label></div><label>Note<textarea disabled={selectedExerciseId === null} value={plannedSetForm.note} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, note: e.target.value })} /></label><button className="primary-button" disabled={selectedExerciseId === null} type="submit">{editingPlannedSetId ? "Save planned set" : "Add planned set"}</button></form><div className="program-list"><h3>Planned set weights</h3>{selectedExercise ? <p className="muted">For {selectedExercise.movement_name}</p> : <p className="empty-state">Select an exercise first. Weights without an exercise are just numbers doing cosplay.</p>}<div className="program-cards">{plannedSets.map((set) => <article className="program-card" key={set.id}><div><h4>Set {set.set_number}</h4><p>{set.target_reps} reps · {set.suggested_weight ?? "—"} {set.weight_unit}</p><span>{set.note || "No note"}</span></div><div className="card-actions"><button className="secondary-button compact-button" onClick={() => { setEditingPlannedSetId(set.id); setPlannedSetForm({ set_number: String(set.set_number), target_reps: set.target_reps, suggested_weight: set.suggested_weight === null ? "" : String(set.suggested_weight), weight_unit: set.weight_unit, note: set.note }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deletePlannedSet(set.id)} type="button">Delete</button></div></article>)}</div></div></div>

      <div className="program-grid"><form className="program-form" onSubmit={handleYouTubeSubmit}><h3>Add YouTube example</h3><p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none"}</p><button className="secondary-button" disabled={selectedExerciseId === null || loading !== null} type="button" onClick={() => void findYouTubeExamples()}>Find YouTube examples automatically</button><label>YouTube link or video ID<input disabled={selectedExerciseId === null} placeholder="https://youtu.be/... or video ID" value={youtubeForm.input} onChange={(e) => setYoutubeForm({ ...youtubeForm, input: e.target.value })} /></label><label>Title<input disabled={selectedExerciseId === null} placeholder="Bench Press tutorial" value={youtubeForm.title} onChange={(e) => setYoutubeForm({ ...youtubeForm, title: e.target.value })} /></label><div className="inline-fields"><label>Channel<input disabled={selectedExerciseId === null} value={youtubeForm.channel_name} onChange={(e) => setYoutubeForm({ ...youtubeForm, channel_name: e.target.value })} /></label><label>Order<input disabled={selectedExerciseId === null} type="number" value={youtubeForm.display_order} onChange={(e) => setYoutubeForm({ ...youtubeForm, display_order: e.target.value })} /></label></div><label>Thumbnail URL optional<input disabled={selectedExerciseId === null} value={youtubeForm.thumbnail_url} onChange={(e) => setYoutubeForm({ ...youtubeForm, thumbnail_url: e.target.value })} /></label><button className="primary-button" disabled={selectedExerciseId === null} type="submit">Add video manually</button></form><div className="program-list"><h3>YouTube examples</h3>{selectedExercise ? <p className="muted">Stored videos for {selectedExercise.movement_name}</p> : <p className="empty-state">Select an exercise first. Videos need a movement, not vibes.</p>}<div className="video-grid">{youtubeVideos.map((video) => <article className="video-card" key={video.id}><iframe className="video-frame" src={`https://www.youtube.com/embed/${video.youtube_video_id}`} title={video.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen /><div className="video-meta"><h4>{video.title}</h4><p>{video.channel_name || "Unknown channel"}</p><button className="danger-button compact-button" onClick={() => void deleteYouTubeVideo(video.id)} type="button">Remove</button></div></article>)}</div></div></div>
    </section>
  </main>;
}

export default App;
