import json
import os
from typing import Any

from fastapi import HTTPException, status
from openai import OpenAI

from app import schemas
from app.services.runtime_settings import get_openai_api_key

WORKOUT_IMPORT_JSON_SCHEMA: dict[str, Any] = {
    "name": "workout_plan_import_analysis",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "parsed_plan",
            "overall_confidence",
            "warnings",
            "questions_for_user",
            "trainer_review_required",
        ],
        "properties": {
            "parsed_plan": {
                "type": "object",
                "additionalProperties": False,
                "required": ["program", "workout_days"],
                "properties": {
                    "program": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "goal", "duration_weeks"],
                        "properties": {
                            "name": {"type": "string"},
                            "goal": {"type": "string"},
                            "duration_weeks": {"type": "integer", "minimum": 1, "maximum": 104},
                        },
                    },
                    "workout_days": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["name", "day_order", "exercises"],
                            "properties": {
                                "name": {"type": "string"},
                                "day_order": {"type": "integer", "minimum": 1, "maximum": 14},
                                "exercises": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "additionalProperties": False,
                                        "required": [
                                            "movement_name",
                                            "sets",
                                            "reps",
                                            "rest_seconds",
                                            "notes",
                                            "exercise_order",
                                            "confidence",
                                            "warnings",
                                        ],
                                        "properties": {
                                            "movement_name": {"type": "string"},
                                            "sets": {"type": "integer", "minimum": 1, "maximum": 20},
                                            "reps": {"type": "string"},
                                            "rest_seconds": {"type": "integer", "minimum": 0, "maximum": 900},
                                            "notes": {"type": "string"},
                                            "exercise_order": {"type": "integer", "minimum": 1, "maximum": 100},
                                            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                            "warnings": {"type": "array", "items": {"type": "string"}},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "overall_confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "questions_for_user": {"type": "array", "items": {"type": "string"}},
            "trainer_review_required": {"type": "boolean"},
        },
    },
    "strict": True,
}

SYSTEM_INSTRUCTIONS = """
You are the AI workout plan importer for SetPilot.
Convert messy plain-text workout plans into strict structured data.

Rules:
- Preserve the user's apparent intent.
- Do not invent exotic exercises if the text is ambiguous.
- Use practical defaults only when information is missing:
  - missing program name: Imported Workout Plan
  - missing goal: Imported from plain text
  - missing duration: 8 weeks
  - missing sets: 3
  - missing reps: 8-10
  - missing rest: 90 seconds
- Put every assumption in warnings.
- Add questions_for_user when ambiguity matters.
- Set trainer_review_required true when the plan has ambiguity, high volume, unclear exercise names, missing major details, or potentially risky programming.
- This is not medical advice. Do not diagnose injuries or health conditions.
"""


def analyze_workout_plan_with_ai(raw_text: str) -> schemas.WorkoutPlanImportAnalysis:
    api_key = get_openai_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Save it in Settings or set OPENAI_API_KEY in your backend environment.",
        )

    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_WORKOUT_IMPORT_MODEL", "gpt-4.1-mini"),
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": raw_text},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": WORKOUT_IMPORT_JSON_SCHEMA["name"],
                    "schema": WORKOUT_IMPORT_JSON_SCHEMA["schema"],
                    "strict": True,
                }
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI workout import failed: {exc}",
        ) from exc

    try:
        raw_output = response.output_text
        parsed = json.loads(raw_output)
        return schemas.WorkoutPlanImportAnalysis.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI returned an invalid workout import response: {exc}",
        ) from exc
