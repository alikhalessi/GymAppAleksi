from fastapi.testclient import TestClient

from app.main import app
from app.routers import youtube_videos

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
    assert created["approved"] is True
    assert created["rejected"] is False
    assert created["preferred"] is False
    assert created["quality_label"] == ""
    assert created["user_note"] == ""

    video_id = created["id"]

    duplicate_response = client.post(
        base_url,
        json={
            "youtube_video_id": "dQw4w9WgXcQ",
            "title": "Duplicate Bench Press Tutorial",
            "channel_name": "Example Coach",
            "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            "display_order": 2,
            "approved": True,
        },
    )
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "YouTube video already exists for this exercise."

    list_response = client.get(base_url)
    assert list_response.status_code == 200
    assert any(video["id"] == video_id for video in list_response.json())

    update_response = client.put(
        f"{base_url}/{video_id}",
        json={
            "display_order": 2,
            "approved": False,
            "rejected": True,
            "quality_label": "Needs review",
            "user_note": "Elbow position is hard to see.",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["display_order"] == 2
    assert update_response.json()["approved"] is False
    assert update_response.json()["rejected"] is True
    assert update_response.json()["quality_label"] == "Needs review"
    assert update_response.json()["user_note"] == "Elbow position is hard to see."

    delete_response = client.delete(f"{base_url}/{video_id}")
    assert delete_response.status_code == 204

    after_delete = client.get(base_url)
    assert after_delete.status_code == 200
    assert all(video["id"] != video_id for video in after_delete.json())


def test_preferred_video_unsets_other_videos() -> None:
    exercise_id = create_exercise()
    base_url = f"/exercises/{exercise_id}/youtube-videos"

    first_response = client.post(
        base_url,
        json={
            "youtube_video_id": "firstVideo01",
            "title": "First Bench Tutorial",
            "channel_name": "Coach One",
            "display_order": 1,
            "preferred": True,
        },
    )
    second_response = client.post(
        base_url,
        json={
            "youtube_video_id": "secondVideo2",
            "title": "Second Bench Tutorial",
            "channel_name": "Coach Two",
            "display_order": 2,
            "preferred": True,
        },
    )
    assert first_response.status_code == 201
    assert second_response.status_code == 201

    videos_after_create = client.get(base_url).json()
    assert sum(1 for video in videos_after_create if video["preferred"]) == 1
    assert next(video for video in videos_after_create if video["id"] == second_response.json()["id"])["preferred"] is True

    first_video_id = int(first_response.json()["id"])
    second_video_id = int(second_response.json()["id"])
    preferred_response = client.put(f"{base_url}/{first_video_id}", json={"preferred": True})

    assert preferred_response.status_code == 200
    assert preferred_response.json()["preferred"] is True

    videos = client.get(base_url).json()
    assert sum(1 for video in videos if video["preferred"]) == 1
    assert next(video for video in videos if video["id"] == first_video_id)["preferred"] is True
    assert next(video for video in videos if video["id"] == second_video_id)["preferred"] is False


def test_search_and_save_skips_existing_youtube_ids(monkeypatch) -> None:
    exercise_id = create_exercise()
    base_url = f"/exercises/{exercise_id}/youtube-videos"

    existing_response = client.post(
        base_url,
        json={
            "youtube_video_id": "existingVid",
            "title": "Existing Bench Tutorial",
            "channel_name": "Coach One",
            "display_order": 1,
        },
    )
    assert existing_response.status_code == 201

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {
                "items": [
                    {
                        "id": {"videoId": "existingVid"},
                        "snippet": {
                            "title": "Existing Duplicate",
                            "channelTitle": "Coach Duplicate",
                            "thumbnails": {"high": {"url": "https://example.com/existing.jpg"}},
                        },
                    },
                    {
                        "id": {"videoId": "newVideo123"},
                        "snippet": {
                            "title": "New Bench Tutorial",
                            "channelTitle": "Coach Two",
                            "thumbnails": {"medium": {"url": "https://example.com/new.jpg"}},
                        },
                    },
                ]
            }

    monkeypatch.setattr(youtube_videos.os, "getenv", lambda key: "fake-youtube-key" if key == "YOUTUBE_API_KEY" else None)
    monkeypatch.setattr(youtube_videos.httpx, "get", lambda *args, **kwargs: FakeResponse())

    search_response = client.post(f"{base_url}/search-and-save")

    assert search_response.status_code == 200
    saved = search_response.json()
    assert len(saved) == 1
    assert saved[0]["youtube_video_id"] == "newVideo123"
    assert saved[0]["approved"] is True
    assert saved[0]["rejected"] is False
    assert saved[0]["preferred"] is False

    list_response = client.get(base_url)
    videos = list_response.json()
    assert len([video for video in videos if video["youtube_video_id"] == "existingVid"]) == 1
    assert len([video for video in videos if video["youtube_video_id"] == "newVideo123"]) == 1
