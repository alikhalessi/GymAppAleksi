from fastapi import APIRouter, status

from app import schemas
from app.services import runtime_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/openai-key", response_model=schemas.OpenAIKeyStatus)
def get_openai_key_status() -> schemas.OpenAIKeyStatus:
    return schemas.OpenAIKeyStatus.model_validate(runtime_settings.get_openai_key_status())


@router.post("/openai-key", response_model=schemas.OpenAIKeyStatus)
def set_openai_key(request: schemas.OpenAIKeySetRequest) -> schemas.OpenAIKeyStatus:
    runtime_settings.set_session_openai_api_key(request.api_key)
    return schemas.OpenAIKeyStatus.model_validate(runtime_settings.get_openai_key_status())


@router.delete("/openai-key", response_model=schemas.OpenAIKeyStatus, status_code=status.HTTP_200_OK)
def clear_openai_key() -> schemas.OpenAIKeyStatus:
    runtime_settings.clear_session_openai_api_key()
    return schemas.OpenAIKeyStatus.model_validate(runtime_settings.get_openai_key_status())
