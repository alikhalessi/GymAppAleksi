from fastapi.testclient import TestClient

from app.main import app
from app.services import ai_session_reflection

client = TestClient(app)


def create_training_plan() -> tuple[int, int, int]:
    program_response = client.post(
        "/programs",
        json={
            "name": "Session Mode Test",
            "goal": "Verify workout execution",
            "duration_weeks": 6,
        },
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Upper Session", "day_order": 1},
    )
    assert day_response.status_code == 201
    workout_day_id = int(day_response.json()["id"])

    exercise_response = client.post(
        f"/programs/{program_id}/workout-days/{workout_day_id}/exercises",
        json={
            "movement_name": "Bench Press",
            "sets": 3,
            "reps": "6-8",
            "rest_seconds": 120,
            "notes": "Stay tight.",
            "exercise_order": 1,
        },
    )
    assert exercise_response.status_code == 201
    workout_exercise_id = int(exercise_response.json()["id"])

    return program_id, workout_day_id, workout_exercise_id


def start_test_session() -> tuple[int, int]:
    program_id, workout_day_id, workout_exercise_id = create_training_plan()
    start_response = client.post(
        "/sessions/start",
        json={
            "program_id": program_id,
            "workout_day_id": workout_day_id,
            "readiness_score": 7,
            "notes": "Ready enough.",
        },
    )
    assert start_response.status_code == 201
    return int(start_response.json()["id"]), workout_exercise_id


def create_test_session_set(session_id: int, workout_exercise_id: int) -> int:
    create_set_response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "workout_exercise_id": workout_exercise_id,
            "set_number": 1,
            "planned_reps": "6-8",
            "planned_weight": 60,
            "weight_unit": "kg",
        },
    )
    assert create_set_response.status_code == 201
    return int(create_set_response.json()["id"])


def test_workout_session_mode_flow() -> None:
    program_id, workout_day_id, workout_exercise_id = create_training_plan()

    start_response = client.post(
        "/sessions/start",
        json={
            "program_id": program_id,
            "workout_day_id": workout_day_id,
            "readiness_score": 7,
            "notes": "Ready enough.",
        },
    )
    assert start_response.status_code == 201
    started = start_response.json()
    assert started["program_id"] == program_id
    assert started["workout_day_id"] == workout_day_id
    assert started["status"] == "active"
    assert started["finished_at"] is None
    session_id = int(started["id"])

    create_set_response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "workout_exercise_id": workout_exercise_id,
            "set_number": 1,
            "planned_reps": "6-8",
            "planned_weight": 60,
            "weight_unit": "kg",
        },
    )
    assert create_set_response.status_code == 201
    created_set = create_set_response.json()
    assert created_set["workout_session_id"] == session_id
    assert created_set["workout_exercise_id"] == workout_exercise_id
    assert created_set["exercise_name_snapshot"] == "Bench Press"
    assert created_set["workout_day_name_snapshot"] == "Upper Session"
    assert created_set["program_name_snapshot"] == "Session Mode Test"
    assert created_set["planned_rest_seconds_snapshot"] == 120
    assert created_set["completed"] is False
    session_set_id = int(created_set["id"])

    rename_exercise_response = client.put(
        f"/programs/{program_id}/workout-days/{workout_day_id}/exercises/{workout_exercise_id}",
        json={"movement_name": "Incline Bench Press"},
    )
    assert rename_exercise_response.status_code == 200

    update_set_response = client.put(
        f"/sessions/{session_id}/sets/{session_set_id}",
        json={
            "actual_reps": 8,
            "actual_weight": 62.5,
            "difficulty_rating": 8,
            "completed": True,
            "rest_seconds_used": 130,
            "notes": "Solid first set.",
        },
    )
    assert update_set_response.status_code == 200
    updated_set = update_set_response.json()
    assert updated_set["actual_reps"] == 8
    assert updated_set["actual_weight"] == 62.5
    assert updated_set["difficulty_rating"] == 8
    assert updated_set["completed"] is True

    finish_response = client.post(
        f"/sessions/{session_id}/finish",
        json={"notes": "Finished cleanly.", "readiness_score": 7},
    )
    assert finish_response.status_code == 200
    finished = finish_response.json()
    assert finished["status"] == "completed"
    assert finished["finished_at"] is not None
    assert finished["notes"] == "Finished cleanly."
    assert len(finished["session_sets"]) == 1

    get_response = client.get(f"/sessions/{session_id}")
    assert get_response.status_code == 200
    session_detail = get_response.json()
    assert session_detail["id"] == session_id
    assert session_detail["session_sets"][0]["exercise_name_snapshot"] == "Bench Press"
    assert session_detail["session_sets"][0]["workout_day_name_snapshot"] == "Upper Session"
    assert session_detail["session_sets"][0]["program_name_snapshot"] == "Session Mode Test"
    assert session_detail["session_sets"][0]["planned_rest_seconds_snapshot"] == 120

    recent_response = client.get("/sessions/recent")
    assert recent_response.status_code == 200
    recent_session = next(session for session in recent_response.json() if session["id"] == session_id)
    assert recent_session["session_sets"][0]["exercise_name_snapshot"] == "Bench Press"
    assert recent_session["session_sets"][0]["workout_day_name_snapshot"] == "Upper Session"
    assert recent_session["session_sets"][0]["program_name_snapshot"] == "Session Mode Test"
    assert recent_session["session_sets"][0]["planned_rest_seconds_snapshot"] == 120


def test_duplicate_session_set_creation_is_rejected() -> None:
    session_id, workout_exercise_id = start_test_session()
    create_test_session_set(session_id, workout_exercise_id)

    duplicate_response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "workout_exercise_id": workout_exercise_id,
            "set_number": 1,
            "planned_reps": "6-8",
            "planned_weight": 60,
            "weight_unit": "kg",
        },
    )

    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Session set already exists. Use update instead."


