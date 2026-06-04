import json
import os
from typing import Any

from fastapi import HTTPException, status
from openai import OpenAI

from app.services.runtime_settings import get_openai_api_key

CHANGE_PROPOSAL_JSON_SCHEMA: dict[str, Any] = {
    "name": "plan_change_proposal",
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "proposal_title",
            "proposal_summary",
            "proposed_changes",
            "caution_notes",
            "trainer_review_recommended",
        ],
        "properties": {
            "proposal_title": {"type": "string"},
            "proposal_summary": {"type": "string"},
            "proposed_changes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "change_type",
                        "target",
                        "original",
                        "proposed",
                        "reason",
                        "risk_or_caution",
                    ],
                    "properties": {
                        "change_type": {"type": "string"},
                        "target": {"type": "string"},
                        "original": {"type": "string"},
                        "proposed": {"type": "string"},
                        "reason": {"type": "string"},
                        "risk_or_caution": {"type": "string"},
                    },
                },
            },
            "caution_notes": {"type": "string"},
            "trainer_review_recommended": {"type": "boolean"},
        },
    },
    "strict": True,
}

SYSTEM_INSTRUCTIONS = """
You are SetPilot's AI workout change proposal assistant.
You create proposals only.
You never mutate the plan.
You analyze only provided context.
You do not diagnose medical conditions.
You do not give medication advice.
You do not claim certainty about injury risk.
You do not invent unavailable equipment.
You preserve original plan as much as possible.
If pain, injury, severe fatigue, very high difficulty, or health limitations are mentioned, set trainer_review_recommended true.
If information is insufficient, state assumptions and ask for review.
Keep tone direct, practical, serious, and not childish.
Output valid JSON only.
"""


def get_change_proposal_model() -> str:
    return os.getenv(
        "OPENAI_CHANGE_PROPOSAL_MODEL",
        os.getenv(
            "OPENAI_WORKOUT_ENHANCE_MODEL",
            os.getenv("OPENAI_WORKOUT_IMPORT_MODEL", "gpt-5.5"),
        ),
    )


def build_user_message(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


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


def generate_change_proposal_with_ai(payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
    api_key = get_openai_api_key()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI API key is not configured. Save it in Settings or set OPENAI_API_KEY in your backend environment.",
        )

    model = get_change_proposal_model()
    client = OpenAI(api_key=api_key)

    try:
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": build_user_message(payload)},
            ],
            reasoning={"effort": "high"},
            text={
                "format": {
                    "type": "json_schema",
                    "name": CHANGE_PROPOSAL_JSON_SCHEMA["name"],
                    "schema": CHANGE_PROPOSAL_JSON_SCHEMA["schema"],
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
            detail=f"AI change proposal failed with model {model}: {exc}",
        ) from exc

    try:
        parsed = json.loads(raw_output)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI returned an invalid change proposal response: {exc}",
        ) from exc

    if not isinstance(parsed, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI returned an invalid change proposal response: expected a JSON object.",
        )

    required_fields = set(CHANGE_PROPOSAL_JSON_SCHEMA["schema"]["required"])
    missing_fields = required_fields - set(parsed)
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI change proposal response is missing fields: {', '.join(sorted(missing_fields))}",
        )

    return parsed, model
