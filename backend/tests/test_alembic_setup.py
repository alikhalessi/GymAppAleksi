from pathlib import Path


def test_alembic_configuration_files_exist() -> None:
    assert Path("alembic.ini").is_file()
    assert Path("alembic/env.py").is_file()
    assert Path("alembic/script.py.mako").is_file()
    assert Path("alembic/versions").is_dir()


def test_initial_migration_exists() -> None:
    migration_files = list(Path("alembic/versions").glob("*initial_schema.py"))

    assert len(migration_files) == 1
    assert "20260606_0001" in migration_files[0].read_text(encoding="utf-8")


def test_user_owned_data_migration_exists() -> None:
    migration_files = list(Path("alembic/versions").glob("*add_user_owned_data.py"))

    assert len(migration_files) == 1
    migration_text = migration_files[0].read_text(encoding="utf-8")
    assert "20260606_0002" in migration_text
    assert 'down_revision: str | None = "20260606_0001"' in migration_text
    assert "user_id" in migration_text


def test_alembic_env_uses_application_database_config() -> None:
    env_text = Path("alembic/env.py").read_text(encoding="utf-8")

    assert "from app.database import Base, get_connect_args, get_database_url" in env_text
    assert "target_metadata = Base.metadata" in env_text
    assert "get_database_url()" in env_text


def test_requirements_include_alembic_dependency() -> None:
    requirements_text = Path("requirements.txt").read_text(encoding="utf-8")

    assert "alembic" in requirements_text
