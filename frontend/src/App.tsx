import { FormEvent, useEffect, useMemo, useState } from "react";
import "./App.css";

type Program = { id: number; name: string; goal: string; duration_weeks: number; created_at: string };
type WorkoutDay = { id: number; program_id: number; name: string; day_order: number; created_at: string };
type WorkoutExercise = { id: number; workout_day_id: number; movement_name: string; sets: number; reps: string; rest_seconds: number; notes: string; exercise_order: number; created_at: string };
type PlannedSet = { id: number; workout_exercise_id: number; set_number: number; target_reps: string; suggested_weight: number | null; weight_unit: string; note: string; created_at: string };
type SessionSet = { id: number; workout_session_id: number; workout_exercise_id: number; set_number: number; planned_reps: string; planned_weight: number | null; actual_reps: number | null; actual_weight: number | null; weight_unit: string; difficulty_rating: number | null; completed: boolean; rest_seconds_used: number | null; notes: string; created_at: string };
type WorkoutSession = { id: number; program_id: number; workout_day_id: number; started_at: string; finished_at: string | null; readiness_score: number | null; notes: string; status: string; session_sets: SessionSet[] };
type YouTubeVideo = { id: number; workout_exercise_id: number; youtube_video_id: string; title: string; channel_name: string; thumbnail_url: string; display_order: number; approved: boolean; created_at: string };
type OpenAIKeyStatus = { configured: boolean; source: string | null; masked_key: string | null };
type AIParsedExercise = { movement_name: string; sets: number; reps: string; rest_seconds: number; notes: string; exercise_order: number; confidence: number; warnings: string[] };
type AIParsedWorkoutDay = { name: string; day_order: number; exercises: AIParsedExercise[] };
type AIParsedPlan = { program: { name: string; goal: string; duration_weeks: number }; workout_days: AIParsedWorkoutDay[] };
type ImportAnalysis = { parsed_plan: AIParsedPlan; overall_confidence: number; warnings: string[]; questions_for_user: string[]; trainer_review_required: boolean };
type ReadinessProfile = { age: number | null; sex: string; height_cm: number | null; weight_kg: number | null; bmi: number | null; training_experience: string; primary_goal: string; energy_level: number; sleep_quality: number; soreness_level: number; stress_level: number; pain_or_limitations: string; available_equipment: string; session_time_limit_minutes: number | null; difficulty_preference: string; extra_notes: string };
type EnhancementResponse = { adjusted_plan: AIParsedPlan; changes: { day_name: string; exercise_name: string | null; change_type: string; original: string; adjusted: string; reason: string }[]; summary: string; warnings: string[]; questions_for_user: string[]; trainer_review_required: boolean };
type ActiveView = "dashboard" | "import" | "enhance" | "programs" | "training" | "settings";

const API_BASE_URL = "http://127.0.0.1:8000";
const sampleImportText = `Program: Strength Foundation\nDuration: 8 weeks\nGoal: Build strength and muscle\n\nDay 1 - Upper Body\nBench Press - 4 sets - 6-8 reps - 120 sec rest\nLat Pulldown - 3 sets - 10 reps - 90 sec rest\n\nDay 2 - Lower Body\nSquat - 5x5 - 180 sec rest\nRomanian Deadlift - 3x8 - 120 sec rest`;
const defaultReadiness: ReadinessProfile = { age: 45, sex: "", height_cm: 167, weight_kg: 98, bmi: 35.1, training_experience: "intermediate", primary_goal: "strength and fat loss", energy_level: 7, sleep_quality: 7, soreness_level: 4, stress_level: 5, pain_or_limitations: "", available_equipment: "full gym", session_time_limit_minutes: 75, difficulty_preference: "moderate", extra_notes: "" };
const navItems: { id: ActiveView; label: string; subtitle: string }[] = [
  { id: "dashboard", label: "Dashboard", subtitle: "mission control" },
  { id: "import", label: "Import", subtitle: "extract chaos" },
  { id: "enhance", label: "Enhance", subtitle: "readiness brain" },
  { id: "training", label: "Training", subtitle: "sets + videos" },
  { id: "programs", label: "Programs", subtitle: "library" },
  { id: "settings", label: "Settings", subtitle: "keys" },
];

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

function summarizeSession(session: WorkoutSession) {
  const completedSets = session.session_sets.filter((set) => set.completed);
  const exerciseIds = new Set(completedSets.map((set) => set.workout_exercise_id));
  const ratings = completedSets.map((set) => set.difficulty_rating).filter((rating): rating is number => rating !== null);
  const averageDifficulty = ratings.length ? ratings.reduce((sum, rating) => sum + rating, 0) / ratings.length : null;
  return {
    totalSets: session.session_sets.length,
    completedSets: completedSets.length,
    exercisesTouched: exerciseIds.size,
    averageDifficulty,
  };
}

