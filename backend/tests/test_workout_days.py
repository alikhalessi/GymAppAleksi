from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_program() -> int:
    response = client.post(
        "/programs",
        json={
            "name": "Four Day Strength",
            "goal": "Organize weekly strength sessions",
            "duration_weeks": 8,
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def test_workout_day_crud_flow() -> None:
    program_id = create_program()

    create_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Upper Body", "day_order": 1},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["program_id"] == program_id
    assert created["name"] == "Upper Body"
    assert created["day_order"] == 1

    workout_day_id = created["id"]

    list_response = client.get(f"/programs/{program_id}/workout-days")
    assert list_response.status_code == 200
    assert any(day["id"] == workout_day_id for day in list_response.json())

    get_response = client.get(f"/programs/{program_id}/workout-days/{workout_day_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == workout_day_id

    update_response = client.put(
        f"/programs/{program_id}/workout-days/{workout_day_id}",
        json={"name": "Upper Strength", "day_order": 2},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Upper Strength"
    assert update_response.json()["day_order"] == 2

    delete_response = client.delete(f"/programs/{program_id}/workout-days/{workout_day_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/programs/{program_id}/workout-days/{workout_day_id}")
    assert missing_response.status_code == 404


def test_workout_day_requires_existing_program() -> None:
    response = client.post(
        "/programs/999999/workout-days",
        json={"name": "Ghost Day", "day_order": 1},
    )
    assert response.status_code == 404
