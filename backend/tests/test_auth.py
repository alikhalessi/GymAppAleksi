import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.services import auth

client = TestClient(app)


def test_auth_status_works_without_secrets(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    monkeypatch.delenv("SUPABASE_JWKS_URL", raising=False)
    monkeypatch.delenv("AUTH_REQUIRED", raising=False)

    response = client.get("/auth/status")

    assert response.status_code == 200
    assert response.json() == {
        "auth_required": False,
        "supabase_url_configured": False,
        "jwt_secret_configured": False,
        "jwks_url_configured": False,
        "verification_configured": False,
        "verification_mode": "disabled",
    }


def test_auth_status_never_exposes_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_URL", "https://project-ref.example.invalid")
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "placeholder-jwt-value")
    monkeypatch.setenv("SUPABASE_JWKS_URL", "https://project-ref.example.invalid/auth/v1/.well-known/jwks.json")
    monkeypatch.setenv("AUTH_REQUIRED", "true")

    response = client.get("/auth/status")
    payload = response.json()

    assert response.status_code == 200
    assert payload["auth_required"] is True
    assert payload["supabase_url_configured"] is True
    assert payload["jwt_secret_configured"] is True
    assert payload["jwks_url_configured"] is True
    assert "placeholder-jwt-value" not in response.text
    assert "project-ref" not in response.text


def test_auth_me_without_token_returns_local_mode_when_auth_not_required(monkeypatch) -> None:
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    monkeypatch.setenv("AUTH_REQUIRED", "false")

    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json()["authenticated"] is False
    assert response.json()["auth_required"] is False
    assert "disabled" in response.json()["message"].lower()


def test_auth_me_without_token_returns_401_when_auth_required(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_REQUIRED", "true")

    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication required."


def test_parse_bearer_token_rejects_wrong_scheme() -> None:
    response = client.get("/auth/me", headers={"Authorization": "Basic abc123"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header must use Bearer token format."


def test_auth_me_uses_mocked_verification_without_network(monkeypatch) -> None:
    monkeypatch.setenv("SUPABASE_JWT_SECRET", "configured")
    monkeypatch.setenv("AUTH_REQUIRED", "false")

    def fake_verify(token: str) -> auth.AuthUser:
        assert token == "fake-token"
        return auth.AuthUser(
            user_id="user_123",
            email="founder@example.invalid",
            raw_claims={"sub": "user_123", "email": "founder@example.invalid"},
        )

    monkeypatch.setattr(auth, "verify_supabase_jwt", fake_verify)

    response = client.get("/auth/me", headers={"Authorization": "Bearer fake-token"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["authenticated"] is True
    assert payload["user"]["user_id"] == "user_123"
    assert payload["user"]["email"] == "founder@example.invalid"


def test_verify_supabase_jwt_with_configured_secret(monkeypatch) -> None:
    jwt_secret = "local-test-secret-with-32-byte-minimum"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", jwt_secret)
    token = jwt.encode(
        {"sub": "supabase-user-id", "email": "founder@example.invalid"},
        jwt_secret,
        algorithm="HS256",
    )

    user = auth.verify_supabase_jwt(token)

    assert user.user_id == "supabase-user-id"
    assert user.email == "founder@example.invalid"