function App() {
  const [activeView, setActiveView] = useState<ActiveView>("dashboard");
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
  const [sessionSetForm, setSessionSetForm] = useState({ set_number: "1", actual_reps: "", actual_weight: "", difficulty_rating: "", notes: "" });
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
  const [activeSession, setActiveSession] = useState<WorkoutSession | null>(null);
  const [recentSessions, setRecentSessions] = useState<WorkoutSession[]>([]);
  const [selectedSessionDetail, setSelectedSessionDetail] = useState<WorkoutSession | null>(null);
  const [sessionFinishedMessage, setSessionFinishedMessage] = useState<string | null>(null);
  const [restSuggestionSeconds, setRestSuggestionSeconds] = useState<number | null>(null);
  const [restTimerSeconds, setRestTimerSeconds] = useState<number | null>(null);
  const [restTimerRunning, setRestTimerRunning] = useState(false);
  const [restTimerMessage, setRestTimerMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectedProgram = useMemo(() => programs.find((p) => p.id === selectedProgramId) ?? null, [programs, selectedProgramId]);
  const selectedWorkoutDay = useMemo(() => workoutDays.find((d) => d.id === selectedWorkoutDayId) ?? null, [workoutDays, selectedWorkoutDayId]);
  const selectedExercise = useMemo(() => exercises.find((e) => e.id === selectedExerciseId) ?? null, [exercises, selectedExerciseId]);
  const selectedPlannedSet = useMemo(() => plannedSets.find((set) => set.set_number === Number(sessionSetForm.set_number)) ?? null, [plannedSets, sessionSetForm.set_number]);
  const computedBmi = useMemo(() => {
    if (!readiness.height_cm || !readiness.weight_kg) return null;
    const meters = readiness.height_cm / 100;
    return Number((readiness.weight_kg / (meters * meters)).toFixed(1));
  }, [readiness.height_cm, readiness.weight_kg]);
  const readinessScore = Math.round((readiness.energy_level + readiness.sleep_quality + (11 - readiness.soreness_level) + (11 - readiness.stress_level)) / 4);
  const totalExercises = exercises.length;
  const totalVideos = youtubeVideos.length;
  const activeSessionSummary = useMemo(() => {
    if (!activeSession || activeSession.status !== "completed") return null;
    return summarizeSession(activeSession);
  }, [activeSession]);

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
  async function loadRecentSessions() { setRecentSessions(await api<WorkoutSession[]>("/sessions/recent")); }
  async function loadSessionDetail(sessionId: number) {
    setError(null); setLoading("Loading session detail");
    try { setSelectedSessionDetail(await api<WorkoutSession>(`/sessions/${sessionId}`)); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not load session detail."); }
    finally { setLoading(null); }
  }

  useEffect(() => { void loadOpenAIKeyStatus().catch((e) => setError(e.message)); void loadPrograms().catch((e) => setError(e.message)); void loadRecentSessions().catch((e) => setError(e.message)); }, []);
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
  useEffect(() => {
    if (!restTimerRunning || restTimerSeconds === null) return;
    if (restTimerSeconds <= 0) {
      setRestTimerRunning(false);
      setRestTimerMessage("Rest complete. Next set is ready.");
      return;
    }

    const timerId = window.setInterval(() => {
      setRestTimerSeconds((current) => current === null ? current : Math.max(current - 1, 0));
    }, 1000);

    return () => window.clearInterval(timerId);
  }, [restTimerRunning, restTimerSeconds]);

  async function saveOpenAIKey(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setLoading("Saving key");
    try { setOpenAIKeyStatus(await api<OpenAIKeyStatus>("/settings/openai-key", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ api_key: openAIKeyInput }) })); setOpenAIKeyInput(""); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save key."); }
    finally { setLoading(null); }
  }
  async function clearOpenAIKey() { setError(null); setLoading("Clearing key"); try { setOpenAIKeyStatus(await api<OpenAIKeyStatus>("/settings/openai-key", { method: "DELETE" })); } catch (e) { setError(e instanceof Error ? e.message : "Could not clear key."); } finally { setLoading(null); } }
  async function analyzeImport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(null); setEnhancement(null); setImportAnalysis(null); setLoading("Extracting plan");
    try { setImportAnalysis(await api<ImportAnalysis>("/imports/workout-plan/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ raw_text: importText }) })); setActiveView("import"); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not analyze workout plan."); }
    finally { setLoading(null); }
  }
  async function enhancePlan() {
    if (!importAnalysis) return;
    setError(null); setEnhancement(null); setLoading("Enhancing plan");
    try { setEnhancement(await api<EnhancementResponse>("/imports/workout-plan/enhance", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ parsed_plan: importAnalysis.parsed_plan, readiness }) })); setActiveView("enhance"); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not enhance workout plan."); }
    finally { setLoading(null); }
  }
  async function savePlan(plan: AIParsedPlan, approvalStatus: string) {
    setError(null); setLoading("Saving plan");
    try { const saved = await api<{ program: Program }>("/imports/workout-plan/save", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ parsed_plan: plan, approval_status: approvalStatus }) }); setSelectedProgramId(saved.program.id); await loadPrograms(); setActiveView("dashboard"); }
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
    const payload = { youtube_video_id, title: youtubeForm.title.trim() || `${selectedExercise?.movement_name ?? "Exercise"} example`, channel_name: youtubeForm.channel_name.trim(), thumbnail_url: youtubeForm.thumbnail_url.trim() || `https://img.youtube.com/vi/${youtube_video_id}/hqdefault.jpg`, display_order: Number(youtubeForm.display_order || youtubeVideos.length + 1), approved: true };
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

  async function startWorkoutSession() {
    if (selectedProgramId === null || selectedWorkoutDayId === null) return;
    setError(null); setSessionFinishedMessage(null); setRestSuggestionSeconds(null); setRestTimerSeconds(null); setRestTimerRunning(false); setRestTimerMessage(null); setLoading("Starting session");
    try {
      const session = await api<WorkoutSession>("/sessions/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          program_id: selectedProgramId,
          workout_day_id: selectedWorkoutDayId,
          readiness_score: readinessScore,
          notes: "",
        }),
      });
      setActiveSession(session);
      await loadRecentSessions();
    }
    catch (e) { setError(e instanceof Error ? e.message : "Could not start session."); }
    finally { setLoading(null); }
  }

  async function saveSessionSet(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!activeSession || !selectedExercise) return;
    setError(null); setLoading("Saving set");

    const setNumber = Number(sessionSetForm.set_number);
    const existingSet = activeSession.session_sets.find((set) => set.workout_exercise_id === selectedExercise.id && set.set_number === setNumber);
    const payload = {
      workout_exercise_id: selectedExercise.id,
      set_number: setNumber,
      planned_reps: selectedPlannedSet?.target_reps ?? selectedExercise.reps,
      planned_weight: selectedPlannedSet?.suggested_weight ?? null,
      actual_reps: sessionSetForm.actual_reps ? Number(sessionSetForm.actual_reps) : null,
      actual_weight: sessionSetForm.actual_weight ? Number(sessionSetForm.actual_weight) : null,
      weight_unit: selectedPlannedSet?.weight_unit ?? "kg",
      difficulty_rating: sessionSetForm.difficulty_rating ? Number(sessionSetForm.difficulty_rating) : null,
      completed: true,
      rest_seconds_used: selectedExercise.rest_seconds,
      notes: sessionSetForm.notes.trim(),
    };

    try {
      const savedSet = existingSet
        ? await api<SessionSet>(`/sessions/${activeSession.id}/sets/${existingSet.id}`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) })
        : await api<SessionSet>(`/sessions/${activeSession.id}/sets`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });

      setActiveSession((current) => {
        if (!current) return current;
        const hasSet = current.session_sets.some((set) => set.id === savedSet.id);
        return {
          ...current,
          session_sets: hasSet
            ? current.session_sets.map((set) => set.id === savedSet.id ? savedSet : set)
            : [...current.session_sets, savedSet],
        };
      });
      setSessionSetForm({ set_number: String(setNumber + 1), actual_reps: "", actual_weight: "", difficulty_rating: "", notes: "" });
      setRestSuggestionSeconds(selectedExercise.rest_seconds);
      setRestTimerSeconds(selectedExercise.rest_seconds);
      setRestTimerRunning(false);
      setRestTimerMessage(null);
    }
    catch (e) { setError(e instanceof Error ? e.message : "Could not save set."); }
    finally { setLoading(null); }
  }

  async function finishWorkoutSession() {
    if (!activeSession) return;
    setError(null); setLoading("Finishing session");
    try {
      const finished = await api<WorkoutSession>(`/sessions/${activeSession.id}/finish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          readiness_score: readinessScore,
          notes: `Completed ${activeSession.session_sets.filter((set) => set.completed).length} logged sets.`,
        }),
      });
      setActiveSession(finished);
      setSessionFinishedMessage(`Session finished. ${finished.session_sets.filter((set) => set.completed).length} sets saved.`);
      setRestSuggestionSeconds(null);
      setRestTimerSeconds(null);
      setRestTimerRunning(false);
      setRestTimerMessage(null);
      await loadRecentSessions();
    }
    catch (e) { setError(e instanceof Error ? e.message : "Could not finish session."); }
    finally { setLoading(null); }
  }

  async function deleteProgram(id: number) { await api(`/programs/${id}`, { method: "DELETE" }); await loadPrograms(); }
  async function deleteWorkoutDay(id: number) { if (selectedProgramId !== null) { await api(`/programs/${selectedProgramId}/workout-days/${id}`, { method: "DELETE" }); await loadWorkoutDays(selectedProgramId); } }
  async function deleteExercise(id: number) { if (selectedProgramId !== null && selectedWorkoutDayId !== null) { await api(`/programs/${selectedProgramId}/workout-days/${selectedWorkoutDayId}/exercises/${id}`, { method: "DELETE" }); await loadExercises(selectedProgramId, selectedWorkoutDayId); } }
  async function deletePlannedSet(id: number) { if (selectedExerciseId !== null) { await api(`/exercises/${selectedExerciseId}/planned-sets/${id}`, { method: "DELETE" }); await loadPlannedSets(selectedExerciseId); } }
  async function deleteYouTubeVideo(id: number) { if (selectedExerciseId !== null) { await api(`/exercises/${selectedExerciseId}/youtube-videos/${id}`, { method: "DELETE" }); await loadYouTubeVideos(selectedExerciseId); } }

  function startRestTimer() {
    if (restSuggestionSeconds === null) return;
    setRestTimerSeconds((current) => current === null || current <= 0 ? restSuggestionSeconds : current);
    setRestTimerMessage(null);
    setRestTimerRunning(true);
  }

  function pauseRestTimer() {
    setRestTimerRunning(false);
  }

  function resetRestTimer() {
    if (restSuggestionSeconds === null) return;
    setRestTimerSeconds(restSuggestionSeconds);
    setRestTimerRunning(false);
    setRestTimerMessage(null);
  }

  function markRestDone() {
    setRestSuggestionSeconds(null);
    setRestTimerSeconds(null);
    setRestTimerRunning(false);
    setRestTimerMessage("Rest marked done.");
  }

  function updateReadiness<K extends keyof ReadinessProfile>(key: K, value: ReadinessProfile[K]) { setReadiness((current) => ({ ...current, [key]: value })); }
  function selectExercise(exercise: WorkoutExercise) { setSelectedExerciseId(exercise.id); setPlannedSetForm({ set_number: "1", target_reps: exercise.reps, suggested_weight: "", weight_unit: "kg", note: "" }); setSessionSetForm({ set_number: "1", actual_reps: "", actual_weight: "", difficulty_rating: "", notes: "" }); setYoutubeForm({ input: "", title: "", channel_name: "", thumbnail_url: "", display_order: "1" }); }
  function renderPlan(plan: AIParsedPlan) { return <div className="program-cards">{plan.workout_days.map((day) => <article className="program-card" key={`${day.day_order}-${day.name}`}><div><h4>Day {day.day_order}: {day.name}</h4>{day.exercises.map((ex) => <p key={`${day.name}-${ex.exercise_order}-${ex.movement_name}`}>{ex.exercise_order}. {ex.movement_name}: {ex.sets} × {ex.reps}, rest {ex.rest_seconds}s {ex.notes ? `— ${ex.notes}` : ""}</p>)}</div></article>)}</div>; }

  function renderDashboard() {
    const selectedDetailSummary = selectedSessionDetail ? summarizeSession(selectedSessionDetail) : null;

    return <section className="program-workspace cockpit-view">
      <div className="section-heading"><div><p className="eyebrow">Mission control</p><h2>Today’s Training Cockpit</h2></div><p>The app now starts where the user starts: what am I doing today, how ready am I, and what is the next useful action?</p></div>
      <div className="cockpit-grid">
        <article className="mission-card primary-mission"><p className="eyebrow">Current mission</p><h3>{selectedWorkoutDay ? selectedWorkoutDay.name : "No workout day selected"}</h3><p>{selectedProgram ? selectedProgram.name : "Create or import a program to activate the cockpit."}</p><div className="form-actions"><button className="primary-button" type="button" onClick={() => setActiveView("training")}>{selectedWorkoutDay ? "Prepare session" : "Build program"}</button><button className="secondary-button" type="button" onClick={() => setActiveView("import")}>Import plan</button></div></article>
        <article className="mission-card"><p className="eyebrow">Readiness</p><h3>{readinessScore}/10</h3><p>Energy {readiness.energy_level}, sleep {readiness.sleep_quality}, soreness {readiness.soreness_level}, stress {readiness.stress_level}.</p><button className="secondary-button compact-button" type="button" onClick={() => setActiveView("enhance")}>Adjust readiness</button></article>
        <article className="mission-card"><p className="eyebrow">Program memory</p><h3>{programs.length} programs</h3><p>{workoutDays.length} days loaded · {totalExercises} exercises in selected day.</p><button className="secondary-button compact-button" type="button" onClick={() => setActiveView("programs")}>Open library</button></article>
        <article className="mission-card"><p className="eyebrow">Technique layer</p><h3>{totalVideos} videos</h3><p>{selectedExercise ? `Selected: ${selectedExercise.movement_name}` : "Select an exercise to attach examples."}</p><button className="secondary-button compact-button" type="button" onClick={() => setActiveView("training")}>Open exercise cockpit</button></article>
      </div>
      <div className="program-list recent-sessions-card">
        <div className="list-header"><h3>Recent Sessions</h3><button className="secondary-button compact-button" type="button" onClick={() => void loadRecentSessions()}>Refresh</button></div>
        {recentSessions.length === 0 ? <p className="empty-state">No sessions yet. Start one from the Training cockpit and completed sets will show here.</p> : <div className="program-cards">{recentSessions.slice(0, 5).map((session) => {
          const completedCount = session.session_sets.filter((set) => set.completed).length;
          return <article className="program-card" key={session.id}><div><h4>Session #{session.id}</h4><p>Status: {session.status} · completed sets: {completedCount}</p><span>Started: {new Date(session.started_at).toLocaleString()}</span>{session.finished_at ? <span>Finished: {new Date(session.finished_at).toLocaleString()}</span> : <span>Finished: not yet</span>}</div><div className="card-actions"><button className="secondary-button compact-button" type="button" onClick={() => void loadSessionDetail(session.id)}>View details</button></div></article>;
        })}</div>}
      </div>
      {selectedSessionDetail && selectedDetailSummary ? <div className="program-list session-detail-panel">
        <div className="list-header"><h3>Session #{selectedSessionDetail.id} Details</h3><button className="secondary-button compact-button" type="button" onClick={() => setSelectedSessionDetail(null)}>Close</button></div>
        <div className="session-detail-grid">
          <p><strong>Status:</strong> {selectedSessionDetail.status}</p>
          <p><strong>Started:</strong> {new Date(selectedSessionDetail.started_at).toLocaleString()}</p>
          <p><strong>Finished:</strong> {selectedSessionDetail.finished_at ? new Date(selectedSessionDetail.finished_at).toLocaleString() : "not yet"}</p>
          <p><strong>Readiness:</strong> {selectedSessionDetail.readiness_score ?? "not recorded"}</p>
          <p><strong>Total sets:</strong> {selectedDetailSummary.totalSets}</p>
          <p><strong>Completed sets:</strong> {selectedDetailSummary.completedSets}</p>
          <p><strong>Exercises touched:</strong> {selectedDetailSummary.exercisesTouched}</p>
          <p><strong>Average difficulty:</strong> {selectedDetailSummary.averageDifficulty === null ? "not rated" : `${selectedDetailSummary.averageDifficulty.toFixed(1)}/10`}</p>
        </div>
        <p><strong>Notes:</strong> {selectedSessionDetail.notes || "No notes"}</p>
        <h4>Logged sets</h4>
        {/* TODO: Ask backend for exercise name snapshots or joined exercise names in session set reads. */}
        {selectedSessionDetail.session_sets.length === 0 ? <p className="empty-state">No sets were logged in this session.</p> : <div className="session-set-list">{selectedSessionDetail.session_sets.map((set) => <article className="program-card" key={set.id}><div><h4>Exercise #{set.workout_exercise_id} - Set {set.set_number}</h4><p>{set.actual_reps ?? "-"} reps - {set.actual_weight ?? "-"} {set.weight_unit} - difficulty {set.difficulty_rating ?? "-"}/10</p><span>{set.notes || "No notes"}</span></div></article>)}</div>}
      </div> : null}
      <div className="program-grid"><div className="program-list"><h3>Quick Actions</h3><div className="quick-actions"><button className="primary-button" type="button" onClick={() => setActiveView("import")}>Paste / extract plan</button><button className="secondary-button" type="button" onClick={() => setActiveView("enhance")}>Enhance current plan</button><button className="secondary-button" type="button" onClick={() => setActiveView("training")}>Weights & videos</button><button className="secondary-button" type="button" onClick={() => setActiveView("settings")}>API settings</button></div></div><div className="program-list"><h3>Next product milestone</h3><p>Session mode is the real shark-tank milestone: start workout, log actual sets, run rest timer, finish summary, and make next workout smarter.</p></div></div>
    </section>;
  }

  function renderImportView() {
    return <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Import</p><h2>AI Workout Plan Import</h2></div><p>Pure extraction. No coaching. No judging. No creative nonsense.</p></div><form className="program-form import-form" onSubmit={analyzeImport}><label>Plain text workout plan<textarea className="import-textarea" value={importText} onChange={(e) => setImportText(e.target.value)} /></label><button className="primary-button" disabled={!openAIKeyStatus.configured || loading !== null} type="submit">{openAIKeyStatus.configured ? "Extract plan" : "Add API key first"}</button></form>{importAnalysis ? <div className="program-list import-preview"><div className="list-header"><h3>Extracted Plan Preview</h3><button className="primary-button compact-button" onClick={() => void savePlan(importAnalysis.parsed_plan, "approved_extracted_plan")}>Save extracted plan</button></div><p><strong>{importAnalysis.parsed_plan.program.name}</strong> · {importAnalysis.parsed_plan.program.duration_weeks} weeks · extraction confidence {Math.round(importAnalysis.overall_confidence * 100)}%</p><p>{importAnalysis.parsed_plan.program.goal}</p>{importAnalysis.trainer_review_required ? <p className="warning-pill">Review recommended because extraction used assumptions or ambiguity exists.</p> : null}{renderPlan(importAnalysis.parsed_plan)}</div> : null}</section>;
  }

  function renderEnhanceView() {
    return <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Enhance</p><h2>Enhance Based on Profile & Readiness</h2></div><p>Optional adjustment. BMI is context, not a verdict. Original plan remains untouched.</p></div>{!importAnalysis ? <div className="program-list"><h3>No extracted plan yet</h3><p>Import a plan first, then use this screen to adapt it based on readiness and profile.</p><button className="primary-button" type="button" onClick={() => setActiveView("import")}>Go to Import</button></div> : <><div className="program-grid"><div className="program-form"><h3>Trainee profile</h3><div className="inline-fields"><label>Age<input type="number" value={readiness.age ?? ""} onChange={(e) => updateReadiness("age", e.target.value ? Number(e.target.value) : null)} /></label><label>Sex / optional<input value={readiness.sex} onChange={(e) => updateReadiness("sex", e.target.value)} /></label></div><div className="inline-fields"><label>Height cm<input type="number" value={readiness.height_cm ?? ""} onChange={(e) => updateReadiness("height_cm", e.target.value ? Number(e.target.value) : null)} /></label><label>Weight kg<input type="number" value={readiness.weight_kg ?? ""} onChange={(e) => updateReadiness("weight_kg", e.target.value ? Number(e.target.value) : null)} /></label></div><p className="muted">Calculated BMI: {computedBmi ?? "add height and weight"}</p><h3>Readiness</h3><div className="inline-fields"><label>Experience<input value={readiness.training_experience} onChange={(e) => updateReadiness("training_experience", e.target.value)} /></label><label>Goal<input value={readiness.primary_goal} onChange={(e) => updateReadiness("primary_goal", e.target.value)} /></label></div><div className="inline-fields"><label>Energy 1-10<input type="number" min="1" max="10" value={readiness.energy_level} onChange={(e) => updateReadiness("energy_level", Number(e.target.value))} /></label><label>Sleep 1-10<input type="number" min="1" max="10" value={readiness.sleep_quality} onChange={(e) => updateReadiness("sleep_quality", Number(e.target.value))} /></label></div><div className="inline-fields"><label>Soreness 1-10<input type="number" min="1" max="10" value={readiness.soreness_level} onChange={(e) => updateReadiness("soreness_level", Number(e.target.value))} /></label><label>Stress 1-10<input type="number" min="1" max="10" value={readiness.stress_level} onChange={(e) => updateReadiness("stress_level", Number(e.target.value))} /></label></div><div className="inline-fields"><label>Difficulty<input value={readiness.difficulty_preference} onChange={(e) => updateReadiness("difficulty_preference", e.target.value)} /></label><label>Time limit minutes<input type="number" value={readiness.session_time_limit_minutes ?? ""} onChange={(e) => updateReadiness("session_time_limit_minutes", e.target.value ? Number(e.target.value) : null)} /></label></div><label>Limitations / difficulties<textarea value={readiness.pain_or_limitations} onChange={(e) => updateReadiness("pain_or_limitations", e.target.value)} /></label><label>Available equipment<textarea value={readiness.available_equipment} onChange={(e) => updateReadiness("available_equipment", e.target.value)} /></label><label>Extra notes<textarea value={readiness.extra_notes} onChange={(e) => updateReadiness("extra_notes", e.target.value)} /></label><button className="primary-button" disabled={loading !== null} type="button" onClick={() => void enhancePlan()}>Enhance plan</button></div><div className="program-list"><h3>Enhancement promise</h3><p>The adjusted plan is a proposal. Save adjusted version only after review.</p></div></div>{enhancement ? <div className="program-list import-preview"><div className="list-header"><h3>Adjusted Plan Preview</h3><button className="primary-button compact-button" onClick={() => void savePlan(enhancement.adjusted_plan, "approved_adjusted_plan")}>Save adjusted plan</button></div><p>{enhancement.summary}</p>{enhancement.trainer_review_required ? <p className="warning-pill">Trainer review recommended.</p> : null}<h4>Changes</h4>{enhancement.changes.length ? <ul>{enhancement.changes.map((change, index) => <li key={`${change.day_name}-${change.change_type}-${index}`}><strong>{change.change_type}</strong> — {change.original} → {change.adjusted}. {change.reason}</li>)}</ul> : <p>No major changes proposed.</p>}{renderPlan(enhancement.adjusted_plan)}</div> : null}</>}</section>;
  }

  function renderProgramsView() {
    return <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Programs</p><h2>Program Library</h2></div><p>Create manually or save from AI import/enhancement.</p></div><div className="program-grid"><form className="program-form" onSubmit={handleProgramSubmit}><h3>{editingProgramId ? "Edit program" : "Create program"}</h3><label>Program name<input value={programForm.name} onChange={(e) => setProgramForm({ ...programForm, name: e.target.value })} /></label><label>Goal<textarea value={programForm.goal} onChange={(e) => setProgramForm({ ...programForm, goal: e.target.value })} /></label><label>Duration weeks<input type="number" value={programForm.duration_weeks} onChange={(e) => setProgramForm({ ...programForm, duration_weeks: e.target.value })} /></label><button className="primary-button" type="submit">{editingProgramId ? "Save" : "Create"}</button></form><div className="program-list"><h3>Saved programs</h3><div className="program-cards">{programs.map((p) => <article className={`program-card${selectedProgramId === p.id ? " selected-card" : ""}`} key={p.id}><div><h4>{p.name}</h4><p>{p.goal}</p><span>{p.duration_weeks} weeks</span></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => { setSelectedProgramId(p.id); setActiveView("dashboard"); }} type="button">{selectedProgramId === p.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingProgramId(p.id); setProgramForm({ name: p.name, goal: p.goal, duration_weeks: String(p.duration_weeks) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteProgram(p.id)} type="button">Delete</button></div></article>)}</div></div></div></section>;
  }

  function renderTrainingView() {
    return <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Training cockpit</p><h2>Workout Days, Exercises, Weights & Videos</h2></div><p>{selectedProgram ? `Selected program: ${selectedProgram.name}` : "Select a program first."}</p></div><div className="program-grid"><form className="program-form" onSubmit={handleWorkoutDaySubmit}><h3>{editingWorkoutDayId ? "Edit day" : "Add day"}</h3><label>Day name<input disabled={selectedProgramId === null} value={workoutDayForm.name} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, name: e.target.value })} /></label><label>Order<input disabled={selectedProgramId === null} type="number" value={workoutDayForm.day_order} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, day_order: e.target.value })} /></label><button className="primary-button" disabled={selectedProgramId === null} type="submit">{editingWorkoutDayId ? "Save day" : "Add day"}</button></form><div className="program-list"><h3>Days</h3><div className="program-cards">{workoutDays.map((d) => <article className={`program-card${selectedWorkoutDayId === d.id ? " selected-card" : ""}`} key={d.id}><div><h4>{d.name}</h4><p>Order: {d.day_order}</p></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => setSelectedWorkoutDayId(d.id)} type="button">{selectedWorkoutDayId === d.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingWorkoutDayId(d.id); setWorkoutDayForm({ name: d.name, day_order: String(d.day_order) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteWorkoutDay(d.id)} type="button">Delete</button></div></article>)}</div></div></div><div className="program-grid"><form className="program-form" onSubmit={handleExerciseSubmit}><h3>{editingExerciseId ? "Edit exercise" : "Add exercise"}</h3><label>Movement<input disabled={selectedWorkoutDayId === null} value={exerciseForm.movement_name} onChange={(e) => setExerciseForm({ ...exerciseForm, movement_name: e.target.value })} /></label><div className="inline-fields"><label>Sets<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.sets} onChange={(e) => setExerciseForm({ ...exerciseForm, sets: e.target.value })} /></label><label>Reps<input disabled={selectedWorkoutDayId === null} value={exerciseForm.reps} onChange={(e) => setExerciseForm({ ...exerciseForm, reps: e.target.value })} /></label></div><div className="inline-fields"><label>Rest seconds<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.rest_seconds} onChange={(e) => setExerciseForm({ ...exerciseForm, rest_seconds: e.target.value })} /></label><label>Order<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.exercise_order} onChange={(e) => setExerciseForm({ ...exerciseForm, exercise_order: e.target.value })} /></label></div><label>Notes<textarea disabled={selectedWorkoutDayId === null} value={exerciseForm.notes} onChange={(e) => setExerciseForm({ ...exerciseForm, notes: e.target.value })} /></label><button className="primary-button" disabled={selectedWorkoutDayId === null} type="submit">{editingExerciseId ? "Save exercise" : "Add exercise"}</button></form><div className="program-list"><h3>Exercises {selectedWorkoutDay ? `for ${selectedWorkoutDay.name}` : ""}</h3><div className="program-cards">{exercises.map((e) => <article className={`program-card exercise-card${selectedExerciseId === e.id ? " selected-card" : ""}`} key={e.id}><div><h4>{e.exercise_order}. {e.movement_name}</h4><p>{e.sets} sets × {e.reps} · Rest {e.rest_seconds}s</p><span>{e.notes || "No notes"}</span></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => selectExercise(e)} type="button">{selectedExerciseId === e.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingExerciseId(e.id); setExerciseForm({ movement_name: e.movement_name, sets: String(e.sets), reps: e.reps, rest_seconds: String(e.rest_seconds), notes: e.notes, exercise_order: String(e.exercise_order) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteExercise(e.id)} type="button">Delete</button></div></article>)}</div></div></div><div className="program-grid"><form className="program-form" onSubmit={handlePlannedSetSubmit}><h3>{editingPlannedSetId ? "Edit planned set" : "Add planned set weight"}</h3><p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none"}</p><div className="inline-fields"><label>Set number<input disabled={selectedExerciseId === null} type="number" value={plannedSetForm.set_number} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, set_number: e.target.value })} /></label><label>Target reps<input disabled={selectedExerciseId === null} value={plannedSetForm.target_reps} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, target_reps: e.target.value })} /></label></div><div className="inline-fields"><label>Suggested weight<input disabled={selectedExerciseId === null} list="weight-options" type="number" step="0.5" value={plannedSetForm.suggested_weight} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, suggested_weight: e.target.value })} /><datalist id="weight-options"><option value="20" /><option value="30" /><option value="40" /><option value="50" /><option value="60" /><option value="80" /><option value="100" /></datalist></label><label>Unit<select disabled={selectedExerciseId === null} value={plannedSetForm.weight_unit} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, weight_unit: e.target.value })}><option value="kg">kg</option><option value="lb">lb</option><option value="bodyweight">bodyweight</option></select></label></div><label>Note<textarea disabled={selectedExerciseId === null} value={plannedSetForm.note} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, note: e.target.value })} /></label><button className="primary-button" disabled={selectedExerciseId === null} type="submit">{editingPlannedSetId ? "Save planned set" : "Add planned set"}</button></form><div className="program-list"><h3>Planned set weights</h3>{selectedExercise ? <p className="muted">For {selectedExercise.movement_name}</p> : <p className="empty-state">Select an exercise first. Weights without an exercise are just numbers doing cosplay.</p>}<div className="program-cards">{plannedSets.map((set) => <article className="program-card" key={set.id}><div><h4>Set {set.set_number}</h4><p>{set.target_reps} reps · {set.suggested_weight ?? "—"} {set.weight_unit}</p><span>{set.note || "No note"}</span></div><div className="card-actions"><button className="secondary-button compact-button" onClick={() => { setEditingPlannedSetId(set.id); setPlannedSetForm({ set_number: String(set.set_number), target_reps: set.target_reps, suggested_weight: set.suggested_weight === null ? "" : String(set.suggested_weight), weight_unit: set.weight_unit, note: set.note }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deletePlannedSet(set.id)} type="button">Delete</button></div></article>)}</div></div></div><div className="program-grid"><form className="program-form" onSubmit={handleYouTubeSubmit}><h3>Add YouTube example</h3><p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none"}</p><button className="secondary-button" disabled={selectedExerciseId === null || loading !== null} type="button" onClick={() => void findYouTubeExamples()}>Find YouTube examples automatically</button><label>YouTube link or video ID<input disabled={selectedExerciseId === null} placeholder="https://youtu.be/... or video ID" value={youtubeForm.input} onChange={(e) => setYoutubeForm({ ...youtubeForm, input: e.target.value })} /></label><label>Title<input disabled={selectedExerciseId === null} placeholder="Bench Press tutorial" value={youtubeForm.title} onChange={(e) => setYoutubeForm({ ...youtubeForm, title: e.target.value })} /></label><div className="inline-fields"><label>Channel<input disabled={selectedExerciseId === null} value={youtubeForm.channel_name} onChange={(e) => setYoutubeForm({ ...youtubeForm, channel_name: e.target.value })} /></label><label>Order<input disabled={selectedExerciseId === null} type="number" value={youtubeForm.display_order} onChange={(e) => setYoutubeForm({ ...youtubeForm, display_order: e.target.value })} /></label></div><label>Thumbnail URL optional<input disabled={selectedExerciseId === null} value={youtubeForm.thumbnail_url} onChange={(e) => setYoutubeForm({ ...youtubeForm, thumbnail_url: e.target.value })} /></label><button className="primary-button" disabled={selectedExerciseId === null} type="submit">Add video manually</button></form><div className="program-list"><h3>YouTube examples</h3>{selectedExercise ? <p className="muted">Stored videos for {selectedExercise.movement_name}</p> : <p className="empty-state">Select an exercise first. Videos need a movement, not vibes.</p>}<div className="video-grid">{youtubeVideos.map((video) => <article className="video-card" key={video.id}><iframe className="video-frame" src={`https://www.youtube.com/embed/${video.youtube_video_id}`} title={video.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen /><div className="video-meta"><h4>{video.title}</h4><p>{video.channel_name || "Unknown channel"}</p><button className="danger-button compact-button" onClick={() => void deleteYouTubeVideo(video.id)} type="button">Remove</button></div></article>)}</div></div></div></section>;
  }

  function renderTrainingViewV2() {
    const sessionIsActive = activeSession?.status === "active";
    const completedSets = activeSession?.session_sets.filter((set) => set.completed) ?? [];

    return <section className="program-workspace">
      <div className="section-heading">
        <div><p className="eyebrow">Training cockpit</p><h2>Workout Days, Exercises, Weights & Videos</h2></div>
        <p>{selectedProgram ? `Selected program: ${selectedProgram.name}` : "Select a program first."}</p>
      </div>

      <div className="session-panel">
        <div className="session-panel-header">
          <div>
            <p className="eyebrow">Session mode v1</p>
            <h3>{selectedWorkoutDay ? selectedWorkoutDay.name : "No workout day selected"}</h3>
            <p>{activeSession ? `Session #${activeSession.id} - ${activeSession.status} - ${completedSets.length} completed sets logged` : "Start a workout from the selected day, then log actual set performance."}</p>
            <p>Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none selected"}</p>
          </div>
          <div className="card-actions">
            <button className="primary-button" disabled={selectedProgramId === null || selectedWorkoutDayId === null || sessionIsActive || loading !== null} type="button" onClick={() => void startWorkoutSession()}>Start Session</button>
            <button className="danger-button" disabled={!sessionIsActive || loading !== null} type="button" onClick={() => void finishWorkoutSession()}>Finish Session</button>
          </div>
        </div>
        {sessionFinishedMessage ? <p className="success-message">{sessionFinishedMessage}</p> : null}
        {activeSessionSummary ? <div className="session-summary-panel"><h3>Session summary</h3><p>Total sets: {activeSessionSummary.totalSets}</p><p>Total completed sets: {activeSessionSummary.completedSets}</p><p>Exercises touched: {activeSessionSummary.exercisesTouched}</p><p>Average difficulty: {activeSessionSummary.averageDifficulty === null ? "not rated" : `${activeSessionSummary.averageDifficulty.toFixed(1)}/10`}</p><p>Status: {activeSession?.status ?? "unknown"}</p><p>Notes: {activeSession?.notes || "No notes"}</p></div> : null}
        {sessionIsActive ? <div className="program-grid session-grid">
          <form className="program-form" onSubmit={saveSessionSet}>
            <h3>Log set</h3>
            <p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "select an exercise below"}</p>
            <div className="inline-fields">
              <label>Set number<input min="1" type="number" value={sessionSetForm.set_number} onChange={(e) => setSessionSetForm({ ...sessionSetForm, set_number: e.target.value })} /></label>
              <label>Difficulty 1-10<input max="10" min="1" type="number" value={sessionSetForm.difficulty_rating} onChange={(e) => setSessionSetForm({ ...sessionSetForm, difficulty_rating: e.target.value })} /></label>
            </div>
            <div className="inline-fields">
              <label>Actual reps<input min="0" type="number" value={sessionSetForm.actual_reps} onChange={(e) => setSessionSetForm({ ...sessionSetForm, actual_reps: e.target.value })} /></label>
              <label>Actual weight<input min="0" step="0.5" type="number" value={sessionSetForm.actual_weight} onChange={(e) => setSessionSetForm({ ...sessionSetForm, actual_weight: e.target.value })} /></label>
            </div>
            <p className="muted">Target: {selectedPlannedSet?.target_reps ?? selectedExercise?.reps ?? "none"} reps · {selectedPlannedSet?.suggested_weight ?? "no planned weight"} {selectedPlannedSet?.weight_unit ?? "kg"}</p>
            <label>Set notes<textarea value={sessionSetForm.notes} onChange={(e) => setSessionSetForm({ ...sessionSetForm, notes: e.target.value })} /></label>
            <button className="primary-button" disabled={!selectedExercise || loading !== null} type="submit">Save set</button>
            {restSuggestionSeconds !== null ? <div className="rest-timer-panel"><div><p>Suggested rest: {restSuggestionSeconds} seconds</p><strong className="timer-value">{restTimerSeconds ?? restSuggestionSeconds}s</strong><p className="muted">{restTimerRunning ? "Rest timer running." : "Timer is ready."}</p></div><div className="timer-actions"><button className="secondary-button compact-button" type="button" onClick={startRestTimer}>Start Rest</button><button className="secondary-button compact-button" disabled={!restTimerRunning} type="button" onClick={pauseRestTimer}>Pause</button><button className="secondary-button compact-button" type="button" onClick={resetRestTimer}>Reset</button><button className="primary-button compact-button" type="button" onClick={markRestDone}>Mark rest done</button></div></div> : null}
            {restTimerMessage ? <p className="muted">{restTimerMessage}</p> : null}
          </form>
          <div className="program-list">
            <h3>Saved sets</h3>
            {completedSets.length === 0 ? <p className="empty-state">No sets logged yet.</p> : null}
            <div className="program-cards">{completedSets.map((set) => {
              const exercise = exercises.find((item) => item.id === set.workout_exercise_id);
              return <article className="program-card" key={set.id}><div><h4>{exercise?.movement_name ?? "Exercise"} · Set {set.set_number}</h4><p>{set.actual_reps ?? "—"} reps · {set.actual_weight ?? "—"} {set.weight_unit} · difficulty {set.difficulty_rating ?? "—"}/10</p><span>{set.notes || "No notes"}</span></div></article>;
            })}</div>
          </div>
        </div> : null}
      </div>

      <div className="program-grid"><form className="program-form" onSubmit={handleWorkoutDaySubmit}><h3>{editingWorkoutDayId ? "Edit day" : "Add day"}</h3><label>Day name<input disabled={selectedProgramId === null} value={workoutDayForm.name} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, name: e.target.value })} /></label><label>Order<input disabled={selectedProgramId === null} type="number" value={workoutDayForm.day_order} onChange={(e) => setWorkoutDayForm({ ...workoutDayForm, day_order: e.target.value })} /></label><button className="primary-button" disabled={selectedProgramId === null} type="submit">{editingWorkoutDayId ? "Save day" : "Add day"}</button></form><div className="program-list"><h3>Days</h3><div className="program-cards">{workoutDays.map((d) => <article className={`program-card${selectedWorkoutDayId === d.id ? " selected-card" : ""}`} key={d.id}><div><h4>{d.name}</h4><p>Order: {d.day_order}</p></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => setSelectedWorkoutDayId(d.id)} type="button">{selectedWorkoutDayId === d.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingWorkoutDayId(d.id); setWorkoutDayForm({ name: d.name, day_order: String(d.day_order) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteWorkoutDay(d.id)} type="button">Delete</button></div></article>)}</div></div></div>
      <div className="program-grid"><form className="program-form" onSubmit={handleExerciseSubmit}><h3>{editingExerciseId ? "Edit exercise" : "Add exercise"}</h3><label>Movement<input disabled={selectedWorkoutDayId === null} value={exerciseForm.movement_name} onChange={(e) => setExerciseForm({ ...exerciseForm, movement_name: e.target.value })} /></label><div className="inline-fields"><label>Sets<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.sets} onChange={(e) => setExerciseForm({ ...exerciseForm, sets: e.target.value })} /></label><label>Reps<input disabled={selectedWorkoutDayId === null} value={exerciseForm.reps} onChange={(e) => setExerciseForm({ ...exerciseForm, reps: e.target.value })} /></label></div><div className="inline-fields"><label>Rest seconds<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.rest_seconds} onChange={(e) => setExerciseForm({ ...exerciseForm, rest_seconds: e.target.value })} /></label><label>Order<input disabled={selectedWorkoutDayId === null} type="number" value={exerciseForm.exercise_order} onChange={(e) => setExerciseForm({ ...exerciseForm, exercise_order: e.target.value })} /></label></div><label>Notes<textarea disabled={selectedWorkoutDayId === null} value={exerciseForm.notes} onChange={(e) => setExerciseForm({ ...exerciseForm, notes: e.target.value })} /></label><button className="primary-button" disabled={selectedWorkoutDayId === null} type="submit">{editingExerciseId ? "Save exercise" : "Add exercise"}</button></form><div className="program-list"><h3>Exercises {selectedWorkoutDay ? `for ${selectedWorkoutDay.name}` : ""}</h3><div className="program-cards">{exercises.map((e) => <article className={`program-card exercise-card${selectedExerciseId === e.id ? " selected-card" : ""}`} key={e.id}><div><h4>{e.exercise_order}. {e.movement_name}</h4><p>{e.sets} sets × {e.reps} · Rest {e.rest_seconds}s</p><span>{e.notes || "No notes"}</span></div><div className="card-actions"><button className="primary-button compact-button" onClick={() => selectExercise(e)} type="button">{selectedExerciseId === e.id ? "Selected" : "Select"}</button><button className="secondary-button compact-button" onClick={() => { setEditingExerciseId(e.id); setExerciseForm({ movement_name: e.movement_name, sets: String(e.sets), reps: e.reps, rest_seconds: String(e.rest_seconds), notes: e.notes, exercise_order: String(e.exercise_order) }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deleteExercise(e.id)} type="button">Delete</button></div></article>)}</div></div></div>
      <div className="program-grid"><form className="program-form" onSubmit={handlePlannedSetSubmit}><h3>{editingPlannedSetId ? "Edit planned set" : "Add planned set weight"}</h3><p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none"}</p><div className="inline-fields"><label>Set number<input disabled={selectedExerciseId === null} type="number" value={plannedSetForm.set_number} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, set_number: e.target.value })} /></label><label>Target reps<input disabled={selectedExerciseId === null} value={plannedSetForm.target_reps} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, target_reps: e.target.value })} /></label></div><div className="inline-fields"><label>Suggested weight<input disabled={selectedExerciseId === null} list="weight-options" type="number" step="0.5" value={plannedSetForm.suggested_weight} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, suggested_weight: e.target.value })} /><datalist id="weight-options"><option value="20" /><option value="30" /><option value="40" /><option value="50" /><option value="60" /><option value="80" /><option value="100" /></datalist></label><label>Unit<select disabled={selectedExerciseId === null} value={plannedSetForm.weight_unit} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, weight_unit: e.target.value })}><option value="kg">kg</option><option value="lb">lb</option><option value="bodyweight">bodyweight</option></select></label></div><label>Note<textarea disabled={selectedExerciseId === null} value={plannedSetForm.note} onChange={(e) => setPlannedSetForm({ ...plannedSetForm, note: e.target.value })} /></label><button className="primary-button" disabled={selectedExerciseId === null} type="submit">{editingPlannedSetId ? "Save planned set" : "Add planned set"}</button></form><div className="program-list"><h3>Planned set weights</h3>{selectedExercise ? <p className="muted">For {selectedExercise.movement_name}</p> : <p className="empty-state">Select an exercise first.</p>}<div className="program-cards">{plannedSets.map((set) => <article className="program-card" key={set.id}><div><h4>Set {set.set_number}</h4><p>{set.target_reps} reps · {set.suggested_weight ?? "—"} {set.weight_unit}</p><span>{set.note || "No note"}</span></div><div className="card-actions"><button className="secondary-button compact-button" onClick={() => { setEditingPlannedSetId(set.id); setPlannedSetForm({ set_number: String(set.set_number), target_reps: set.target_reps, suggested_weight: set.suggested_weight === null ? "" : String(set.suggested_weight), weight_unit: set.weight_unit, note: set.note }); }} type="button">Edit</button><button className="danger-button compact-button" onClick={() => void deletePlannedSet(set.id)} type="button">Delete</button></div></article>)}</div></div></div>
      <div className="program-grid"><form className="program-form" onSubmit={handleYouTubeSubmit}><h3>Add YouTube example</h3><p className="muted">Selected exercise: {selectedExercise ? selectedExercise.movement_name : "none"}</p><button className="secondary-button" disabled={selectedExerciseId === null || loading !== null} type="button" onClick={() => void findYouTubeExamples()}>Find YouTube examples automatically</button><label>YouTube link or video ID<input disabled={selectedExerciseId === null} placeholder="https://youtu.be/... or video ID" value={youtubeForm.input} onChange={(e) => setYoutubeForm({ ...youtubeForm, input: e.target.value })} /></label><label>Title<input disabled={selectedExerciseId === null} placeholder="Bench Press tutorial" value={youtubeForm.title} onChange={(e) => setYoutubeForm({ ...youtubeForm, title: e.target.value })} /></label><div className="inline-fields"><label>Channel<input disabled={selectedExerciseId === null} value={youtubeForm.channel_name} onChange={(e) => setYoutubeForm({ ...youtubeForm, channel_name: e.target.value })} /></label><label>Order<input disabled={selectedExerciseId === null} type="number" value={youtubeForm.display_order} onChange={(e) => setYoutubeForm({ ...youtubeForm, display_order: e.target.value })} /></label></div><label>Thumbnail URL optional<input disabled={selectedExerciseId === null} value={youtubeForm.thumbnail_url} onChange={(e) => setYoutubeForm({ ...youtubeForm, thumbnail_url: e.target.value })} /></label><button className="primary-button" disabled={selectedExerciseId === null} type="submit">Add video manually</button></form><div className="program-list"><h3>YouTube examples</h3>{selectedExercise ? <p className="muted">Stored videos for {selectedExercise.movement_name}</p> : <p className="empty-state">Select an exercise first.</p>}<div className="video-grid">{youtubeVideos.map((video) => <article className="video-card" key={video.id}><iframe className="video-frame" src={`https://www.youtube.com/embed/${video.youtube_video_id}`} title={video.title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen /><div className="video-meta"><h4>{video.title}</h4><p>{video.channel_name || "Unknown channel"}</p><button className="danger-button compact-button" onClick={() => void deleteYouTubeVideo(video.id)} type="button">Remove</button></div></article>)}</div></div></div>
    </section>;
  }

  function renderSettingsView() {
    return <section className="program-workspace"><div className="section-heading"><div><p className="eyebrow">Settings</p><h2>API Keys & Configuration</h2></div><p>Settings are now utility controls, not the product’s front door.</p></div><div className="program-grid"><form className="program-form" onSubmit={saveOpenAIKey}><h3>OpenAI access</h3><p className="muted">Status: {openAIKeyStatus.configured ? `Configured from ${openAIKeyStatus.source} (${openAIKeyStatus.masked_key})` : "Not configured"}</p><label>API key<input autoComplete="off" type="password" value={openAIKeyInput} onChange={(e) => setOpenAIKeyInput(e.target.value)} /></label><div className="form-actions"><button className="primary-button" disabled={!openAIKeyInput.trim()} type="submit">Save key</button><button className="secondary-button" type="button" onClick={() => void loadOpenAIKeyStatus()}>Check</button><button className="danger-button" type="button" onClick={() => void clearOpenAIKey()}>Clear</button></div></form><div className="program-list"><h3>YouTube key</h3><p>YouTube search uses backend environment variable <strong>YOUTUBE_API_KEY</strong>. Keep it in PowerShell/backend environment, not in GitHub.</p></div></div></section>;
  }

  return <main className="app-shell">
    <header className="top-bar"><h1 className="brand">SetPilot</h1><span className="phase-label">Training Operating System</span></header>
    <section className="dashboard"><div className="intro"><h2>Train the plan, not the chaos.</h2><p>SetPilot is shifting from a form-heavy prototype into a dashboard-first training cockpit: import, enhance, execute, learn.</p></div><nav className="actions" aria-label="SetPilot navigation">{navItems.map((item) => <button className={`action-button${activeView === item.id ? " active-action" : ""}`} key={item.id} type="button" onClick={() => setActiveView(item.id)}>{item.label}<span>{item.subtitle}</span></button>)}</nav></section>
    {error ? <section className="program-workspace"><p className="error-message global-error">{error}</p></section> : null}
    {loading ? <section className="program-workspace"><p className="global-error">{loading}... The beast is working, not sleeping.</p></section> : null}
    {activeView === "dashboard" ? renderDashboard() : null}
    {activeView === "import" ? renderImportView() : null}
    {activeView === "enhance" ? renderEnhanceView() : null}
    {activeView === "programs" ? renderProgramsView() : null}
    {activeView === "training" ? renderTrainingViewV2() : null}
    {activeView === "settings" ? renderSettingsView() : null}
  </main>;
}

export default App;
