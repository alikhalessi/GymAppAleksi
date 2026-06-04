import json
import os
from typing import Any

from fastapi import HTTPException, status
from openai import OpenAI

from app import schemas
from app.services.runtime_settings import get_openai_api_key

ENHANCE_JSON_SCHEMA: dict[str, Any] = {
    "name": "workout_plan_enhancement",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["adjusted_plan", "changes", "summary", "warnings", "questions_for_user", "trainer_review_required"],
        "properties": {
            "adjusted_plan": {
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
                                        "required": ["movement_name", "sets", "reps", "rest_seconds", "notes", "exercise_order", "confidence", "warnings"],
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
            "changes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["day_name", "exercise_name", "change_type", "original", "adjusted", "reason"],
                    "properties": {
                        "day_name": {"type": "string"},
                        "exercise_name": {"type": ["string", "null"]},
                        "change_type": {"type": "string"},
                        "original": {"type": "string"},
                        "adjusted": {"type": "string"},
                        "reason": {"type": "string"},
                    },
                },
            },
            "summary": {"type": "string"},
            "warnings": {"type": "array", "items": {"type": "string"}},
            "questions_for_user": {"type": "array", "items": {"type": "string"}},
            "trainer_review_required": {"type": "boolean"},
        },
    },
    "strict": True,
}

SYSTEM_INSTRUCTIONS = """
You are SetPilot's readiness-aware workout adjustment engine.
This is Step 2 after pure extraction. You may adapt the extracted plan using the trainee's profile, readiness, limitations, equipment, time limit, and difficulty preference.

Rules:
- Keep the original plan recognizable.
- Prefer small practical changes instead of rewriting everything.
- Every change must be listed with original, adjusted, and reason.
- Do not silently overwrite anything.
- Do not diagnose or provide medical treatment advice.
- Age, height, weight, and BMI are context signals, not labels or verdicts.
- Use BMI conservatively only to guide workload caution, movement selection, and progression pace. Never shame, classify character, or make crude assumptions from BMI alone.
- If height and weight are present but BMI is missing, you may infer approximate BMI for reasoning, but do not add fields outside the schema.
- If the user's limitations are unclear, set trainer_review_required true and ask a question.
- If energy or sleep is low, or soreness or stress is high, reduce workload sensibly.
- If equipment is missing, replace unavailable movements with reasonable alternatives.
- Preserve Persian/Farsi and English names where practical.
"""


def build_user_message(request: schemas.WorkoutPlanEnhanceRequest) -> str:
    return json.dumps(request.model_dump(), ensure_ascii=False, indent=2)


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


def enhance_workout_plan_with_ai(request: schemas.WorkoutPlanEnhanceRequest) -> schemas.WorkoutPlanEnhancementResponse:
    api_key = get_openai_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Save it in Settings or set OPENAI_API_KEY in your backend environment.",
        )

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_WORKOUT_ENHANCE_MODEL", os.getenv("OPENAI_WORKOUT_IMPORT_MODEL", "gpt-5.5"))

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": build_user_message(request)},
            ],
            reasoning={"effort": "high"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": ENHANCE_JSON_SCHEMA["name"],
                    "schema": ENHANCE_JSON_SCHEMA["schema"],
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
                f"AI workout enhancement failed while contacting OpenAI with model {model}. "
                "Check backend network access, API key permissions, and model access."
            ),
        ) from exc

    try:
        parsed = json.loads(raw_output)
        return schemas.WorkoutPlanEnhancementResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned a workout enhancement response SetPilot could not read. Try again with simpler readiness context.",
        ) from exc
