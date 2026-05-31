from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_exercise() -> int:
    program_response = client.post(
        "/programs",
        json={"name": "Video Plan", "goal": "Test YouTube examples", "duration_weeks": 8},
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


def test_youtube_video_crud_flow() -> None:
    exercise_id = create_exercise()
    base_url = f"/exercises/{exercise_id}/youtube-videos"

    create_response = client.post(
        base_url,
        json={
            "youtube_video_id": "dQw4w9WgXcQ",
            "title": "Bench Press Tutorial",
            "channel_name": "Example Coach",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            "display_order": 1,
            "approved": True,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["workout_exercise_id"] == exercise_id
    assert created["youtube_video_id"] == "dQw4w9WgXcQ"

    video_id = created["id"]

    list_response = client.get(base_url)
    assert list_response.status_code == 200
    assert any(video["id"] == video_id for video in list_response.json())

    update_response = client.put(
        f"{base_url}/{video_id}",
        json={"display_order": 2, "approved": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["display_order"] == 2
    assert update_response.json()["approved"] is False

    delete_response = client.delete(f"{base_url}/{video_id}")
    assert delete_response.status_code == 204

    after_delete = client.get(base_url)
    assert after_delete.status_code == 200
    assert all(video["id"] != video_id for video in after_delete.json())
