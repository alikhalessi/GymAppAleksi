import os

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/exercises/{exercise_id}/youtube-videos", tags=["youtube videos"])

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"


def get_exercise_or_404(exercise_id: int, db: Session) -> models.WorkoutExercise:
    exercise = db.get(models.WorkoutExercise, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout exercise not found")
    return exercise


def get_video_or_404(exercise_id: int, video_id: int, db: Session) -> models.YouTubeVideo:
    video = db.get(models.YouTubeVideo, video_id)
    if video is None or video.workout_exercise_id != exercise_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="YouTube video not found")
    return video


def get_existing_youtube_ids(exercise_id: int, db: Session) -> set[str]:
    return set(
        db.scalars(
            select(models.YouTubeVideo.youtube_video_id).where(
                models.YouTubeVideo.workout_exercise_id == exercise_id
            )
        )
    )


def assert_youtube_video_is_new(exercise_id: int, youtube_video_id: str, db: Session) -> None:
    existing = db.scalar(
        select(models.YouTubeVideo.id).where(
            models.YouTubeVideo.workout_exercise_id == exercise_id,
            models.YouTubeVideo.youtube_video_id == youtube_video_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This YouTube video is already attached to this exercise.",
        )


@router.post("", response_model=schemas.YouTubeVideoRead, status_code=status.HTTP_201_CREATED)
def create_youtube_video(
    exercise_id: int,
    video_in: schemas.YouTubeVideoCreate,
    db: Session = Depends(get_db),
) -> models.YouTubeVideo:
    get_exercise_or_404(exercise_id, db)
    assert_youtube_video_is_new(exercise_id, video_in.youtube_video_id, db)
    video = models.YouTubeVideo(workout_exercise_id=exercise_id, **video_in.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.post("/search-and-save", response_model=list[schemas.YouTubeVideoRead])
def search_and_save_youtube_videos(
    exercise_id: int,
    query: str | None = Query(default=None, max_length=200),
    max_results: int = Query(default=5, ge=1, le=5),
    db: Session = Depends(get_db),
) -> list[models.YouTubeVideo]:
    exercise = get_exercise_or_404(exercise_id, db)
    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="YouTube API key is not configured. Set YOUTUBE_API_KEY in the backend environment and restart uvicorn.",
        )

    search_query = query or f"{exercise.movement_name} exercise proper form tutorial"
    params = {
        "part": "snippet",
        "q": search_query,
        "type": "video",
        "maxResults": max_results,
        "videoEmbeddable": "true",
        "safeSearch": "strict",
        "key": api_key,
    }

    try:
        response = httpx.get(YOUTUBE_SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "YouTube search failed because YouTube rejected the request. "
                "Check YOUTUBE_API_KEY permissions, quota, and API enablement."
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="YouTube search failed because the backend could not reach YouTube. Check network access and try again.",
        ) from exc

    existing_ids = get_existing_youtube_ids(exercise_id, db)
    saved_videos: list[models.YouTubeVideo] = []
    current_count = len(existing_ids)

    for item in payload.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        snippet = item.get("snippet", {})
        if not video_id or video_id in existing_ids:
            continue

        thumbnails = snippet.get("thumbnails", {})
        thumbnail_url = (
            thumbnails.get("high", {}).get("url")
            or thumbnails.get("medium", {}).get("url")
            or thumbnails.get("default", {}).get("url")
            or f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        )

        video = models.YouTubeVideo(
            workout_exercise_id=exercise_id,
            youtube_video_id=video_id,
            title=snippet.get("title") or f"{exercise.movement_name} video",
            channel_name=snippet.get("channelTitle") or "",
            thumbnail_url=thumbnail_url,
            display_order=current_count + len(saved_videos) + 1,
            approved=True,
        )
        db.add(video)
        saved_videos.append(video)
        existing_ids.add(video_id)

    db.commit()
    for video in saved_videos:
        db.refresh(video)

    return saved_videos


@router.get("", response_model=list[schemas.YouTubeVideoRead])
def list_youtube_videos(
    exercise_id: int,
    db: Session = Depends(get_db),
) -> list[models.YouTubeVideo]:
    get_exercise_or_404(exercise_id, db)
    return list(
        db.scalars(
            select(models.YouTubeVideo)
            .where(models.YouTubeVideo.workout_exercise_id == exercise_id)
            .order_by(models.YouTubeVideo.display_order.asc(), models.YouTubeVideo.created_at.asc())
        )
    )


@router.put("/{video_id}", response_model=schemas.YouTubeVideoRead)
def update_youtube_video(
    exercise_id: int,
    video_id: int,
    video_in: schemas.YouTubeVideoUpdate,
    db: Session = Depends(get_db),
) -> models.YouTubeVideo:
    get_exercise_or_404(exercise_id, db)
    video = get_video_or_404(exercise_id, video_id, db)
    updates = video_in.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(video, field, value)
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_youtube_video(
    exercise_id: int,
    video_id: int,
    db: Session = Depends(get_db),
) -> None:
    get_exercise_or_404(exercise_id, db)
    video = get_video_or_404(exercise_id, video_id, db)
    db.delete(video)
    db.commit()
