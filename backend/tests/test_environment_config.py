import importlib

import app
from app.database import (
    DEFAULT_SQLITE_DATABASE_URL,
    get_connect_args,
    get_database_url,
    normalize_database_url,
)
from app.main import DEFAULT_ALLOWED_ORIGINS, get_allowed_origins


def test_database_url_defaults_to_local_sqlite(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("SETPILOT_DATABASE_URL", raising=False)

    assert get_database_url() == DEFAULT_SQLITE_DATABASE_URL


def test_database_url_prefers_phase_2_database_url(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./phase2.db")
    monkeypatch.setenv("SETPILOT_DATABASE_URL", "sqlite:///./legacy.db")

    assert get_database_url() == "sqlite:///./phase2.db"


def test_database_url_keeps_legacy_override_for_local_tests(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SETPILOT_DATABASE_URL", "sqlite:///./legacy.db")

    assert get_database_url() == "sqlite:///./legacy.db"


def test_connect_args_are_sqlite_only() -> None:
    assert get_connect_args("sqlite:///./setpilot.db") == {"check_same_thread": False}
    assert get_connect_args("postgresql://example.invalid/setpilot") == {}
    assert get_connect_args("postgresql+psycopg://example.invalid/setpilot") == {}
    assert get_connect_args("postgresql+psycopg2://example.invalid/setpilot") == {}


def test_postgres_url_is_normalized_for_sqlalchemy(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgres://user:password@example.invalid:5432/setpilot")

    assert get_database_url() == "postgresql+psycopg://user:password@example.invalid:5432/setpilot"


def test_bare_postgresql_url_uses_selected_psycopg_driver(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:password@example.invalid:5432/setpilot")

    assert get_database_url() == "postgresql+psycopg://user:password@example.invalid:5432/setpilot"


def test_supported_postgresql_driver_urls_are_preserved() -> None:
    assert (
        normalize_database_url("postgresql+psycopg://user:password@example.invalid/setpilot")
        == "postgresql+psycopg://user:password@example.invalid/setpilot"
    )
    assert (
        normalize_database_url("postgresql+psycopg2://user:password@example.invalid/setpilot")
        == "postgresql+psycopg2://user:password@example.invalid/setpilot"
    )


def test_app_package_imports_without_postgresql_server() -> None:
    assert importlib.import_module(app.__name__) is app


def test_allowed_origins_default_to_local_frontend(monkeypatch) -> None:
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)

    assert get_allowed_origins() == DEFAULT_ALLOWED_ORIGINS


def test_allowed_origins_parse_comma_separated_values(monkeypatch) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://setpilot.example, http://localhost:5173")

    assert get_allowed_origins() == ["https://setpilot.example", "http://localhost:5173"]


def test_allowed_origins_parse_bracketed_values(monkeypatch) -> None:
    monkeypatch.setenv("ALLOWED_ORIGINS", "[https://setpilot.example,http://localhost:5173]")

    assert get_allowed_origins() == ["https://setpilot.example", "http://localhost:5173"]
