import json
import os
from typing import Any

from fastapi import HTTPException, status
from openai import OpenAI

from app import models
from app.services.runtime_settings import get_openai_api_key

SESSION_REFLECTION_JSON_SCHEMA: dict[str, Any] = {
    "name": "session_reflection",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "summary",
            "what_went_well",
            "what_was_difficult",
            "next_session_suggestion",
            "caution_flags",
            "trainer_review_recommended",
        ],
        "properties": {
            "summary": {"type": "string"},
            "what_went_well": {"type": "string"},
            "what_was_difficult": {"type": "string"},
            "next_session_suggestion": {"type": "string"},
            "caution_flags": {"type": "string"},
            "trainer_review_recommended": {"type": "boolean"},
        },
    },
    "strict": True,
}

SYSTEM_INSTRUCTIONS = """
You are SetPilot's AI session reflection assistant.
Analyze only the provided session data.
Do not diagnose medical conditions.
Do not give medication advice.
Do not claim certainty about injury risk.
Do not modify the workout plan.
Do not invent exercises or sets.
If data is limited, say so.
If pain, severe underperformance, very high difficulty, concerning notes, or repeated failures appear, set trainer_review_recommended true.
Keep tone direct, practical, serious, and not childish.
Output valid JSON only.
"""


def build_session_payload(session: models.WorkoutSession) -> dict[str, Any]:
    program_snapshot = ""
    workout_day_snapshot = ""
    for session_set in session.session_sets:
        if session_set.program_name_snapshot and not program_snapshot:
            program_snapshot = session_set.program_name_snapshot
        if session_set.workout_day_name_snapshot and not workout_day_snapshot:
            workout_day_snapshot = session_set.workout_day_name_snapshot

    return {
        "session_id": session.id,
        "status": session.status,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "finished_at": session.finished_at.isoformat() if session.finished_at else None,
        "readiness_score": session.readiness_score,
        "session_notes": session.notes,
        "program_snapshot": program_snapshot,
        "workout_day_snapshot": workout_day_snapshot,
        "sets": [
            {
                "exercise_name_snapshot": session_set.exercise_name_snapshot,
                "set_number": session_set.set_number,
                "planned_reps": session_set.planned_reps,
                "planned_weight": session_set.planned_weight,
                "actual_reps": session_set.actual_reps,
                "actual_weight": session_set.actual_weight,
                "weight_unit": session_set.weight_unit,
                "difficulty_rating": session_set.difficulty_rating,
                "completed": session_set.completed,
                "rest_seconds_used": session_set.rest_seconds_used,
                "planned_rest_seconds_snapshot": session_set.planned_rest_seconds_snapshot,
                "notes": session_set.notes,
            }
            for session_set in sorted(
                session.session_sets,
                key=lambda item: (item.exercise_name_snapshot, item.set_number, item.id),
            )
        ],
    }


def build_user_message(session: models.WorkoutSession) -> str:
    return json.dumps(build_session_payload(session), ensure_ascii=False, indent=2)


def _extract_text_from_responses_api(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    output = getattr(response, "output", None) or []
    for item in output:
        for content in getattr(item, "content", None) or []:
            text = getattr(content, "text", None)
            if text:
                return text

    raise ValueError("empty model response")


def get_session_reflection_model() -> str:
    return os.getenv(
        "OPENAI_SESSION_REFLECTION_MODEL",
        os.getenv("OPENAI_WORKOUT_ENHANCE_MODEL", os.getenv("OPENAI_WORKOUT_IMPORT_MODEL", "gpt-5.5")),
    )


def generate_session_reflection_with_ai(session: models.WorkoutSession) -> tuple[dict[str, Any], str]:
    api_key = get_openai_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Save it in Settings or set OPENAI_API_KEY in your backend environment.",
        )

    model = get_session_reflection_model()
    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": build_user_message(session)},
            ],
            reasoning={"effort": "high"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": SESSION_REFLECTION_JSON_SCHEMA["name"],
                    "schema": SESSION_REFLECTION_JSON_SCHEMA["schema"],
                    "strict": True,
                }
            },
        )
        raw_output = _extract_text_from_responses_api(response)
    except AttributeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The installed OpenAI Python SDK is too old for the Responses API. Run: pip install --upgrade -r requirements.txt",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"AI session reflection failed while contacting OpenAI with model {model}. "
                "Check backend network access, API key permissions, and model access."
            ),
        ) from exc

    try:
        parsed = json.loads(raw_output)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned a session reflection response SetPilot could not read. Try again after reviewing the session data.",
        ) from exc

    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned an invalid session reflection response: expected a JSON object.",
        )

    required_fields = set(SESSION_REFLECTION_JSON_SCHEMA["schema"]["required"])
    missing_fields = required_fields - set(parsed)
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI session reflection response is missing fields: {', '.join(sorted(missing_fields))}",
        )

    return parsed, model
