from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_program_crud(client: TestClient) -> None:
    create_response = client.post(
        "/programs",
        json={
            "name": "Upper Lower",
            "goal": "Build strength consistently",
            "duration_weeks": 8,
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["id"] > 0
    assert created["name"] == "Upper Lower"
    assert created["goal"] == "Build strength consistently"
    assert created["duration_weeks"] == 8
    assert "created_at" in created

    list_response = client.get("/programs")

    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/programs/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Upper Lower"

    update_response = client.put(
        f"/programs/{created['id']}",
        json={
            "name": "Strength Base",
            "goal": "Improve main lifts",
            "duration_weeks": 10,
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Strength Base"
    assert updated["goal"] == "Improve main lifts"
    assert updated["duration_weeks"] == 10

    delete_response = client.delete(f"/programs/{created['id']}")

    assert delete_response.status_code == 204
    assert client.get(f"/programs/{created['id']}").status_code == 404


def test_program_validation_rejects_blank_name(client: TestClient) -> None:
    response = client.post(
        "/programs",
        json={
            "name": "   ",
            "goal": "Build consistency",
            "duration_weeks": 8,
        },
    )

    assert response.status_code == 422


def test_program_validation_rejects_invalid_duration(client: TestClient) -> None:
    response = client.post(
        "/programs",
        json={
            "name": "Beginner Plan",
            "goal": "Learn the basics",
            "duration_weeks": 0,
        },
    )

    assert response.status_code == 422