def test_cannot_add_set_after_finishing_session() -> None:
    session_id, workout_exercise_id = start_test_session()

    finish_response = client.post(
        f"/sessions/{session_id}/finish",
        json={"notes": "Done.", "readiness_score": 7},
    )
    assert finish_response.status_code == 200

    create_after_finish_response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "workout_exercise_id": workout_exercise_id,
            "set_number": 1,
            "planned_reps": "6-8",
            "planned_weight": 60,
            "weight_unit": "kg",
        },
    )

    assert create_after_finish_response.status_code == 400
    assert create_after_finish_response.json()["detail"] == "Cannot add sets to a finished session"


def test_cannot_update_set_after_finishing_session() -> None:
    session_id, workout_exercise_id = start_test_session()
    session_set_id = create_test_session_set(session_id, workout_exercise_id)

    finish_response = client.post(
        f"/sessions/{session_id}/finish",
        json={"notes": "Done.", "readiness_score": 7},
    )
    assert finish_response.status_code == 200

    update_after_finish_response = client.put(
        f"/sessions/{session_id}/sets/{session_set_id}",
        json={
            "actual_reps": 8,
            "actual_weight": 62.5,
            "difficulty_rating": 8,
            "completed": True,
        },
    )

    assert update_after_finish_response.status_code == 400
    assert update_after_finish_response.json()["detail"] == "Cannot update sets in a finished session"


def fake_reflection_payload(summary: str = "Session completed with useful training data.") -> tuple[dict, str]:
    return (
        {
            "summary": summary,
            "what_went_well": "The completed set was logged with actual reps, load, and difficulty.",
            "what_was_difficult": "Difficulty was high enough to watch next-session fatigue.",
            "next_session_suggestion": "Repeat the same planned work and compare actual reps before changing the plan.",
            "caution_flags": "No pain notes were logged. Stay cautious if high difficulty repeats.",
            "trainer_review_recommended": False,
        },
        "test-reflection-model",
    )


def finish_test_session_with_set() -> int:
    session_id, workout_exercise_id = start_test_session()
    session_set_id = create_test_session_set(session_id, workout_exercise_id)
    update_response = client.put(
        f"/sessions/{session_id}/sets/{session_set_id}",
        json={
            "actual_reps": 8,
            "actual_weight": 62.5,
            "difficulty_rating": 8,
            "completed": True,
            "rest_seconds_used": 120,
            "notes": "Hard but controlled.",
        },
    )
    assert update_response.status_code == 200

    finish_response = client.post(
        f"/sessions/{session_id}/finish",
        json={"notes": "Finished cleanly.", "readiness_score": 7},
    )
    assert finish_response.status_code == 200
    return session_id


def test_cannot_generate_reflection_for_active_session(monkeypatch) -> None:
    called = False

    def fake_generate(_session):
        nonlocal called
        called = True
        return fake_reflection_payload()

    monkeypatch.setattr(ai_session_reflection, "generate_session_reflection_with_ai", fake_generate)
    session_id, _workout_exercise_id = start_test_session()

    response = client.post(f"/sessions/{session_id}/reflection")

    assert response.status_code == 400
    assert response.json()["detail"] == "AI reflection is available only after finishing the session."
    assert called is False


def test_can_generate_and_get_saved_reflection_for_completed_session(monkeypatch) -> None:
    def fake_generate(_session):
        return fake_reflection_payload()

    monkeypatch.setattr(ai_session_reflection, "generate_session_reflection_with_ai", fake_generate)
    session_id = finish_test_session_with_set()

    generate_response = client.post(f"/sessions/{session_id}/reflection")
    assert generate_response.status_code == 200
    generated = generate_response.json()
    assert generated["workout_session_id"] == session_id
    assert generated["summary"] == "Session completed with useful training data."
    assert generated["model_used"] == "test-reflection-model"
    assert generated["trainer_review_recommended"] is False

    get_response = client.get(f"/sessions/{session_id}/reflection")
    assert get_response.status_code == 200
    saved = get_response.json()
    assert saved["id"] == generated["id"]
    assert saved["summary"] == generated["summary"]


def test_get_reflection_returns_latest_saved_reflection(monkeypatch) -> None:
    call_count = 0

    def fake_generate(_session):
        nonlocal call_count
        call_count += 1
        return fake_reflection_payload(f"Reflection version {call_count}")

    monkeypatch.setattr(ai_session_reflection, "generate_session_reflection_with_ai", fake_generate)
    session_id = finish_test_session_with_set()

    first_response = client.post(f"/sessions/{session_id}/reflection")
    assert first_response.status_code == 200
    second_response = client.post(f"/sessions/{session_id}/reflection")
    assert second_response.status_code == 200

    get_response = client.get(f"/sessions/{session_id}/reflection")
    assert get_response.status_code == 200
    latest = get_response.json()
    assert latest["summary"] == "Reflection version 2"
    assert latest["id"] == second_response.json()["id"]


def test_generate_reflection_missing_session_returns_404(monkeypatch) -> None:
    def fake_generate(_session):
        return fake_reflection_payload()

    monkeypatch.setattr(ai_session_reflection, "generate_session_reflection_with_ai", fake_generate)

    response = client.post("/sessions/999999/reflection")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout session not found"


def test_get_reflection_missing_session_returns_404() -> None:
    response = client.get("/sessions/999999/reflection")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout session not found"


def test_get_reflection_missing_reflection_returns_404() -> None:
    session_id = finish_test_session_with_set()

    response = client.get(f"/sessions/{session_id}/reflection")

    assert response.status_code == 404
    assert response.json()["detail"] == "No reflection found for this session."
