from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def parsed_plan_payload() -> dict:
    return {
        "parsed_plan": {
            "program": {
                "name": "Imported Strength Plan",
                "goal": "Imported from plain text",
                "duration_weeks": 8,
            },
            "workout_days": [
                {
                    "name": "Upper Body",
                    "day_order": 1,
                    "exercises": [
                        {
                            "movement_name": "Bench Press",
                            "sets": 4,
                            "reps": "6-8",
                            "rest_seconds": 120,
                            "notes": "Keep shoulder blades tight.",
                            "exercise_order": 1,
                            "confidence": 0.92,
                            "warnings": [],
                        }
                    ],
                }
            ],
        },
        "approval_status": "approved_by_user",
    }


def test_analyze_requires_openai_api_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = client.post(
        "/imports/workout-plan/analyze",
        json={"raw_text": "Upper body day\nBench Press 4x8 rest 120 seconds"},
    )

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]


def test_save_imported_workout_plan() -> None:
    response = client.post("/imports/workout-plan/save", json=parsed_plan_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["approval_status"] == "approved_by_user"
    assert data["program"]["name"] == "Imported Strength Plan"
    assert len(data["workout_days"]) == 1
    assert data["workout_days"][0]["name"] == "Upper Body"
    assert len(data["exercises"]) == 1
    assert data["exercises"][0]["movement_name"] == "Bench Press"
