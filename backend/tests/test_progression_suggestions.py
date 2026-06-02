from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_progression_plan() -> tuple[int, int, int]:
    program_response = client.post(
        "/programs",
        json={"name": "Progression Test", "goal": "Verify rules", "duration_weeks": 6},
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Strength Day", "day_order": 1},
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
            "notes": "",
            "exercise_order": 1,
        },
    )
    assert exercise_response.status_code == 201
    workout_exercise_id = int(exercise_response.json()["id"])
    return program_id, workout_day_id, workout_exercise_id


def start_progression_session() -> tuple[int, int]:
    program_id, workout_day_id, workout_exercise_id = create_progression_plan()
    response = client.post(
        "/sessions/start",
        json={
            "program_id": program_id,
            "workout_day_id": workout_day_id,
            "readiness_score": 7,
            "notes": "",
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"]), workout_exercise_id


def add_session_set(
    session_id: int,
    workout_exercise_id: int,
    set_number: int,
    actual_reps: int | None,
    actual_weight: float | None,
    difficulty_rating: int | None,
    completed: bool = True,
) -> None:
    response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "workout_exercise_id": workout_exercise_id,
            "set_number": set_number,
            "planned_reps": "6-8",
            "planned_weight": 60,
            "actual_reps": actual_reps,
            "actual_weight": actual_weight,
            "weight_unit": "kg",
            "difficulty_rating": difficulty_rating,
            "completed": completed,
            "rest_seconds_used": 120,
            "notes": "",
        },
    )
    assert response.status_code == 201


def finish_session(session_id: int) -> None:
    response = client.post(
        f"/sessions/{session_id}/finish",
        json={"readiness_score": 7, "notes": "Done."},
    )
    assert response.status_code == 200


def test_cannot_generate_progression_suggestions_for_active_session() -> None:
    session_id, _workout_exercise_id = start_progression_session()

    response = client.post(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 400
    assert response.json()["detail"] == "Progression suggestions are available only after finishing the session."


def test_completed_low_difficulty_session_suggests_increase_weight() -> None:
    session_id, workout_exercise_id = start_progression_session()
    for set_number in range(1, 4):
        add_session_set(session_id, workout_exercise_id, set_number, 8, 60, 7)
    finish_session(session_id)

    response = client.post(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 200
    suggestions = response.json()
    assert len(suggestions) == 1
    assert suggestions[0]["suggestion_type"] == "increase_weight"
    assert suggestions[0]["suggested_weight"] == 62.5
    assert suggestions[0]["confidence"] == "high"


def test_high_difficulty_session_suggests_reduce_weight() -> None:
    session_id, workout_exercise_id = start_progression_session()
    for set_number in range(1, 4):
        add_session_set(session_id, workout_exercise_id, set_number, 6, 60, 9)
    finish_session(session_id)

    response = client.post(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 200
    suggestion = response.json()[0]
    assert suggestion["suggestion_type"] == "reduce_weight"
    assert suggestion["suggested_weight"] == 57.5


def test_incomplete_sets_suggest_improve_completion() -> None:
    session_id, workout_exercise_id = start_progression_session()
    add_session_set(session_id, workout_exercise_id, 1, 8, 60, 6, completed=True)
    add_session_set(session_id, workout_exercise_id, 2, None, None, None, completed=False)
    add_session_set(session_id, workout_exercise_id, 3, None, None, None, completed=False)
    finish_session(session_id)

    response = client.post(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 200
    suggestion = response.json()[0]
    assert suggestion["suggestion_type"] == "improve_completion"
    assert suggestion["suggested_weight"] == 60
    assert suggestion["suggested_reps"] == "6-8"


def test_insufficient_data_returns_insufficient_data() -> None:
    session_id, workout_exercise_id = start_progression_session()
    add_session_set(session_id, workout_exercise_id, 1, None, None, None, completed=False)
    finish_session(session_id)

    response = client.post(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 200
    suggestion = response.json()[0]
    assert suggestion["suggestion_type"] == "insufficient_data"
    assert suggestion["confidence"] == "low"


def test_get_returns_saved_progression_suggestions() -> None:
    session_id, workout_exercise_id = start_progression_session()
    add_session_set(session_id, workout_exercise_id, 1, 8, 60, 7)
    finish_session(session_id)
    generate_response = client.post(f"/sessions/{session_id}/progression-suggestions")
    assert generate_response.status_code == 200

    response = client.get(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 200
    assert response.json() == generate_response.json()


def test_regenerating_progression_suggestions_replaces_old_suggestions() -> None:
    session_id, workout_exercise_id = start_progression_session()
    add_session_set(session_id, workout_exercise_id, 1, 8, 60, 7)
    finish_session(session_id)

    first_response = client.post(f"/sessions/{session_id}/progression-suggestions")
    assert first_response.status_code == 200
    second_response = client.post(f"/sessions/{session_id}/progression-suggestions")
    assert second_response.status_code == 200

    get_response = client.get(f"/sessions/{session_id}/progression-suggestions")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1
    assert get_response.json() == second_response.json()


def test_get_progression_suggestions_missing_session_returns_404() -> None:
    response = client.get("/sessions/999999/progression-suggestions")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workout session not found"


def test_get_progression_suggestions_returns_empty_list_when_none_exist() -> None:
    session_id, _workout_exercise_id = start_progression_session()
    finish_session(session_id)

    response = client.get(f"/sessions/{session_id}/progression-suggestions")

    assert response.status_code == 200
    assert response.json() == []
