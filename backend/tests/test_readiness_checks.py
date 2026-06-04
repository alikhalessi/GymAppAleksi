from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import get_db
from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        models.Base.metadata.drop_all(bind=engine)


def create_training_plan(client: TestClient) -> tuple[int, int]:
    program_response = client.post(
        "/programs",
        json={"name": "Readiness Session Test", "goal": "Verify context", "duration_weeks": 4},
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Full Body", "day_order": 1},
    )
    assert day_response.status_code == 201
    return program_id, int(day_response.json()["id"])


def test_create_readiness_check_calculates_score(client: TestClient) -> None:
    response = client.post(
        "/readiness-checks",
        json={
            "energy_level": 8,
            "sleep_quality": 6,
            "soreness_level": 4,
            "stress_level": 3,
            "pain_or_limitations_today": "Left shoulder feels tight.",
            "available_time_minutes": 70,
            "notes": "Keep pressing controlled.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["energy_level"] == 8
    assert data["sleep_quality"] == 6
    assert data["soreness_level"] == 4
    assert data["stress_level"] == 3
    assert data["readiness_score"] == 7
    assert data["created_at"] is not None


def test_create_readiness_check_with_missing_values_returns_null_score(client: TestClient) -> None:
    response = client.post(
        "/readiness-checks",
        json={
            "pain_or_limitations_today": "",
            "notes": "No numbers entered today.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["energy_level"] is None
    assert data["readiness_score"] is None


def test_invalid_readiness_value_returns_validation_error(client: TestClient) -> None:
    response = client.post("/readiness-checks", json={"energy_level": 11})

    assert response.status_code == 422


def test_latest_readiness_check_returns_404_when_empty(client: TestClient) -> None:
    response = client.get("/readiness-checks/latest")

    assert response.status_code == 404
    assert response.json()["detail"] == "No readiness check found."


def test_latest_readiness_check_returns_newest(client: TestClient) -> None:
    first_response = client.post("/readiness-checks", json={"energy_level": 4})
    second_response = client.post("/readiness-checks", json={"energy_level": 9})

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    latest_response = client.get("/readiness-checks/latest")

    assert latest_response.status_code == 200
    assert latest_response.json()["id"] == second_response.json()["id"]
    assert latest_response.json()["readiness_score"] == 9


def test_list_readiness_checks_returns_newest_first(client: TestClient) -> None:
    responses = [
        client.post("/readiness-checks", json={"energy_level": value})
        for value in (3, 5, 7)
    ]
    for response in responses:
        assert response.status_code == 201

    list_response = client.get("/readiness-checks?limit=2")

    assert list_response.status_code == 200
    data = list_response.json()
    assert [item["id"] for item in data] == [
        responses[2].json()["id"],
        responses[1].json()["id"],
    ]


def test_session_start_accepts_latest_readiness_score(client: TestClient) -> None:
    check_response = client.post(
        "/readiness-checks",
        json={
            "energy_level": 8,
            "sleep_quality": 8,
            "soreness_level": 3,
            "stress_level": 3,
        },
    )
    assert check_response.status_code == 201
    program_id, workout_day_id = create_training_plan(client)

    start_response = client.post(
        "/sessions/start",
        json={
            "program_id": program_id,
            "workout_day_id": workout_day_id,
            "readiness_score": check_response.json()["readiness_score"],
            "notes": "",
        },
    )

    assert start_response.status_code == 201
    assert start_response.json()["readiness_score"] == check_response.json()["readiness_score"]
