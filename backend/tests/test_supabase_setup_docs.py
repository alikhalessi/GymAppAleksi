from pathlib import Path

from scripts.check_database_url import build_database_url_report


DOCS_ROOT = Path(__file__).resolve().parents[2] / "docs"


def test_supabase_setup_docs_exist() -> None:
    assert (DOCS_ROOT / "SUPABASE_POSTGRES_SETUP.md").is_file()
    assert (DOCS_ROOT / "SUPABASE_VALIDATION_CHECKLIST.md").is_file()


def test_supabase_setup_docs_do_not_include_real_secret_markers() -> None:
    docs_text = "\n".join(
        [
            (DOCS_ROOT / "SUPABASE_POSTGRES_SETUP.md").read_text(encoding="utf-8"),
            (DOCS_ROOT / "SUPABASE_VALIDATION_CHECKLIST.md").read_text(encoding="utf-8"),
        ]
    )

    assert "service" + "_role" not in docs_text
    assert "eyJ" not in docs_text
    assert "SUPABASE_" + "SERVICE_ROLE_KEY" not in docs_text
    assert "YOUR_PASSWORD" in docs_text


def test_database_url_report_masks_postgres_connection_details() -> None:
    url = "postgresql://postgres:notrealvalue@db.project-ref.example.invalid:5432/postgres"

    report = "\n".join(build_database_url_report(url))

    assert "Database dialect: postgresql" in report
    assert "Driver: psycopg" in report
    assert "Host: masked" in report
    assert "Credentials: masked" in report
    assert "notrealvalue" not in report
    assert "project-ref" not in report


def test_database_url_report_keeps_sqlite_local() -> None:
    report = "\n".join(build_database_url_report("sqlite:///./setpilot.db"))

    assert "Database dialect: sqlite" in report
    assert "Host: local-file" in report
    assert "Credentials: none" in report
