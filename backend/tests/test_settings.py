from fastapi.testclient import TestClient

from app.main import app
from app.services import runtime_settings

client = TestClient(app)


def test_openai_key_status_empty(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    runtime_settings.clear_session_openai_api_key()

    response = client.get("/settings/openai-key")

    assert response.status_code == 200
    assert response.json() == {
        "configured": False,
        "source": None,
        "masked_key": None,
    }


def test_set_and_clear_session_openai_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    runtime_settings.clear_session_openai_api_key()

    set_response = client.post(
        "/settings/openai-key",
        json={"api_key": "sk-test1234567890abcdef"},
    )

    assert set_response.status_code == 200
    assert set_response.json()["configured"] is True
    assert set_response.json()["source"] == "session"
    assert set_response.json()["masked_key"] == "sk-test...cdef"

    status_response = client.get("/settings/openai-key")
    assert status_response.status_code == 200
    assert status_response.json()["configured"] is True
    assert status_response.json()["source"] == "session"

    clear_response = client.delete("/settings/openai-key")
    assert clear_response.status_code == 200
    assert clear_response.json()["configured"] is False
