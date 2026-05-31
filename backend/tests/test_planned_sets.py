from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_exercise() -> int:
    program_response = client.post(
        "/programs",
        json={"name": "Strength", "goal": "Test planned sets", "duration_weeks": 8},
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Upper", "day_order": 1},
    )
    assert day_response.status_code == 201
    day_id = int(day_response.json()["id"])

    exercise_response = client.post(
        f"/programs/{program_id}/workout-days/{day_id}/exercises",
        json={
            "movement_name": "Bench Press",
            "sets": 4,
            "reps": "6-8",
            "rest_seconds": 120,
            "notes": "",
            "exercise_order": 1,
        },
    )
    assert exercise_response.status_code == 201
    return int(exercise_response.json()["id"])


def test_planned_set_crud_flow() -> None:
    exercise_id = create_exercise()
    base_url = f"/exercises/{exercise_id}/planned-sets"

    create_response = client.post(
        base_url,
        json={
            "set_number": 1,
            "target_reps": "6-8",
            "suggested_weight": 50,
            "weight_unit": "kg",
            "note": "Conservative first working set",
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["workout_exercise_id"] == exercise_id
    assert created["set_number"] == 1
    assert created["suggested_weight"] == 50
    assert created["weight_unit"] == "kg"

    planned_set_id = created["id"]

    list_response = client.get(base_url)
    assert list_response.status_code == 200
    assert any(item["id"] == planned_set_id for item in list_response.json())

    update_response = client.put(
        f"{base_url}/{planned_set_id}",
        json={"suggested_weight": 52.5, "note": "Small increase"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["suggested_weight"] == 52.5
    assert update_response.json()["note"] == "Small increase"

    delete_response = client.delete(f"{base_url}/{planned_set_id}")
    assert delete_response.status_code == 204

    missing_after_delete = client.get(base_url)
    assert missing_after_delete.status_code == 200
    assert all(item["id"] != planned_set_id for item in missing_after_delete.json())


def test_planned_set_requires_existing_exercise() -> None:
    response = client.post(
        "/exercises/999999/planned-sets",
        json={
            "set_number": 1,
            "target_reps": "8",
            "suggested_weight": 20,
            "weight_unit": "kg",
            "note": "Should fail",
        },
    )
    assert response.status_code == 404
