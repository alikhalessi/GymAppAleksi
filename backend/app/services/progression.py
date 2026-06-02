import re
from collections import defaultdict
from typing import Any

from app import models


def _parse_reps_floor(planned_reps: str) -> int | None:
    numbers = [int(match) for match in re.findall(r"\d+", planned_reps)]
    if not numbers:
        return None
    return min(numbers)


def _increment_for_unit(weight_unit: str) -> float:
    return 5.0 if weight_unit.lower() == "lb" else 2.5


def _build_suggestion(
    session: models.WorkoutSession,
    sets: list[models.SessionSet],
    suggestion_type: str,
    rationale: str,
    confidence: str,
    suggested_weight: float | None = None,
    suggested_reps: str = "",
) -> dict[str, Any]:
    first_set = sets[0]
    return {
        "workout_session_id": session.id,
        "workout_exercise_id": first_set.workout_exercise_id,
        "exercise_name_snapshot": first_set.exercise_name_snapshot,
        "suggestion_type": suggestion_type,
        "suggested_weight": suggested_weight,
        "weight_unit": first_set.weight_unit or "kg",
        "suggested_reps": suggested_reps,
        "rationale": rationale,
        "confidence": confidence,
    }


def _analyze_exercise_group(
    session: models.WorkoutSession,
    sets: list[models.SessionSet],
) -> dict[str, Any]:
    total_sets = len(sets)
    completed_sets = [session_set for session_set in sets if session_set.completed]
    actual_reps = [session_set.actual_reps for session_set in completed_sets if session_set.actual_reps is not None]
    actual_weights = [session_set.actual_weight for session_set in completed_sets if session_set.actual_weight is not None]
    ratings = [
        session_set.difficulty_rating
        for session_set in completed_sets
        if session_set.difficulty_rating is not None
    ]
    average_difficulty = sum(ratings) / len(ratings) if ratings else None
    highest_actual_weight = max(actual_weights) if actual_weights else None
    first_unit = sets[0].weight_unit or "kg"

    target_misses = 0
    for session_set in completed_sets:
        reps_floor = _parse_reps_floor(session_set.planned_reps)
        if reps_floor is not None and session_set.actual_reps is not None and session_set.actual_reps < reps_floor:
            target_misses += 1

    many_targets_missed = bool(completed_sets) and target_misses >= max(1, len(completed_sets) // 2)
    all_sets_completed = total_sets > 0 and len(completed_sets) == total_sets
    most_sets_completed = total_sets > 0 and len(completed_sets) / total_sets >= 0.75

    if not completed_sets or not actual_reps or highest_actual_weight is None:
        return _build_suggestion(
            session,
            sets,
            "insufficient_data",
            "Not enough completed sets with actual reps and weight to suggest progression.",
            "low",
        )

    if average_difficulty is not None and (average_difficulty >= 9 or many_targets_missed):
        increment = _increment_for_unit(first_unit)
        return _build_suggestion(
            session,
            sets,
            "reduce_weight",
            "High difficulty or missed rep targets suggest reducing load or repeating with caution.",
            "medium",
            suggested_weight=max(highest_actual_weight - increment, 0),
        )

    if all_sets_completed and average_difficulty is not None and average_difficulty <= 7:
        increment = _increment_for_unit(first_unit)
        return _build_suggestion(
            session,
            sets,
            "increase_weight",
            "All sets were completed and difficulty was manageable.",
            "high",
            suggested_weight=highest_actual_weight + increment,
        )

    if all_sets_completed and average_difficulty is not None and 7 < average_difficulty <= 8.5:
        return _build_suggestion(
            session,
            sets,
            "repeat_weight",
            "The session was completed, but difficulty suggests repeating before increasing.",
            "medium",
            suggested_weight=highest_actual_weight,
        )

    if most_sets_completed and average_difficulty is not None and 7 < average_difficulty <= 8.5:
        return _build_suggestion(
            session,
            sets,
            "repeat_weight",
            "Most sets were completed, but difficulty suggests repeating the load before increasing.",
            "medium",
            suggested_weight=highest_actual_weight,
        )

    return _build_suggestion(
        session,
        sets,
        "improve_completion",
        "Complete all planned sets before increasing load.",
        "medium",
        suggested_weight=highest_actual_weight,
        suggested_reps=sets[0].planned_reps,
    )


def generate_progression_suggestions(session: models.WorkoutSession) -> list[dict[str, Any]]:
    grouped_sets: dict[tuple[int, str], list[models.SessionSet]] = defaultdict(list)
    for session_set in session.session_sets:
        key = (session_set.workout_exercise_id, session_set.exercise_name_snapshot)
        grouped_sets[key].append(session_set)

    suggestions: list[dict[str, Any]] = []
    for sets in grouped_sets.values():
        ordered_sets = sorted(sets, key=lambda item: (item.set_number, item.id))
        suggestions.append(_analyze_exercise_group(session, ordered_sets))

    return suggestions
