from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/exercises/{exercise_id}/youtube-videos", tags=["youtube videos"])


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


@router.post("", response_model=schemas.YouTubeVideoRead, status_code=status.HTTP_201_CREATED)
def create_youtube_video(
    exercise_id: int,
    video_in: schemas.YouTubeVideoCreate,
    db: Session = Depends(get_db),
) -> models.YouTubeVideo:
    get_exercise_or_404(exercise_id, db)
    video = models.YouTubeVideo(workout_exercise_id=exercise_id, **video_in.model_dump())
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


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
