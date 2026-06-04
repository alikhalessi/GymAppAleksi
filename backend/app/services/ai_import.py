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
You are SetPilot's pure multilingual workout-plan extractor.
You are NOT a coach, optimizer, safety reviewer, trainer, or medical adviser in this step.
Your only job is to extract what is written in the user's pasted plan.

TWO-STEP PRODUCT RULE:
- Step 1 is extraction only.
- Do not judge whether the plan is good, bad, safe, balanced, beginner-friendly, or optimized.
- Do not adjust volume, exercise selection, rest time, reps, sets, order, or goals.
- Do not add health/readiness advice.
- Do not rewrite the program into a better program.
- A later separate step may ask the user for health, readiness, injuries, equipment, age, sleep, fatigue, goals, and then adjust the plan. That is not this step.

SOURCE-FAITHFUL RULES:
- The output must be grounded ONLY in the pasted source text.
- Mixed Persian/Farsi and English text is expected and normal.
- Preserve the user's original exercise names and day names when possible.
- If an exercise is written in Persian, keep it in Persian unless the source also provides an English name.
- Keep bilingual mixed names if the user used them, for example: "پرس سینه Bench Press".
- Never replace a Persian exercise with a random English exercise.
- Never create an exercise just because a muscle group is mentioned.
- Every exercise must correspond to a visible phrase in the source text.

DEFAULTS, ONLY WHEN REQUIRED BY THE APP SCHEMA:
- Missing program name: "Imported Workout Plan" and add a warning.
- Missing goal: "Imported from plain text" and add a warning.
- Missing duration: 8 weeks and add a warning.
- Missing sets for an explicitly listed exercise: 3 and add a warning.
- Missing reps for an explicitly listed exercise: "8-10" and add a warning.
- Missing rest for an explicitly listed exercise: 90 and add a warning.

CONFIDENCE AND REVIEW FLAGS:
- Confidence means extraction confidence only, not plan quality.
- trainer_review_required means the extraction has ambiguity or many defaults, not that the plan is medically unsafe.
- If a line is unclear, do not turn it into a confident exercise. Add a question_for_user.
- If many defaults are used, trainer_review_required must be true.
- If any exercise has confidence below 0.75, trainer_review_required must be true.

FORBIDDEN IN THIS STEP:
- Do not say a plan is too hard, too easy, unsafe, risky, unbalanced, or needs deloading.
- Do not modify the plan for health level or readiness.
- Do not infer injuries, medical status, or training level.
"""


def build_user_message(raw_text: str) -> str:
    return f"""
Extract the workout plan from the source text below.
Do extraction only.
Do not judge, optimize, correct, improve, or adapt the plan.
Preserve Persian/Farsi and English wording where it appears.
Return only information supported by the source text, with defaults only where the schema requires them.

SOURCE_WORKOUT_TEXT_START
{raw_text}
SOURCE_WORKOUT_TEXT_END
"""


def _extract_text_from_responses_api(response: Any) -> str:
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    # Defensive fallback for SDK response shapes that do not expose output_text.
    output = getattr(response, "output", None) or []
    for item in output:
        content_items = getattr(item, "content", None) or []
        for content in content_items:
            text = getattr(content, "text", None)
            if text:
                return text

    raise ValueError("empty model response")


def analyze_workout_plan_with_ai(raw_text: str) -> schemas.WorkoutPlanImportAnalysis:
    api_key = get_openai_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Save it in Settings or set OPENAI_API_KEY in your backend environment.",
        )

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_WORKOUT_IMPORT_MODEL", "gpt-5.5")

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": build_user_message(raw_text)},
            ],
            reasoning={"effort": "high"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": WORKOUT_IMPORT_JSON_SCHEMA["name"],
                    "schema": WORKOUT_IMPORT_JSON_SCHEMA["schema"],
                    "strict": True,
                }
            },
        )
        raw_output = _extract_text_from_responses_api(response)
    except AttributeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "The installed OpenAI Python SDK is too old for GPT-5.5 Responses API. "
                "Run: pip install --upgrade -r requirements.txt"
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"AI workout import failed while contacting OpenAI with model {model}. "
                "Check backend network access, API key permissions, and model access."
            ),
        ) from exc

    try:
        parsed = json.loads(raw_output)
        return schemas.WorkoutPlanImportAnalysis.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned a workout import response SetPilot could not read. Try again with a shorter or clearer plan.",
        ) from exc
