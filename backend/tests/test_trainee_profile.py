from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
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


def test_get_trainee_profile_creates_default_profile(client: TestClient) -> None:
    response = client.get("/trainee-profile")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["display_name"] == ""
    assert data["age"] is None
    assert data["bmi"] is None
    assert data["training_experience"] == ""
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_put_trainee_profile_updates_fields_and_calculates_bmi(client: TestClient) -> None:
    response = client.put(
        "/trainee-profile",
        json={
            "display_name": "Aleksi",
            "age": 45,
            "sex": "optional",
            "height_cm": 167,
            "weight_kg": 98,
            "training_experience": "intermediate",
            "primary_goal": "strength and fat loss",
            "limitations": "Shoulder gets irritated by sloppy pressing.",
            "available_equipment": "Full gym",
            "preferred_session_minutes": 75,
            "notes": "Train conservatively when sleep is poor.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Aleksi"
    assert data["age"] == 45
    assert data["height_cm"] == 167
    assert data["weight_kg"] == 98
    assert data["bmi"] == 35.1
    assert data["primary_goal"] == "strength and fat loss"
    assert data["preferred_session_minutes"] == 75


def test_bmi_becomes_null_when_height_or_weight_missing(client: TestClient) -> None:
    create_response = client.put(
        "/trainee-profile",
        json={"height_cm": 180, "weight_kg": 80},
    )
    assert create_response.status_code == 200
    assert create_response.json()["bmi"] == 24.7

    update_response = client.put("/trainee-profile", json={"weight_kg": None})

    assert update_response.status_code == 200
    assert update_response.json()["weight_kg"] is None
    assert update_response.json()["bmi"] is None


def test_repeated_get_returns_same_profile_without_duplicates(client: TestClient) -> None:
    first_response = client.get("/trainee-profile")
    second_response = client.get("/trainee-profile")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == second_response.json()["id"]

    with next(app.dependency_overrides[get_db]()) as db:
        profiles = list(db.scalars(select(models.TraineeProfile)))
    assert len(profiles) == 1


def test_invalid_profile_values_return_validation_error(client: TestClient) -> None:
    response = client.put(
        "/trainee-profile",
        json={
            "age": 8,
            "height_cm": 20,
            "weight_kg": 5,
            "preferred_session_minutes": 2,
        },
    )

    assert response.status_code == 422
