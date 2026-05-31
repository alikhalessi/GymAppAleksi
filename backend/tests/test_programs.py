from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_program_crud_flow() -> None:
    create_response = client.post(
        "/programs",
        json={
            "name": "Strength Foundation",
            "goal": "Build strength while learning core lifts",
            "duration_weeks": 8,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Strength Foundation"
    assert created["goal"] == "Build strength while learning core lifts"
    assert created["duration_weeks"] == 8
    assert "id" in created

    program_id = created["id"]

    list_response = client.get("/programs")
    assert list_response.status_code == 200
    assert any(program["id"] == program_id for program in list_response.json())

    get_response = client.get(f"/programs/{program_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == program_id

    update_response = client.put(
        f"/programs/{program_id}",
        json={"duration_weeks": 10},
    )
    assert update_response.status_code == 200
    assert update_response.json()["duration_weeks"] == 10

    delete_response = client.delete(f"/programs/{program_id}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/programs/{program_id}")
    assert missing_response.status_code == 404
