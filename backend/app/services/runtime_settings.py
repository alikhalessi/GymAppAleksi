import os

_session_openai_api_key: str | None = None


def set_session_openai_api_key(api_key: str) -> None:
    global _session_openai_api_key
    cleaned_key = api_key.strip()
    _session_openai_api_key = cleaned_key or None


def clear_session_openai_api_key() -> None:
    global _session_openai_api_key
    _session_openai_api_key = None


def get_openai_api_key() -> str | None:
    return _session_openai_api_key or os.getenv("OPENAI_API_KEY")


def get_openai_key_status() -> dict[str, bool | str | None]:
    if _session_openai_api_key:
        return {
            "configured": True,
            "source": "session",
            "masked_key": mask_api_key(_session_openai_api_key),
        }

    environment_key = os.getenv("OPENAI_API_KEY")
    if environment_key:
        return {
            "configured": True,
            "source": "environment",
            "masked_key": mask_api_key(environment_key),
        }

    return {"configured": False, "source": None, "masked_key": None}


def mask_api_key(api_key: str) -> str:
    if len(api_key) <= 10:
        return "***"
    return f"{api_key[:7]}...{api_key[-4:]}"
