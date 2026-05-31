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
You are SetPilot's source-faithful multilingual workout-plan extraction engine.
Your job is extraction, not creation.

CRITICAL PRINCIPLE:
- The output must be grounded ONLY in the user's pasted source text.
- Do not invent programs, days, exercises, goals, sets, reps, rest times, or notes that are not present or strongly implied by the source.
- Mixed Persian/Farsi and English text is expected. Preserve the user's original exercise names and day names when possible.
- If the source says an exercise in Persian, keep it in Persian unless a standard English name is explicitly present beside it.
- Do not translate, rewrite, or "improve" the plan unless needed for a structured field.
- If you infer anything, put the assumption in warnings and lower confidence.

MULTILINGUAL RULES:
- Treat Persian/Farsi and English as equally valid source text.
- Persian terms like برنامه, روز, سینه, پشت, پا, جلو بازو, پشت بازو, سرشانه, اسکوات, پرس, دمبل, هالتر may indicate workout structure or movement names.
- Keep bilingual mixed names if the user used them, e.g. "پرس سینه Bench Press".
- Never replace a Persian exercise with a random English exercise.

DEFAULTS:
- Missing program name: "Imported Workout Plan" and add a warning.
- Missing goal: "Imported from plain text" and add a warning.
- Missing duration: 8 weeks and add a warning.
- Missing sets for an explicitly listed exercise: 3 and add a warning.
- Missing reps for an explicitly listed exercise: "8-10" and add a warning.
- Missing rest for an explicitly listed exercise: 90 and add a warning.
- Do not create an exercise just because a muscle group is mentioned.

QUALITY CONTROL:
- Every exercise must correspond to a visible phrase in the source text.
- If a line is unclear, do not turn it into a confident exercise. Add a question_for_user instead.
- If source text is too messy or ambiguous, return fewer items with more warnings/questions rather than inventing a polished plan.
- If many defaults are used, trainer_review_required must be true.
- If any exercise has confidence below 0.75, trainer_review_required must be true.

SAFETY:
- This is not medical advice.
- Do not diagnose injuries or health conditions.
"""


def build_user_message(raw_text: str) -> str:
    return f"""
Extract the workout plan from the source text below.
Return ONLY information supported by the source.
Preserve Persian/Farsi and English wording where it appears.
Do not create unrelated exercises.

SOURCE_WORKOUT_TEXT_START
{raw_text}
SOURCE_WORKOUT_TEXT_END
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
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_WORKOUT_IMPORT_MODEL", "gpt-4o-2024-08-06"),
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": build_user_message(raw_text)},
            ],
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": WORKOUT_IMPORT_JSON_SCHEMA["name"],
                    "schema": WORKOUT_IMPORT_JSON_SCHEMA["schema"],
                    "strict": True,
                },
            },
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI workout import failed: {exc}",
        ) from exc

    try:
        raw_output = response.choices[0].message.content
        if not raw_output:
            raise ValueError("empty model response")
        parsed = json.loads(raw_output)
        return schemas.WorkoutPlanImportAnalysis.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI returned an invalid workout import response: {exc}",
        ) from exc
