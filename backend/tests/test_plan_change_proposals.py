import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import get_db
from app.main import app
from app.routers import plan_change_proposals


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


def create_program_context(client: TestClient) -> tuple[int, int, int, int]:
    program_response = client.post(
        "/programs",
        json={"name": "Proposal Test Plan", "goal": "Build strength", "duration_weeks": 6},
    )
    assert program_response.status_code == 201
    program_id = int(program_response.json()["id"])

    version_response = client.post(
        f"/programs/{program_id}/versions",
        json={
            "version_label": "Original imported plan",
            "version_type": "imported_original",
            "source": "import",
            "is_active": True,
        },
    )
    assert version_response.status_code == 201
    version_id = int(version_response.json()["id"])

    day_response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": "Lower Body", "day_order": 1},
    )
    assert day_response.status_code == 201
    day_id = int(day_response.json()["id"])

    exercise_response = client.post(
        f"/programs/{program_id}/workout-days/{day_id}/exercises",
        json={
            "movement_name": "Deadlift",
            "sets": 4,
            "reps": "5",
            "rest_seconds": 180,
            "notes": "Heavy hinge.",
            "exercise_order": 1,
        },
    )
    assert exercise_response.status_code == 201
    exercise_id = int(exercise_response.json()["id"])

    return program_id, version_id, day_id, exercise_id


def fake_proposal_payload() -> tuple[dict, str]:
    return (
        {
            "proposal_title": "Reduce lower body loading",
            "proposal_summary": "Make today's lower body work easier without changing the saved program.",
            "proposed_changes": [
                {
                    "change_type": "volume_reduction",
                    "target": "Lower Body - Deadlift",
                    "original": "Deadlift 4 sets of 5",
                    "proposed": "Deadlift 2 sets of 5 at a lighter load",
                    "reason": "User reported low energy and asked for an easier session.",
                    "risk_or_caution": "Do not train through sharp pain; review if symptoms persist.",
                }
            ],
            "caution_notes": "Advisory only. Keep technique controlled.",
            "trainer_review_recommended": True,
        },
        "test-change-model",
    )


def test_post_creates_plan_change_proposal_with_mocked_ai(
    client: TestClient,
    monkeypatch,
) -> None:
    program_id, version_id, day_id, exercise_id = create_program_context(client)
    captured_payload: dict = {}

    def fake_generate(payload):
        captured_payload.update(payload)
        return fake_proposal_payload()

    monkeypatch.setattr(plan_change_proposals.ai_change_proposal, "generate_change_proposal_with_ai", fake_generate)

    response = client.post(
        "/plan-change-proposals",
        json={
            "program_id": program_id,
            "workout_day_id": day_id,
            "user_request": "Make today easier because energy is low.",
            "context_note": "Keep the original plan preserved.",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["program_id"] == program_id
    assert data["program_version_id"] == version_id
    assert data["workout_day_id"] == day_id
    assert data["proposal_title"] == "Reduce lower body loading"
    assert data["trainer_review_recommended"] is True
    assert data["status"] == "draft"
    assert data["model_used"] == "test-change-model"
    stored_changes = json.loads(data["proposed_changes_json"])
    assert stored_changes[0]["target"] == "Lower Body - Deadlift"
    assert captured_payload["program"]["name"] == "Proposal Test Plan"
    assert captured_payload["active_or_selected_program_version"]["id"] == version_id
    assert captured_payload["selected_workout_day"]["id"] == day_id

    with next(app.dependency_overrides[get_db]()) as db:
        exercise = db.get(models.WorkoutExercise, exercise_id)
        assert exercise is not None
        assert exercise.movement_name == "Deadlift"
        assert exercise.sets == 4


def test_get_list_and_detail_return_proposal(client: TestClient, monkeypatch) -> None:
    program_id, _version_id, day_id, _exercise_id = create_program_context(client)
    monkeypatch.setattr(
        plan_change_proposals.ai_change_proposal,
        "generate_change_proposal_with_ai",
        lambda _payload: fake_proposal_payload(),
    )
    create_response = client.post(
        "/plan-change-proposals",
        json={
            "program_id": program_id,
            "workout_day_id": day_id,
            "user_request": "Replace deadlift today.",
        },
    )
    assert create_response.status_code == 201
    proposal_id = int(create_response.json()["id"])

    list_response = client.get(f"/plan-change-proposals?program_id={program_id}")
    detail_response = client.get(f"/plan-change-proposals/{proposal_id}")

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [proposal_id]
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == proposal_id


def test_status_update_changes_status_only(client: TestClient, monkeypatch) -> None:
    program_id, _version_id, day_id, exercise_id = create_program_context(client)
    monkeypatch.setattr(
        plan_change_proposals.ai_change_proposal,
        "generate_change_proposal_with_ai",
        lambda _payload: fake_proposal_payload(),
    )
    create_response = client.post(
        "/plan-change-proposals",
        json={
            "program_id": program_id,
            "workout_day_id": day_id,
            "user_request": "Shorten this workout to 45 minutes.",
        },
    )
    proposal_id = int(create_response.json()["id"])

    update_response = client.put(
        f"/plan-change-proposals/{proposal_id}/status",
        json={"status": "accepted"},
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["status"] == "accepted"
    assert data["updated_at"] is not None

    with next(app.dependency_overrides[get_db]()) as db:
        exercise = db.scalar(select(models.WorkoutExercise).where(models.WorkoutExercise.id == exercise_id))
        assert exercise is not None
        assert exercise.movement_name == "Deadlift"
        assert exercise.sets == 4


def test_invalid_status_is_rejected(client: TestClient, monkeypatch) -> None:
    program_id, _version_id, day_id, _exercise_id = create_program_context(client)
    monkeypatch.setattr(
        plan_change_proposals.ai_change_proposal,
        "generate_change_proposal_with_ai",
        lambda _payload: fake_proposal_payload(),
    )
    create_response = client.post(
        "/plan-change-proposals",
        json={
            "program_id": program_id,
            "workout_day_id": day_id,
            "user_request": "Make this more hypertrophy focused.",
        },
    )
    proposal_id = int(create_response.json()["id"])

    response = client.put(
        f"/plan-change-proposals/{proposal_id}/status",
        json={"status": "applied"},
    )

    assert response.status_code == 422


def test_missing_program_returns_404_without_calling_ai(client: TestClient, monkeypatch) -> None:
    called = False

    def fake_generate(_payload):
        nonlocal called
        called = True
        return fake_proposal_payload()

    monkeypatch.setattr(plan_change_proposals.ai_change_proposal, "generate_change_proposal_with_ai", fake_generate)

    response = client.post(
        "/plan-change-proposals",
        json={
            "program_id": 999999,
            "user_request": "Make today easier.",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Program not found"
    assert called is False
