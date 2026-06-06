from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_render_blueprint_exists_and_targets_backend_service() -> None:
    render_yaml = (REPO_ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "name: setpilot-api" in render_yaml
    assert "runtime: python" in render_yaml
    assert "rootDir: backend" in render_yaml
    assert "buildCommand: pip install -r requirements.txt" in render_yaml
    assert "startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT" in render_yaml
    assert "healthCheckPath: /health" in render_yaml


def test_render_blueprint_uses_dashboard_secrets() -> None:
    render_yaml = (REPO_ROOT / "render.yaml").read_text(encoding="utf-8")

    for key in (
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "YOUTUBE_API_KEY",
        "ALLOWED_ORIGINS",
        "SUPABASE_URL",
        "SUPABASE_JWKS_URL",
        "SUPABASE_JWT_SECRET",
    ):
        assert f"key: {key}" in render_yaml

    assert render_yaml.count("sync: false") >= 7
    assert "sk-" not in render_yaml
    assert "eyJ" not in render_yaml
    assert "postgresql://" not in render_yaml
    assert "postgres://" not in render_yaml
    assert "service_role" not in render_yaml


def test_render_deployment_doc_exists_with_manual_settings() -> None:
    doc_text = (REPO_ROOT / "docs" / "RENDER_BACKEND_DEPLOYMENT.md").read_text(encoding="utf-8")

    required_text = [
        "setpilot-api",
        "alikhalessi/GymAppAleksi",
        "Root directory: `backend`",
        "Build command: `pip install -r requirements.txt`",
        "Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`",
        "Health check path: `/health`",
        "DATABASE_URL",
        "ALLOWED_ORIGINS",
        "AUTH_REQUIRED",
        "Wrong Root Directory",
        "Migration Not Applied",
    ]

    for expected in required_text:
        assert expected in doc_text


def test_readme_links_render_backend_deployment_doc() -> None:
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    assert "docs/RENDER_BACKEND_DEPLOYMENT.md" in readme_text
