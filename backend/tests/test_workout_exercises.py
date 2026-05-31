from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_program_and_day() -> tuple[int, int]:
    program_response = client.post(
        "/programs",
        json={
            "name": "Strength Split",
            "goal": "Build structured lifting days",
            "duration_weeks": 8,
        },
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Upper Body", "day_order": 1},
    )
    assert day_response.status_code == 201
    workout_day_id = int(day_response.json()["id"])

    return program_id, workout_day_id


def test_workout_exercise_crud_flow() -> None:
    program_id, workout_day_id = create_program_and_day()
    base_url = f"/programs/{program_id}/workout-days/{workout_day_id}/exercises"

    create_response = client.post(
        base_url,
        json={
            "movement_name": "Bench Press",
            "sets": 4,
            "reps": "6-8",
            "rest_seconds": 120,
            "notes": "Keep shoulder blades tight.",
            "exercise_order": 1,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["workout_day_id"] == workout_day_id
    assert created["movement_name"] == "Bench Press"
    assert created["sets"] == 4
    assert created["reps"] == "6-8"
    assert created["rest_seconds"] == 120

    exercise_id = created["id"]

    list_response = client.get(base_url)
    assert list_response.status_code == 200
    assert any(exercise["id"] == exercise_id for exercise in list_response.json())

    get_response = client.get(f"{base_url}/{exercise_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == exercise_id

    update_response = client.put(
        f"{base_url}/{exercise_id}",
        json={"sets": 5, "rest_seconds": 150},
    )
    assert update_response.status_code == 200
    assert update_response.json()["sets"] == 5
    assert update_response.json()["rest_seconds"] == 150

    delete_response = client.delete(f"{base_url}/{exercise_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"{base_url}/{exercise_id}")
    assert missing_response.status_code == 404


def test_workout_exercise_requires_existing_workout_day() -> None:
    program_id, _ = create_program_and_day()

    response = client.post(
        f"/programs/{program_id}/workout-days/999999/exercises",
        json={
            "movement_name": "Ghost Press",
            "sets": 3,
            "reps": "10",
            "rest_seconds": 90,
            "notes": "This should fail.",
            "exercise_order": 1,
        },
    )
    assert response.status_code == 404
