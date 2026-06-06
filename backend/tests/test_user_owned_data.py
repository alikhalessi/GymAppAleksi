from collections.abc import Callable, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import get_db
from app.main import app
from app.services import auth


def auth_user(user_id: str) -> auth.AuthUser:
    return auth.AuthUser(
        user_id=user_id,
        email=f"{user_id}@example.invalid",
        raw_claims={"sub": user_id},
    )


@pytest.fixture()
def user_client() -> Iterator[tuple[TestClient, Callable[[str], None]]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)
    current_user = {"value": auth_user("user-a")}

    def override_get_db() -> Iterator[Session]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    def override_current_user() -> auth.AuthUser:
        return current_user["value"]

    def set_user(user_id: str) -> None:
        current_user["value"] = auth_user(user_id)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[auth.get_current_user] = override_current_user
    try:
        yield TestClient(app), set_user
    finally:
        app.dependency_overrides.pop(auth.get_current_user, None)
        app.dependency_overrides.pop(get_db, None)
        models.Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def local_fallback_client() -> Iterator[TestClient]:
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
    app.dependency_overrides.pop(auth.get_current_user, None)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)
        models.Base.metadata.drop_all(bind=engine)


def create_program(client: TestClient, name: str = "Owned Program") -> int:
    response = client.post(
        "/programs",
        json={"name": name, "goal": "User isolation", "duration_weeks": 4},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_day(client: TestClient, program_id: int, name: str = "Upper") -> int:
    response = client.post(
        f"/programs/{program_id}/workout-days",
        json={"name": name, "day_order": 1},
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_exercise(client: TestClient, program_id: int, day_id: int) -> int:
    response = client.post(
        f"/programs/{program_id}/workout-days/{day_id}/exercises",
        json={
            "movement_name": "Bench Press",
            "sets": 3,
            "reps": "6-8",
            "rest_seconds": 120,
            "notes": "",
            "exercise_order": 1,
        },
    )
    assert response.status_code == 201
    return int(response.json()["id"])


def create_completed_session(client: TestClient, program_name: str) -> int:
    program_id = create_program(client, program_name)
    day_id = create_day(client, program_id)
    exercise_id = create_exercise(client, program_id, day_id)

    start_response = client.post(
        "/sessions/start",
        json={
            "program_id": program_id,
            "workout_day_id": day_id,
            "readiness_score": 7,
            "notes": "",
        },
    )
    assert start_response.status_code == 201
    session_id = int(start_response.json()["id"])

    set_response = client.post(
        f"/sessions/{session_id}/sets",
        json={
            "workout_exercise_id": exercise_id,
            "set_number": 1,
            "planned_reps": "6-8",
            "planned_weight": 60,
            "actual_reps": 8,
            "actual_weight": 60,
            "weight_unit": "kg",
            "difficulty_rating": 7,
            "completed": True,
        },
    )
    assert set_response.status_code == 201

    finish_response = client.post(
        f"/sessions/{session_id}/finish",
        json={"readiness_score": 7, "notes": "Done."},
    )
    assert finish_response.status_code == 200
    return session_id


def test_programs_are_isolated_by_current_user(user_client: tuple[TestClient, Callable[[str], None]]) -> None:
    client, set_user = user_client
    program_id = create_program(client, "User A Program")

    set_user("user-b")

    assert client.get("/programs").json() == []
    assert client.get(f"/programs/{program_id}").status_code == 404
    assert client.put(f"/programs/{program_id}", json={"name": "Stolen"}).status_code == 404
    assert client.delete(f"/programs/{program_id}").status_code == 404


def test_child_records_cannot_be_created_under_another_users_parent(
    user_client: tuple[TestClient, Callable[[str], None]],
) -> None:
    client, set_user = user_client
    program_id = create_program(client)
    day_id = create_day(client, program_id)

    set_user("user-b")

    response = client.post(
        f"/programs/{program_id}/workout-days/{day_id}/exercises",
        json={
            "movement_name": "Should Fail",
            "sets": 3,
            "reps": "10",
            "rest_seconds": 90,
            "notes": "",
            "exercise_order": 1,
        },
    )
    assert response.status_code == 404


def test_dashboard_summary_excludes_other_users_sessions(
    user_client: tuple[TestClient, Callable[[str], None]],
) -> None:
    client, set_user = user_client
    user_a_session_id = create_completed_session(client, "User A Dashboard")

    set_user("user-b")
    user_b_session_id = create_completed_session(client, "User B Dashboard")

    set_user("user-a")
    summary = client.get("/sessions/dashboard-summary").json()

    assert summary["total_sessions"] == 1
    assert summary["completed_sessions"] == 1
    assert summary["latest_completed_session_id"] == user_a_session_id
    assert summary["latest_program_name"] == "User A Dashboard"
    assert user_b_session_id != summary["latest_completed_session_id"]


def test_trainee_profile_is_user_scoped(user_client: tuple[TestClient, Callable[[str], None]]) -> None:
    client, set_user = user_client
    update_response = client.put("/trainee-profile", json={"display_name": "User A"})
    assert update_response.status_code == 200
    user_a_profile_id = update_response.json()["id"]

    set_user("user-b")
    user_b_response = client.get("/trainee-profile")

    assert user_b_response.status_code == 200
    assert user_b_response.json()["display_name"] == ""
    assert user_b_response.json()["id"] != user_a_profile_id


def test_readiness_checks_are_user_scoped(user_client: tuple[TestClient, Callable[[str], None]]) -> None:
    client, set_user = user_client
    create_response = client.post("/readiness-checks", json={"energy_level": 8})
    assert create_response.status_code == 201

    set_user("user-b")

    assert client.get("/readiness-checks").json() == []
    latest_response = client.get("/readiness-checks/latest")
    assert latest_response.status_code == 404


def test_workout_sessions_are_user_scoped(user_client: tuple[TestClient, Callable[[str], None]]) -> None:
    client, set_user = user_client
    session_id = create_completed_session(client, "User A Session")

    set_user("user-b")

    assert client.get("/sessions/recent").json() == []
    assert client.get(f"/sessions/{session_id}").status_code == 404


def test_auth_required_rejects_missing_token_on_protected_data_routes(monkeypatch) -> None:
    app.dependency_overrides.pop(auth.get_current_user, None)
    monkeypatch.setenv("AUTH_REQUIRED", "true")

    response = TestClient(app).get("/programs")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_local_fallback_user_still_supports_local_crud(
    local_fallback_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUTH_REQUIRED", "false")
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)

    program_id = create_program(local_fallback_client, "Local Fallback Program")
    list_response = local_fallback_client.get("/programs")

    assert list_response.status_code == 200
    assert any(program["id"] == program_id for program in list_response.json())
