from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import get_db
from app.main import app
from app.services import ai_session_reflection


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


def create_dashboard_plan(client: TestClient) -> tuple[int, int, int]:
    program_response = client.post(
        "/programs",
        json={"name": "Dashboard Strength", "goal": "Track training memory", "duration_weeks": 8},
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Upper Dashboard", "day_order": 1},
    )
    assert day_response.status_code == 201
    workout_day_id = int(day_response.json()["id"])

    exercise_response = client.post(
        f"/programs/{program_id}/workout-days/{workout_day_id}/exercises",
        json={
            "movement_name": "Bench Press",
            "sets": 2,
            "reps": "6-8",
            "rest_seconds": 120,
            "notes": "",
            "exercise_order": 1,
        },
    )
    assert exercise_response.status_code == 201
    workout_exercise_id = int(exercise_response.json()["id"])
    return program_id, workout_day_id, workout_exercise_id


def start_dashboard_session(client: TestClient) -> tuple[int, int]:
    program_id, workout_day_id, workout_exercise_id = create_dashboard_plan(client)
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


def add_dashboard_set(
    client: TestClient,
    session_id: int,
    workout_exercise_id: int,
    set_number: int,
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
            "actual_reps": 8 if completed else None,
            "actual_weight": 60 if completed else None,
            "weight_unit": "kg",
            "difficulty_rating": difficulty_rating,
            "completed": completed,
            "rest_seconds_used": 120,
            "notes": "",
        },
    )
    assert response.status_code == 201


def finish_dashboard_session(client: TestClient, session_id: int) -> None:
    response = client.post(
        f"/sessions/{session_id}/finish",
        json={"readiness_score": 7, "notes": "Finished."},
    )
    assert response.status_code == 200


def test_dashboard_summary_without_sessions_returns_empty_shape(client: TestClient) -> None:
    response = client.get("/sessions/dashboard-summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_sessions": 0,
        "completed_sessions": 0,
        "active_sessions": 0,
        "total_logged_sets": 0,
        "completed_sets": 0,
        "average_difficulty": None,
        "latest_completed_session_id": None,
        "latest_completed_session_started_at": None,
        "latest_completed_session_finished_at": None,
        "latest_program_name": None,
        "latest_workout_day_name": None,
        "latest_exercise_names": [],
        "latest_reflection_summary": None,
        "latest_progression_suggestions": [],
    }


def test_dashboard_summary_counts_completed_sets_and_average_difficulty(client: TestClient) -> None:
    completed_session_id, workout_exercise_id = start_dashboard_session(client)
    add_dashboard_set(client, completed_session_id, workout_exercise_id, 1, 6)
    add_dashboard_set(client, completed_session_id, workout_exercise_id, 2, 8)
    finish_dashboard_session(client, completed_session_id)
    start_dashboard_session(client)

    response = client.get("/sessions/dashboard-summary")

    assert response.status_code == 200
    summary = response.json()
    assert summary["total_sessions"] == 2
    assert summary["completed_sessions"] == 1
    assert summary["active_sessions"] == 1
    assert summary["total_logged_sets"] == 2
    assert summary["completed_sets"] == 2
    assert summary["average_difficulty"] == 7
    assert summary["latest_completed_session_id"] == completed_session_id
    assert summary["latest_program_name"] == "Dashboard Strength"
    assert summary["latest_workout_day_name"] == "Upper Dashboard"
    assert summary["latest_exercise_names"] == ["Bench Press"]
    assert summary["latest_completed_session_started_at"] is not None
    assert summary["latest_completed_session_finished_at"] is not None


def test_dashboard_summary_uses_non_null_difficulty_only(client: TestClient) -> None:
    session_id, workout_exercise_id = start_dashboard_session(client)
    add_dashboard_set(client, session_id, workout_exercise_id, 1, 9)
    add_dashboard_set(client, session_id, workout_exercise_id, 2, None)
    finish_dashboard_session(client, session_id)

    response = client.get("/sessions/dashboard-summary")

    assert response.status_code == 200
    assert response.json()["average_difficulty"] == 9


def test_dashboard_summary_includes_latest_reflection_and_progression_without_api_keys(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_generate(_session):
        return (
            {
                "summary": "Dashboard reflection summary.",
                "what_went_well": "Logged sets include usable difficulty data.",
                "what_was_difficult": "No major issue.",
                "next_session_suggestion": "Repeat and compare.",
                "caution_flags": "No caution flags.",
                "trainer_review_recommended": False,
            },
            "test-model",
        )

    monkeypatch.setattr(ai_session_reflection, "generate_session_reflection_with_ai", fake_generate)
    session_id, workout_exercise_id = start_dashboard_session(client)
    add_dashboard_set(client, session_id, workout_exercise_id, 1, 6)
    add_dashboard_set(client, session_id, workout_exercise_id, 2, 7)
    finish_dashboard_session(client, session_id)

    reflection_response = client.post(f"/sessions/{session_id}/reflection")
    progression_response = client.post(f"/sessions/{session_id}/progression-suggestions")
    summary_response = client.get("/sessions/dashboard-summary")

    assert reflection_response.status_code == 200
    assert progression_response.status_code == 200
    assert summary_response.status_code == 200
    summary = summary_response.json()
    assert summary["latest_reflection_summary"] == "Dashboard reflection summary."
    assert summary["latest_progression_suggestions"]
    assert "Bench Press" in summary["latest_progression_suggestions"][0]
